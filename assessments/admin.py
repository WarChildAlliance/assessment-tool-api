from django.contrib import admin

from .models import (Assessment, AssessmentTopic, AssessmentTopicAccess, Attachment, DominoOption, LearningObjective, Question, QuestionCalcul, QuestionDomino, QuestionFindHotspot,
                     QuestionInput, QuestionSEL, QuestionSelect, QuestionSort, QuestionNumberLine, QuestionDragAndDrop,
                     SelectOption, SortOption, Hint, AreaOption, DraggableOption, Subtopic)


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'question_id', 'question_value', 'select_option_id', 'select_option_value', 'draggable_option_id', 'background_image')
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

    def draggable_option_id(self, obj):
        if (obj.draggable_option):
            return obj.draggable_option.id
        else:
            return None

    def select_option_value(self, obj):
        if (obj.select_option):
            return obj.select_option.value
        else:
            return None
    
    def question_value(self, obj):
        if (obj.question):
            return obj.question.value
        else:
            return None

class QuestionSelectAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'value')
    search_fields = ('title',)

class SelectOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'value', 'question_select_value')
    search_fields = ('value',)

    def question_select_value(self, obj):
        if (obj.question_select):
            return obj.question_select.value
        else:
            return None


class AssessmentTopicAccessAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'topic_name', 'start_date', 'end_date', )

    def student_name(self, obj):
        return obj.student.first_name

    def topic_name(self, obj):
        return obj.topic.name

class AreaOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'question', 'question_id')

    def question_id(self, obj):
        if (obj.question_drag_and_drop):
            return obj.question_drag_and_drop.id
        elif (obj.question_find_hotspot):
            return obj.question_find_hotspot.id
    
    def question(self, obj):
        if (obj.question_drag_and_drop):
            return 'Drag and Drop'
        elif (obj.question_find_hotspot):
            return 'Find hotspot'

admin.site.register(Assessment, admin.ModelAdmin)
admin.site.register(AssessmentTopic, admin.ModelAdmin)
admin.site.register(AssessmentTopicAccess, AssessmentTopicAccessAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(QuestionSEL, admin.ModelAdmin)
admin.site.register(QuestionInput, admin.ModelAdmin)
admin.site.register(QuestionSelect, QuestionSelectAdmin)
admin.site.register(QuestionSort, admin.ModelAdmin)
admin.site.register(QuestionDragAndDrop, admin.ModelAdmin)
admin.site.register(QuestionFindHotspot, admin.ModelAdmin)
admin.site.register(QuestionNumberLine, admin.ModelAdmin)
admin.site.register(QuestionCalcul, admin.ModelAdmin)
admin.site.register(SelectOption, SelectOptionAdmin)
admin.site.register(SortOption, admin.ModelAdmin)
admin.site.register(Hint, admin.ModelAdmin)
admin.site.register(AreaOption, AreaOptionAdmin)
admin.site.register(DraggableOption, admin.ModelAdmin)
admin.site.register(Subtopic, admin.ModelAdmin)
admin.site.register(LearningObjective, admin.ModelAdmin)
admin.site.register(QuestionDomino, admin.ModelAdmin)
admin.site.register(DominoOption, admin.ModelAdmin)
