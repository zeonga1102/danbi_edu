from django.shortcuts import redirect
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from task.models import Task, SubTask
from task.serializers import TaskSerializer
from user.models import User
from danbi_edu.const import team_choices


class TaskView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "task/task_list.html"

    def get(self, request):
        user = request.user

        if user.is_authenticated:
            return Response(status=status.HTTP_200_OK)
        
        return redirect("login")
    

class TaskRegisterView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "task/task_register.html"

    def get(self, request):
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
