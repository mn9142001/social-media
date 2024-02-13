import django_filters 
from django.db.models import Q
from user.models import User, Region, ShipmentProfile
from django.forms import CharField
from django.contrib.auth.models import Permission


class PermissionFilter(django_filters.FilterSet):
    model = django_filters.CharFilter(field_name="content_type__model")
    app_label = django_filters.CharFilter(field_name="content_type__app_label")

    class Meta:
        model = Permission
        fields = ['model', 'app_label']


class RegionNameFilter(django_filters.CharFilter):
    field_class = CharField

    def filter(self, qs, value):
        if not value: return qs
        return qs.filter(name__text__icontainss = value).distinct()
    

class UserMailFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(lookup_expr='icontainss')

    class Meta:
        model = User
        fields = ['email']


class RegionsFilter(django_filters.FilterSet):
    name = RegionNameFilter()
    is_country = django_filters.BooleanFilter(field_name="parent_region", lookup_expr="isnull")
    
    class Meta:
        model = Region
        fields = ['parent_region', 'name', 'country_code']


class ProfileFilter(django_filters.FilterSet):
    
    class ProfileFilter(django_filters.CharFilter):
        def filter(self, qs, value):
            if not value: return qs
            qs = qs.filter(
                Q(
                    Q(
                        Q(email__icontains=value) | Q(first_name__icontains=value) | Q(last_name__icontains=value) | Q(phone__icontains=value) | Q(alternate_phone__icontains=value)
                    )
                    |
                    Q(
                        Q(user__email__icontains=value) | Q(user__first_name__icontains=value) | Q(user__last_name__icontains=value)
                    )
                )
            ).distinct('id').order_by('id')
            return qs
    
    q = ProfileFilter()

    class Meta:
        model = ShipmentProfile
        fields = ['q']


class UserListFilter(django_filters.FilterSet):

    class UserFilter(django_filters.CharFilter):
        def filter(self, qs, value):
            if not value: return qs
            qs = qs.filter(
                Q(
                        Q(email__icontains=value) | Q(first_name__icontains=value) | Q(last_name__icontains=value) | Q(username__icontains=value) | Q(user_phone_set__phone__icontains=value)
                )
            ).distinct('id').order_by('id')
            return qs
    
    q = UserFilter()

    class Meta:
        model = User
        fields = ['q', "username", "email", "is_blocked", "is_active", "is_staff"]

