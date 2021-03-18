from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm

from .models import User, UserGroup


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('groups', 'country', 'language')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False

    def clean(self):
        """
        Clean and validate form data
        """
        cleaned_data = self.cleaned_data
        group = self.cleaned_data.get('groups')
        if group.name == 'Supervisor' and self.cleaned_data.get('password1') == '':
            raise forms.ValidationError('Password required for supervisors.')
        if group.name == 'Student':
            self.cleaned_data['password1'] = None
            self.cleaned_data['password2'] = None
        return cleaned_data


class CustomUserAdmin(UserAdmin):
    list_display = ('first_name', 'last_name', 'username', 'groups',
                    'country', 'language', 'is_staff',)
    list_display_links = ('username',)
    list_filter = ('is_staff', 'groups', 'language', 'country',)
    search_fields = ('username', 'first_name', 'last_name', 'email',)
    ordering = ('username',)
    filter_horizontal = ('user_permissions',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name',
                                      'email', 'country', 'language',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                    'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "groups", "first_name", "last_name",
                           "password1", "password2", "country", "language"),
            },
        ),
    )


class UserGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserGroup, UserGroupAdmin)
