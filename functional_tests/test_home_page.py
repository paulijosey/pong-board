"""Functional tests for the home page."""

from datetime import datetime
import time

from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY
from django.contrib.sessions.backends.db import SessionStore
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

from leaderboard.models import Player, Match


class LeaderboardHomePage(LiveServerTestCase):
    """Suite of tests to check for a leaderboard on the home page."""
        
    def setUp(self):
        """Start all tests by setting up an authenticated browser."""
        self.browser = webdriver.Firefox()

    def tearDown(self):
        """Stop all tests by shutting down the browser."""
        self.browser.quit()

    def create_preauthenticated_session(self):
        """Login as authenticated user."""
        username = 'bob'
        password = 'bobistheman'
        user = User.objects.create(username=username)
        user.set_password(password)
        user.save()
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('login-link').click()
        login_form = self.browser.find_element_by_id('login-form')
        login_form.find_element_by_name('username').clear()
        login_form.find_element_by_name('username').send_keys(username)
        login_form.find_element_by_name('password').clear()
        login_form.find_element_by_name('password').send_keys(password)
        login_form.submit()
        time.sleep(1)  # allows page to refresh

    def submit_match(self, winner: str, loser: str, winning_score: int, losing_score: int):
        """Submit a match through the website."""
        match_form = self.browser.find_element_by_id('match-form')
        winner_select = Select(match_form.find_element_by_name('winner'))
        loser_select = Select(match_form.find_element_by_name('loser'))
        winner_select.select_by_visible_text(winner)
        loser_select.select_by_visible_text(loser)
        match_form.find_element_by_name('winning_score').clear()
        match_form.find_element_by_name('winning_score').send_keys(winning_score)
        match_form.find_element_by_name('losing_score').clear()
        match_form.find_element_by_name('losing_score').send_keys(losing_score)
        match_form.submit()
        time.sleep(1)  # allows page to refresh

    def add_player(self, first_name: str, last_name: str):
        """Add a new player through the website."""
        player_form = self.browser.find_element_by_id('player-form')
        player_form.find_element_by_name('first_name').clear()
        player_form.find_element_by_name('first_name').send_keys(first_name)
        player_form.find_element_by_name('last_name').clear()
        player_form.find_element_by_name('last_name').send_keys(last_name)
        player_form.submit()
        time.sleep(1)  # allows page to refresh

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
        self.assertEqual(table_headers[2].text, 'Rating')
        self.assertEqual(table_headers[3].text, 'GP')
        self.assertEqual(table_headers[4].text, 'W')
        self.assertEqual(table_headers[5].text, 'L')
        self.assertEqual(table_headers[6].text, 'Win%')
        self.assertEqual(table_headers[7].text, 'PPG')
        self.assertEqual(table_headers[8].text, 'AvgDiff')

        # And he sees a table for most recent games
        self.browser.find_element_by_id('recent-matches')

    def test_recent_games(self):
        """
        Examine recent games on home page.
        
        We want the home page to show the 20 most recent games.
        """
        # Load database with Bob and Sue Hope
        bob = Player.objects.create(first_name='Bob', last_name='Hope')
        sue = Player.objects.create(first_name='Sue', last_name='Hope')

        # Input 20 games
        for _ in range(20):
            Match.objects.create(
                winner=bob,
                loser=sue,
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
            winner=bob,
            loser=sue,
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

    def test_match_submission(self):
        """
        Test the match submission form.

        The match submission form should have a field for the winning
        player, winning score, losing player, and losing score. Upon
        submission, the home page should refresh.
        """
        self.create_preauthenticated_session()

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

        # He tries to submit his winning match against Sue.
        # He accidentally put himself as both the winner and loser.
        self.submit_match(winner='Bob Hope', loser='Bob Hope', winning_score=20, losing_score=-1)

        # He sees an error message and no matches were loaded.
        error = self.browser.find_element_by_class_name('errorlist')
        self.assertEqual(
            'The winner and loser must be different players.',
            error.text
        )
        recent_matches_table = self.browser.find_element_by_id('recent-matches')
        recent_matches = recent_matches_table.find_elements_by_tag_name('li')
        self.assertEqual(len(recent_matches), 0)

        # He tries to correct his error and resubmit, but gets another error.
        # This time his winning score is not high enough.
        self.submit_match(winner='Bob Hope', loser='Sue Hope', winning_score=20, losing_score=-1)
        error = self.browser.find_element_by_class_name('errorlist')
        self.assertEqual(
            'Winning score must be 21 or greater.',
            error.text
        )

        # He tries to submit for a third time, but gets yet another error.
        # This time, his losing score is too low.
        # Bob is clearly drunk and can't enter his match details correctly...
        # It makes you wonder how he managed to beat Sue whilst so drunk.
        self.submit_match(winner='Bob Hope', loser='Sue Hope', winning_score=24, losing_score=-1)
        error = self.browser.find_element_by_class_name('errorlist')
        self.assertEqual(
            'Losing score must be 0 or greater.',
            error.text
        )

        # He tries again... but his winning score is too high relative to the losing score.
        self.submit_match(winner='Bob Hope', loser='Sue Hope', winning_score=24, losing_score=19)
        error = self.browser.find_element_by_class_name('errorlist')
        self.assertEqual(
            'Deuce game! Winner must win by exactly 2 points when above 21.',
            error.text
        )

        # Bob is determined, and resubmits, but this time the losing score is too high.
        self.submit_match(winner='Bob Hope', loser='Sue Hope', winning_score=24, losing_score=25)
        error = self.browser.find_element_by_class_name('errorlist')
        self.assertEqual(
            'Losing score must be less than the winning score by at least 2 points.',
            error.text
        )

        # Bob takes a nap, sobers up, and finally enters his match details correctly.
        self.submit_match(winner='Bob Hope', loser='Sue Hope', winning_score=24, losing_score=22)

        # He sees his match in recent matches!
        recent_matches_table = self.browser.find_element_by_id('recent-matches')
        recent_matches = recent_matches_table.find_elements_by_tag_name('li')
        self.assertEqual(len(recent_matches), 1)
        self.assertIn('24-22', recent_matches[0].text)

    def test_player_submission(self):
        """
        Test that a new player can be submitted.
        
        The player submission form should have a field for player's
        first and last names.
        """
        self.create_preauthenticated_session()
        
        # Load database with Bob Hope
        Player.objects.create(first_name='Bob', last_name='Hope')

        # Bob loads PongBoard
        self.browser.get(self.live_server_url)

        # He just beat Sue, so he's excited to enter submit his match.
        # First he needs to add the players. He tries to add himself.
        self.add_player('Bob', 'Hope')

        # He gets an error message; he forgot he was already added!
        error = self.browser.find_element_by_class_name('errorlist')
        self.assertEqual(
            'Player has already been added with the same first and last name.',
            error.text
        )

        # He adds Sue instead, and can now select her in the match submission form.
        self.add_player('Sue', 'Hope')
        match_form = self.browser.find_element_by_id('match-form')
        winner_select = Select(match_form.find_element_by_name('winner'))
        winner_options = []
        for winner in winner_select.options:
            winner_options.append(winner.text)
        self.assertIn('Sue Hope', winner_options)

    def test_leaderboard(self):
        """
        Test that the leaderboard shows players' rankings.
        """
        # Load database with Bob and Sue Hope
        bob = Player.objects.create(first_name='Bob', last_name='Hope')
        sue = Player.objects.create(first_name='Sue', last_name='Hope')

        # Load database with one match
        Match.objects.create(
            winner=bob,
            loser=sue,
            winning_score=21,
            losing_score=10
        )

        # Bob loads PongBoard and sees him above Sue
        self.browser.get(self.live_server_url)
        player_rankings = self.browser.find_elements_by_id('player-ranking')
        self.assertEqual(len(player_rankings), 2)
        self.assertIn('Bob Hope', player_rankings[0].text)
        self.assertIn('1015', player_rankings[0].text)
        self.assertIn('Sue Hope', player_rankings[1].text)
        self.assertIn('985', player_rankings[1].text)

        # However, he realizes they are unranked
        self.assertIn('N/A', player_rankings[0].text)
        unranked_warning = self.browser.find_element_by_id('unranked-warning')
        self.assertEqual(
            unranked_warning.text,
            'Note: you must play a minimum of 5 games before being ranked.'
        )

        # Submit 4 more matches, and reload
        for _ in range(4):
            Match.objects.create(
                winner=bob,
                loser=sue,
                winning_score=21,
                losing_score=19
            )
        self.browser.get(self.live_server_url)

        # They are now ranked, and the warning is no longer there
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_id('unranked-warning')

        # TODO: test each line in leaderboard for specific stats
