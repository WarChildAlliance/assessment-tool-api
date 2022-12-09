from assessments.models import QuestionSetAccess, Assessment
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
        data = {'country': 'JOR', 'grade': '4', 'language': 'ARA',
                'subject': 'MATH', 'title': 'New assessment'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_edit_assessment(self):
        """
        Ensure that students cannot update the details of an assessment.
        """
        url = reverse('assessments-detail', args=[2])
        data = {'title': 'An assessment should not have this title', 'grade': '1-3'}
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

    def test_get_all_question_sets(self):
        """
        Ensure that students can get the list of question_sets they have access to in an assessment.
        """
        url = reverse('assessment-question-sets-list', args=[1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_get_all_question_sets_no_access(self):
        """
        Ensure that students cannot get the list of question_sets in an assessment \
        they don't have access to.
        """
        url = reverse('assessment-question-sets-list', args=[2])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

    def test_get_one_question_set(self):
        """
        Ensure that students can get one question_set they have access to.
        """
        url = reverse('assessment-question-sets-detail', args=[1, 1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_one_question_set_no_access(self):
        """
        Ensure that students cannot get one question_set they don't have access to.
        """
        url = reverse('assessment-question-sets-detail', args=[2, 3])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

    def test_create_question_set(self):
        """
        Ensure that students cannot create a question_set.
        """
        url = reverse('assessment-question-sets-list', args=[1])
        data = {'assessment': 1, 'name': 'New question set'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_edit_question_set(self):
        """
        Ensure that students cannot edit a question_set.
        """
        url = reverse('assessment-question-sets-detail', args=[1, 1])
        data = {'description': 'New question set description'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_delete_question_set(self):
        """
        Ensure that students cannot delete a question_set.
        """
        url = reverse('assessment-question-sets-detail', args=[1, 1])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 403)

    # QUESTIONS

    def test_get_all_questions(self):
        """
        Ensure that students can get the list of questions in a question_set they have access to.
        """
        url = reverse('question-sets-questions-list', args=[1, 1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 15)

    def test_get_all_questions_no_access(self):
        """
        Ensure that students cannot get the list of questions in a question_set \
        they don't have access to.
        """
        url = reverse('question-sets-questions-list', args=[2, 3])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

    def test_get_one_question(self):
        """
        Ensure that students can get one question in a question_set they have access to.
        """
        url = reverse('question-sets-questions-detail', args=[1, 1, 4])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_one_question_no_access(self):
        """
        Ensure that students cannot get one question in a question_set they don't have access to.
        """
        url = reverse('question-sets-questions-detail', args=[2, 3, 1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

    # ACCESS

    def test_create_bulk_question_set_access(self):
        """
        Ensure that supervisors can give access to question_sets they have access to.
        """
        url = reverse('assessment-accesses-bulk-create', args=[1])
        data = {'students': [1], 'accesses': [{'question_set': 1, 'start_date': '2021-01-01'}]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)
