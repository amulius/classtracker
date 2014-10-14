from django.shortcuts import render

# Create your views here.
from tardy_tracker.models import Course


def teacher_home(request):
    courses = Course.objects.filter(teacher=request.user)
    data = {
        'courses': courses
    }
    return render(request, 'teacher_home.html', data)