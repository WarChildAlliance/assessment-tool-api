from enum import Enum

from rest_framework import serializers


class PolymorphicSerializer(serializers.ModelSerializer):
    """
    Serializer to handle multiple subclasses of another class
    - For serialized dict representations, a 'type' key with the class name as
      the value is expected: ex. {'type': 'Decimal', ... }
    - This type information is used in tandem with get_serializer_map(...) to
      manage serializers for multiple subclasses
    From: https://stackoverflow.com/questions/19976202/django-rest-framework-django-polymorphic-modelserialization/44727343#44727343
    """

    def get_serializer_map(self):
        """
        Return a dict to map class names to their respective serializer classes
        To be implemented by all PolymorphicSerializer subclasses
        """
        raise NotImplementedError

    def to_representation(self, obj):
        """
        Translate object to internal data representation
        Override to allow polymorphism
        """
        if hasattr(obj, 'get_type'):
            type_str = obj.get_type()
            if isinstance(type_str, Enum):
                type_str = type_str.value
        else:
            type_str = obj.__class__.__name__
        try:
            serializer = self.get_serializer_map()[type_str]
        except KeyError:
            raise ValueError(
                'Serializer for "{}" does not exist'.format(type_str), )

        data = serializer(obj, context=self.context,
                          partial=self.partial).to_representation(obj)
        # data['type'] = type_str
        return data

    def to_internal_value(self, data):
        """
        Validate data and initialize primitive types
        Override to allow polymorphism
        """
        try:
            type_str = data['type']
        except KeyError:
            raise serializers.ValidationError({
                'type': 'This field is required',
            })

        try:
            serializer = self.get_serializer_map()[type_str]
        except KeyError:
            raise serializers.ValidationError({
                'type': 'Serializer for "{}" does not exist'.format(type_str),
            })

        validated_data = serializer(
            context=self.context, partial=self.partial).to_internal_value(data)
        validated_data['type'] = type_str
        return validated_data

    def create(self, validated_data):
        """
        Translate validated data representation to object
        Override to allow polymorphism
        """
        serializer = self.get_serializer_map()[validated_data['type']]
        validated_data.pop('type')
        return serializer(context=self.context, partial=self.partial).create(validated_data)

    def update(self, instance, validated_data):
        serializer = self.get_serializer_map()[validated_data['type']]
        validated_data.pop('type')
        return serializer(context=self.context, partial=self.partial).update(instance, validated_data)


class NestedRelatedField(serializers.PrimaryKeyRelatedField):
    """
        Model identical to PrimaryKeyRelatedField but its
        representation will be nested and its input will
        be a primary key.
    """

    def __init__(self, **kwargs):
        self.pk_field = kwargs.pop('pk_field', None)
        self.model = kwargs.pop('model', None)
        self.serializer_class = kwargs.pop('serializer_class', None)
        self.queryset = self.model.objects.all()
        super().__init__(**kwargs)

    def to_representation(self, data):
        pk = super(NestedRelatedField, self).to_representation(data)
        try:
            return self.serializer_class(self.model.objects.get(pk=pk)).data
        except self.model.DoesNotExist:
            return None

    def to_internal_value(self, data):
        return serializers.PrimaryKeyRelatedField.to_internal_value(self, data)
