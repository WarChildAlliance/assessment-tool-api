from assessments.models import Assessment
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class AssessmentsSupervisorTests(APITestCase):
    """
    Assessment tests from a supervisor account.
    """
    fixtures = ['languages_countries.json', 'users.json',
                'assessments-test.json', 'assessments_access.json', 'topics_learningobjectives.json']

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
        data = {'country': 'JOR', 'grade': '4', 'language': 'ARA',
                'subject': 'MATH', 'title': 'New assessment'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.data['private'])
        assessment = Assessment.objects.get(id=response.data['id'])
        self.assertEqual(assessment.created_by.id, 4)

    def test_edit_assessment(self):
        """
        Ensure that supervisors can update the details of an assessment they have access to.
        """
        url = reverse('assessments-detail', args=[2])
        data = {'title': 'This is the right title for this assessment', 'grade': '1-3'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['grade'], '1-3')
        self.assertEqual(response.data['title'], 'This is the right title for this assessment')

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

    # TOPICS

    def test_get_all_question_sets(self):
        """
        Ensure that supervisors can get the list of question_sets in an assessment they have access to.
        """
        url = reverse('assessment-question-sets-list', args=[2])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], 3)

    def test_get_all_question_sets_no_access(self):
        """
        Ensure that supervisors cannot get the list of question_sets in an assessment \
        they don't have access to.
        """
        url = reverse('assessment-question-sets-list', args=[1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

    def test_get_one_question_set(self):
        """
        Ensure that supervisors can get one question_set in an assessment they have access to.
        """
        url = reverse('assessment-question-sets-detail', args=[2, 3])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_one_question_set_no_access(self):
        """
        Ensure that supervisors cannot get one question_set in an assessment they don't have access to.
        """
        url = reverse('assessment-question-sets-detail', args=[1, 1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

    def test_create_question_set(self):
        """
        Ensure that supervisors can create a question_set in an assessment they have created.
        """
        url = reverse('assessment-question-sets-list', args=[2])
        print(self)
        data = {'assessment': 1, 'name': 'New question_set', 'topic': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data['show_feedback'], 2)
        self.assertFalse(response.data['allow_skip'])
        self.assertEqual(response.status_code, 201)

    def test_create_question_set_no_access(self):
        """
        Ensure that supervisors cannot create a question_set in an assessment they haven't created.
        """
        url = reverse('assessment-question-sets-list', args=[1])
        data = {'assessment': 1, 'name': 'New question_set'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_edit_question_set(self):
        """
        Ensure that supervisors can edit a question_set in an assessment they created.
        """
        url = reverse('assessment-question-sets-detail', args=[2, 3])
        data = {'description': 'New question_set description'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['description'], 'New question_set description')

    def test_edit_question_set_no_access(self):
        """
        Ensure that supervisors cannot edit a question_set in an assessment they haven't created.
        """
        url = reverse('assessment-question-sets-detail', args=[1, 1])
        data = {'description': 'New question_set description'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_delete_question_set(self):
        """
        Ensure that supervisors can delete a question_set in an assessment they created.
        """
        url = reverse('assessment-question-sets-detail', args=[2, 3])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 204)

    def test_delete_question_set_no_access(self):
        """
        Ensure that supervisors cannot delete a question_set in an assessment they haven't created.
        """
        url = reverse('assessment-question-sets-detail', args=[1, 1])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 403)

    # QUESTIONS

    def test_get_all_questions(self):
        """
        Ensure that supervisors can get the list of questions in a question_set they have access to.
        """
        url = reverse('question-sets-questions-list', args=[2, 3])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_get_all_questions_no_access(self):
        """
        Ensure that supervisors cannot get the list of questions in a question_set \
        they don't have access to.
        """
        url = reverse('question-sets-questions-list', args=[1, 1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

    def test_get_one_question(self):
        """
        Ensure that supervisors can get one question in a question_set they have access to.
        """
        url = reverse('question-sets-questions-detail', args=[2, 3, 1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_one_question_no_access(self):
        """
        Ensure that supervisors cannot get one question in a question_set they don't have access to.
        """
        url = reverse('question-sets-questions-detail', args=[1, 1, 4])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

    # ACCESS

    def test_create_bulk_question_set_access(self):
        """
        Ensure that supervisors can give access to question_sets they have access to.
        """
        url = reverse('assessment-accesses-bulk-create', args=[2])
        data = {'students': [1, 3], 'accesses': [{'question_set': 3, 'start_date': '2021-01-01'}]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_create_bulk_question_set_access_unauthorized_student(self):
        """
        Ensure that supervisors can give access to question_sets they have access to.
        """
        url = reverse('assessment-accesses-bulk-create', args=[2])
        data = {'students': [2], 'accesses': [{'question_set': 3, 'start_date': '2021-01-01'}]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_bulk_question_set_access_unauthorized_question_set(self):
        """
        Ensure that supervisors can give access to question_sets they have access to.
        """
        url = reverse('assessment-accesses-bulk-create', args=[2])
        data = {'students': [1, 3], 'accesses': [{'question_set': 1}]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_bulk_question_set_access_unauthorized_assessment(self):
        """
        Ensure that supervisors can give access to question_sets they have access to.
        """
        url = reverse('assessment-accesses-bulk-create', args=[1])
        data = {'students': [1, 3], 'accesses': [{'question_set': 1, 'start_date': '2021-01-01'}]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)