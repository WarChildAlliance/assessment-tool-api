from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase
from users.models import User


class StudentTests(APITestCase):
    """
    User tests from a student account.
    """
    fixtures = ['users.json']

    def setUp(self):
        """
        Set up authentication.
        """
        token = Token.objects.get(user__username='111111')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_get_all_users(self):
        """
        Ensure that students cannot get the list of users.
        """
        url = reverse('user-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)


    def test_get_supervisor(self):
        """
        Ensure that students cannot get supervisor data.
        """
        url = reverse('user-detail', args=[4])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

    def test_get_student_self(self):
        """
        Ensure that students can get their data.
        """
        url = reverse('user-detail', args=[1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_student_other(self):
        """
        Ensure that students cannot get other student data.
        """
        url = reverse('user-detail', args=[2])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

    def test_create_user(self):
        """
        Ensure that students cannot create a user.
        """
        url = reverse('user-list')
        data = {'first_name': 'Neville', 'last_name': 'Longbottom', 'country': 'JOR',
                'language': 'en', 'role': 'STUDENT'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)
    
    def test_edit_supervisor(self):
        """
        Ensure that students cannot edit a supervisor.
        """
        url = reverse('user-detail', args=[4])
        data = {'first_name': 'Regulus'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_edit_student_self(self):
        """
        Ensure that students can edit their own data.
        """
        url = reverse('user-detail', args=[1])
        data = {'first_name': 'James'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(id=1)
        self.assertEqual(user.first_name, 'James')
        self.assertFalse(user.has_usable_password())

    def test_edit_student_other(self):
        """
        Ensure that students cannot edit other student data.
        """
        url = reverse('user-detail', args=[3])
        data = {'first_name': 'Ginny'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 403)
        user = User.objects.get(id=3)
        self.assertEqual(user.first_name, 'Ron')

    def test_delete_user(self):
        """
        Ensure that students cannot delete a user (even themselves).
        """
        url = reverse('user-detail', args=[1])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 403)

    def test_update_student_code(self):
        """
        Ensure that students cannot update a student code.
        """
        url = reverse('user-update-student-code', args=[1])
        previous_username = User.objects.get(id=1).username
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)
        new_username = User.objects.get(id=1).username
        self.assertEqual(previous_username, new_username)
