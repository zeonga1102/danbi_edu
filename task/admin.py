from django.contrib import admin

from task.models import Task, SubTask


admin.site.register(Task)
admin.site.register(SubTask)