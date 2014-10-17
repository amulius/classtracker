import datetime
import json
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt
from tardy_tracker.models import Course, CheckIn, User


def login_info(user):
    current_time = datetime.datetime.now().time()
    current_day = datetime.datetime.now().date()
    if user.is_student:
        active_courses = Course.objects.filter(students=user, start_time__lte=current_time, end_time__gte=current_time)
    else:
        active_courses = Course.objects.filter(teacher=user, start_time__lte=current_time, end_time__gte=current_time)

    data = {
        'current_time': current_time,
        'current_day': current_day,
        'active_courses': active_courses,
    }
    return data


def course_status(course, today):
    current_status = []
    for student in User.objects.filter(student_courses=course):
        current_status.append({
            'student': student.username,
            'logged_in': CheckIn.objects.filter(student=student, course=course, date=today)
        })
    return current_status


def base(request):
    return render(request, 'base.html')


def home(request):
    login_data = login_info(request.user)
    if request.user.is_student:
        has_checked_in = []
        total = 0
        if login_data['active_courses']:
            has_checked_in = CheckIn.objects.filter(student=request.user, course=login_data['active_courses'][0], date=login_data['current_day'])
            total = CheckIn.objects.filter(course=login_data['active_courses'][0], student=request.user).count()
        data = {
            'courses': login_data['active_courses'],
            'has_checked_in': has_checked_in,
            'time': login_data['current_time'],
            'total': total
        }
        return render(request, 'student_home.html', data)
    else:
        current_status = []
        if login_data['active_courses']:
            current_status = course_details(login_data['active_courses'][0], login_data['current_day'])
        courses_today = Course.objects.filter(teacher=request.user)
        data = {
            'current_course': login_data['active_courses'],
            'courses_today': courses_today,
            'current_status': current_status
        }
        return render(request, 'teacher_home.html', data)


def ValuesQuerySetToDict(vqs):
    return [item for item in vqs]


@csrf_exempt
def new_check_in(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        student = User.objects.get(username=data['student'])
        course = Course.objects.get(name=data['course'])
        CheckIn.objects.create(course=course, student=student)
        testcheckin = CheckIn.objects.filter(student=student, course=course).count()
        charts = CheckIn.objects.filter(student=student).values('course').annotate(dcount=Count('course'))
        charts_list = ValuesQuerySetToDict(charts)
        check_in_tot = CheckIn.objects.filter(course=course, student=student).count()
        print charts_list, 'charts'
        data = {'count': testcheckin, 'message': 'already_in', 'checkin_total': check_in_tot, 'chart_data': charts_list}
        print data, 'data'
        response = json.dumps(data)
        return HttpResponse(response, content_type='application/json')


def course_details(request, course):
    today = datetime.datetime.now().date()
    active_course = Course.objects.filter(name=course)
    course_status_today = course_status(active_course, today)
    data = {'current_status': course_status_today}

    return render_to_response('includes/class_details.html', data)