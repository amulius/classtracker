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
def checkin(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        #print(data['course'],data['student'])
        stu = (data['student']).lower()# i m seeing username=Manil instead of manil
        #print stu,'stu'
        course = Course.objects.get(name=data['course'])
        student = User.objects.get(username=stu)
        #print course.pk,student.pk,'chk'
        testcheckin = CheckIn.objects.filter(student=student, course=course).count()
        print testcheckin,'test'
        if testcheckin:
            data = {'count':testcheckin,'message':'already_in'}
            #response = serializers.serialize('json', {data})
            response = json.dumps(data)
            return HttpResponse(response, content_type='application/json')

           # return HttpResponse('already_in')
        else :
            check_in = CheckIn.objects.create(student=student, course=course)
            testcheckin+=1
            data = {'count':testcheckin,'message':'in'}
            #response = serializers.serialize('json', {data})
            response = json.dumps(data)
            return HttpResponse(response, content_type='application/json')
            #return HttpResponse('in')
        #print check_in.pk,'chkin'

   # response = serializers.serialize('json', {check_in})
   # return HttpResponse(response, content_type='application/json')