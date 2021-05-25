from django.db.models.signals import post_save
from gamification.models import Profile, TopicCompetency

from answers.models import Answer, AssessmentTopicAnswer
from assessments.models import AssessmentTopic, Question


# This is a receiver for post_save on AssessmentTopicAnswer
def on_topic_answer_submission(sender, **kwargs):

    # Disconnect the event receiver once it has been triggered
    post_save.disconnect(on_topic_answer_submission)

    topic_answer = kwargs['instance']

    if (topic_answer.complete):

        student_profile = Profile.objects.get(student = topic_answer.topic_access.student.id)

        correct_answers_total = Answer.objects.filter(
            topic_answer=topic_answer,
            valid=True
        ).count()


        total_questions = Question.objects.filter(assessment_topic=topic_answer.topic_access.topic).count()

        # Compute the topic competency for the submitted topic answer
        submitted_topic_competency = round(((correct_answers_total * 3) / total_questions), 1)

        # Check if other complete topic answers have already been submitted for same student and topic
        submissions_count = AssessmentTopicAnswer.objects.filter(
            topic_access__topic=topic_answer.topic_access.topic,
            topic_access__student=topic_answer.topic_access.student,
            complete = True
        ).count()

        # Default effort amount for the submission of a complete topic answer
        effort_amount = 2

        # If its the first attempt, increase effort by 5 instead
        if (submissions_count < 2):
            effort_amount = 5

        student_profile.effort += effort_amount
        student_profile.save()

        increase_topic_competency(student_profile, topic_answer.topic_access.topic, submitted_topic_competency)


# Increase the topic competency for a given profile and topic
def increase_topic_competency(profile, topic, new_amount):

    # If the topic competency already exists, if the new value is higher, replace the previous one
    if (TopicCompetency.objects.filter(profile=profile, topic=topic).exists()):

        current_competency = TopicCompetency.objects.get(profile=profile, topic=topic)

        if (new_amount > current_competency.competency):
            current_competency.competency = new_amount
            current_competency.save()

    # If no matching topic competency exists, create a new one with the new value
    else:

        TopicCompetency.objects.create(profile=profile, topic=topic, competency=new_amount)
