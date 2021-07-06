from django.contrib import admin

from .models import Avatar, Profile, TopicCompetency


admin.site.register(Avatar, admin.ModelAdmin)
admin.site.register(Profile, admin.ModelAdmin)
admin.site.register(TopicCompetency, admin.ModelAdmin)
