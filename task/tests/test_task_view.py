from rest_framework.test import APITestCase, APIClient

from task.models import Task, SubTask
from user.models import User
from danbi_edu.const import team_choices


class TaskViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = "/task/list"

        cls.anonymous_client = APIClient()
        cls.authenticated_client = APIClient()
        cls.same_team_user_client = APIClient()
        cls.other_team_user_client = APIClient()

        user_data = {
            "username": "usertest",
            "password": "usertest",
            "team": team_choices[0][0]
        }
        cls.user = User.objects.create_user(**user_data)

        cls.task_list = [
            Task.objects.create(
                create_user=cls.user,
                team=cls.user.team,
                title=f"test title {i}",
                content=f"test content {i}"
            ) for i in range(3)
        ]
        cls.subtask_list = [
            SubTask.objects.create(
                team=team_choices[i][0],
                task=cls.task_list[i]
            ) for i in range(3)
        ]
        cls.subtask_list.append(
            SubTask.objects.create(
                team=team_choices[1][0],
                task=cls.task_list[0]
            )
        )

        same_team_user_data = {
            "username": "sameteamuser",
            "password": "usertest",
            "team": team_choices[0][0]
        }
        cls.same_team_user = User.objects.create_user(**same_team_user_data)
        other_team_user_data = {
            "username": "otherteamuser",
            "password": "usertest",
            "team": team_choices[1][0]
        }
        cls.other_team_user = User.objects.create_user(**other_team_user_data)

        cls.authenticated_client.force_authenticate(user=cls.user)
        cls.same_team_user_client.force_authenticate(user=cls.same_team_user)
        cls.other_team_user_client.force_authenticate(user=cls.other_team_user)

    def test_anonymous_user(self):
        response = self.anonymous_client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user(self):
        response = self.authenticated_client.get(self.url)
        self.assertEqual(len(response.data["tasks"]), len(self.task_list))

    def test_assigned_list(self):
        response = self.authenticated_client.get(f"{self.url}?filter=assigned")
        self.assertEqual(len(response.data["tasks"]), 1)

    def test_my_list(self):
        response = self.authenticated_client.get(f"{self.url}?filter=my")
        self.assertEqual(len(response.data["tasks"]), len(self.task_list))

    def test_same_team_user(self):
        response = self.same_team_user_client.get(self.url)
        self.assertEqual(len(response.data["tasks"]), len(self.task_list))

    def test_same_team_user_assigned_list(self):
        response = self.same_team_user_client.get(f"{self.url}?filter=assigned")
        self.assertEqual(len(response.data["tasks"]), 1)

    def test_same_team_user_my_list(self):
        response = self.same_team_user_client.get(f"{self.url}?filter=my")
        self.assertEqual(len(response.data["tasks"]), 0)

    def test_other_team_user(self):
        response = self.other_team_user_client.get(self.url)
        self.assertEqual(len(response.data["tasks"]), len(self.task_list))

    def test_other_team_user_assigned_list(self):
        response = self.other_team_user_client.get(f"{self.url}?filter=assigned")
        self.assertEqual(len(response.data["tasks"]), 2)

    def test_other_team_user_my_list(self):
        response = self.other_team_user_client.get(f"{self.url}?filter=my")
        self.assertEqual(len(response.data["tasks"]), 0)
