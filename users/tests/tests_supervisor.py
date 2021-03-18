from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase
from users.models import User


class SupervisorTests(APITestCase):
    """
    User tests from a supervisor account.
    """
    fixtures = ['users.json']

    def setUp(self):
        """
        Set up authentication.
        """
        token = Token.objects.get(user__username='supervisor')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_get_all_users(self):
        """
        Ensure that supervisors can get the list of users.
        """
        url = reverse('user-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

    def test_get_supervisors(self):
        """
        Ensure that supervisors can get the list of supervisors.
        """
        url = reverse('user-list') + '?groups__name=Supervisor'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_get_supervisor_self(self):
        """
        Ensure that supervisors can get their own data.
        """
        url = reverse('user-detail', args=[4])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_supervisor_other(self):
        """
        Ensure that supervisors cannot get other supervisor data.
        """
        url = reverse('user-detail', args=[5])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

    def test_create_student(self):
        """
        Ensure that supervisors can create a student.
        """
        url = reverse('user-list')
        data = {'first_name': 'Neville', 'last_name': 'Longbottom', 'country': 'JOR',
                'language': 'en', 'group': 'Student'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertRegex(response.data['username'], r'\d{6,}')
        user = User.objects.get(id=response.data['id'])
        self.assertFalse(user.has_usable_password())
        self.assertEqual(user.groups.name, 'Student')

    def test_create_supervisor(self):
        """
        Ensure that supervisors can create a supervisor.
        """
        url = reverse('user-list')
        data = {'first_name': 'Albus', 'last_name': 'Dumbledore', 'country': 'JOR', 'language': 'en',
                'group': 'Supervisor', 'email': 'albus@yopmail.com', 'password': 'alohomora'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertRegex(response.data['username'], 'albus@yopmail.com')
        user = User.objects.get(id=response.data['id'])
        self.assertTrue(user.has_usable_password())
        self.assertEqual(user.groups.name, 'Supervisor')

    def test_edit_student(self):
        """
        Ensure that supervisors can edit a student.
        """
        url = reverse('user-detail', args=[1])
        data = {'first_name': 'James'}
        previous_username = User.objects.get(id=1).username
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(id=1)
        self.assertEqual(user.first_name, 'James')
        self.assertFalse(user.has_usable_password())
        self.assertEqual(user.username, previous_username)

    def test_edit_supervisor_self(self):
        """
        Ensure that supervisors can edit their own data.
        """
        url = reverse('user-detail', args=[4])
        data = {'first_name': 'Regulus', 'password': 'alohomora'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(id=4)
        self.assertEqual(user.first_name, 'Regulus')
        self.assertTrue(user.has_usable_password())
        self.assertTrue(user.check_password('alohomora'))

    def test_edit_supervisor_other(self):
        """
        Ensure that supervisors cannot edit other supervisor data.
        """
        url = reverse('user-detail', args=[5])
        data = {'last_name': 'Greyback'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_delete_student(self):
        """
        Ensure that supervisors can delete a student.
        """
        url = reverse('user-detail', args=[1])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 204)
        users = User.objects.filter(id=1)
        self.assertEqual(len(users), 0)

    def test_delete_supervisor_self(self):
        """
        Ensure that supervisors can delete themselves.
        """
        url = reverse('user-detail', args=[4])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 204)
        users = User.objects.filter(id=4)
        self.assertEqual(len(users), 0)

    def test_delete_supervisor_other(self):
        """
        Ensure that supervisors cannot delete another supervisor.
        """
        url = reverse('user-detail', args=[5])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 403)
        users = User.objects.filter(id=5)
        self.assertEqual(len(users), 1)

    def test_update_student_code_on_student(self):
        """
        Ensure that supervisors can update a student code.
        """
        url = reverse('user-update-student-code', args=[1])
        previous_username = User.objects.get(id=1).username
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        new_username = User.objects.get(id=1).username
        self.assertNotEqual(previous_username, new_username)
        self.assertEqual(response.data, new_username)

    def test_update_student_code_on_supervisor(self):
        """
        Ensure that supervisors cannot update a student code on a supervisor.
        """
        url = reverse('user-update-student-code', args=[4])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 400)
