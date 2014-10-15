import datetime
from django.shortcuts import render
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
        courses = Course.objects.filter(students=request.user,start_time__lte=datetime.datetime.now().time())
        list = Course.objects.filter(students=request.user)
       # print courses.start_time
        data = {
            'courses': courses
        }
        return render(request, 'student_home.html', data)
    else:
        courses = Course.objects.filter(teacher=request.user)
        print courses.start_time
        data = {
            'courses': courses
        }
        return render(request, 'teacher_home.html', data)


