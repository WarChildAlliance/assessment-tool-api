from django.contrib import admin
from django.http import HttpResponse
import csv

from .models import (Answer, AnswerInput, AnswerNumberLine, AnswerSelect,
                     AnswerSession, AnswerSort, AssessmentTopicAnswer)


class AnswerSelectAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic_answer', 'question_value', 'valid')
    search_fields = ('id',)
    actions = ["export_as_csv"]

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    def question_value(self, obj):
        return obj.question.value

class AnswerNumberlineAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic_answer', 'question_value', 'valid')
    search_fields = ('id',)
    actions = ["export_as_csv"]

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    def question_value(self, obj):
        return obj.question.value


class AssessmentTopicAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'complete', 'student')
    search_fields = ('id',)
    actions = ["export_as_csv"]

    def student(self, obj):
        return obj.student.first_name

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

admin.site.register(AnswerSession, admin.ModelAdmin)
admin.site.register(AnswerInput, admin.ModelAdmin)
admin.site.register(AnswerNumberLine, AnswerNumberlineAnswerAdmin)
admin.site.register(AnswerSelect, AnswerSelectAnswerAdmin)
admin.site.register(AnswerSort, admin.ModelAdmin)
admin.site.register(AssessmentTopicAnswer, AssessmentTopicAnswerAdmin)
