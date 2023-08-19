from django.utils import timezone
from django.shortcuts import redirect
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from task.models import Task, SubTask
from task.serializers import TaskSerializer, SubTaskSerializer
from user.models import User
from danbi_edu.const import team_choices


class TaskView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "task/task_list.html"

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return redirect("login")
        
        filter = request.GET.get("filter", None)

        if filter == "assigned":
            pass
        elif filter == "my":
            pass
        else:
            task_data = Task.objects.all().order_by("-created_at")
        
        serialized_task_data = TaskSerializer(task_data, many=True).data

        return Response({'tasks': serialized_task_data}, status=status.HTTP_200_OK)
    

class TaskRegisterView(APIView):
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
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "task/task_manage.html"

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return redirect("login")
        
        task = request.GET.get("task", None)
        if not task:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        task_data = Task.objects.get(id=task)
        serialized_task_data = TaskSerializer(task_data).data

        return_data = {
            "teams": team_choices,
            "task": serialized_task_data
        }

        return Response(return_data, status=status.HTTP_200_OK)
    
    def put(self, request):
        data = request.data.copy()
        data["subtask"] = data.pop("addSubtask").values()

        task_data = Task.objects.get(id=data["id"])

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


class SubTaskView(APIView):
    def put(self, request):
        data = request.data.copy()
        if data["is_complete"]:
            data["completed_date"] = timezone.now()
        else:
            data["completed_date"] = None

        try:
            subtask_data = SubTask.objects.get(id=data["subtaskId"])
        except SubTask.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        subtask_serializer = SubTaskSerializer(subtask_data, data, partial=True)

        if subtask_serializer.is_valid():
            subtask_serializer.save()

            task_id = subtask_serializer.data["task"]
            is_task_complete = subtask_serializer.data["is_task_complete"]

            if data["is_complete"] and not is_task_complete:
                subtask_data = SubTask.objects.filter(task_id=task_id)

                for st in subtask_data:
                    if not st.is_complete:
                        break
                else:
                    updated_data = {
                        "is_complete": True, 
                        "completed_date": timezone.now()
                    }
                    task_data = Task.objects.get(id=task_id)
                    task_serializer = TaskSerializer(task_data, updated_data, partial=True)

                    if task_serializer.is_valid():
                        task_serializer.save()

            elif not data["is_complete"] and is_task_complete:
                updated_data = {
                    "is_complete": False,
                    "completed_date": None
                }
                task_data = Task.objects.get(id=task_id)
                task_serializer = TaskSerializer(task_data, updated_data, partial=True)

                if task_serializer.is_valid():
                    task_serializer.save()

            return Response({"message": "정상"}, status=status.HTTP_200_OK)
        
        return Response(subtask_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
