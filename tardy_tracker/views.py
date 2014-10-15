import datetime
import json
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render
import time
from django.views.decorators.csrf import csrf_exempt
from tardy_tracker.models import Course, CheckIn, User


def base(request):
    return render(request, 'base.html')


def teacher_home(request):
    courses = Course.objects.filter(teacher=request.user)
    data = {
        'courses': courses
    }
    return render(request, 'teacher_home.html', data)


def student_home(request):
    courses = Course.objects.filter(students=request.user)
    data = {
        'courses': courses
    }
    return render(request, 'student_home.html', data)


def home(request):
    if request.user.is_student:
        current_time = datetime.datetime.now().time()
        today = datetime.datetime.now().date()
        # courses = Course.objects.filter(students=request.user)
        checked_in = []
        courses = Course.objects.filter(students=request.user, start_time__lte=current_time, end_time__gte=current_time)
        if courses:
            checked_in = CheckIn.objects.filter(student=request.user, course=courses[0], date=today)
        data = {
            'courses': courses,
            'checked_in': checked_in,
            'time': current_time
        }
        return render(request, 'student_home.html', data)
    else:
        current_time = datetime.datetime.now().time()
        print current_time
        courses = Course.objects.filter(teacher=request.user, start_time__lte=current_time, end_time__gte=current_time)
        data = {
            'courses': courses
        }
        return render(request, 'teacher_home.html', data)


@csrf_exempt
def new_check_in(request):
    print "check in"
    print request.method
    if request.method == 'POST':
        # print request.body
        # print request.body['student']
        data = json.loads(request.body)
        student = User.objects.get(username=data['student'])
        print student
        course = Course.objects.get(name=data['course'])
        print course
        # check_in = CheckIn(course=course, student=student)
        check_in = CheckIn.objects.create(course=course, student=student)
        print check_in
    response = serializers.serialize('json', {check_in})
    return HttpResponse(response, content_type='application/json')