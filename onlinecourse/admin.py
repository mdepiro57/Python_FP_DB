from django.contrib import admin
# <HINT> Import any new Models here
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Enrollment, Submission
#print("look what I found")      #prints in the runserver window

# <HINT> Register QuestionInline and ChoiceInline classes here
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 3

class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 5

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text','grade']
    inlines = [ChoiceInline]

class ChoiceAdmin(admin.ModelAdmin):
    model = Choice
    list_display = ['choice_text','correct']

class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 5


# Register your models here.
class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']


class LessonAdmin(admin.ModelAdmin):
    model = Lesson
    inlines = [QuestionInline]
    list_display = ['title',Course,'order']
    ordering = ['course_id','order']
    list_filter = ['title']
    search_fields = ['title']

    def get_search_results(self, request, queryset, search_term):
            queryset, may_have_duplicates = super().get_search_results(
                request, queryset, search_term,
            )
            try:
                search_term_as_str = search_term
            except ValueError:
                pass
            else:
                queryset |= self.model.objects.filter(title=search_term_as_str)
            return queryset, may_have_duplicates


class EnrollmentAdmin(admin.ModelAdmin):
#    course = Course.objects.get(id=self.model.objects.course_id)
    #list_display = ['id','user_id','course_id']
    #C = Course.object.get(pk='course_id')
    #U = Auth_user.object.get(pk='user_id')
    #list_select_related = ('user_id','course_id')
    #list_display = ['id','user_id','course_id']
    pass


# <HINT> Register Question and Choice models here
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Question,QuestionAdmin)
admin.site.register(Choice,ChoiceAdmin)

admin.site.register(Enrollment,EnrollmentAdmin)
admin.site.register(Submission)
