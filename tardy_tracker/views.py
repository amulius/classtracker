import datetime
from django.shortcuts import render
import time
from tardy_tracker.models import Course, CheckIn


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


