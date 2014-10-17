from django.test import TestCase
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from factories import TeacherFactory, StudentFactory
from ..models import Course, CheckIn


class ViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        print '\nviews tests'
        password = 'test'
        teacher = TeacherFactory.create(username='teacher', password=password)
        student_1 = StudentFactory.create(username='student_1', password=password)
        student_2 = StudentFactory.create(username='student_2', password=password)
        StudentFactory.create(username='student_3', password=password)
        course = Course.objects.create(name='test course', teacher=teacher, start_time='00:00:00', end_time='23:59:59')
        course.students.add(student_1)
        course.students.add(student_2)
        CheckIn.objects.create(student=student_2, course=course)
        super(ViewTestCase, cls).setUpClass()

    def test_teacher_login(self):
        username = 'teacher'
        password = 'test'
        data = {
            'username': username,
            'password': password,
        }
        response = self.client.post(reverse('login'), data)
        # Check it's a redirect to the profile page
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(response.get('location').endswith(reverse('home')))

    def test_teacher_home(self):
        # Create user and log them in
        self.client.login(username='teacher', password='test')
        # Make the url call and check the html and games queryset length
        response = self.client.get(reverse('home'))
        self.assertInHTML('<strong>test course</strong>', response.content)
        self.assertEqual(response.context['courses_today'].count(), 1)

    def test_student_login(self):
        username = 'student_1'
        password = 'test'
        data = {
            'username': username,
            'password': password,
        }
        response = self.client.post(reverse('login'), data)
        # Check it's a redirect to the profile page
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(response.get('location').endswith(reverse('home')))

    def test_student_home_active_not_check_in(self):
        # Create user and log them in
        self.client.login(username='student_1', password='test')
        # Make the url call and check the html and games queryset length
        response = self.client.get(reverse('home'))
        self.assertInHTML('<h2 id="hasClass">Check in for:</h2>', response.content)
        self.assertEqual(response.context['has_checked_in'].count(), 0)

    def test_student_home_active_checked_in(self):
        # Create user and log them in
        self.client.login(username='student_2', password='test')
        # Make the url call and check the html and games queryset length
        response = self.client.get(reverse('home'))
        self.assertInHTML('<p id="alreadyIn">You have already checked in for test course today.</p>', response.content)
        self.assertEqual(response.context['has_checked_in'].count(), 1)

    def test_student_home_not_active(self):
        # Create user and log them in
        self.client.login(username='student_3', password='test')
        # Make the url call and check the html and games queryset length
        response = self.client.get(reverse('home'))
        self.assertInHTML('<p id="noClass">You have no class at this time today.</p>', response.content)
        self.assertEqual(response.context['has_checked_in'], [])
