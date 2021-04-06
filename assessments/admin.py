from django.contrib import admin

from .models import (Assessment, AssessmentTopic, AssessmentTopicAccess, Attachment, Question,
                     QuestionInput, QuestionSelect, QuestionSort, SelectOption,
                     SortOption)

admin.site.register(Assessment, admin.ModelAdmin)
admin.site.register(AssessmentTopic, admin.ModelAdmin)
admin.site.register(AssessmentTopicAccess, admin.ModelAdmin)
admin.site.register(Attachment, admin.ModelAdmin)
admin.site.register(Question, admin.ModelAdmin)
admin.site.register(SelectOption, admin.ModelAdmin)
admin.site.register(SortOption, admin.ModelAdmin)