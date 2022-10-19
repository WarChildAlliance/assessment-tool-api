import re
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from .models import User, Language, Country, Group as UserGroup
from django.http import HttpResponse
import csv


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role', 'country', 'language')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False

    def clean(self):
        """
        Clean and validate form data
        """
        cleaned_data = self.cleaned_data
        role = self.cleaned_data.get('role')
        if role == User.UserRole.SUPERVISOR and self.cleaned_data.get('password1') == '':
            raise forms.ValidationError('Password required for supervisors.')
        if role == User.UserRole.STUDENT:
            pattern = re.compile("^\d{6,}$")
            if not pattern.search(self.cleaned_data['username']):
                raise forms.ValidationError('Username must be 6 digits.')
            self.cleaned_data['password1'] = None
            self.cleaned_data['password2'] = None
            if (self.cleaned_data.get('language') is None
                    or self.cleaned_data.get('country') is None):
                raise forms.ValidationError(
                    'Language and country required for students.')
        return cleaned_data


class CustomUserAdmin(UserAdmin):
    list_display = ('first_name', 'last_name', 'username', 'role',
                    'country', 'language', 'is_staff', 'group')
    list_display_links = ('username',)
    list_filter = ('is_staff', 'role', 'language', 'country',)
    search_fields = ('username', 'first_name', 'last_name', 'email',)
    ordering = ('group', 'username',)
    actions = ['export_as_csv']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name',
                                      'email', 'country', 'language', 'see_intro',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                    'role',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Supervisor', {'fields': ('created_by',)}),
    )
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "role", "first_name", "last_name",
                           "password1", "password2", "country", "language"),
            },
        ),
    )


class UserGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'supervisor', 'students',)
    list_filter = ('supervisor',)

    def students(self, obj):
        students = UserGroup.objects.filter(id=obj.id)
        exists = User.objects.filter(group__id__in=students).exists()

        if exists:
            return [student['student_group__first_name'] + ' ' + student['student_group__last_name'] + ' (' + student['student_group__username'] + ')'
                    for student in students.values('student_group__username', 'student_group__first_name', 'student_group__last_name')
                    ]
        else:
            return None

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(
            meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field)
                                  for field in field_names])

        return response


admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)
admin.site.register(UserGroup, UserGroupAdmin)
admin.site.register(Language, admin.ModelAdmin)
admin.site.register(Country, admin.ModelAdmin)
