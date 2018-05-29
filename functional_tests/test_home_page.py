"""Functional tests for the home page."""

from datetime import datetime
import time

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import Select

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

    def test_match_form(self):
        """
        Test the match submission form.

        The match submission form should have a field for the winning
        player, winning score, losing player, and losing score. Upon
        submission, the home page should refresh.
        """
        # Load database with Bob and Sue Hope
        Player.objects.create(first_name='Bob', last_name='Hope')
        Player.objects.create(first_name='Sue', last_name='Hope')

        # Bob loads PongBoard
        self.browser.get(self.live_server_url)

        # He sees the match submission form
        match_form = self.browser.find_element_by_id('match-form')

        # He has the option to select either him or Sue as the winner
        winner_select = Select(match_form.find_element_by_name('winner'))
        winner_options = []
        for winner in winner_select.options:
            winner_options.append(winner.text)
        for player in ['Bob Hope', 'Sue Hope']:
            self.assertIn(player, winner_options)

        # He has the option to select either him or Sue as the loser
        loser_select = Select(match_form.find_element_by_name('loser'))
        loser_options = []
        for loser in loser_select.options:
            loser_options.append(loser.text)
        for player in ['Bob Hope', 'Sue Hope']:
            self.assertIn(player, loser_options)

        # He submits his winning match against Sue

        #match_form.submit()

        # The page refreshes and he sees his match in recent games

        self.fail('Finish testing!!!')
