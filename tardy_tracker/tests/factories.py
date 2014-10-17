import factory
from ..models import User


class StudentFactory(factory.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence(lambda i: 'Student{}'.format(i))
    password = factory.PostGenerationMethodCall('set_password',
                                                'password')
    email = 'test@test.com'
    is_student = True


class TeacherFactory(factory.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence(lambda i: 'Teacher{}'.format(i))
    password = factory.PostGenerationMethodCall('set_password',
                                                'password')
    email = 'test@test.com'
    is_student = False
