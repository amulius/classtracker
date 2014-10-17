from time import sleep
from django.core import mail
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.test import TestCase, LiveServerTestCase
from mock import patch, Mock
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from tardy_tracker.models import User, Course
from tardy_tracker.test_utils import run_pyflakes_for_package, run_pep8_for_package


class ViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        password = 'test'
        teacher = User.objects.create_user(username='teacher', email='test@test.com', password=password, is_student=False)
        student = User.objects.create_user(username='student', email='test@test.com', password=password, is_student=True)
        course = Course.objects.create(name='test course', teacher=teacher, start_time='00:00:00', end_time='23:59:59')
        course.students.add(student)
        super(ViewTestCase, cls).setUpClass()

    def test_teacher_login(self):
        username = 'teacher'
        password = 'test'
        data = {
            'username': username,
            'password': password,
        }
        response = self.client.post(reverse('login'), data)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(response.get('location').endswith(reverse('home')))


class SeleniumTests(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        password = 'test'
        teacher_sel = User.objects.create_user(username='teacher_sel', email='test@test.com', password=password, is_student=False)
        student_sel = User.objects.create_user(username='student_sel', email='test@test.com', password=password, is_student=True)
        course = Course.objects.create(name='test course', teacher=teacher_sel, start_time='00:00:00', end_time='00:00:01')
        course.students.add(student_sel)
        cls.selenium = WebDriver()
        super(SeleniumTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumTests, cls).tearDownClass()

    def test_login_active_class(self):
        password = 'pass'
        teacher_test = User.objects.create_user(username='teacher_test', email='test@test.com', password=password, is_student=False)
        student_test = User.objects.create_user(username='student_test', email='test@test.com', password=password, is_student=True)
        course_test = Course.objects.create(name='test course', teacher=teacher_test, start_time='00:02:00', end_time='23:59:59')
        course_test.students.add(student_test)

        self.selenium.get("{}{}".format(self.live_server_url, reverse('base')))

        self.selenium.find_elements_by_link_text('Login')[0].click()
        sleep(0.5)

        self.selenium.find_element_by_name('username').send_keys('teacher_test')
        password_input = self.selenium.find_element_by_name('password')
        password_input.send_keys(password)
        sleep(0.5)
        password_input.send_keys(Keys.RETURN)

        course_name = self.selenium.find_element_by_id('courseInfo1')
        self.assertIn('has', course_name.text)

    def test_login_inactive_class(self):
        password = 'pass'
        inactive_teacher_test = User.objects.create_user(username='inactive_teacher_test', email='test@test.com', password=password, is_student=False)
        inactive_student_test = User.objects.create_user(username='inactive_student_test', email='test@test.com', password=password, is_student=True)
        course_test_2 = Course.objects.create(name='test course 2', teacher=inactive_teacher_test, start_time='00:02:00', end_time='23:59:59')
        inactive_course_test = Course.objects.create(name='inactive test course', teacher=inactive_teacher_test, start_time='00:00:02', end_time='00:01:00')
        course_test_2.students.add(inactive_student_test)
        inactive_course_test.students.add(inactive_student_test)

        self.selenium.get("{}{}".format(self.live_server_url, reverse('base')))

        self.selenium.find_elements_by_link_text('Login')[0].click()
        sleep(0.5)

        self.selenium.find_element_by_name('username').send_keys('inactive_teacher_test')
        password_input = self.selenium.find_element_by_name('password')
        password_input.send_keys(password)
        sleep(0.5)
        password_input.send_keys(Keys.RETURN)

        inactive_course_name = self.selenium.find_element_by_id('2')
        self.assertEqual(inactive_course_name.text, 'inactive test course')

