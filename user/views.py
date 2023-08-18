from django.shortcuts import redirect
from django.contrib.auth import login, logout, authenticate
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from user.serializers import UserSerializer


class LogInView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "user/sign_in.html"

    def get(self, request):
        return Response(status=status.HTTP_200_OK)

    def post(self, request):
        username = request.data.get("username", "")
        password = request.data.get("password", "")

        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({"error": "존재하지 않는 계정이거나 패스워드가 일치하지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)

        login(request, user)
        return redirect("task:task_list")

    def delete(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)
    

class HomeView(APIView):
    def get(self, request):
        user = request.user

        if user.is_authenticated:
            return redirect("task:task_list")
        
        return redirect("login")