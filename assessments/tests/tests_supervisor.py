from assessments.models import Assessment
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class AssessmentsSupervisorTests(APITestCase):
    """
    Assessment tests from a supervisor account.
    """
    fixtures = ['languages_countries.json', 'users.json',
                'assessments.json', 'assessments_access.json']

    def setUp(self):
        """
        Set up authentication.
        """
        token = Token.objects.get(user__username='supervisor')  # id: 4
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    # ASSESSMENTS

    def test_get_all_assessments(self):
        """
        Ensure that supervisors can get the list of assessments (public or created by them).
        """
        url = reverse('assessments-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_get_assessment(self):
        """
        Ensure that supervisors can get one assessment they have access to.
        """
        url = reverse('assessments-detail', args=[2])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_assessment_no_access(self):
        """
        Ensure that supervisors cannot get an assessment they don't have access to.
        """
        url = reverse('assessments-detail', args=[1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 404)

    def test_create_assessment(self):
        """
        Ensure that supervisors can create an assessment.
        """
        url = reverse('assessments-list')
        data = {'country': 'JOR', 'grade': '4', 'language': 'AR',
                'subject': 'MATH', 'title': 'New assessment'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.data['private'])
        self.assertFalse(response.data['allow_skip'])
        self.assertEqual(response.data['show_feedback'], 2)
        assessment = Assessment.objects.get(id=response.data['id'])
        self.assertEqual(assessment.created_by.id, 4)

    def test_edit_assessment(self):
        """
        Ensure that supervisors can update the details of an assessment they have access to.
        """
        url = reverse('assessments-detail', args=[2])
        data = {'show_feedback': 0, 'grade': '1-3'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['grade'], '1-3')
        self.assertEqual(response.data['show_feedback'], 0)

    def test_edit_assessment_no_access(self):
        """
        Ensure that supervisors cannot update the details of an assessment \
        they don't have access to.
        """
        url = reverse('assessments-detail', args=[1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 404)

    def test_delete_assessment(self):
        """
        Ensure that supervisors can delete an assessessment (and related data) they have created.
        """
        url = reverse('assessments-detail', args=[2])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 204)

    def test_delete_assessment_no_access(self):
        """
        Ensure that supervisors cannot delete an assessessment they haven't created.
        """
        url = reverse('assessments-detail', args=[1])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 404)

    # TOPICS

    def test_get_all_topics(self):
        """
        Ensure that supervisors can get the list of topics in an assessment they have access to.
        """
        url = reverse('assessment-topics-list', args=[2])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], 3)

    def test_get_all_topics_no_access(self):
        """
        Ensure that supervisors cannot get the list of topics in an assessment \
        they don't have access to.
        """
        url = reverse('assessment-topics-list', args=[1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

    def test_get_one_topic(self):
        """
        Ensure that supervisors can get one topic in an assessment they have access to.
        """
        url = reverse('assessment-topics-detail', args=[2, 3])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_one_topic_no_access(self):
        """
        Ensure that supervisors cannot get one topic in an assessment they don't have access to.
        """
        url = reverse('assessment-topics-detail', args=[1, 1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

    def test_create_topic(self):
        """
        Ensure that supervisors can create a topic in an assessment they have created.
        """
        url = reverse('assessment-topics-list', args=[2])
        data = {'assessment': 2, 'name': 'New topic'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_create_topic_no_access(self):
        """
        Ensure that supervisors cannot create a topic in an assessment they haven't created.
        """
        url = reverse('assessment-topics-list', args=[1])
        data = {'assessment': 1, 'name': 'New topic'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_edit_topic(self):
        """
        Ensure that supervisors can edit a topic in an assessment they created.
        """
        url = reverse('assessment-topics-detail', args=[2, 3])
        data = {'description': 'New topic description'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['description'], 'New topic description')

    def test_edit_topic_no_access(self):
        """
        Ensure that supervisors cannot edit a topic in an assessment they haven't created.
        """
        url = reverse('assessment-topics-detail', args=[1, 1])
        data = {'description': 'New topic description'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_delete_topic(self):
        """
        Ensure that supervisors can delete a topic in an assessment they created.
        """
        url = reverse('assessment-topics-detail', args=[2, 3])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 204)

    def test_delete_topic_no_access(self):
        """
        Ensure that supervisors cannot delete a topic in an assessment they haven't created.
        """
        url = reverse('assessment-topics-detail', args=[1, 1])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 403)

    # QUESTIONS

    def test_get_all_questions(self):
        """
        Ensure that supervisors can get the list of questions in a topic they have access to.
        """
        url = reverse('topic-questions-list', args=[2, 3])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_get_all_questions_no_access(self):
        """
        Ensure that supervisors cannot get the list of questions in a topic \
        they don't have access to.
        """
        url = reverse('topic-questions-list', args=[1, 1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

    def test_get_one_question(self):
        """
        Ensure that supervisors can get one question in a topic they have access to.
        """
        url = reverse('topic-questions-detail', args=[2, 3, 1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_one_question_no_access(self):
        """
        Ensure that supervisors cannot get one question in a topic they don't have access to.
        """
        url = reverse('topic-questions-detail', args=[1, 1, 4])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

    # ACCESS
