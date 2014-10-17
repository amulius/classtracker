from time import sleep
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from ..models import Course, CheckIn
from factories import StudentFactory, TeacherFactory


class SeleniumTests(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        print '\nselenium tests'
        password = 'test'
        teacher_sel = TeacherFactory.create(username='teacher_sel', password=password)
        student_sel = StudentFactory.create(username='student_sel', password=password)
        course = Course.objects.create(name='test course', teacher=teacher_sel,
                                       start_time='00:00:00', end_time='00:00:01')
        course.students.add(student_sel)
        cls.selenium = WebDriver()
        super(SeleniumTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumTests, cls).tearDownClass()

    def test_login(self):
        password = 'pass'
        teacher_test = TeacherFactory.create(username='teacher_test', password=password)
        student_test = StudentFactory.create(username='student_test', password=password)
        course_test = Course.objects.create(name='test course', teacher=teacher_test,
                                            start_time='00:00:02', end_time='23:59:59')
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
        teacher_test = TeacherFactory.create(username='teacher_test', password=password)
        student_test = StudentFactory.create(username='student_test', password=password)
        course_test = Course.objects.create(name='test course', teacher=teacher_test,
                                            start_time='00:02:00', end_time='23:59:59')
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
        inactive_teacher_test = TeacherFactory.create(username='inactive_teacher_test', password=password)
        inactive_student_test = StudentFactory.create(username='inactive_student_test', password=password)
        course_test_2 = Course.objects.create(name='test course 2', teacher=inactive_teacher_test,
                                              start_time='00:02:00', end_time='23:59:59')
        inactive_course_test = Course.objects.create(name='inactive test course', teacher=inactive_teacher_test,
                                                     start_time='00:00:02', end_time='00:01:00')
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
        TeacherFactory.create(username='teacher_test', password=password)
        StudentFactory.create(username='student_test', password=password)

        self.selenium.get("{}{}".format(self.live_server_url, reverse('base')))

        self.selenium.find_elements_by_link_text('Login')[0].click()
        sleep(0.5)

        self.selenium.find_element_by_name('username').send_keys('student_test')
        password_input = self.selenium.find_element_by_name('password')
        password_input.send_keys(password)
        sleep(0.5)
        password_input.send_keys(Keys.RETURN)
        sleep(1.0)
        course_name = self.selenium.find_element_by_id('noClass')
        self.assertIn('You have no class at this time today.', course_name.text)

    def test_student_has_class_not_checked_in(self):
        password = 'pass'
        teacher_test = TeacherFactory.create(username='teacher_test', password=password)
        student_test = StudentFactory.create(username='student_test', password=password)
        course_test = Course.objects.create(name='test course', teacher=teacher_test,
                                            start_time='01:02:00', end_time='23:59:59')
        course_test.students.add(student_test)

        self.selenium.get("{}{}".format(self.live_server_url, reverse('base')))

        self.selenium.find_elements_by_link_text('Login')[0].click()
        sleep(0.5)

        self.selenium.find_element_by_name('username').send_keys('student_test')
        password_input = self.selenium.find_element_by_name('password')
        password_input.send_keys(password)
        sleep(0.5)
        password_input.send_keys(Keys.RETURN)
        sleep(1.0)
        course_name = self.selenium.find_element_by_id('hasClass')
        self.assertIn('Check in for:', course_name.text)

    def test_student_has_class_checked_in(self):
        password = 'pass'
        teacher_test = TeacherFactory.create(username='teacher_test', password=password)
        student_test = StudentFactory.create(username='student_test', password=password)
        course_test = Course.objects.create(name='test course', teacher=teacher_test,
                                            start_time='01:02:00', end_time='23:59:59')
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
        sleep(1.0)
        course_name = self.selenium.find_element_by_id('alreadyIn')
        self.assertIn('You have already checked in for test course today.', course_name.text)
