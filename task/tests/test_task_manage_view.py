from django.utils import timezone
from rest_framework.test import APITestCase, APIClient

from task.models import Task, SubTask
from user.models import User
from danbi_edu.const import team_choices


class TaskManageViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = "/task/manage"

        cls.anonymous_client = APIClient()
        cls.authenticated_client = APIClient()
        cls.other_client = APIClient()

        user_data = {
            "username": "usertest",
            "password": "usertest",
            "team": team_choices[0][0]
        }
        cls.user = User.objects.create_user(**user_data)
        cls.authenticated_client.force_authenticate(user=cls.user)

        user_data["username"] = "otheruser"
        cls.other_user = User.objects.create_user(**user_data)
        cls.other_client.force_authenticate(user=cls.other_user)

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

        self.completed_task = Task.objects.create(
            create_user=self.user,
            team=self.user.team,
            title="test title",
            content="test content",
            is_complete=True,
            completed_date=timezone.now()
        )

        self.completed_subtask_list = [
            SubTask.objects.create(
                team=team_choices[0][0],
                task=self.completed_task,
                is_complete=True,
                completed_date=timezone.now()
            ),
            SubTask.objects.create(
                team=team_choices[1][0],
                task=self.completed_task,
                is_complete=True,
                completed_date=timezone.now()
            )
        ]

        self.updated_data = {
            "id": self.task.id,
            "title": "updated title",
            "content": "updated content",
            "addSubtask": [],
            "editSubtask": {},
            "deleteSubtask": []
        }

    def test_anonymous_user_get(self):
        response = self.anonymous_client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_success_get(self):
        response = self.authenticated_client.get(f"{self.url}?task={self.task.id}")

        task = response.data["task"]
        subtask = task["subtask_set"][0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(task["title"], self.task.title)
        self.assertEqual(task["content"], self.task.content)
        self.assertEqual(subtask["team"], self.subtask_list[0].team)

    def test_fail_without_query_string_get(self):
        response = self.authenticated_client.get(self.url)
        self.assertEqual(response.status_code, 400)

    def test_fail_not_exist_task_get(self):
        response = self.authenticated_client.get(f"{self.url}?task=99999999")
        self.assertEqual(response.status_code, 404)

    def test_anonymous_user_put(self):
        response = self.anonymous_client.put(self.url)
        self.assertEqual(response.status_code, 401)
    
    def test_success_put(self):
        response = self.authenticated_client.put(self.url, self.updated_data, format="json")

        updated_task = Task.objects.get(id=self.task.id)
        updated_subtask = SubTask.objects.filter(task=updated_task)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated_task.title, self.updated_data["title"])
        self.assertEqual(updated_task.content, self.updated_data["content"])

        self.assertEqual(len(updated_subtask), len(self.subtask_list))
        for ust, st in zip(updated_subtask, self.subtask_list):
            self.assertEqual(ust.id, st.id)
            self.assertEqual(ust.team, st.team)
            self.assertEqual(ust.is_complete, st.is_complete)

    def test_success_with_add_subtask_put(self):
        self.updated_data["addSubtask"] = [team_choices[2][0]]
        response = self.authenticated_client.put(self.url, self.updated_data, format="json")

        updated_task = Task.objects.get(id=self.task.id)
        updated_subtask = SubTask.objects.filter(task=updated_task)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated_task.title, self.updated_data["title"])
        self.assertEqual(updated_task.content, self.updated_data["content"])

        self.assertEqual(len(updated_subtask), len(self.subtask_list) + 1)
        for ust, st in zip(updated_subtask, self.subtask_list):
            self.assertEqual(ust.id, st.id)
            self.assertEqual(ust.team, st.team)
            self.assertEqual(ust.is_complete, st.is_complete)
        
        self.assertEqual(updated_subtask[2].team, team_choices[2][0])

    def test_success_with_edit_subtask_put(self):
        self.updated_data["editSubtask"] = {
                self.subtask_list[0].id: team_choices[3][0],
                self.subtask_list[1].id: team_choices[4][0]
            }
        response = self.authenticated_client.put(self.url, self.updated_data, format="json")

        updated_task = Task.objects.get(id=self.task.id)
        updated_subtask = SubTask.objects.filter(task=updated_task)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated_task.title, self.updated_data["title"])
        self.assertEqual(updated_task.content, self.updated_data["content"])

        self.assertEqual(len(updated_subtask), len(self.subtask_list))
        for ust, st in zip(updated_subtask, self.subtask_list):
            self.assertEqual(ust.id, st.id)
            if ust.id == 1:
                self.assertEqual(ust.team, st.team)
            else:
                self.assertEqual(ust.team, self.updated_data["editSubtask"][st.id])
            self.assertEqual(ust.is_complete, st.is_complete)

    def test_success_with_delete_subtask_put(self):
        self.updated_data["deleteSubtask"] = [ st.id for st in self.subtask_list ]
        response = self.authenticated_client.put(self.url, self.updated_data, format="json")

        updated_task = Task.objects.get(id=self.task.id)
        updated_subtask = SubTask.objects.filter(task=updated_task)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated_task.title, self.updated_data["title"])
        self.assertEqual(updated_task.content, self.updated_data["content"])

        self.assertEqual(len(updated_subtask), 1)
        for ust, st in zip(updated_subtask, self.subtask_list):
            self.assertEqual(ust.id, st.id)
            self.assertEqual(ust.team, st.team)
            self.assertEqual(ust.is_complete, st.is_complete)

    def test_success_change_task_is_complete_true_put(self):
        self.updated_data["deleteSubtask"] = [ st.id for st in self.subtask_list ]
        response = self.authenticated_client.put(self.url, self.updated_data, format="json")

        updated_task = Task.objects.get(id=self.task.id)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(updated_task.is_complete)
        self.assertIsNotNone(updated_task.completed_date)

    def test_success_change_task_is_complete_false_put(self):
        self.updated_data["id"] = self.completed_task.id
        self.updated_data["addSubtask"] = [ team_choices[0][0] ]

        response = self.authenticated_client.put(self.url, self.updated_data, format="json")

        updated_task = Task.objects.get(id=self.completed_task.id)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(updated_task.is_complete)
        self.assertIsNone(updated_task.completed_date)

    def test_fail_not_exist_task_put(self):
        self.updated_data["id"] = 99999999
        response = self.authenticated_client.put(self.url, self.updated_data, format="json")

        self.assertEqual(response.status_code, 404)

    def test_fail_without_title_put(self):
        self.updated_data["title"] = None
        response = self.authenticated_client.put(self.url, self.updated_data, format="json")

        self.assertEqual(response.status_code, 400)

    def test_fail_other_user_put(self):
        response = self.other_client.put(self.url, self.updated_data, format="json")
        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_delete(self):
        response = self.anonymous_client.delete(self.url)
        self.assertEqual(response.status_code, 401)

    def test_success_delete(self):
        response = self.authenticated_client.delete(f"{self.url}?task={self.task.id}")
        self.assertEqual(response.status_code, 200)

    def test_other_user_delete(self):
        response = self.other_client.delete(f"{self.url}?task={self.task.id}")
        self.assertEqual(response.status_code, 403)

    def test_fail_not_exist_task_delete(self):
        response = self.authenticated_client.delete(f"{self.url}?task=9999999")
        self.assertEqual(response.status_code, 404)

    def test_fail_without_query_string_delete(self):
        response = self.authenticated_client.delete(self.url)
        self.assertEqual(response.status_code, 400)

    def test_fail_completed_task_delete(self):
        response = self.authenticated_client.delete(f"{self.url}?task={self.completed_task.id}")
        self.assertEqual(response.status_code, 400)

    