import datetime
from django.shortcuts import render
import time
from tardy_tracker.models import Course



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
        # courses = Course.objects.filter(students=request.user)
        courses = Course.objects.filter(students=request.user, start_time__lte=current_time, end_time__gte=current_time)
        data = {
            'courses': courses
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


