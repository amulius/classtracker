from time import sleep
from django.core import mail
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.test import TestCase, LiveServerTestCase
from mock import patch, Mock
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from tardy_tracker.models import User, Course, CheckIn
from tardy_tracker.test_utils import run_pyflakes_for_package, run_pep8_for_package


class ViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        password = 'test'
        teacher = User.objects.create_user(username='teacher', email='test@test.com', password=password, is_student=False)
        student_1 = User.objects.create_user(username='student_1', email='test@test.com', password=password, is_student=True)
        student_2 = User.objects.create_user(username='student_2', email='test@test.com', password=password, is_student=True)
        student_3 = User.objects.create_user(username='student_3', email='test@test.com', password=password, is_student=True)
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
        self.assertInHTML('<h2 id="hasclass">Check in for:</h2>', response.content)
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
        self.assertInHTML('<p id="noclass">You have no class at this time today.</p>', response.content)
        self.assertEqual(response.context['has_checked_in'], [])


class SyntaxTest(TestCase):
    def test_syntax(self):
        """
        Run pyflakes/pep8 across the code base to check for potential errors.
        """
        packages = ['tardy_tracker']
        warnings = []
        # Eventually should use flake8 instead so we can ignore specific lines via a comment
        for package in packages:
            warnings.extend(run_pyflakes_for_package(package, extra_ignore=("_settings",)))
            warnings.extend(run_pep8_for_package(package, extra_ignore=("_settings",)))
        if warnings:
            self.fail("{0} Syntax warnings!\n\n{1}".format(len(warnings), "\n".join(warnings)))


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

    def test_login(self):
        password = 'pass'
        teacher_test = User.objects.create_user(username='teacher_test', email='test@test.com', password=password, is_student=False)
        student_test = User.objects.create_user(username='student_test', email='test@test.com', password=password, is_student=True)
        course_test = Course.objects.create(name='test course', teacher=teacher_test, start_time='00:00:02', end_time='23:59:59')
        course_test.students.add(student_test)

        self.selenium.get("{}{}".format(self.live_server_url, reverse('base')))
        # print self.selenium.find_elements_by_link_text('Login')
        self.selenium.find_elements_by_link_text('Login')[0].click()
        sleep(0.5)
        # # let's fill out the form with our superuser's username and password
        self.selenium.find_element_by_name('username').send_keys('teacher_test')
        password_input = self.selenium.find_element_by_name('password')
        password_input.send_keys(password)
        sleep(0.5)
        # Submit the form
        password_input.send_keys(Keys.RETURN)

        # self.selenium.find_element_by_id('1').click()
        # self.selenium.find_element_by_id('1').click()
        course_name = self.selenium.find_element_by_id('1')
        self.assertIn('test course', course_name.text)

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

    def test_student_has_no_class(self):
        password = 'pass'
        teacher_test = User.objects.create_user(username='teacher_test', email='test@test.com', password=password, is_student=False)
        student_test = User.objects.create_user(username='student_test', email='test@test.com', password=password, is_student=True)
        #course_test = Course.objects.create(name='test course', teacher=teacher_test, start_time='00:02:00', end_time='23:59:59')
        #course_test.students.add(student_test)

        self.selenium.get("{}{}".format(self.live_server_url, reverse('base')))

        self.selenium.find_elements_by_link_text('Login')[0].click()
        sleep(0.5)

        self.selenium.find_element_by_name('username').send_keys('student_test')
        password_input = self.selenium.find_element_by_name('password')
        password_input.send_keys(password)
        sleep(0.5)
        password_input.send_keys(Keys.RETURN)
        course_name = self.selenium.find_element_by_id('noclass')
        print course_name.text
        self.assertIn('You have no class at this time today.', course_name.text)

    def test_student_has_class_not_checked_in(self):
        password = 'pass'
        teacher_test = User.objects.create_user(username='teacher_test', email='test@test.com', password=password, is_student=False)
        student_test = User.objects.create_user(username='student_test', email='test@test.com', password=password, is_student=True)
        course_test = Course.objects.create(name='test course', teacher=teacher_test, start_time='01:02:00', end_time='23:59:59')
        course_test.students.add(student_test)

        self.selenium.get("{}{}".format(self.live_server_url, reverse('base')))

        self.selenium.find_elements_by_link_text('Login')[0].click()
        sleep(0.5)

        self.selenium.find_element_by_name('username').send_keys('student_test')
        password_input = self.selenium.find_element_by_name('password')
        password_input.send_keys(password)
        sleep(0.5)
        password_input.send_keys(Keys.RETURN)
        course_name = self.selenium.find_element_by_id('hasclass')
        print course_name.text
        self.assertIn('Check in for:', course_name.text)

    def test_student_has_class_checked_in(self):
        password = 'pass'
        teacher_test = User.objects.create_user(username='teacher_test', email='test@test.com', password=password, is_student=False)
        student_test = User.objects.create_user(username='student_test', email='test@test.com', password=password, is_student=True)
        course_test = Course.objects.create(name='test course', teacher=teacher_test, start_time='01:02:00', end_time='23:59:59')
        course_test.students.add(student_test)
        CheckIn.objects.create(course=course_test, student=student_test)

        self.selenium.get("{}{}".format(self.live_server_url, reverse('base')))

        self.selenium.find_elements_by_link_text('Login')[0].click()
        sleep(0.5)

        self.selenium.find_element_by_name('username').send_keys('student_test')
        password_input = self.selenium.find_element_by_name('password')
        password_input.send_keys(password)
        sleep(0.5)
        password_input.send_keys(Keys.RETURN)
        course_name = self.selenium.find_element_by_id('alreadyIn')
        print course_name.text
        self.assertIn('You have already checked in for test course today.', course_name.text)
