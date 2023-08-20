from django.utils import timezone
from django.shortcuts import redirect
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from task.models import Task, SubTask
from task.serializers import TaskSerializer, SubTaskSerializer
from user.models import User
from danbi_edu.permissions import IsAuthenticatedOrIsReadOnly
from danbi_edu.const import team_choices


class TaskView(APIView):
    permission_classes = [IsAuthenticatedOrIsReadOnly]

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "task/task_list.html"

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return redirect("login")
        
        filter = request.GET.get("filter", None)

        if filter == "assigned":
            task_data = Task.objects.filter(subtask__team=user.team).prefetch_related("subtask_set").select_related("create_user").distinct().order_by("-created_at")
        elif filter == "my":
            task_data = Task.objects.filter(create_user=user).select_related("create_user").prefetch_related("subtask_set").order_by("-created_at")
        else:
            task_data = Task.objects.all().select_related("create_user").prefetch_related("subtask_set").order_by("-created_at")
        
        serialized_task_data = TaskSerializer(task_data, many=True).data

        return Response({'tasks': serialized_task_data}, status=status.HTTP_200_OK)
    

class TaskRegisterView(APIView):
    permission_classes = [IsAuthenticatedOrIsReadOnly]

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "task/task_register.html"

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return redirect("login")
        
        return Response({"teams": team_choices}, status=status.HTTP_200_OK)
    
    def post(self, request):
        data = request.data.copy()
        data["create_user"] = request.user.id
        data["team"] = User.objects.get(id=request.user.id).team

        task_serializer = TaskSerializer(data=data)
        if task_serializer.is_valid():
            task_serializer.save()
            return Response({"message": "정상"}, status=status.HTTP_200_OK)
        
        return Response(task_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TaskManageView(APIView):
    permission_classes = [IsAuthenticatedOrIsReadOnly]

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "task/task_manage.html"

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return redirect("login")
        
        task = request.GET.get("task", None)
        if not task:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        task_data = Task.objects.filter(id=task).select_related("create_user").prefetch_related("subtask_set")
        if not task_data:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serialized_task_data = TaskSerializer(task_data.first()).data

        return_data = {
            "teams": team_choices,
            "task": serialized_task_data
        }

        return Response(return_data, status=status.HTTP_200_OK)
    
    def put(self, request):
        data = request.data.copy()
        data["subtask"] = data.pop("addSubtask")

        task_data = Task.objects.filter(id=data["id"]).select_related("create_user").prefetch_related("subtask_set")
        if not task_data:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        task_data = task_data.first()
        
        if task_data.create_user != request.user:
            return Response({"message": "권한 없음"}, status=status.HTTP_403_FORBIDDEN)

        SubTask.objects.filter(id__in=data["deleteSubtask"], is_complete=False).delete()
        subtask_data = SubTask.objects.filter(id__in=list(map(int, data["editSubtask"].keys())), is_complete=False)
        for sd in subtask_data:
            sd.team = data["editSubtask"][f"{sd.id}"]
        SubTask.objects.bulk_update(subtask_data, ["team"])

        task_serializer = TaskSerializer(task_data, data, partial=True)
        if task_serializer.is_valid():
            task_serializer.save()

            return Response({"message": "정상"}, status=status.HTTP_200_OK)

        return Response(task_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        task_id = request.GET.get("task", None)
        if not task_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        task = Task.objects.filter(id=int(task_id)).select_related("create_user").prefetch_related("subtask_set")
        if not task:
            return Response(status=status.HTTP_404_NOT_FOUND)

        task = task.first()

        if task.create_user != request.user:
            return Response({"message": "권한 없음"}, status=status.HTTP_403_FORBIDDEN)

        if task.is_complete:
            return Response({"message": "완료된 업무는 삭제 불가"}, status=status.HTTP_400_BAD_REQUEST)
        
        task.delete()
        return Response({"message": "정상"}, status=status.HTTP_200_OK)


class SubTaskView(APIView):
    permission_classes = [IsAuthenticatedOrIsReadOnly]

    def put(self, request):
        data = request.data.copy()
        data["is_complete"] = data.pop("isComplete")

        if data["is_complete"]:
            data["completed_date"] = timezone.now()
        else:
            data["completed_date"] = None

        try:
            subtask_data = SubTask.objects.get(id=data["subtaskId"])
        except SubTask.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if subtask_data.team != request.user.team:
            return Response({"message": "권한 없음"}, status=status.HTTP_403_FORBIDDEN)

        subtask_serializer = SubTaskSerializer(subtask_data, data, partial=True)

        if subtask_serializer.is_valid():
            subtask_serializer.save()

            return Response({"message": "정상"}, status=status.HTTP_200_OK)
        
        return Response(subtask_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
