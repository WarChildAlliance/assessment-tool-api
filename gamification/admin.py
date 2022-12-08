from django.contrib import admin

from .models import Avatar, Profile, QuestionSetCompetency


admin.site.register(Avatar, admin.ModelAdmin)
admin.site.register(Profile, admin.ModelAdmin)
admin.site.register(QuestionSetCompetency, admin.ModelAdmin)
