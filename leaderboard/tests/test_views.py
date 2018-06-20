from django.test import TestCase
from django.utils.html import escape
from django.contrib.auth.models import User
from django.core.paginator import Paginator

from leaderboard.models import Player, Match
from leaderboard.forms import MatchForm, PlayerForm, DUPLICATE_ERROR


class HomePageTest(TestCase):
    
    def setUp(self):
        """Set up tests with players."""
        self.client.force_login(User.objects.create_user(username='testuser'))
        self.player1 = Player.objects.create(first_name='Bob', last_name='Hope')
        self.player2 = Player.objects.create(first_name='Sue', last_name='Hope')
        self.valid_match_data = {
            'winner': self.player1.id,
            'loser': self.player2.id,
            'winning_score': 21,
            'losing_score': 19,
        }
        self.invalid_match_data = {
            'winner': self.player1.id,
            'loser': self.player2.id,
            'winning_score': 21,
            'losing_score': 24,
        }
        self.valid_player_data = {
            'first_name': 'Joe',
            'last_name': 'Hope'
        }
        self.invalid_player_data = {
            'first_name': 'Bob',
            'last_name': 'Hope'
        }
        self.match_submission_url = '/'
        self.player_add_url = '/'

    def test_uses_template(self):
        """Test that the correct template is used."""
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_match_submission(self):
        """Test that a match gets submitted and saved to database."""
        self.client.post(
            self.match_submission_url,
            self.valid_match_data
        )
        self.assertEqual(Match.objects.count(), 1)

    def test_correct_match_form(self):
        """Test that the correct match form is used."""
        response = self.client.get('/')
        self.assertIsInstance(response.context['match_form'], MatchForm)

    def test_match_post_redirects(self):
        """Test that match post redirects back to home page."""
        response = self.client.post(
            self.match_submission_url,
            self.valid_match_data
        )
        self.assertRedirects(response, '/')

    def test_invalid_match_doesnt_save(self):
        """Test that an invalid match submission doesn't save."""
        self.client.post(
            self.match_submission_url,
            self.invalid_match_data
        )
        self.assertEqual(Match.objects.count(), 0)

    def test_invalid_match_renders_error(self):
        """Test that invalid match submission renders error message."""
        response = self.client.post(
            self.match_submission_url,
            self.invalid_match_data
        )
        self.assertContains(
            response,
            'Losing score must be less than the winning score by at least 2 points.'
        )

    def test_invalid_match_returns_form(self):
        """Test that invalid match form is returned by the server."""
        response = self.client.post(
            self.match_submission_url,
            self.invalid_match_data
        )
        form = response.context['match_form']
        expected_form = MatchForm(self.invalid_match_data)
        self.assertEqual(form.as_p(), expected_form.as_p())

    def test_player_add(self):
        """Test that a player gets added and saved to database."""
        self.client.post(
            self.player_add_url,
            self.valid_player_data
        )
        self.assertEqual(Player.objects.count(), 3)

    def test_correct_player_form(self):
        """Test that the correct form is used."""
        response = self.client.get('/')
        self.assertIsInstance(response.context['player_form'], PlayerForm)

    def test_player_post_redirects(self):
        """Test that player post redirects back to home page."""
        response = self.client.post(
            self.player_add_url,
            self.valid_player_data
        )
        self.assertRedirects(response, '/')

    def test_invalid_player_doesnt_save(self):
        """Test that invalid player submission doesn't save."""
        self.client.post(
            self.player_add_url,
            self.invalid_player_data
        )
        self.assertEqual(Player.objects.count(), 2)

    def test_invalid_player_renders_error(self):
        """Test that invalid player submission renders error message."""
        response = self.client.post(
            self.player_add_url,
            self.invalid_player_data
        )
        self.assertContains(
            response,
            DUPLICATE_ERROR
        )

    def test_invalid_player_returns_form(self):
        """Test that an invalid player form is returned by the server."""
        response = self.client.post(
            self.player_add_url,
            self.invalid_player_data
        )
        form = response.context['player_form']
        expected_form = PlayerForm(self.invalid_player_data)
        self.assertEqual(form.as_p(), expected_form.as_p())


class AllMatchesTest(TestCase):

    @classmethod
    def setUpClass(cls):
        """Add matches to database for each test."""
        super().setUpClass()  # Needed to run only once for all tests
        cls.player1 = Player.objects.create(first_name='Bob', last_name='Hope')
        cls.player2 = Player.objects.create(first_name='Sue', last_name='Hope')
        for _ in range(51):
            Match.objects.create(
                winner=cls.player1,
                loser=cls.player2,
                winning_score=21,
                losing_score=10
            )

    def test_correct_template(self):
        """Test that the match HTML template is used."""
        response = self.client.get('/matches/')
        self.assertTemplateUsed(response, 'all_matches.html')

    def test_paginator_with_all_matches(self):
        """Test view has paginator with all matches."""
        response = self.client.get('/matches/')
        matches = response.context['matches']
        self.assertEqual(matches.paginator.count, 51)

    def test_num_pages(self):
        """Test paginator has correct number of pages."""
        response = self.client.get('/matches/')
        matches = response.context['matches']
        self.assertEqual(matches.paginator.num_pages, 2)

    def test_returns_num_matches(self):
        """Test that 50 matches are returned."""
        response = self.client.get('/matches/')
        matches = response.context['matches']
        self.assertEqual(len(matches), 50)

    def test_default_first_page(self):
        """Test that the default page is page 1."""
        response = self.client.get('/matches/')
        matches = response.context['matches']
        self.assertFalse(matches.has_previous())

    def test_get_page(self):
        """Test page requested through GET."""
        response = self.client.get('/matches/?page=2')
        matches = response.context['matches']
        self.assertEqual(matches.number, 2)

    def test_empty_page(self):
        """Test empty page defaults to last page."""
        response = self.client.get('/matches/?page=1000')
        matches = response.context['matches']
        self.assertFalse(matches.has_next())

    def test_num_matches_last_page(self):
        """Test that 1 match returned in last page."""
        response = self.client.get('/matches/?page=2')
        matches = response.context['matches']
        self.assertEqual(len(matches), 1)
