from rest_framework import serializers

from task.models import Task, SubTask


class SubTaskSerializer(serializers.ModelSerializer):
     class Meta:
          model = SubTask
          fields = ["team", "is_complete", "completed_date"]


class TaskSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    subtask = serializers.ListField()
    subtask_set = SubTaskSerializer(many=True, read_only=True)

    def get_username(self, obj):
        return obj.create_user.username
    
    
    def create(self, validated_data):
        subtask = validated_data.pop("subtask")
        task = Task.objects.create(**validated_data)

        for st in subtask:
            SubTask(team=st, task=task).save()
        
        return validated_data

    class Meta:
        model = Task
        fields = ["id", "create_user", "team", "title", "content","is_complete", "complete_date", "created_at", "username", "subtask_set", "subtask"]

        extra_kwargs = {
            "subtask": {"write_only": True}
        }
