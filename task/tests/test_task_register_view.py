from rest_framework.test import APITestCase, APIClient

from user.models import User
from danbi_edu.const import team_choices


class TaskRegisterViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = "/task/register"

        cls.anonymous_client = APIClient()
        cls.authenticated_client = APIClient()

        user_data = {
            "username": "usertest",
            "password": "usertest",
            "team": team_choices[0][0]
        }
        cls.user = User.objects.create_user(**user_data)
        cls.authenticated_client.force_authenticate(user=cls.user)

    def setUp(self):
        self.task_data = {
            "title": "test title",
            "content": "test content",
            "subtask": [team_choices[0][0]]
        }

    def test_anonymous_user_get(self):
        response = self.anonymous_client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_get(self):
        response = self.authenticated_client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_post(self):
        response = self.anonymous_client.post(self.url)
        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_without_data_post(self):
        response = self.authenticated_client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_success_post(self):
        response = self.authenticated_client.post(self.url, self.task_data)
        self.assertEqual(response.status_code, 200)
    
    def test_fail_without_title_post(self):
        del self.task_data["title"]

        response = self.authenticated_client.post(self.url, self.task_data)
        self.assertEqual(response.status_code, 400)

    def test_fail_without_content_post(self):
        del self.task_data["content"]

        response = self.authenticated_client.post(self.url, self.task_data)
        self.assertEqual(response.status_code, 400)

    def test_fail_without_subtask_post(self):
        del self.task_data["subtask"]

        response = self.authenticated_client.post(self.url, self.task_data)
        self.assertEqual(response.status_code, 400)
