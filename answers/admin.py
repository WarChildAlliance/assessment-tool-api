from django.contrib import admin

from .models import (Answer, AnswerInput, AnswerNumberLine, AnswerSelect,
                     AnswerSession, AnswerSort, AssessmentTopicAnswer)


admin.site.register(Answer, admin.ModelAdmin)
admin.site.register(AnswerInput, admin.ModelAdmin)
admin.site.register(AnswerNumberLine, admin.ModelAdmin)
admin.site.register(AnswerSelect, admin.ModelAdmin)
admin.site.register(AnswerSession, admin.ModelAdmin)
admin.site.register(AnswerSort, admin.ModelAdmin)
admin.site.register(AssessmentTopicAnswer, admin.ModelAdmin)
