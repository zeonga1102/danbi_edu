from rest_framework.test import APITestCase

from user.models import User
from danbi_edu.const import team_choices


class SignupTest(APITestCase):
    def setUp(self):
        self.data = {
            "username": "usertest",
            "password": "usertest",
            "team": team_choices[0][0]
        }

    def test_signup(self):
        response = self.client.post("/signup", self.data)
        self.assertEqual(response.status_code, 302)


class LoginTest(APITestCase):
    def setUp(self):
        self.data = {
            "username": "usertest",
            "password": "usertest",
            "team": team_choices[0][0]
        }
        self.user = User.objects.create_user(**self.data)

    def test_login(self):
        response = self.client.post("/login", self.data)
        self.assertEqual(response.status_code, 302)