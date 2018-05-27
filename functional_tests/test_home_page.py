"""Functional tests for the home page."""

from datetime import datetime
import time

from django.test import LiveServerTestCase
from selenium import webdriver

from leaderboard.models import Player, Match


class LeaderboardHomePage(LiveServerTestCase):
    """Suite of tests to check for a leaderboard on the home page."""
        
    def setUp(self):
        """Start all tests by setting up a browser."""
        self.browser = webdriver.Firefox()

    def tearDown(self):
        """Stop all tests by shutting down the browser."""
        self.browser.quit()

    def test_load_home_page(self):
        """Load home page and check for expected tables."""
        # Bob wants to checkout PongBoard!
        self.browser.get(self.live_server_url)

        # He notices the page title and header mentions PongBoard
        self.assertIn('PongBoard', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('PongBoard', header_text)

        # He then sees the leaderboard table!
        leaderboard_table = self.browser.find_element_by_id('leaderboard')
        table_headers = leaderboard_table.find_elements_by_tag_name('th')
        self.assertEqual(table_headers[0].text, 'Rank')
        self.assertEqual(table_headers[1].text, 'Name')

        # And he sees a table for most recent games
        recent_matches_table = self.browser.find_element_by_id('recent-matches')

    def test_recent_games(self):
        """
        Examine recent games on home page.
        
        We want the home page to show the 20 most recent games.
        """
        # Input 20 games
        for _ in range(20):
            Match.objects.create(
                winner=Player.objects.create(first_name='Bob', last_name='Hope'),
                loser=Player.objects.create(first_name='Sue', last_name='Hope'),
                winning_score=21,
                losing_score=19
            )

        # Bob loads PongBoard
        self.browser.get(self.live_server_url)

        # He see all 20 games
        recent_matches_table = self.browser.find_element_by_id('recent-matches')
        recent_matches = recent_matches_table.find_elements_by_tag_name('li')
        self.assertEqual(len(recent_matches), 20)
        expected_match_text = (
            datetime.now().strftime("%m/%d/%Y") + ': Bob Hope defeated Sue Hope 21-19'
        )
        for game in recent_matches:
            self.assertEqual(game.text, expected_match_text)

        # Input 1 more game
        Match.objects.create(
            winner=Player.objects.create(first_name='Bob', last_name='Hope'),
            loser=Player.objects.create(first_name='Sue', last_name='Hope'),
            winning_score=21,
            losing_score=10
        )

        # Bob refreshes the page, and sees the 20 most recent games
        self.browser.refresh()
        self.browser.implicitly_wait(1)
        recent_matches_table = self.browser.find_element_by_id('recent-matches')
        recent_matches = recent_matches_table.find_elements_by_tag_name('li')
        self.assertEqual(len(recent_matches), 20)
        self.assertIn('21-10', recent_matches[0].text)
