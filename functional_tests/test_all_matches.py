import time

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from leaderboard.models import Player, Match


class AllMatchesTest(LiveServerTestCase):

    def setUp(self):
        """Start all tests by setting up an authenticated browser."""
        self.browser = webdriver.Firefox()

    def tearDown(self):
        """Stop all tests by shutting down the browser."""
        self.browser.quit()

    def test_all_matches(self):
        """
        Test all matches page view.

        The page should load the 50 most recent matches, and show links
        at the bottom to switch pages.
        """
        # Load database with Bob and Sue Hope
        bob = Player.objects.create(first_name='Bob', last_name='Hope')
        sue = Player.objects.create(first_name='Sue', last_name='Hope')

        # Input 30 games
        for _ in range(30):
            Match.objects.create(
                winner=bob,
                loser=sue,
                winning_score=21,
                losing_score=19
            )

        # Bob loads the home page, and notices a link for all matches.
        self.browser.get(self.live_server_url)
        all_matches_link = self.browser.find_element_by_id('all-matches-link')
        all_matches_link.click()

        # It takes him to a page where he sees all matches.
        matches_url = self.live_server_url + '/matches/'
        self.assertEqual(matches_url, self.browser.current_url)
        matches = self.browser.find_elements_by_id('match')
        self.assertEqual(len(matches), 30)

        # He notices a paginator showing him what page he's on.
        current_page = self.browser.find_element_by_id('current-page')
        self.assertEqual(current_page.text, 'Page 1 of 1')

        # Because there's only 1 page, there are no links to next or previous page
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_id('previous-page-link')
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_id('next-page-link')

       # Input 80 more games and refresh page
        for _ in range(80):
            Match.objects.create(
                winner=bob,
                loser=sue,
                winning_score=21,
                losing_score=19
            ) 
        self.browser.refresh()

        # He notices a paginator showing him he's on page 1 of 3 with a link to the next page.
        matches = self.browser.find_elements_by_id('match')
        self.assertEqual(len(matches), 50)
        current_page = self.browser.find_element_by_id('current-page')
        self.assertEqual(current_page.text, 'Page 1 of 3')
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_id('previous-page-link')
        next_page_link = self.browser.find_element_by_id('next-page-link')
        self.assertEqual(next_page_link.text, 'Next')
        
        # He goes to the next page, and sees a previous page link.
        next_page_link.click()
        matches = self.browser.find_elements_by_id('match')
        self.assertEqual(len(matches), 50)
        current_page = self.browser.find_element_by_id('current-page')
        self.assertEqual(current_page.text, 'Page 2 of 3')
        previous_page_link = self.browser.find_element_by_id('previous-page-link')
        self.assertEqual(previous_page_link.text, 'Previous')
        
        # He goes to the final page, and sees no next page link.
        self.browser.find_element_by_id('next-page-link').click()
        matches = self.browser.find_elements_by_id('match')
        self.assertEqual(len(matches), 10)
        current_page = self.browser.find_element_by_id('current-page')
        self.assertEqual(current_page.text, 'Page 3 of 3')
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_id('next-page-link')

        # He goes back to the previous page.
        self.browser.find_element_by_id('previous-page-link').click()
        current_page = self.browser.find_element_by_id('current-page')
        self.assertEqual(current_page.text, 'Page 2 of 3')

        # Lastly he see a link to go back to the home page, and clicks this
        home_page_link = self.browser.find_element_by_id('home-page-link')
        self.assertEqual(home_page_link.text, 'Back to leaderboard')
        home_page_link.click()
        home_url = self.live_server_url + '/'
        self.assertEqual(home_url, self.browser.current_url)
