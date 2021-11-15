from django.contrib import admin

from .models import (Answer, AnswerInput, AnswerNumberLine, AnswerSelect,
                     AnswerSession, AnswerSort, AssessmentTopicAnswer)


class AnswerSelectAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic_answer', 'question_identifier', 'valid')
    search_fields = ('id',)

    def question_identifier(self, obj):
        return obj.question.identifier

class AnswerNumberlineAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic_answer', 'question_identifier', 'valid')
    search_fields = ('id',)

    def question_identifier(self, obj):
        return obj.question.identifier




admin.site.register(AnswerSession, admin.ModelAdmin)
admin.site.register(AnswerInput, admin.ModelAdmin)
admin.site.register(AnswerNumberLine, AnswerNumberlineAnswerAdmin)
admin.site.register(AnswerSelect, AnswerSelectAnswerAdmin)
admin.site.register(AnswerSort, admin.ModelAdmin)
admin.site.register(AssessmentTopicAnswer, admin.ModelAdmin)
