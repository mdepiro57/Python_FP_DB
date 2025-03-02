from django.shortcuts import render
from django.http import HttpResponseRedirect
# <HINT> Import any new Models here
from .models import Course, Enrollment, Question, Choice, Submission, Lesson
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
from pprint import pprint
import logging
# Get an instance of a logger
logger = logging.getLogger('django')

# Create your views here.

def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()
    else:
        print(user.username + " is already enrolled")

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


# <HINT> Create a submit view to create an exam submission record for a course enrollment,
# you may implement it based on following logic:
         # Get user and course object, then get the associated enrollment object created when the user enrolled the course
         # Create a submission object referring to the enrollment
         # Collect the selected choices from exam form
         # Add each selected choice object to the submission object
         # Redirect to show_exam_result with the submission id
#def submit(request, course_id):

# <HINT> A example method to collect the selected choices from the exam form from the request object
#def extract_answers(request):
#    submitted_anwsers = []
#    for key in request.POST:
#        if key.startswith('choice'):
#            value = request.POST[key]
#            choice_id = int(value)
#            submitted_anwsers.append(choice_id)
#    return submitted_anwsers
def extract_answers(request):
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            choice_id = int(value)
            submitted_answers.append(choice_id)
            logger.debug("extract_answers '" + key + "' choice " + value)
    return submitted_answers

# <HINT> Create an exam result view to check if learner passed exam and show their question results and result for each question,
# you may implement it based on the following logic:
        # Get course and submission based on their ids
        # Get the selected choice ids from the submission record
        # For each selected choice, check if it is a correct answer or not
        # Calculate the total score

def show_exam_result(request, course_id, submission_id):
    print("show_exam_result")
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    lessons = Lesson.objects.filter(course_id=course.id)
    TheAnswers = set()
    for answer in  submission.choices.all():
        TheAnswers.add(answer.id)

    print(TheAnswers)
    grade_points = 0
    total_points = 0
    context = {'user': request.user}
    context['course'] = course
    context['ThePage'] = []     #See structure below

    """
    {
        'ThePage' : [
                        {
                            'Question' : question_text,
                            'Choices' : [
                                            {
                                                'Text' : choice_text,
                                                'Correct' : 0|1,
                                                'Chosen' : 0|1
                                            }
                                        ]
                        }
                    ]
    }
    """

    for lesson in lessons:
        #print('LESSON ' + str(lesson.order) + ' ' + lesson.title)
        for question in Question.objects.filter(lesson_id=lesson.id):
            #print('QUESTION ' + question.question_text)
            #print('Total points ' + str(total_points) + ' Grade ' + str(question.grade) + ' Points ' + str(grade_points))
            total_points += question.grade
            OneQuestion = {'Question' : question.question_text, 'Grade' : question.grade, 'Choices' : [] }
            for choice in Choice.objects.filter(question_id=question.id):
                #print('CHOICE ' + choice.choice_text + ' ' + str(choice.correct))
                OneChoice = {'Text' : choice.choice_text, 'Correct' : choice.correct, 'Chosen' : 0}
                if (choice.id in TheAnswers):
                    OneChoice['Chosen'] = 1
                    if (choice.correct):
                        grade_points += question.grade
                    #print(str(lesson.order) + '|' + lesson.title + '|' + question.question_text + '|' + choice.choice_text + '|' + str(choice.correct) + ' >CHOSEN<')
                #else:
                    #print(str(lesson.order) + '|' + lesson.title + '|' + question.question_text + '|' + choice.choice_text + '|' + str(choice.correct) + ' >NOT CHOSEN<')
                OneQuestion['Choices'].append(OneChoice)

            context['ThePage'].append(OneQuestion)

    #print('END Total points ' + str(total_points) + ' Points ' + str(grade_points))
    context['total'] = total_points
    context['gradepoints'] = grade_points
    context['grade'] = int((grade_points/total_points) * 100)
    #pprint(context)
    print("Rendering")
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)

    """
	From prints above...
	1|Python Overview|What is Python?|Part of Family Boidae|False >NOT CHOSEN<
	1|Python Overview|What is Python?|An interpreted computer language|True >CHOSEN<
	1|Python Overview|What is Python?|Part of Family Pythonidae|False >NOT CHOSEN<
	1|Python Overview|Lesson 1 Question 2|Correct|True >CHOSEN<
	1|Python Overview|Lesson 1 Question 2|Not correct|False >NOT CHOSEN<
	2|Python Variables|Variables must start with what character(s)?|Any character on keyboard|False >CHOSEN<
	2|Python Variables|Variables must start with what character(s)?|A number [0--9]|False >CHOSEN<
	2|Python Variables|Variables must start with what character(s)?|A graphic character|False >NOT CHOSEN<
	2|Python Variables|Variables must start with what character(s)?|underscore or letter|True >NOT CHOSEN<
	2|Python Variables|Lesson 2 Question 2|Correct|True >CHOSEN<
	2|Python Variables|Lesson 2 Question 2|Not correct|False >NOT CHOSEN<
	3|Python Operators|The '+' is used to do what operation?|Addition|True >CHOSEN<
	3|Python Operators|The '+' is used to do what operation?|Concatenation|True >NOT CHOSEN<
	3|Python Operators|The '+' is used to do what operation?|None of the above|False >NOT CHOSEN<
	3|Python Operators|Lesson 3 Question 2|Correct|True >CHOSEN<
	3|Python Operators|Lesson 3 Question 2|Not correct|False >NOT CHOSEN<

    for answer in answers:  #Usually a subset of all possible choices
        total_points += answer.question.grade
        if answer.correct:
            alert = 'alert-sucess'
            grade_points += answer.question.grade
        else:
            alert = 'alert-danger'
        sometuple =  (answer.question.question_text,answer.choice_text,alert,answer.correct)
        context['answers'] = context['answers'] + (sometuple,)
    #context['answers'] = context['answers'][1:len(context['answers'])]  #Drop the first empty tuple
    """

def submit(request, course_id):
    user = request.user
    course = get_object_or_404(Course, pk=course_id)
    enrollment = Enrollment.objects.get(user=user, course=course)
    submission=Submission.objects.create(enrollment=enrollment)
    answers=extract_answers(request)
    for answer in answers:
        choice = Choice.objects.get(id=answer)
        submission.choices.add(choice)
    print("redirecting to 'onlinecourse:show_exam_result'")
    return HttpResponseRedirect(reverse(viewname='onlinecourse:show_exam_result', args=(course.id, submission.id)))

#select U.username,E.date_enrolled,K.name,
# L.title,Q.question_text,C.choice_text,C.correct
# from auth_user as U left outer join
#      onlinecourse_enrollment as E on (E.user_id = U.id) left outer join
#      onlinecourse_submission as S on (S.enrollment_id = E.id) left outer join
#      onlinecourse_submission_choices as P on (P.submission_id = S.id) left outer join
#      onlinecourse_choice as C on (C.id = P.choice_id) left outer join
#      onlinecourse_question as Q on (Q.id = C.question_id) left outer join
#      onlinecourse_lesson as L on (L.id = Q.lesson_id) left outer join
#      onlinecourse_course as K on (K.id = L.course_id)
# where U.username = 'student'
# Result:
#student|2021-06-16|Introduction to Python|Python Overview|What is Python?|An interpreted computer language|1
#student|2021-06-16|Introduction to Python|Python Variables|Variables must start with what characters?|underscore or letter|1
#student|2021-06-16|Introduction to Python|Python Operators|The '+' is used to do what operation?|None of the above|0

