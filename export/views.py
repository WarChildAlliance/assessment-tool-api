from datetime import date
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from answers.models import Answer
from assessments.models import Question
from export.serializers import CompleteStudentAnswersSerializer, AnswerTableSerializer
from visualization.serializers import AssessmentTableSerializer
from assessments.serializers import QuestionSerializer, AssessmentTopicSerializer
from visualization.views import AssessmentTableViewSet
from assessments.views import QuestionsViewSet, AssessmentTopicsViewSet
from admin.lib.viewsets import ModelViewSet
from .utils.reports import AssessmentPDFReport


class CompleteStudentAnswersViewSet(ModelViewSet):
    """
    Exposes all answers from all students
    """
    serializer_class = AnswerTableSerializer

    def get_queryset(self):
        return Answer.objects.all().select_subclasses().order_by('topic_answer__topic_access__student', 'topic_answer__topic_access__topic__assessment', 'topic_answer__topic_access__topic', 'topic_answer__start_date', 'question')
    

    def retrieve(self, request, pk=None):
        return Response('Cannot retrieve export', status=403)


class SupervisorStudentAnswerViewSet(ModelViewSet):

    serializer_class = AnswerTableSerializer

    def get_queryset(self):
        supervisor_id = int(self.kwargs.get('supervisor_id', None))
        return Answer.objects.filter(topic_answer__topic_access__student__created_by=supervisor_id).select_subclasses().order_by('topic_answer__topic_access__student', 'topic_answer__topic_access__topic__assessment', 'topic_answer__topic_access__topic', 'topic_answer__start_date', 'question')
    
    def retrieve(self, request, *args, **kwargs):
        assessment_id = kwargs['pk']
        supervisor_id = int(self.kwargs.get('supervisor_id', None))
        answers_by_assessment = Answer.objects.filter(topic_answer__topic_access__student__created_by=supervisor_id, topic_answer__topic_access__topic__assessment=assessment_id).select_subclasses().order_by('topic_answer__topic_access__student', 'topic_answer__topic_access__topic__assessment', 'topic_answer__topic_access__topic', 'topic_answer__start_date', 'question')
        serializer = AnswerTableSerializer(
            answers_by_assessment, many=True,
        )

        return Response(serializer.data)


class QuestionReportViewSet(GenericViewSet):

    def retrieve(self, request, *args, **kwargs) -> FileResponse:
        """
        Generates a PDF report for a specific question
        """
        question_pk = self.kwargs.get('pk', None)
        question = get_object_or_404(
            QuestionsViewSet.get_queryset(self), pk=question_pk)
        serializer_data = QuestionSerializer(question, many=False).data

        builder = AssessmentPDFReport()
        builder.write_nested_data('questions', serializer_data)

        doc = builder.build()
        doc_name = '{}_{}.pdf'.format(serializer_data['title'], date.today())

        response = FileResponse(doc, as_attachment=True, filename=doc_name)
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'

        return response


class AssessmentTopicReportViewSet(GenericViewSet):

    def retrieve(self, request, *args, **kwargs):
        """
        Generates a PDF report for a specific topic
        """
        topic_pk = self.kwargs.get('pk', None)
        assessment_pk = self.kwargs.get('assessment_pk', None)

        topic = get_object_or_404(
            AssessmentTopicsViewSet.get_queryset(self), pk=topic_pk)
        questions = Question.objects.filter(
            assessment_topic=topic_pk,
            assessment_topic__assessment=assessment_pk
        )

        topic_data = AssessmentTopicSerializer(topic, many=False).data
        questions_data = QuestionSerializer(questions, many=True).data

        topic_data['questions'] = questions_data
        topic_data['questions_nb'] = len(questions_data)

        builder = AssessmentPDFReport()
        builder.write_nested_data('topics', topic_data)

        doc = builder.build()
        doc_name = '{}_{}.pdf'.format(topic_data['name'], date.today())

        response = FileResponse(doc, as_attachment=True, filename=doc_name)
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'

        return response


class AssessmentReportViewSet(GenericViewSet):

    def __fetch_questions_for_topic(self, assessment_pk, topic_data):
        self.kwargs['topic_pk'] = topic_data['id']
        questions = QuestionsViewSet.get_queryset(self).select_subclasses()
        questions_data = QuestionSerializer(questions, many=True).data
        topic_data.update({'questions': questions_data})
        topic_data['questions_nb'] = len(questions_data)

        return topic_data


    def retrieve(self, request, *args, **kwargs):
        """
        Generates a PDF report for a specific assessment
        """
        assessment_pk = self.kwargs.get('pk', None)

        assessment = get_object_or_404(
            AssessmentTableViewSet.get_queryset(self), pk=assessment_pk)

        if assessment_pk:
            self.kwargs['assessment_pk'] = self.kwargs.pop('pk')
        topics = AssessmentTopicsViewSet.get_queryset(self)

        assessment_data = AssessmentTableSerializer(assessment, many=False).data
        topics_data = AssessmentTopicSerializer(topics, many=True).data
        topics_data = list(map(
            lambda e: self.__fetch_questions_for_topic(assessment_pk, e),
            topics_data
        ))

        assessment_data['topics'] = topics_data

        builder = AssessmentPDFReport()
        builder.write_nested_data('assessments', assessment_data)

        doc = builder.build()
        doc_name = '{}_{}.pdf'.format(assessment_data['title'], date.today())

        response = FileResponse(doc, as_attachment=True, filename=doc_name)
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'

        return response
