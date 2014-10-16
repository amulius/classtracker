import datetime
import json
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
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
        has_checked_in = []
        courses = Course.objects.filter(students=request.user, start_time__lte=current_time, end_time__gte=current_time)
        print courses
        if courses:
            has_checked_in = CheckIn.objects.filter(student=request.user, course=courses[0], date=today)
            print has_checked_in
        data = {
            'courses': courses,
            'has_checked_in': has_checked_in,
            'time': current_time
        }
        return render(request, 'student_home.html', data)
    else:
        current_time = datetime.datetime.now().time()
        today = datetime.datetime.now().date()
        current_course = Course.objects.filter(teacher=request.user, start_time__lte=current_time, end_time__gte=current_time)
        current_status = []
        if current_course:
            for student in User.objects.filter(student_courses=current_course[0]):
                current_status.append({
                    'student': student.username,
                    'logged_in': CheckIn.objects.filter(student=student, course=current_course[0], date=today)
                })
        courses_today = Course.objects.filter(teacher=request.user)
        data = {
            'current_course': current_course,
            'courses_today': courses_today,
            'current_status': current_status
        }
        return render(request, 'teacher_home.html', data)


@csrf_exempt
def new_check_in(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        student = User.objects.get(username=data['student'])
        course = Course.objects.get(name=data['course'])
        check_in = CheckIn.objects.create(course=course, student=student)
        response = serializers.serialize('json', {check_in})
        return HttpResponse(response, content_type='application/json')


def course_details(request, course):
    course_status = []
    today = datetime.datetime.now().date()
    active_course = Course.objects.filter(name=course)
    for student in User.objects.filter(student_courses=active_course[0]):
        course_status.append({
            'student': student.username,
            'logged_in': CheckIn.objects.filter(student=student, course=active_course[0], date=today)
        })
    data = {'current_status': course_status}

    return render_to_response('includes/class_details.html', data)