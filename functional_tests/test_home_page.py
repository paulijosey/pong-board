"""Functional tests for the home page."""

from django.test import LiveServerTestCase
from selenium import webdriver


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
        recent_games_table = self.browser.find_element_by_id('recent-games')

    def test_recent_games(self):
        """
        Examine recent games on home page.
        
        We want the home page to show the 20 most recent games. If more
        than 20 games have been played, there's a load more link. If 20
        or less games have been played, no link is present.
        """
        # Input 20 games

        # Bob loads PongBoard

        # He see all 20 games in the correct order

        # He doesn't see a link to load more

        # Input 1 more game

        # Bob refreshes the page, and sees the 20 most recent games

        # He now sees a link to load more

        self.fail('Finish testing!!!')
