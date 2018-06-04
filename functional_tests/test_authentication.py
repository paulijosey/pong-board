import time

from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class AuthenticationTest(LiveServerTestCase):
        
    def setUp(self):
        """Start all tests by setting up a browser and user."""
        self.browser = webdriver.Firefox()

    def tearDown(self):
        """Stop all tests by shutting down the browser."""
        self.browser.quit()

    def test_authentication(self):
        """
        Test the user authentication experience.

        An anonymous user doesn't see forms to add players or submit
        matches, but they do see a login link. This redirects them to
        a login page, which once logged in, redirects back to home
        (which now has a logout page).
        """
        # Setup user
        username = 'bob'
        password = 'bobistheman'
        user = User.objects.create(username=username)
        user.set_password(password)
        user.save()

        # Bob loads PongBoard.
        self.browser.get(self.live_server_url)

        # He's not logged in, and sees the leaderboard table and recent games
        # but does not see forms to add players or submit matches.
        self.browser.find_element_by_id('leaderboard')
        self.browser.find_element_by_id('recent-matches')
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_id('match-form')
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_id('player-form')

        # He sees a login link, and clicks it
        login_link = self.browser.find_element_by_id('login-link')
        login_link.click()

        # It loads a new page.
        self.assertEqual(self.live_server_url + '/accounts/login/', self.browser.current_url)
        
        # He sees a form to login, and attempts to login
        login_form = self.browser.find_element_by_id('login-form')
        login_form.find_element_by_name('username').send_keys(username)
        login_form.find_element_by_name('password').send_keys('password')
        login_form.submit()
        time.sleep(1)  # allows page to refresh

        # He used the wrong password, and sees an error message
        expected_error = "Your username and password didn't match. Please try again."
        error = self.browser.find_element_by_tag_name('p')
        self.assertEqual(error.text, expected_error)

        # He remembers the correct password, and tries again
        login_form = self.browser.find_element_by_id('login-form')
        login_form.find_element_by_name('username').clear()
        login_form.find_element_by_name('username').send_keys(username)
        login_form.find_element_by_name('password').clear()
        login_form.find_element_by_name('password').send_keys(password)
        login_form.submit()
        time.sleep(1)  # allows page to refresh

        # It logged him in, and went back to the home page.
        self.assertEqual(self.live_server_url + '/', self.browser.current_url)

        # He now sees the submission forms
        self.browser.find_element_by_id('match-form')
        self.browser.find_element_by_id('player-form')
        
        # He sees a logout link as well, and clicks it
        logout_link = self.browser.find_element_by_id('logout-link')
        logout_link.click()

        # It leads a new page, informing he that he was logged out
        self.assertEqual(self.live_server_url + '/accounts/logout/', self.browser.current_url)
        logout_info = self.browser.find_element_by_tag_name('p')
        self.assertEqual(logout_info.text, 'Logged out!')

        # It has a link to log back in, which he clicks and takes him back to login page.
        self.browser.find_element_by_link_text('Click here to login again.').click()
        self.assertEqual(self.live_server_url + '/accounts/login/', self.browser.current_url)
