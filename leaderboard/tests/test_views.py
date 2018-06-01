from django.test import TestCase
from django.utils.html import escape

from leaderboard.models import Player, Match
from leaderboard.forms import MatchForm


class HomePageTest(TestCase):
    
    def setUp(self):
        """Set up tests with players."""
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
        self.match_submission_url = '/'

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

    def test_correct_form(self):
        """Test that the correct form is used."""
        response = self.client.post(
            self.match_submission_url,
            self.valid_match_data
        )
        form = response.context['form']
        expected_form = MatchForm(self.invalid_match_data)
        self.assertEqual(form.as_p(), expected_form.as_p())

    def test_post_redirects(self):
        """Test that the post redirects back to home page."""
        response = self.client.post(
            self.match_submission_url,
            self.valid_match_data
        )
        self.assertRedirects(response, '/')

    def test_invalid_doesnt_save(self):
        """Test that an invalid match submission doesn't save."""
        self.client.post(
            self.match_submission_url,
            self.invalid_match_data
        )
        self.assertEqual(Match.objects.count(), 0)

    def test_invalid_renders_error(self):
        """Test that an invalid match submission renders error message."""
        response = self.client.post(
            self.match_submission_url,
            self.invalid_match_data
        )
        self.assertContains(
            response,
            'Losing score must be less than the winning score by at least 2 points.'
        )
