from django.test import TestCase

from leaderboard.models import Player, Match
from leaderboard.forms import MatchForm


class MatchFormTest(TestCase):

    def setUp(self):
        """Set up tests with players."""
        self.player1 = Player.objects.create(first_name='Bob', last_name='Hope')
        self.player2 = Player.objects.create(first_name='Sue', last_name='Hope')
        self.players = Player.objects.all()

    def test_form_saves(self):
        """Test that the form saves to the match database."""
        form = MatchForm(
            data={
                'winner': self.player1.id,
                'loser': self.player2.id,
                'winning_score': 21,
                'losing_score': 19,
            }
        )
        form.save()
        self.assertEqual(Match.objects.all()[0].winner, self.player1)

    def test_winner_select_options(self):
        """
        Test the selection options for the winner field.

        The options should include the full names of players.
        """
        form = MatchForm()
        winner_field = form['winner']
        for player in self.players:
            self.assertIn(player.full_name, str(winner_field))

    def test_loser_select_options(self):
        """
        Test the selection options for the loser field.

        The options should include the full names of players.
        """
        form = MatchForm()
        loser_field = form['loser']
        for player in self.players:
            self.assertIn(player.full_name, str(loser_field))

    def test_winning_score_greater_than_20(self):
        """Test that the winning score must be greater than 20."""
        form = MatchForm(
            data={
                'winner': self.player1.id,
                'loser': self.player2.id,
                'winning_score': 20,
                'losing_score': 19,
            }
        )
        self.assertFalse(form.is_valid())
    
    def test_losing_score_positive(self):
        """Test that the losing score must be 0 or greater."""
        form = MatchForm(
            data={
                'winner': self.player1.id,
                'loser': self.player2.id,
                'winning_score': 21,
                'losing_score': -1,
            }
        )
        self.assertFalse(form.is_valid())

    def test_losing_score_below_winning(self):
        """Test that losing score is at least 2 under winning score."""
        form1 = MatchForm(
            data={
                'winner': self.player1.id,
                'loser': self.player2.id,
                'winning_score': 21,
                'losing_score': 20,
            }
        )
        form2 = MatchForm(
            data={
                'winner': self.player1.id,
                'loser': self.player2.id,
                'winning_score': 21,
                'losing_score': 24,
            }
        )
        self.assertFalse(form1.is_valid())
        self.assertFalse(form2.is_valid())

    def test_deuce_scores(self):
        """Test that winning score in deuce is 2 above losing score."""
        form1 = MatchForm(
            data={
                'winner': self.player1.id,
                'loser': self.player2.id,
                'winning_score': 24,
                'losing_score': 21,
            }
        )
        form2 = MatchForm(
            data={
                'winner': self.player1.id,
                'loser': self.player2.id,
                'winning_score': 24,
                'losing_score': 22,
            }
        )
        self.assertFalse(form1.is_valid())
        self.assertTrue(form2.is_valid())

    def test_initial_winning_score(self):
        """Test that the initial winning score is 21."""
        form = MatchForm()
        initial_winning_score = form['winning_score'].initial
        self.assertEqual(initial_winning_score, 21)
