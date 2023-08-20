from django.utils import timezone
from rest_framework.test import APITestCase, APIClient

from task.models import Task, SubTask
from user.models import User
from danbi_edu.const import team_choices


class SubTaskViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = "/task/subtask"

        cls.anonymous_client = APIClient()
        cls.authenticated_client = APIClient()
        cls.other_team_client = APIClient()

        user_data = {
            "username": "usertest",
            "password": "usertest",
            "team": team_choices[0][0]
        }
        cls.user = User.objects.create_user(**user_data)
        cls.authenticated_client.force_authenticate(user=cls.user)

        user_data["username"] = "otheruser"
        user_data["team"] = team_choices[1][0]
        cls.other_team_user = User.objects.create_user(**user_data)
        cls.other_team_client.force_authenticate(user=cls.other_team_user)

    def setUp(self):
        self.task = Task.objects.create(
            create_user=self.user,
            team=self.user.team,
            title="test title",
            content="test content"
        )

        self.subtask_list = [
            SubTask.objects.create(
                team=team_choices[0][0],
                task=self.task,
                is_complete=True,
                completed_date=timezone.now()
            ),
            SubTask.objects.create(
                team=team_choices[1][0],
                task=self.task
            )
        ]

        self.updated_data = {
            "subtaskId": self.subtask_list[0].id,
            "isComplete": False
        }

    def test_anonymous_user_put(self):
        response = self.anonymous_client.put(self.url)
        self.assertEqual(response.status_code, 401)

    def test_success_put(self):
        response = self.authenticated_client.put(self.url, self.updated_data, format="json")
        
        updated_subtask_data = SubTask.objects.get(id=self.updated_data["subtaskId"])
        self.assertEqual(response.status_code, 200)
        self.assertFalse(updated_subtask_data.is_complete)
    
    def test_success_other_team_user_put(self):
        self.updated_data["subtaskId"] = self.subtask_list[1].id
        self.updated_data["isComplete"] = True

        response = self.other_team_client.put(self.url, self.updated_data, format="json")
        
        updated_subtask_data = SubTask.objects.get(id=self.updated_data["subtaskId"])
        self.assertEqual(response.status_code, 200)
        self.assertTrue(updated_subtask_data.is_complete)

    def test_success_change_task_is_complete_true_put(self):
        self.updated_data["subtaskId"] = self.subtask_list[1].id
        self.updated_data["isComplete"] = True

        response = self.other_team_client.put(self.url, self.updated_data, format="json")
        
        task_data = Task.objects.get(id=self.task.id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(task_data.is_complete)
        self.assertIsNotNone(task_data.completed_date)

    def test_success_change_task_is_complete_false_put(self):
        response = self.authenticated_client.put(self.url, self.updated_data, format="json")

        task_data = Task.objects.get(id=self.task.id)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(task_data.is_complete)
        self.assertIsNone(task_data.completed_date)

    def test_fail_not_exist_subtask_put(self):
        self.updated_data["subtaskId"] = 99999999
        response = self.authenticated_client.put(self.url, self.updated_data, format="json")

        self.assertEqual(response.status_code, 404)

    def test_fail_other_team_user_put(self):
        response = self.other_team_client.put(self.url, self.updated_data, format="json")
        self.assertEqual(response.status_code, 403)
