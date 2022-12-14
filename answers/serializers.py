from assessments.models import (QuestionSetAccess, DraggableOption, Question,
                                AreaOption, SelectOption, SortOption)
from assessments.serializers import (QuestionSetAccessSerializer,
                                     SelectOptionSerializer,
                                     SortOptionSerializer,
                                     DraggableOptionSerializer,
                                     AreaOptionSerializer)
from rest_framework import serializers
from users.models import User
from users.serializers import UserSerializer

from admin.lib.serializers import NestedRelatedField, PolymorphicSerializer

from .models import (Answer, AnswerCalcul, AnswerDomino, AnswerInput, AnswerNumberLine, AnswerSEL,
                     AnswerSelect, AnswerSession, AnswerSort, DragAndDropAreaEntry,
                     AnswerDragAndDrop, QuestionSetAnswer, AnswerCustomizedDragAndDrop)


class QuestionSetAnswerSerializer(serializers.ModelSerializer):
    """
    Question set answer serializer.
    """

    class Meta:
        model = QuestionSetAnswer
        fields = '__all__'


class AnswerSessionSerializer(serializers.ModelSerializer):
    """
    Answer session serializer.
    """

    class Meta:
        model = AnswerSession
        fields = '__all__'


class AnswerSerializer(PolymorphicSerializer):
    """
    Answer serializer.
    """

    class Meta:
        model = Answer
        fields = '__all__'

    def get_serializer_map(self):
        return {
            'AnswerInput': AnswerInputSerializer,
            'AnswerNumberLine': AnswerNumberLineSerializer,
            'AnswerSelect': AnswerSelectSerializer,
            'AnswerSort': AnswerSortSerializer,
            'AnswerDragAndDrop': AnswerDragAndDropSerializer,
            'AnswerSEL': AnswerSELSerializer,
            'AnswerDomino': AnswerDominoSerializer,
            'AnswerCalcul': AnswerCalculSerializer,
            'AnswerCustomizedDragAndDrop': AnswerCustomizedDragAndDropSerializer
        }

    def to_internal_value(self, data):
        data = data.copy()
        question = Question.objects.get_subclass(id=data['question'])
        question_type = type(question).__name__
        if question_type == 'QuestionInput':
            data['type'] = 'AnswerInput'
        elif question_type == 'QuestionNumberLine':
            data['type'] = 'AnswerNumberLine'
        elif question_type == 'QuestionSelect':
            data['type'] = 'AnswerSelect'
        elif question_type == 'QuestionSort':
            data['type'] = 'AnswerSort'
        elif question_type == 'QuestionDragAndDrop':
            data['type'] = 'AnswerDragAndDrop'
        elif question_type == 'QuestionSEL':
            data['type'] = 'AnswerSEL'
        elif question_type == 'QuestionDomino':
            data['type'] = 'AnswerDomino'
        elif question_type == 'QuestionCalcul':
            data['type'] = 'AnswerCalcul'
        elif question_type == 'QuestionCustomizedDragAndDrop':
            data['type'] = 'AnswerCustomizedDragAndDrop'
        return super().to_internal_value(data)


    def to_representation(self, obj):
        sub_obj = Answer.objects.get_subclass(id=obj.id)
        return super().to_representation(sub_obj)


class AbstractAnswerSerializer(serializers.ModelSerializer):
    """
    Abstract serializer for Answer models.
    """

    class Meta:
        model = Answer
        fields = ('question_set_answer', 'question', 'valid', 'start_datetime', 'end_datetime')
        extra_kwargs = {'question_set_answer': {'required': False}}

    def create(self, validated_data):
        """
        Create answer, checking that question_set_answer exists
        """

        if 'question_set_answer' not in validated_data or validated_data['question_set_answer'] is None:
            raise serializers.ValidationError({
                'question_set_answer': 'This field is required',
            })


        answer = super().create(validated_data)
        return answer


class AnswerInputSerializer(AbstractAnswerSerializer):
    """
    Answer input serializer.
    """

    class Meta(AbstractAnswerSerializer.Meta):
        model = AnswerInput
        fields = AbstractAnswerSerializer.Meta.fields + ('value',)


class AnswerSelectSerializer(AbstractAnswerSerializer):
    """
    Answer select serializer.
    """
    selected_option = NestedRelatedField(
        model=SelectOption, serializer_class=SelectOptionSerializer, many=False, required=False)

    class Meta(AbstractAnswerSerializer.Meta):
        model = AnswerSelect
        fields = AbstractAnswerSerializer.Meta.fields + ('selected_option',)


class AnswerSortSerializer(AbstractAnswerSerializer):
    """
    Answer sort serializer.
    """
    category_A = NestedRelatedField(
        model=SortOption, serializer_class=SortOptionSerializer, many=True, required=False)
    category_B = NestedRelatedField(
        model=SortOption, serializer_class=SortOptionSerializer, many=True, required=False)

    class Meta(AbstractAnswerSerializer.Meta):
        model = AnswerSort
        fields = AbstractAnswerSerializer.Meta.fields + \
            ('category_A', 'category_B',)


class AnswerNumberLineSerializer(AbstractAnswerSerializer):
    """
    Answer number line serializer.
    """

    class Meta(AbstractAnswerSerializer.Meta):
        model = AnswerNumberLine
        fields = AbstractAnswerSerializer.Meta.fields + ('value',)

class AnswerCalculSerializer(AbstractAnswerSerializer):
    """
    Answer calcul serializer.
    """

    class Meta(AbstractAnswerSerializer.Meta):
        model = AnswerCalcul
        fields = AbstractAnswerSerializer.Meta.fields + ('value',)

class AnswerCustomizedDragAndDropSerializer(AbstractAnswerSerializer):
    """
    Answer Customized Drag And Drop serializer.
    """

    class Meta(AbstractAnswerSerializer.Meta):
        model = AnswerCustomizedDragAndDrop
        fields = AbstractAnswerSerializer.Meta.fields + ('left_value',  'right_value', 'final_value',)

class DragAndDropAreaEntrySerializer(serializers.ModelSerializer):
    """
    Drag and drop area entry serializer.
    """
    selected_draggable_option = NestedRelatedField(
        model=DraggableOption, serializer_class=DraggableOptionSerializer, many=False, required=False)

    area = NestedRelatedField(
        model=AreaOption, serializer_class=AreaOptionSerializer, many=False)

    class Meta:
        model = DragAndDropAreaEntry
        fields = '__all__'


class AnswerDragAndDropSerializer(AbstractAnswerSerializer):
    """
    Answer drag and drop serializer.
    """
    answers_per_area = DragAndDropAreaEntrySerializer(
        many=True, required=False)

    class Meta(AbstractAnswerSerializer.Meta):
        model = AnswerDragAndDrop
        fields = AbstractAnswerSerializer.Meta.fields + \
            ('answers_per_area',)

    def create(self, validated_data):
        if 'answers_per_area' in validated_data:
            answers_per_area_data = validated_data.pop('answers_per_area')

        instance = super().create(validated_data)

        # Saving answers for each drop area
        if instance is not None:
            for area_entry in answers_per_area_data:
                area_entry_serializer = DragAndDropAreaEntrySerializer(
                    data={
                        'area': area_entry['area'].id,
                        'selected_draggable_option': area_entry['selected_draggable_option'].id,
                        'answer': instance
                    }
                )
                area_entry_serializer.is_valid(raise_exception=True)
                area_entry_serializer.save()

        return instance

class AnswerSELSerializer(AbstractAnswerSerializer):
    """
    Answer SEL serializer.
    """

    class Meta(AbstractAnswerSerializer.Meta):
        model = AnswerSEL
        fields = AbstractAnswerSerializer.Meta.fields + ('statement',)

class AnswerDominoSerializer(AbstractAnswerSerializer):
    """
    Answer Domino serializer.
    """

    class Meta(AbstractAnswerSerializer.Meta):
        model = AnswerDomino
        fields = AbstractAnswerSerializer.Meta.fields + ('selected_domino',)

class QuestionSetAnswerFullSerializer(serializers.ModelSerializer):
    """
    Question set answer serializer.
    """

    question_set_access = NestedRelatedField(
        model=QuestionSetAccess, serializer_class=QuestionSetAccessSerializer)
    answers = AnswerSerializer(many=True)

    class Meta:
        model = QuestionSetAnswer
        fields = '__all__'
        extra_kwargs = {'session': {'required': False}}

    def create(self, validated_data):
        """
        Create assessment question set answer with answers.
        """

        if 'answers' in validated_data:
            validated_data.pop('answers')
            answers = self.initial_data['answers']

        question_set_answer = super().create(validated_data)

        if answers is not None:
            for answer in answers:
                answer_serializer = AnswerSerializer(
                    data={**answer, 'question_set_answer': question_set_answer.id})
                answer_serializer.is_valid(raise_exception=True)
                answer_serializer.save()

        return question_set_answer


class AnswerSessionFullSerializer(serializers.ModelSerializer):
    """
    Answer session full serializer (with question set and answers).
    """
    question_set_answers = QuestionSetAnswerFullSerializer(many=True)
    student = NestedRelatedField(
        model=User, serializer_class=UserSerializer)

    class Meta:
        model = AnswerSession
        fields = '__all__'

    def create(self, validated_data):
        """
        Create session with assessment question set answers.
        """
        if 'question_set_answers' in validated_data:
            validated_data.pop('question_set_answers')
            question_set_answers = self.initial_data['question_set_answers']

        session = super().create(validated_data)

        if question_set_answers is not None:
            for question_set_answer in question_set_answers:
                question_set_answer_serializer = QuestionSetAnswerFullSerializer(
                    data={**question_set_answer, 'session': session.id})
                question_set_answer_serializer.is_valid(raise_exception=True)
                question_set_answer_serializer.save()

        return session

