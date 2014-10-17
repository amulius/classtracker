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
        print response
        # Check it's a redirect to the profile page
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(response.get('location').endswith(reverse('home')))
        # self.assertInHTML('test course', response.content)
        # self.assertEqual(response.context['courses_today'].count(), 1)


from selenium import webdriver

class SeleniumTests(LiveServerTestCase):
    # def __init__(self):
    #     self.driver = webdriver.Firefox()
    #     self.driver.implicitly_wait(30)
    #     self.base_url = "http://127.0.0.1:8000/"
    #     self.verificationErrors = []


    @classmethod
    def setUpClass(cls):
        password = 'test'
        teacher_sel = User.objects.create_user(username='teacher_sel', email='test@test.com', password=password, is_student=False)
        student_sel = User.objects.create_user(username='student_sel', email='test@test.com', password=password, is_student=True)
        course = Course.objects.create(name='test course', teacher=teacher_sel, start_time='00:00:00', end_time='00:00:01')
        course.students.add(student_sel)
        cls.selenium = WebDriver()
        super(SeleniumTests, cls).setUpClass()

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

        # self.selenium.find_elements_by_link_text('Check In')[0].click()
        # sleep(0.5)
        # chkin_name = self.selenium.find_element_by_id('checkInButton')
        # print chkin_name.text
        # self.assertIn('Checked In!', chkin_name.text)

    # def tearDown(self):
    #     self.driver.quit()

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

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumTests, cls).tearDownClass()
        print 'end tear down'

    # def test_login(self):
    #     password = 'pass'
    #     teacher_test = User.objects.create_user(username='teacher_test', email='test@test.com', password=password, is_student=False)
    #     student_test = User.objects.create_user(username='student_test', email='test@test.com', password=password, is_student=True)
    #     course_test = Course.objects.create(name='test course', teacher=teacher_test, start_time='00:00:02', end_time='23:59:59')
    #     course_test.students.add(student_test)
    #     print 'test login'
    #     sleep(1)
    #
    #
    #     self.selenium.get("{}{}".format(self.live_server_url, reverse('base')))
    #     # print self.selenium.find_elements_by_link_text('Login')
    #     self.selenium.find_elements_by_link_text('Login')[0].click()
    #     sleep(1)
    #     # # let's fill out the form with our superuser's username and password
    #     self.selenium.find_element_by_name('username').send_keys('teacher_test')
    #     password_input = self.selenium.find_element_by_name('password')
    #     password_input.send_keys(password)
    #     print ''
    #     sleep(1)
    #     # Submit the form
    #     password_input.send_keys(Keys.RETURN)
    #
    #     # self.selenium.find_element_by_id('1').click()
    #     # self.selenium.find_element_by_id('1').click()
    #     course_name = self.selenium.find_element_by_id('1')
    #     self.assertIn('test course', course_name.text)
    #
    # def test_login_active_class(self):
    #     password = 'pass'
    #     teacher_test = User.objects.create_user(username='teacher_test', email='test@test.com', password=password, is_student=False)
    #     student_test = User.objects.create_user(username='student_test', email='test@test.com', password=password, is_student=True)
    #     course_test = Course.objects.create(name='test course', teacher=teacher_test, start_time='00:02:00', end_time='23:59:59')
    #     course_test.students.add(student_test)
    #
    #     self.selenium.get("{}{}".format(self.live_server_url, reverse('base')))
    #
    #     self.selenium.find_elements_by_link_text('Login')[0].click()
    #     sleep(0.5)
    #
    #     self.selenium.find_element_by_name('username').send_keys('teacher_test')
    #     password_input = self.selenium.find_element_by_name('password')
    #     password_input.send_keys(password)
    #     sleep(0.5)
    #     password_input.send_keys(Keys.RETURN)
    #
    #     course_name = self.selenium.find_element_by_id('courseInfo1')
    #     self.assertIn('has', course_name.text)
    #
    # def test_login_inactive_class(self):
    #     password = 'pass'
    #     inactive_teacher_test = User.objects.create_user(username='inactive_teacher_test', email='test@test.com', password=password, is_student=False)
    #     inactive_student_test = User.objects.create_user(username='inactive_student_test', email='test@test.com', password=password, is_student=True)
    #     course_test_2 = Course.objects.create(name='test course 2', teacher=inactive_teacher_test, start_time='00:02:00', end_time='23:59:59')
    #     inactive_course_test = Course.objects.create(name='inactive test course', teacher=inactive_teacher_test, start_time='00:00:02', end_time='00:01:00')
    #     course_test_2.students.add(inactive_student_test)
    #     inactive_course_test.students.add(inactive_student_test)
    #
    #     self.selenium.get("{}{}".format(self.live_server_url, reverse('base')))
    #
    #     self.selenium.find_elements_by_link_text('Login')[0].click()
    #     sleep(0.5)
    #
    #     self.selenium.find_element_by_name('username').send_keys('inactive_teacher_test')
    #     password_input = self.selenium.find_element_by_name('password')
    #     password_input.send_keys(password)
    #     sleep(0.5)
    #     password_input.send_keys(Keys.RETURN)
    #
    #     inactive_course_name = self.selenium.find_element_by_id('2')
    #     self.assertEqual(inactive_course_name.text, 'inactive test course')


# class SyntaxTest(TestCase):
#     def test_syntax(self):
#         """
#         Run pyflakes/pep8 across the code base to check for potential errors.
#         """
#         packages = ['tardy_tracker']
#         warnings = []
#         # Eventually should use flake8 instead so we can ignore specific lines via a comment
#         for package in packages:
#             warnings.extend(run_pyflakes_for_package(package, extra_ignore=("_settings",)))
#             warnings.extend(run_pep8_for_package(package, extra_ignore=("_settings",)))
#         if warnings:
#             self.fail("{0} Syntax warnings!\n\n{1}".format(len(warnings), "\n".join(warnings)))


# class SeleniumTests(LiveServerTestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.selenium = WebDriver()
#         super(SeleniumTests, cls).setUpClass()
#
#     @classmethod
#     def tearDownClass(cls):
#         cls.selenium.quit()
#         super(SeleniumTests, cls).tearDownClass()
#
#     def admin_login(self):
#         # Create a superuser
#         Player.objects.create_superuser('superuser', 'superuser@test.com', 'mypassword')
#
#         # let's open the admin login page
#         self.selenium.get("{}{}".format(self.live_server_url, reverse('admin:index')))
#
#         # let's fill out the form with our superuser's username and password
#         self.selenium.find_element_by_name('username').send_keys('superuser')
#         password_input = self.selenium.find_element_by_name('password')
#         password_input.send_keys('mypassword')
#
#         # Submit the form
#         password_input.send_keys(Keys.RETURN)
#
#     def test_admin_login(self):
#         self.admin_login()
#
#         # sleep for half a second to let the page load
#         sleep(.5)
#
#         # We check to see if 'Site administration' is now on the page, this means we logged in successfully
#         body = self.selenium.find_element_by_tag_name('body')
#         self.assertIn('Site administration', body.text)
#
#     def test_admin_create_card(self):
#         self.admin_login()
#         sleep(.5)
#         # We can check that our Card model is registered with the admin and we can click on it
#         # Get the 2nd one, since the first is the header
#         self.selenium.find_elements_by_link_text('Cards')[1].click()
#         sleep(.5)
#         # Let's click to add a new card
#         self.selenium.find_element_by_link_text('Add card').click()
#         sleep(.5)
#         # Let's fill out the card form
#         self.selenium.find_element_by_name('rank').send_keys("ace")
#         sleep(.5)
#         suit_dropdown = self.selenium.find_element_by_name('suit')
#         sleep(.5)
#         for option in suit_dropdown.find_elements_by_tag_name('option'):
#             if option.text == "heart":
#                 option.click()
#         sleep(.5)
#         # Click save to create the new card
#         self.selenium.find_element_by_css_selector("input[value='Save']").click()
#
#         sleep(.5)
#
#         # Check to see we get the card was added success message
#         body = self.selenium.find_element_by_tag_name('body')
#         self.assertIn('The card "ace of hearts" was added successfully', body.text)
#
#     def test_login(self):
#         username = 'user'
#         password = 'pass'
#         Player.objects.create_user(username, 'user@test.com', password)
#
#         self.selenium.get("{}{}".format(self.live_server_url, reverse('home')))
#         # print self.selenium.find_elements_by_link_text('Login')
#         self.selenium.find_elements_by_link_text('Login')[0].click()
#         sleep(0.5)
#         # # let's fill out the form with our superuser's username and password
#         self.selenium.find_element_by_name('username').send_keys(username)
#         password_input = self.selenium.find_element_by_name('password')
#         password_input.send_keys(password)
#         sleep(0.5)
#         # Submit the form
#         password_input.send_keys(Keys.RETURN)
#
#         body = self.selenium.find_element_by_tag_name('body')
#         self.assertIn('Hi {},'.format(username), body.text)
#
#     def test_admin_create_user(self):
#         self.admin_login()
#         sleep(.5)
#         # We can check that our Card model is registered with the admin and we can click on it
#         # Get the 2nd one, since the first is the header
#         self.selenium.find_elements_by_link_text('Users')[0].click()
#         sleep(.5)
#         # Let's click to add a new card
#         self.selenium.find_element_by_link_text('Add user').click()
#         sleep(.5)
#         # Let's fill out the card form
#         self.selenium.find_element_by_name('password').send_keys('password')
#         self.selenium.find_element_by_name('username').send_keys('TestUser')
#         self.selenium.find_element_by_name('phone').send_keys('555-555-5555')
#         sleep(.5)
#         self.selenium.find_element_by_css_selector("input[value='Save']").click()
#         sleep(.5)
#         # Check to see we get the card was added success message
#         body = self.selenium.find_element_by_tag_name('body')
#         self.assertIn('was added successfully', body.text)