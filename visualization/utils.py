from assessments.models import QuestionSetAccess, QuestionSet, Question
from answers.models import QuestionSetAnswer, Answer

def get_question_set_correct_answers_percentage(question_set):
        """
        Get the percentage of correct answers for the given question_set
        """
        correct_answers_percentage = 0
        question_set_total_answers = Question.objects.filter(question_set=question_set).exclude(question_type='SEL').count()
        question_set_answers = QuestionSetAnswer.objects.filter(question_set_access__question_set=question_set)
        if not question_set_total_answers or not question_set_answers:
            return None
        question_set_total_correct_answers = Answer.objects.filter(
                question_set_answer__in=question_set_answers,
                valid=True
            ).exclude(question__question_type='SEL').count()
        question_set_total_wrong_answers = 0
        if question_set_total_correct_answers == 0:
            question_set_total_wrong_answers = Answer.objects.filter(
                question_set_answer__in=question_set_answers,
                valid=False
            ).exclude(question__question_type='SEL').count()
        if (question_set_total_answers != 0):
            if question_set_total_correct_answers != 0:
                correct_answers_percentage = round((question_set_total_correct_answers / question_set_total_answers) * 100, 1)
            elif question_set_total_wrong_answers != 0:
                correct_answers_percentage = 0

        return min(correct_answers_percentage, 100.0)

def calculate_student_score(assessment, student_pk):
        question_set_accesses = QuestionSetAccess.objects.filter(
            question_set__assessment__id=assessment,
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

def calculate_assessments_score(assessments):
    assessments_score = []
    for assessment in assessments:
        question_sets = QuestionSet.objects.filter(assessment=assessment)
        question_sets_answers = []

        for question_set in question_sets:
            if question_set.evaluated:
                correct_answers_percentage = get_question_set_correct_answers_percentage(question_set)
                if correct_answers_percentage is not None:
                    question_sets_answers.append(correct_answers_percentage)

        score = None
        if question_sets_answers:
            score = sum(question_sets_answers) / float(len(question_sets_answers))
            
            assessments_score.append(score)

    return assessments_score