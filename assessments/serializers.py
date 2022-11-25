from datetime import date

from django.db.models.query_utils import RegisterLookupMixin
from answers.models import Answer, AssessmentTopicAnswer
from rest_framework import serializers
from users.models import Country, Language, User
from users.serializers import (CountrySerializer, LanguageSerializer,
                               UserSerializer)

from admin.lib.serializers import NestedRelatedField, PolymorphicSerializer

from users.models import Language, Country
from users.serializers import LanguageSerializer, CountrySerializer

from .models import (AreaOption, Assessment, AssessmentTopic, AssessmentTopicAccess,
                     Attachment, DominoOption, DraggableOption, Hint, Question, QuestionCalcul, QuestionDomino, QuestionDragAndDrop, QuestionFindHotspot, QuestionInput,
                     QuestionNumberLine, QuestionSEL, QuestionSelect, QuestionSort,
                     SelectOption, SortOption, Subtopic, LearningObjective, NumberRange)


class AttachmentSerializer(serializers.ModelSerializer):
    """
    Attachment serializer.
    """

    class Meta:
        model = Attachment
        fields = '__all__'

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        return instance


class AssessmentSerializer(serializers.ModelSerializer):
    """
    Assessment serializer.
    """

    language = NestedRelatedField(
        model=Language, serializer_class=LanguageSerializer)
    country = NestedRelatedField(
        model=Country, serializer_class=CountrySerializer)

    # THIS IS ONLY TEMPORARY FOR PRE-SEL AND POST-SEL, TODO REMOVE AFTERWARD
    # Verifies that all topics linked to this assessment are complete
    all_topics_complete = serializers.SerializerMethodField()
    # END OF TEMPORARY

    class Meta:
        model = Assessment
        fields = '__all__'
        extra_kwargs = {'created_by': {
            'default': serializers.CurrentUserDefault(),
            'write_only': True
        }}

    # THIS IS ONLY TEMPORARY FOR PRE-SEL AND POST-SEL, TODO REMOVE AFTERWARD

    def get_all_topics_complete(self, instance):

        if not ('student_pk' in self.context):
            return None

        student_pk = self.context['student_pk']

        completed_assessment_topics = AssessmentTopic.objects.filter(
            assessment=instance,
            assessmenttopicaccess__student=student_pk,
            assessmenttopicaccess__assessment_topic_answers__session__student=student_pk
        ).distinct().count()

        total_assessment_topics = AssessmentTopic.objects.filter(
            assessment=instance,
        ).distinct().count()

        return (completed_assessment_topics == total_assessment_topics)
    # END OF TEMPORARY


class SubtopicSerializer(serializers.ModelSerializer):
    """
    Subtopic serializer.
    """
    class Meta:
        model = Subtopic
        fields = ('id', 'name',)


class AssessmentTopicSerializer(serializers.ModelSerializer):
    """
    Assessment topic serializer.
    """
    attachments = AttachmentSerializer(many=True, required=False)
    can_edit = serializers.SerializerMethodField()
    subtopic = NestedRelatedField(
        model=Subtopic, serializer_class=SubtopicSerializer, allow_null=True)
    sel_question = serializers.SerializerMethodField()
    questions_count = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = AssessmentTopic
        fields = '__all__'

    def to_internal_value(self, data):
        data = data.copy()
        kwargs = self.context['request'].parser_context['kwargs']
        if 'assessment' not in data:
            data['assessment'] = kwargs.get('assessment_pk', None)
        return super().to_internal_value(data)

    def get_can_edit(self, instance):
        if 'request' not in self.context:
            return None
        supervisor = self.context['request'].user
        assessment = instance.assessment
        if assessment.created_by == supervisor:
            return True
        else:
            return False

    def get_sel_question(self, instance):
        return instance.order == 1 and instance.assessment.sel_question

    def get_questions_count(self, instance):
        return Question.objects.filter(assessment_topic=instance).count()

class HintSerializer(serializers.ModelSerializer):
    """
    Hint serializer.
    """
    attachments = AttachmentSerializer(many=True, required=False)

    class Meta:
        model = Hint
        fields = '__all__'
        extra_kwargs = {'question': {
            'required': False,
            'write_only': True
        }}

    def create(self, validated_data):
        """
        Create hint with attachments.
        """
        if validated_data['question'] is None:
            raise serializers.ValidationError({
                'question': 'This field is required',
            })

        attachments_data = validated_data.pop(
            'attachments') if 'attachments' in validated_data else None

        hint = super().create(validated_data)

        if attachments_data is not None:
            for attachment_data in attachments_data:
                Attachment.objects.create(
                    hint=hint, **attachment_data)

        return hint


class SelectOptionSerializer(serializers.ModelSerializer):
    """
    Select option serializer.
    """
    attachments = AttachmentSerializer(many=True, required=False)

    class Meta:
        model = SelectOption
        fields = '__all__'
        extra_kwargs = {'question_select': {
            'required': False,
            'write_only': True
        }}

    def create(self, validated_data):
        """
        Create select option with attachments.
        """
        if validated_data['question_select'] is None:
            raise serializers.ValidationError({
                'question_select': 'This field is required',
            })

        attachments_data = validated_data.pop(
            'attachments') if 'attachments' in validated_data else None

        select_option = super().create(validated_data)

        if attachments_data is not None:
            for attachment_data in attachments_data:
                Attachment.objects.create(
                    select_option=select_option, **attachment_data)

        return select_option


class DominoOptionSerializer(serializers.ModelSerializer):
    """
    Domino option serializer.
    """
    class Meta:
        model = DominoOption
        fields = '__all__'
        extra_kwargs = {'question_domino': {
            'required': False,
            'write_only': True
            }
        }

    def create(self, validated_data):
        """
        Create domino option.
        """

        if validated_data['question_domino'] is None:
            raise serializers.ValidationError({
                'question_domino': 'This field is required',
            })

        domino_option = super().create(validated_data)
        return domino_option

class SortOptionSerializer(serializers.ModelSerializer):
    """
    Sort option serializer.
    """
    attachments = AttachmentSerializer(many=True, required=False)

    class Meta:
        model = SortOption
        fields = '__all__'
        extra_kwargs = {'question_sort': {
            'required': False,
            'write_only': True
        }}

    def create(self, validated_data):
        """
        Create select option with attachments.
        """
        if validated_data['question_sort'] is None:
            raise serializers.ValidationError({
                'question_sort': 'This field is required',
            })

        attachments_data = validated_data.pop(
            'attachments') if 'attachments' in validated_data else None

        sort_option = super().create(validated_data)

        if attachments_data is not None:
            for attachment_data in attachments_data:
                Attachment.objects.create(
                    sort_option=sort_option, **attachment_data)

        return sort_option

class AreaOptionSerializer(serializers.ModelSerializer):
    """
    Area option serializer.
    """
    class Meta:
        model = AreaOption
        fields = '__all__'
        extra_kwargs = {
            'question_drag_and_drop': {
                'required': False,
                'write_only': True
            },
            'question_find_hotspot': {
                'required': False,
                'write_only': True
            }
        }

    def create(self, validated_data):
        """
        Create area option with coordenates.
        """
        if validated_data['question_drag_and_drop'] is None:
            raise serializers.ValidationError({'question_drag_and_drop': 'This field is required',})
        
        area_option = super().create(validated_data)

        return area_option

class DraggableOptionSerializer(serializers.ModelSerializer):
    """
    Draggable option serializer.
    """
    attachments = AttachmentSerializer(many=True, required=False)

    class Meta:
        model = DraggableOption
        fields = '__all__'
        extra_kwargs = {
            'question_drag_and_drop': {
                'required': False,
                'write_only': True
            }
        }

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        return instance

class LearningObjectiveSerializer(serializers.ModelSerializer):
    """
    Learning objective serializer.
    """
    subtopic = NestedRelatedField(
        model=Subtopic, serializer_class=SubtopicSerializer)

    class Meta:
        model = LearningObjective
        fields = ('code', 'grade', 'name_eng', 'name_ara', 'subtopic')

class NumberRangeSerializer(serializers.ModelSerializer):
    """
    Number range serializer.
    """

    class Meta:
        model = NumberRange
        fields = ('id', 'min', 'max', 'handle')

class QuestionSerializer(PolymorphicSerializer):
    """
    Question serializer.
    """
    class Meta:
        model = Question
        fields = '__all__'

    def get_serializer_map(self):
        return {
            'QuestionSEL': QuestionSELSerializer,
            'QuestionInput': QuestionInputSerializer,
            'QuestionNumberLine': QuestionNumberLineSerializer,
            'QuestionSelect': QuestionSelectSerializer,
            'QuestionDomino': QuestionDominoSerializer,
            'QuestionSort': QuestionSortSerializer,
            'QuestionCalcul': QuestionCalculSerializer,
            'QuestionDragAndDrop': QuestionDragAndDropSerializer,
            'QuestionFindHotspot': QuestionFindHotspotSerializer
        }

    def to_representation(self, obj):
        sub_obj = Question.objects.get_subclass(id=obj.id)
        return super().to_representation(sub_obj)

    def to_internal_value(self, data):
        data = data.copy()
        type_dict = {
            Question.QuestionType.SEL: 'QuestionSEL',
            Question.QuestionType.INPUT: 'QuestionInput',
            Question.QuestionType.SELECT: 'QuestionSelect',
            Question.QuestionType.SORT: 'QuestionSort',
            Question.QuestionType.DOMINO: 'QuestionDomino',
            Question.QuestionType.NUMBER_LINE: 'QuestionNumberLine',
            Question.QuestionType.FIND_HOTSPOT: 'QuestionFindHotspot',
            Question.QuestionType.CALCUL: 'QuestionCalcul',
            Question.QuestionType.DRAG_AND_DROP: 'QuestionDragAndDrop'
        }
        if 'question_type' in data and data['question_type'] in type_dict:
            data['type'] = type_dict[data['question_type']]
        elif self.instance:
            data['type'] = type_dict[self.instance.question_type]
        else:
            raise serializers.ValidationError({
                'question_type': 'Unkown question type',
            })

        kwargs = self.context['request'].parser_context['kwargs']
        if 'assessment_topic' not in data:
            data['assessment_topic'] = kwargs.get('topic_pk', None)
        return super().to_internal_value(data)


class AbstractQuestionSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, required=False)
    hint = HintSerializer(required=False, allow_null=True)

    # Does the question have answers?
    answered = serializers.SerializerMethodField()

    learning_objective = NestedRelatedField(
        model=LearningObjective, serializer_class=LearningObjectiveSerializer, allow_null=True)

    def get_answered(self, instance):
        return Answer.objects.filter(question=instance).exists()

    def create(self, validated_data):
        """
        Create question with hint and attachments.
        """
        # Validated conditions to create SEL questions
        question_assessment = Assessment.objects.get(id=validated_data['assessment_topic'].assessment.id)
        if validated_data['question_type'] == 'SEL':
            if (not question_assessment.sel_question) or validated_data['assessment_topic'].order != 1:
                raise serializers.ValidationError({
                    'question_type': 'Question of the type SEL can only be created in Assessments with “Contains SEL questions” set as true and in the first topic only',
                })
            if Question.objects.filter(assessment_topic=validated_data['assessment_topic'], question_type='SEL').count() == 5:
                raise serializers.ValidationError({
                    'question_type': 'Only up to 5 Questions of the type SEL can be created by assessment.',
                })
        
        hint_data = validated_data.pop(
            'hint') if 'hint' in validated_data else None
        attachments_data = validated_data.pop(
            'attachments') if 'attachments' in validated_data else None

        question = super().create(validated_data)

        # Reorder all other questions to maintain consistent order
        request_order = validated_data['order']
        questions = Question.objects.filter(assessment_topic=validated_data['assessment_topic']).select_subclasses()
        # Create an array with the topics from the InheritanceQuerySet
        questions_list = list(questions)
        # Places the question in the position of the array equivalent to its new order
        questions_list.remove(question)
        questions_list.insert((request_order - 1) if (request_order > 0) else 0, question)
        # Order of each question is its position in the array + 1 (order can't be zero)
        for index, question in enumerate(questions_list):
            question.order = index + 1
            question.save()

        if hint_data is not None:
            hint_serializer = HintSerializer(
                data={**hint_data, 'question': question.id})
            hint_serializer.is_valid(raise_exception=True)
            hint_serializer.save()

        if attachments_data is not None:
            for attachment_data in attachments_data:
                Attachment.objects.create(**attachment_data, question=question)

        return question

    def update(self, instance, validated_data):
        """
        Update question with hint, attachments and order.
        """
        instance.title = validated_data.get('title', instance.title)

        new_question_type = validated_data.get('question_type', None)
        if new_question_type is not None and new_question_type != instance.question_type:
            if instance.question_type == Question.QuestionType.SEL:
                QuestionSEL.objects.get(id=instance.id).delete()
            elif instance.question_type == Question.QuestionType.INPUT:
                QuestionInput.objects.get(id=instance.id).delete()
            elif instance.question_type == Question.QuestionType.SELECT:
                QuestionSelect.objects.get(id=instance.id).delete()
            elif instance.question_type == Question.QuestionType.SORT:
                QuestionSort.objects.get(id=instance.id).delete()
            elif instance.question_type == Question.QuestionType.DOMINO:
                QuestionDomino.objects.get(id=instance.id).delete()
            elif instance.question_type == Question.QuestionType.NUMBER_LINE:
                QuestionNumberLine.objects.get(id=instance.id).delete()
            elif instance.question_type == Question.QuestionType.DRAG_AND_DROP:
                QuestionDragAndDrop.objects.get(id=instance.id).delete()
            elif instance.question_type == Question.QuestionType.FIND_HOTSPOT:
                QuestionFindHotspot.objects.get(id=instance.id).delete()
            elif instance.question_type == Question.QuestionType.CALCUL:
                QuestionCalcul.objects.get(id=instance.id).delete()
            instance.question_type = new_question_type

        if 'attachments' in validated_data:
            instance.attachments.clear()
            for attachment_data in validated_data.get('attachments', []):
                Attachment.objects.create(**attachment_data, question=instance)
            validated_data.pop('attachments')

        if 'hint' in validated_data:
            if hasattr(instance, 'hint'):
                instance.hint.delete()
            elif validated_data['hint'] is not None:
                hint_serializer = HintSerializer(
                    instance.hint,
                    data={**validated_data['hint'], 'question': instance.id})
                hint_serializer.is_valid(raise_exception=True)
                hint_serializer.save()
            validated_data.pop('hint')

        # Check if question order changed to reorder all others questions
        if 'order' in validated_data and instance.order != validated_data['order']:
            request_order = validated_data['order']
            questions = Question.objects.filter(assessment_topic=validated_data['assessment_topic']).select_subclasses()

            # Create an array with the topics from the InheritanceQuerySet
            questions_list = list(questions)

            # Places the question in the position of the array equivalent to its new order
            questions_list.remove(instance)
            questions_list.insert((request_order - 1) if (request_order > 0) else 0, instance)

            # Order of each question is its position in the array + 1 (order can't be zero)
            for index, question in enumerate(questions_list):
                question.order = index + 1
                question.save()

        return super().update(instance, validated_data)

class QuestionDominoSerializer(AbstractQuestionSerializer):
    """
    Question Domino serializer.
    """
    options = DominoOptionSerializer(many=True)

    class Meta:
        model = QuestionDomino
        fields = '__all__'
    
    def create(self, validated_data):
        """
        Create question domino with options.
        """
        options_data = validated_data.pop(
            'options') if 'options' in validated_data else None

        question = super().create(validated_data)

        if options_data is not None:
            for option_data in options_data:
                domino_option_serializer = DominoOptionSerializer(
                    data={**option_data, 'question_domino': question.id})
                domino_option_serializer.is_valid(raise_exception=True)
                domino_option_serializer.save()

        return question

    def update(self, instance, validated_data):
        """
        Update question domino with options.
        """
        if 'options' in validated_data:
            all_options = DominoOption.objects.filter(question_domino=instance)
            for index, option_data in enumerate(validated_data.get('options', [])):
                domino_option = all_options[index]
                domino_option.left_side_value = option_data['left_side_value']
                domino_option.right_side_value = option_data['right_side_value']
                domino_option.valid = option_data['valid']
                domino_option.save()

            validated_data.pop('options')

        return super().update(instance, validated_data)

class QuestionSELSerializer(AbstractQuestionSerializer):
    """
    Question SEL serializer.
    """

    class Meta:
        model = QuestionSEL
        fields = '__all__'

class QuestionInputSerializer(AbstractQuestionSerializer):
    """
    Question input serializer.
    """

    class Meta:
        model = QuestionInput
        fields = '__all__'

class QuestionFindHotspotSerializer(AbstractQuestionSerializer):
    """
    Question find hotspot serializer.
    """

    class Meta:
        model = QuestionFindHotspot
        fields = '__all__'

class QuestionSelectSerializer(AbstractQuestionSerializer):
    """
    Question select serializer.
    """
    options = SelectOptionSerializer(many=True)

    class Meta:
        model = QuestionSelect
        fields = '__all__'

    def create(self, validated_data):
        """
        Create question select with options.
        """
        options_data = validated_data.pop(
            'options') if 'options' in validated_data else None

        question = super().create(validated_data)

        if options_data is not None:
            for option_data in options_data:
                select_option_serializer = SelectOptionSerializer(
                    data={**option_data, 'question_select': question.id})
                select_option_serializer.is_valid(raise_exception=True)
                select_option_serializer.save()

        return question

    def update(self, instance, validated_data):
        """
        Update question select with options.
        """
        instance_class = instance.__class__.__name__

        if 'options' in validated_data:
            if instance_class == 'QuestionSelect':
                instance.options.all().delete()
            for option_data in validated_data.get('options', []):
                select_option_serializer = SelectOptionSerializer(
                    data={**option_data, 'question_select': instance.id})
                select_option_serializer.is_valid(raise_exception=True)
                select_option_serializer.save()
            validated_data.pop('options')

        return super().update(instance, validated_data)


class QuestionDragAndDropSerializer(AbstractQuestionSerializer):
    """
    Question drag and drop serializer.
    """
    drop_areas = AreaOptionSerializer(many=True)

    class Meta:
        model = QuestionDragAndDrop
        fields = '__all__'
    
    def create(self, validated_data):
        """
        Create question question drag and drop with area options.
        """
        options_data = validated_data.pop('drop_areas') if 'drop_areas' in validated_data else None

        question = super().create(validated_data)

        if options_data is not None:
            for option_data in options_data:
                area_option_serializer = AreaOptionSerializer(
                    data={
                        **option_data, 
                        'question_drag_and_drop': question.id,
                        })
                area_option_serializer.is_valid(raise_exception=True)
                area_option_serializer.save()

        return question

    def update(self, instance, validated_data):
        """
        Update question drag and drop with areas options.
        """
        instance_class = instance.__class__.__name__

        if 'drop_areas' in validated_data:
            if instance_class == 'QuestionDragAndDrop':
                instance.drop_areas.all().delete()
                instance.drag_options.all().delete()

            for option_data in validated_data.get('drop_areas', []):
                area_option_serializer = AreaOptionSerializer(
                    data={
                        **option_data, 
                        'question_drag_and_drop': instance.id,
                        })
                area_option_serializer.is_valid(raise_exception=True)
                area_option_serializer.save()

            validated_data.pop('drop_areas')

        return super().update(instance, validated_data)

class QuestionSortSerializer(AbstractQuestionSerializer):
    """
    Question sort serializer.
    """
    options = SortOptionSerializer(many=True)

    class Meta:
        model = QuestionSort
        fields = '__all__'

    def create(self, validated_data):
        """
        Create question select with options.
        """
        options_data = validated_data.pop(
            'options') if 'options' in validated_data else None

        question = super().create(validated_data)

        if options_data is not None:
            for option_data in options_data:
                sort_option_serializer = SortOptionSerializer(
                    data={**option_data, 'question_sort': question.id})
                sort_option_serializer.is_valid(raise_exception=True)
                sort_option_serializer.save()

        return question

    def update(self, instance, validated_data):
        """
        Update question select with options.
        """
        instance_class = instance.__class__.__name__

        if 'options' in validated_data:
            if instance_class == 'QuestionSelect':
                instance.options.clear()
            for option_data in validated_data.get('options', []):
                sort_option_serializer = SortOptionSerializer(
                    data={**option_data, 'question_sort': instance.id})
                sort_option_serializer.is_valid(raise_exception=True)
                sort_option_serializer.save()
            validated_data.pop('options')

        return super().update(instance, validated_data)


class QuestionNumberLineSerializer(AbstractQuestionSerializer):
    """
    Question number line serializer.
    """

    class Meta:
        model = QuestionNumberLine
        fields = '__all__'

class QuestionCalculSerializer(AbstractQuestionSerializer):
    """
    Question calcul serializer.
    """

    class Meta:
        model = QuestionCalcul
        fields = '__all__'

class AssessmentTopicAccessListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        to_create = []
        to_update = []
        for item in validated_data:
            try:
                obj = AssessmentTopicAccess.objects.get(
                    student=item['student'], topic=item['topic'])
                obj.start_date = item['start_date']
                obj.end_date = item['end_date']
                to_update.append(obj)
            except AssessmentTopicAccess.DoesNotExist:
                to_create.append(AssessmentTopicAccess(**item))

        created = AssessmentTopicAccess.objects.bulk_create(to_create)
        AssessmentTopicAccess.objects.bulk_update(
            to_update, ['start_date', 'end_date'])
        return (created if created is not None else []) + to_update


class AssessmentTopicAccessSerializer(serializers.ModelSerializer):
    """
    Assessment topic access serializer.
    """
    topic = NestedRelatedField(
        model=AssessmentTopic, serializer_class=AssessmentTopicSerializer)
    student = NestedRelatedField(
        model=User, serializer_class=UserSerializer)

    class Meta:
        model = AssessmentTopicAccess
        fields = '__all__'
        list_serializer_class = AssessmentTopicAccessListSerializer


class AssessmentTopicDeepSerializer(serializers.ModelSerializer):

    questions = QuestionSerializer(
        many=True, read_only=True, source='question_set')
    has_sel_question = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentTopic
        fields = '__all__'

    def get_has_sel_question(self, instance):
        return instance.order == 1 and instance.assessment.sel_question and Question.objects.filter(question_type='SEL', assessment_topic=instance).exists()

class AssessmentDeepSerializer(serializers.ModelSerializer):

    topics = serializers.SerializerMethodField()
    all_topics_complete = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = '__all__'

    def get_topics(self, instance):
        student_pk = self.context['student_pk']

        accessible_topics = AssessmentTopic.objects.filter(
            assessment=instance,
            assessmenttopicaccess__student=student_pk,
            assessmenttopicaccess__start_date__lte=date.today(),
            assessmenttopicaccess__end_date__gte=date.today()
        ).distinct()

        serializer = AssessmentTopicDeepSerializer(
            accessible_topics, many=True, read_only=True
        )

        return serializer.data

    def get_all_topics_complete(self, instance):

        if not ('student_pk' in self.context):
            return None

        student_pk = self.context['student_pk']

        completed_assessment_topics = AssessmentTopic.objects.filter(
            assessment=instance,
            assessmenttopicaccess__student=student_pk,
            assessmenttopicaccess__assessment_topic_answers__complete=True,
            #assessmenttopicaccess__assessment_topic_answers__assessment_topic_access__student=student_pk
        ).distinct().count()

        total_assessment_accessible_topics = AssessmentTopic.objects.filter(
            assessmenttopicaccess__student=student_pk,
            assessment=instance,
        ).distinct().count()

        return (completed_assessment_topics == total_assessment_accessible_topics)
