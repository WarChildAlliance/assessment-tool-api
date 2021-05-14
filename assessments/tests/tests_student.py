from assessments.models import AssessmentTopicAccess, Assessment
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class AssessmentsStudentTests(APITestCase):
    """
    Assessment tests from a student account.
    """
    fixtures = ['languages_countries.json', 'users.json',
                'assessments.json', 'assessments_access.json']

    def setUp(self):
        """
        Set up authentication.
        """
        token = Token.objects.get(user__username='111111')  # id: 1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    # ASSESSMENTS

    def test_get_all_assessments(self):
        """
        Ensure that students can get the list of assessments they have access to.
        """
        url = reverse('assessments-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_assessment(self):
        """
        Ensure that students can get one assessment they have access to.
        """
        url = reverse('assessments-detail', args=[1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_assessment_no_access(self):
        """
        Ensure that students cannot get an assessment they don't have access to.
        """
        url = reverse('assessments-detail', args=[2])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 404)

    def test_create_assessment(self):
        """
        Ensure that students cannot create an assessment.
        """
        url = reverse('assessments-list')
        data = {'country': 'JOR', 'grade': '4', 'language': 'AR',
                'subject': 'MATH', 'title': 'New assessment'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_edit_assessment(self):
        """
        Ensure that students cannot update the details of an assessment.
        """
        url = reverse('assessments-detail', args=[2])
        data = {'show_feedback': 0, 'grade': '1-3'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_delete_assessment(self):
        """
        Ensure that students cannot delete an assessessment.
        """
        url = reverse('assessments-detail', args=[2])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 403)

    # TOPICS

    def test_get_all_topics(self):
        """
        Ensure that students can get the list of topics they have access to in an assessment.
        """
        url = reverse('assessment-topics-list', args=[1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_get_all_topics_no_access(self):
        """
        Ensure that students cannot get the list of topics in an assessment \
        they don't have access to.
        """
        url = reverse('assessment-topics-list', args=[2])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

    def test_get_one_topic(self):
        """
        Ensure that students can get one topic they have access to.
        """
        url = reverse('assessment-topics-detail', args=[1, 1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_one_topic_no_access(self):
        """
        Ensure that students cannot get one topic they don't have access to.
        """
        url = reverse('assessment-topics-detail', args=[2, 3])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

    def test_create_topic(self):
        """
        Ensure that students cannot create a topic.
        """
        url = reverse('assessment-topics-list', args=[1])
        data = {'assessment': 1, 'name': 'New topic'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_edit_topic(self):
        """
        Ensure that students cannot edit a topic.
        """
        url = reverse('assessment-topics-detail', args=[1, 1])
        data = {'description': 'New topic description'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_delete_topic(self):
        """
        Ensure that students cannot delete a topic.
        """
        url = reverse('assessment-topics-detail', args=[1, 1])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 403)

    # QUESTIONS

    def test_get_all_questions(self):
        """
        Ensure that students can get the list of questions in a topic they have access to.
        """
        url = reverse('topic-questions-list', args=[1, 1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_all_questions_no_access(self):
        """
        Ensure that students cannot get the list of questions in a topic \
        they don't have access to.
        """
        url = reverse('topic-questions-list', args=[2, 3])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

    def test_get_one_question(self):
        """
        Ensure that students can get one question in a topic they have access to.
        """
        url = reverse('topic-questions-detail', args=[1, 1, 4])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_one_question_no_access(self):
        """
        Ensure that students cannot get one question in a topic they don't have access to.
        """
        url = reverse('topic-questions-detail', args=[2, 3, 1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

    # ACCESS
