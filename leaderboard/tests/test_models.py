from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from leaderboard.models import Player, Match


class PlayerModelTest(TestCase):

    def test_first_name(self):
        """Test that the player model has a first name field."""
        first_name = 'Bob'
        player = Player.objects.create(first_name=first_name)
        self.assertEqual(player.first_name, first_name)

    def test_last_name(self):
        """Test that the player model has a last name field."""
        last_name = 'Hope'
        player = Player.objects.create(last_name=last_name)
        self.assertEqual(player.last_name, last_name)


class MatchModelTest(TestCase):

    def setUp(self):
        """Set up tests with example match."""
        self.winner = Player.objects.create()
        self.winning_score = 21
        self.loser = Player.objects.create()
        self.losing_score = 19
        self.current_datetime = timezone.now()
        self.match = Match.objects.create(
            winner=self.winner,
            winning_score=self.winning_score,
            loser=self.loser,
            losing_score=self.losing_score
        )

    def test_winner(self):
        """
        Test that the match model has a winner field.

        The winner must be an player id (from the player table).
        """
        self.assertEqual(self.match.winner.id, self.winner.id)
    
    def test_winning_score(self):
        """Test that match model has a winning score field."""
        self.assertEqual(self.match.winning_score, self.winning_score)

    def test_loser(self):
        """
        Test that the match model has a loser field.

        The loser must be an player id (from the player table).
        """
        self.assertEqual(self.match.loser.id, self.loser.id)

    def test_losing_score(self):
        """Test that match model has a losing score field."""
        self.assertEqual(self.match.losing_score, self.losing_score)
    
    def test_match_datetime(self):
        """
        Test that match model has a datetime field.

        The datetime field should be automatically set to the current
        datetime.
        """
        self.assertAlmostEqual(self.match.datetime, self.current_datetime, delta=timedelta(seconds=1))
