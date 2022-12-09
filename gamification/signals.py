from  django.dispatch import receiver
from django.db.models.signals import post_save
from gamification.models import Profile, QuestionSetCompetency

from answers.models import Answer, QuestionSetAnswer
from assessments.models import QuestionSet, Question


# This is a receiver for post_save on QuestionSetAnswer
@receiver(post_save, sender=QuestionSetAnswer)
def on_question_set_answer_submission(sender, **kwargs):

    question_set_answer = kwargs['instance']

"""
    if (question_set_answer.complete):

        student_profile = Profile.objects.get(student = question_set_answer.question_set_access.student.id)

        correct_answers_total = Answer.objects.filter(
            question_set_answer=question_set_answer,
            valid=True
        ).count()

        total_questions = Question.objects.filter(question_set=question_set_answer.question_set_access.question_set).count()

        submitted_question_set_competency = 3

        if (question_set_answer.question_set_access.question_set.evaluated == True & total_questions > 0):
            # Compute the question_set competency for the submitted question_set answer
            submitted_question_set_competency = round(((correct_answers_total * 3) / total_questions), 1)

        # Check if other complete question_set answers have already been submitted for same student and question_set
        submissions_count = QuestionSetAnswer.objects.filter(
            question_set_access__question_set=question_set_answer.question_set_access.question_set,
            question_set_access__student=question_set_answer.question_set_access.student,
            complete = True
        ).count()

        # Default effort amount for the submission of a complete question_set answer
        effort_amount = 2

        # If its the first attempt, increase effort by 5 instead
        if (submissions_count < 2):
            effort_amount = 5

        student_profile.effort += effort_amount
        student_profile.save()

        increase_question_set_competency(student_profile, question_set_answer.question_set_access.question_set, submitted_question_set_competency)
"""

# Increase the question_set competency for a given profile and question_set
def increase_question_set_competency(profile, question_set, new_amount):

    # If the question_set competency already exists, if the new value is higher, replace the previous one
    if (QuestionSetCompetency.objects.filter(profile=profile, question_set=question_set).exists()):

        current_competency = QuestionSetCompetency.objects.get(profile=profile, question_set=question_set)

        if (new_amount > current_competency.competency):
            current_competency.competency = new_amount
            current_competency.save()

    # If no matching question_set competency exists, create a new one with the new value
    else:

        QuestionSetCompetency.objects.create(profile=profile, question_set=question_set, competency=new_amount)
