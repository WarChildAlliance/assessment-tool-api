from django.contrib import admin

from .models import Profile, TopicCompetency


admin.site.register(Profile, admin.ModelAdmin)
admin.site.register(TopicCompetency, admin.ModelAdmin)
