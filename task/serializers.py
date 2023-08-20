from django.utils import dateformat, timezone
from rest_framework import serializers

from task.models import Task, SubTask


class SubTaskSerializer(serializers.ModelSerializer):
    str_completed_date = serializers.SerializerMethodField()

    def get_str_completed_date(self, obj):
        if obj.completed_date:
            return dateformat.format(obj.completed_date, "y-m-d H:i")
        
        return obj.completed_date
    
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        if validated_data["is_complete"] and not instance.task.is_complete:
            subtask_data = SubTask.objects.filter(task=instance.task)

            for st in subtask_data:
                if not st.is_complete:
                    break
            else:
                updated_data = {
                    "is_complete": True, 
                    "completed_date": timezone.now()
                }
                task_serializer = TaskSerializer(instance.task, updated_data, partial=True)

                if task_serializer.is_valid():
                    task_serializer.save()
        elif not validated_data["is_complete"] and instance.task.is_complete:
            updated_data = {
                "is_complete": False,
                "completed_date": None
            }
            task_serializer = TaskSerializer(instance.task, updated_data, partial=True)

            if task_serializer.is_valid():
                task_serializer.save()

        return instance

    class Meta:
          model = SubTask
          fields = [
              "id", "team", "is_complete", "completed_date", "task",  "str_completed_date"
            ]


class TaskSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    subtask = serializers.ListField(write_only=True)
    subtask_set = SubTaskSerializer(many=True, read_only=True)
    str_completed_date = serializers.SerializerMethodField()

    def get_username(self, obj):
        return obj.create_user.username
    
    def get_str_completed_date(self, obj):
        if obj.completed_date:
            return dateformat.format(obj.completed_date, "y-m-d H:i")
        
        return obj.completed_date
    
    def create(self, validated_data):
        subtask = validated_data.pop("subtask")
        task = Task.objects.create(**validated_data)

        SubTask.objects.bulk_create([SubTask(team=st, task=task) for st in subtask])

        
        return validated_data
    
    def update(self, instance, validated_data):
        subtask = validated_data.pop("subtask", [])
        uncomplete_subtask_data = SubTask.objects.filter(task=instance, is_complete=False)

        if subtask:
            validated_data["is_complete"] = False
            validated_data["completed_date"] = None
        elif not uncomplete_subtask_data and not instance.is_complete:
            validated_data["is_complete"] = True
            validated_data["completed_date"] = timezone.now()

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        SubTask.objects.bulk_create([SubTask(team=st, task=instance) for st in subtask])

        return instance

    class Meta:
        model = Task
        fields = [
            "id", "create_user", "team", "title", "content","is_complete", 
            "completed_date", "created_at", "username", "subtask_set", "subtask", 
            "str_completed_date"
        ]
