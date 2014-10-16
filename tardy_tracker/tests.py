from time import sleep
from django.core import mail
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.test import TestCase, LiveServerTestCase
from mock import patch, Mock
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
# from cards.forms import EmailUserCreationForm
# from cards.models import Card, Player, WarGame
# from cards.test_utils import run_pyflakes_for_package, run_pep8_for_package
# from cards.utils import create_deck


class UtilTestCase(TestCase):
    def test_create_deck_count(self):
        self.assertEqual(Card.objects.count(), 0)
        create_deck()
        self.assertEqual(Card.objects.count(), 52)


class CardModelTestCase(TestCase):
    def setUp(self):
        self.card = Card.objects.create(suit=Card.CLUB, rank="jack")
        self.card_higher = Card.objects.create(suit=Card.CLUB, rank="ace")

    def test_get_ranking(self):
        self.assertEqual(self.card.get_ranking(), 11)

    def test_war_result(self):
        self.assertEquals(self.card_higher.get_war_result(self.card), 1)
        self.assertEquals(self.card_higher.get_war_result(self.card_higher), 0)
        self.assertEquals(self.card.get_war_result(self.card_higher), -1)


class FormTestCase(TestCase):
    def setUp(self):
        self.test_name = 'test-user'
        self.test_other_name = 'other-test-user'
        self.user = Player.objects.create_user(username=self.test_name)

    def test_clean_username_exception(self):
        # set up the form for testing
        form = EmailUserCreationForm()
        form.cleaned_data = {'username': self.test_name}

        # use a context manager to watch for the validation error being raised
        with self.assertRaises(ValidationError):
            form.clean_username()

    def test_clean_username_pass(self):
        # set up the form for testing
        form = EmailUserCreationForm()
        form.cleaned_data = {'username': self.test_other_name}

        # use a context manager to watch for the validation error being raised
        self.assertEquals(form.clean_username(), self.test_other_name)


class EmailSentTestCase(TestCase):
    def test_register_sends_email(self):
        form = EmailUserCreationForm()
        form.cleaned_data = {
            'username': 'test',
            'email': 'test@test.com',
            'password1': 'test-pw',
            'password2': 'test-pw',
        }
        form.save()
        # Check there is an email to send
        self.assertEqual(len(mail.outbox), 1)
        # Check the subject is what we expect
        self.assertEqual(mail.outbox[0].subject, 'Welcome!')


class UserGetWinLossTestCase(TestCase):
    def setUp(self):
        self.user = Player.objects.create_user(username='test-user', email='test@test.com', password='password')
        self.create_war_game(self.user, WarGame.WIN)
        self.create_war_game(self.user, WarGame.WIN)
        self.create_war_game(self.user, WarGame.LOSS)
        self.create_war_game(self.user, WarGame.LOSS)
        self.create_war_game(self.user, WarGame.LOSS)

    def create_war_game(self, user, result=WarGame.LOSS):
        WarGame.objects.create(result=result, player=user)

    def test_get_wins(self):
        self.assertEqual(self.user.get_results(WarGame.WIN), 2)

    def test_get_losses(self):
        self.assertEqual(self.user.get_results(WarGame.LOSS), 3)


class ViewTestCase(TestCase):
    def setUp(self):
        create_deck()

    def test_deck_page(self):
        response = self.client.get(reverse('deck'))
        self.assertIn('<p>Suit: spade, Rank: two</p>', response.content)
        self.assertEqual(response.context['cards'].count(), 52)

    def test_faq_page(self):
        response = self.client.get(reverse('faq'))
        self.assertIn('<p>Q: Can I win real money on this website?</p>', response.content)

    def test_filters_page(self):
        response = self.client.get(reverse('filters'))
        self.assertIn('We have 52 cards!', response.content)
        self.assertIn('Uppercased Rank: THREE', response.content)
        self.assertEqual(response.context['cards'].count(), 52)

    def test_register_page(self):
        username = 'new-user'
        data = {
            'username': username,
            'email': 'test@test.com',
            'password1': 'test',
            'password2': 'test'
        }
        response = self.client.post(reverse('register'), data)

        # Check this user was created in the database
        self.assertTrue(Player.objects.filter(username=username).exists())

        # Check it's a redirect to the profile page
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(response.get('location').endswith(reverse('profile')))

    def test_login_page(self):
        username = 'new-user'
        password = 'test'
        Player.objects.create_user(username=username, email='test@test.com', password=password)
        data = {
            'username': username,
            'password': password,
        }
        response = self.client.post(reverse('login'), data)

        # Check it's a redirect to the profile page
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(response.get('location').endswith(reverse('profile')))

    def create_war_game(self, user, result=WarGame.LOSS):
        WarGame.objects.create(result=result, player=user)

    def test_profile_page(self):
        # Create user and log them in
        password = 'passsword'
        user = Player.objects.create_user(username='test-user', email='test@test.com', password=password)
        self.client.login(username=user.username, password=password)

        # Set up some war game entries
        self.create_war_game(user)
        self.create_war_game(user, WarGame.WIN)

        # Make the url call and check the html and games queryset length
        response = self.client.get(reverse('profile'))
        self.assertInHTML('<p>Your email address is {}</p>'.format(user.email), response.content)
        self.assertEqual(len(response.context['games']), 2)

    def test_war_page(self):
        # Create user and log them in
        password = 'passsword'
        user = Player.objects.create_user(username='test-user', email='test@test.com', password=password)
        self.client.login(username=user.username, password=password)

        # Make the url call and check the html and games queryset length
        response = self.client.get(reverse('war'))

        self.assertInHTML('<h2>War!</h2>', response.content)
        self.assertEqual(len(response.context['user_cards']), 1)
        self.assertEqual(len(response.context['dealer_cards']), 1)

    @patch('cards.utils.requests')
    def test_home_page(self, mock_requests):
        mock_comic = {
            'num': 1433,
            'year': "2014",
            'safe_title': "Lightsaber",
            'alt': "A long time in the future, in a galaxy far, far, away.",
            'transcript': "An unusual gamma-ray burst originating from somewhere across the universe.",
            'img': "http://imgs.xkcd.com/comics/lightsaber.png",
            'title': "Lightsaber",
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_comic
        mock_requests.get.return_value = mock_response
        response = self.client.get(reverse('home'))
        self.assertIn('<h3>{} - {}</h3>'.format(mock_comic['safe_title'], mock_comic['year']),
                      response.content)
        self.assertIn('<img alt="{}" src="{}">'.format(mock_comic['alt'], mock_comic['img']),
                      response.content)
        self.assertIn('<p>{}</p>'.format(mock_comic['transcript']), response.content)


class SyntaxTest(TestCase):
    def test_syntax(self):
        """
        Run pyflakes/pep8 across the code base to check for potential errors.
        """
        packages = ['cards']
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
        cls.selenium = WebDriver()
        super(SeleniumTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumTests, cls).tearDownClass()

    def admin_login(self):
        # Create a superuser
        Player.objects.create_superuser('superuser', 'superuser@test.com', 'mypassword')

        # let's open the admin login page
        self.selenium.get("{}{}".format(self.live_server_url, reverse('admin:index')))

        # let's fill out the form with our superuser's username and password
        self.selenium.find_element_by_name('username').send_keys('superuser')
        password_input = self.selenium.find_element_by_name('password')
        password_input.send_keys('mypassword')

        # Submit the form
        password_input.send_keys(Keys.RETURN)

    def test_admin_login(self):
        self.admin_login()

        # sleep for half a second to let the page load
        sleep(.5)

        # We check to see if 'Site administration' is now on the page, this means we logged in successfully
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('Site administration', body.text)

    def test_admin_create_card(self):
        self.admin_login()
        sleep(.5)
        # We can check that our Card model is registered with the admin and we can click on it
        # Get the 2nd one, since the first is the header
        self.selenium.find_elements_by_link_text('Cards')[1].click()
        sleep(.5)
        # Let's click to add a new card
        self.selenium.find_element_by_link_text('Add card').click()
        sleep(.5)
        # Let's fill out the card form
        self.selenium.find_element_by_name('rank').send_keys("ace")
        sleep(.5)
        suit_dropdown = self.selenium.find_element_by_name('suit')
        sleep(.5)
        for option in suit_dropdown.find_elements_by_tag_name('option'):
            if option.text == "heart":
                option.click()
        sleep(.5)
        # Click save to create the new card
        self.selenium.find_element_by_css_selector("input[value='Save']").click()

        sleep(.5)

        # Check to see we get the card was added success message
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('The card "ace of hearts" was added successfully', body.text)

    def test_login(self):
        username = 'user'
        password = 'pass'
        Player.objects.create_user(username, 'user@test.com', password)

        self.selenium.get("{}{}".format(self.live_server_url, reverse('home')))
        # print self.selenium.find_elements_by_link_text('Login')
        self.selenium.find_elements_by_link_text('Login')[0].click()
        sleep(0.5)
        # # let's fill out the form with our superuser's username and password
        self.selenium.find_element_by_name('username').send_keys(username)
        password_input = self.selenium.find_element_by_name('password')
        password_input.send_keys(password)
        sleep(0.5)
        # Submit the form
        password_input.send_keys(Keys.RETURN)

        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('Hi {},'.format(username), body.text)

    def test_admin_create_user(self):
        self.admin_login()
        sleep(.5)
        # We can check that our Card model is registered with the admin and we can click on it
        # Get the 2nd one, since the first is the header
        self.selenium.find_elements_by_link_text('Users')[0].click()
        sleep(.5)
        # Let's click to add a new card
        self.selenium.find_element_by_link_text('Add user').click()
        sleep(.5)
        # Let's fill out the card form
        self.selenium.find_element_by_name('password').send_keys('password')
        self.selenium.find_element_by_name('username').send_keys('TestUser')
        self.selenium.find_element_by_name('phone').send_keys('555-555-5555')
        sleep(.5)
        self.selenium.find_element_by_css_selector("input[value='Save']").click()
        sleep(.5)
        # Check to see we get the card was added success message
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('was added successfully', body.text)