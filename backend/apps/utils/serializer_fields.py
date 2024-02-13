from django.core.cache import cache
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, NotFound
import operator
from functools import reduce
from django.db.models import Q
from collections import Counter
from django.core.exceptions import ObjectDoesNotExist


class CurrentUserRelatedField(serializers.SlugRelatedField):

    def __init__(self, slug_field="id", user_field="user_id", **kwargs):
        self.user_field = user_field
        super().__init__(slug_field, **kwargs)

    def get_queryset(self):
        user = self.context['request'].user

        qs = super().get_queryset()

        if user.is_superuser:
            return qs

        qs = qs.filter(**{self.user_field : self.context['request'].user.id} ) 
        return qs


class StringCurrentUserRelatedField(CurrentUserRelatedField):
    
    def to_representation(self, obj):
        data = super().to_representation(obj)
        return str(data)
    
    
class QuerySetField(serializers.ListSerializer):

    @property
    def user(self):
        return self.root.context['request'].user
    
    def __init__(self, queryset, *args, slug_field ="id",  **kwargs):
        kwargs.setdefault('child', serializers.IntegerField())
        self.slug_field = slug_field
        self.querset = queryset
        super().__init__(*args, **kwargs)
        
    def validate_length(self, qs, len):
        if qs.count() < len:
            raise NotFound
        
    def to_internal_value(self, data):
        ids : list[int] = super().to_internal_value(data)
        qs = self.querset.filter(**{f"{self.slug_field}__in" : ids})
        self.validate_length(qs, len(ids))
        return qs
    
    def to_representation(self, data):
        return [getattr(obj, self.slug_field) for obj in data.all()]


class FirstFoundField(serializers.SlugRelatedField):
    
    def to_internal_value(self, data):
        queryset = self.get_queryset()
        try:
            obj = queryset.filter(**{self.slug_field: data}).first()
            if obj is None:
                raise ObjectDoesNotExist

            return obj

        except ObjectDoesNotExist:
            self.fail('does_not_exist', slug_name=self.slug_field, value=str(data))
        except (TypeError, ValueError):
            self.fail('invalid')


class CacheSerializerField(serializers.CharField):
    default_error_messages = serializers.SlugRelatedField.default_error_messages
    
    def __init__(self, model=None, **kwargs):
        self.model = model
        super().__init__(**kwargs)
    
    def to_internal_value(self, data):
        cache_key = super().to_internal_value(data)

        cached_value = cache.get(key=cache_key)

        if cached_value is None:
            self.fail('does_not_exist', slug_name=self.field_name, value=cache_key)

        if self.model is not None:
            return self.model(**cached_value)

        return cached_value
