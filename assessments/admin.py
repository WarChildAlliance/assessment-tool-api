from django.contrib import admin

from .models import (Assessment, AssessmentTopic, AssessmentTopicAccess, Attachment, Question,
                     QuestionInput, QuestionSelect, QuestionSort, QuestionNumberLine,
                     SelectOption, SortOption, Hint)


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'select_option_id')
    search_fields = ('file',)

    def select_option_id(self, obj):
        if (obj.select_option):
            return obj.select_option.id
        else:
            return None

class QuestionSelectAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)

class SelectOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'value')
    search_fields = ('value',)

admin.site.register(Assessment, admin.ModelAdmin)
admin.site.register(AssessmentTopic, admin.ModelAdmin)
admin.site.register(AssessmentTopicAccess, admin.ModelAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(QuestionInput, admin.ModelAdmin)
admin.site.register(QuestionSelect, QuestionSelectAdmin)
admin.site.register(QuestionSort, admin.ModelAdmin)
admin.site.register(QuestionNumberLine, admin.ModelAdmin)
admin.site.register(SelectOption, SelectOptionAdmin)
admin.site.register(SortOption, admin.ModelAdmin)
admin.site.register(Hint, admin.ModelAdmin)
