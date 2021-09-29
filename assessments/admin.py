from django.contrib import admin

from .models import (Assessment, AssessmentTopic, AssessmentTopicAccess, Attachment, Question,
                     QuestionInput, QuestionSelect, QuestionSort, QuestionNumberLine,
                     SelectOption, SortOption, Hint)


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'question_id', 'select_option_id', )
    search_fields = ('file',)

    def select_option_id(self, obj):
        if (obj.select_option):
            return obj.select_option.id
        else:
            return None
    
    def question_id(self, obj):
        if (obj.question):
            return obj.question.id
        else:
            return None

class QuestionSelectAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)

class SelectOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'value')
    search_fields = ('value',)


class AssessmentTopicAccessAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'topic_name', 'start_date', 'end_date', )

    def student_name(self, obj):
        return obj.student.first_name

    def topic_name(self, obj):
        return obj.topic.name


    

admin.site.register(Assessment, admin.ModelAdmin)
admin.site.register(AssessmentTopic, admin.ModelAdmin)
admin.site.register(AssessmentTopicAccess, AssessmentTopicAccessAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(QuestionInput, admin.ModelAdmin)
admin.site.register(QuestionSelect, QuestionSelectAdmin)
admin.site.register(QuestionSort, admin.ModelAdmin)
admin.site.register(QuestionNumberLine, admin.ModelAdmin)
admin.site.register(SelectOption, SelectOptionAdmin)
admin.site.register(SortOption, admin.ModelAdmin)
admin.site.register(Hint, admin.ModelAdmin)
