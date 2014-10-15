import datetime
import json
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render
import time
from django.views.decorators.csrf import csrf_exempt
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


@csrf_exempt
def new_check_in(request):
    if request.method == 'POST':
        print(request.body)
        data = json.loads(request.body)
        print(data)
        check_in = CheckIn.objects.create(data)
    response = serializers.serialize('json', {check_in})
    return HttpResponse(response, content_type='application/json')