from django.urls import path
from task import views

app_name = "task"

urlpatterns = [
    path("list", views.TaskView.as_view(), name="task_list"),
    path("register", views.TaskRegisterView.as_view(), name="task_register"),
    path("manage", views.TaskManageView.as_view(), name="task_manage"),
    path("subtask", views.SubTaskView.as_view(), name="subtask"),
]