from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

from .models import User, Language, Country


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
            self.cleaned_data['password1'] = None
            self.cleaned_data['password2'] = None
        return cleaned_data


class CustomUserAdmin(UserAdmin):
    list_display = ('first_name', 'last_name', 'username', 'role',
                    'country', 'language', 'is_staff',)
    list_display_links = ('username',)
    list_filter = ('is_staff', 'role', 'language', 'country',)
    search_fields = ('username', 'first_name', 'last_name', 'email',)
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name',
                                      'email', 'country', 'language',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                    'role',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
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


admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)
admin.site.register(Language, admin.ModelAdmin)
admin.site.register(Country, admin.ModelAdmin)
