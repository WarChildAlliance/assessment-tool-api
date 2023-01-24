from assessments.models import QuestionSetAccess
from answers.models import QuestionSetAnswer

def calculate_student_score(assessment, student_pk):
        question_set_accesses = QuestionSetAccess.objects.filter(
            question_set__assessment=assessment,
            student__id=student_pk
        )
        student_score = None
        if question_set_accesses:
            total_score = 0
            total_question_count = 0
            for question_set_access in question_set_accesses:
                question_set_answer = QuestionSetAnswer.objects.filter(
                    question_set_access=question_set_access,
                    complete=True
                )
                if question_set_answer:
                    question_set_answer = question_set_answer.first()
                    correct_answers = question_set_answer.answers.filter(valid=True)
                    total_score += correct_answers.count()
                    total_question_count += question_set_answer.answers.count()
            if total_question_count:
                student_score = total_score / total_question_count
        return student_score