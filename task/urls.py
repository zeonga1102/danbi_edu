from django.urls import path
from task import views

app_name = "task"

urlpatterns = [
    path("list", views.TaskView.as_view(), name="task_list"),
    path("register", views.TaskRegisterView.as_view(), name="task_register"),
]