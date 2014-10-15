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
        courses = Course.objects.filter(students=request.user)
        data = {
            'courses': courses
        }
        return render(request, 'student_home.html', data)
    else:
        courses = Course.objects.filter(teacher=request.user)
        data = {
            'courses': courses
        }
        return render(request, 'teacher_home.html', data)


def view_course(request, course_id):
    course = Course.objects.get(pk=course_id)
    data = {"course": course}
    return render(request, "view_course.html", data)

