from django.contrib import admin

from .models import (Assessment, AssessmentTopic, AssessmentTopicAccess, Attachment, Question,
                     QuestionInput, QuestionSelect, QuestionSort, QuestionNumberLine,
                     SelectOption, SortOption, Hint)


admin.site.register(Assessment, admin.ModelAdmin)
admin.site.register(AssessmentTopic, admin.ModelAdmin)
admin.site.register(AssessmentTopicAccess, admin.ModelAdmin)
admin.site.register(Attachment, admin.ModelAdmin)
admin.site.register(QuestionInput, admin.ModelAdmin)
admin.site.register(QuestionSelect, admin.ModelAdmin)
admin.site.register(QuestionSort, admin.ModelAdmin)
admin.site.register(QuestionNumberLine, admin.ModelAdmin)
admin.site.register(SelectOption, admin.ModelAdmin)
admin.site.register(SortOption, admin.ModelAdmin)
admin.site.register(Hint, admin.ModelAdmin)
