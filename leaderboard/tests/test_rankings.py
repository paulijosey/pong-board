from django.test import TestCase

from leaderboard.rankings import EloRating, DEFAULT_ELO_RATING, DEFAULT_K_FACTOR
from leaderboard.models import PlayerRating, Player


class EloRatingTest(TestCase):

    def setUp(self):
        """Set up tests with players and Elo calculated ratings."""
        self.winner_rating = 1300
        self.loser_rating = 900
        self.winner_expected_score = 1 / (
            1 + 10 ** ((self.loser_rating - self.winner_rating) / 400)
        )
        self.loser_expected_score = 1 / (
            1 + 10 ** ((self.winner_rating - self.loser_rating) / 400)
        )
        self.new_winner_rating = self.winner_rating + DEFAULT_K_FACTOR * (
            1 - self.winner_expected_score
        )
        self.new_loser_rating = self.loser_rating + DEFAULT_K_FACTOR * (
            0 - self.loser_expected_score
        )

    def test_default_rating(self):
        """Test that the default rating is correct."""
        self.assertEqual(EloRating().get_rating('player'), DEFAULT_ELO_RATING)

    def test_winner_expected_score(self):
        """Test that winner's expected score is calculated properly."""
        winner_expected_score = EloRating.calculate_expected_score(
            self.winner_rating, self.loser_rating
        )
        self.assertEqual(winner_expected_score, self.winner_expected_score)

    def test_loser_expected_score(self):
        """Test that loser's expected score is calculated properly."""
        loser_expected_score = EloRating.calculate_expected_score(
            self.loser_rating, self.winner_rating
        )
        self.assertEqual(loser_expected_score, self.loser_expected_score)

    def test_new_ratings(self):
        """Test that new ratings are calculated properly."""
        new_winner_rating, new_loser_rating = EloRating().calculate_new_ratings(
            self.winner_rating,
            self.loser_rating
        )
        self.assertEqual(new_winner_rating, self.new_winner_rating)
        self.assertEqual(new_loser_rating, self.new_loser_rating)

    def test_default_expected_score(self):
        """
        Test that the default expected score is calculated properly.
        
        With two players who have never played before, their default
        expected score should be 0.5.
        """
        default_expected_score = EloRating().get_expected_score('player1', 'player2')
        self.assertEqual(default_expected_score, 0.5)

    def test_rating_updates(self):
        """Test that the EloRating class updates and stores ratings."""
        rating = EloRating()
        rating.update_ratings(winner='player1', loser='player2')
        winner_rating = rating.get_rating('player1')
        loser_rating = rating.get_rating('player2')
        expected_winner_rating = DEFAULT_ELO_RATING + DEFAULT_K_FACTOR * 0.5
        expected_loser_rating = DEFAULT_ELO_RATING - DEFAULT_K_FACTOR * 0.5
        self.assertEqual(winner_rating, expected_winner_rating)
        self.assertEqual(loser_rating, expected_loser_rating)

    def test_use_current_rating(self):
        """Test that the EloRating class can use current ratings."""
        player = Player.objects.create(first_name='Bob', last_name='Hope')
        test_rating = 1013
        rated_player = PlayerRating.objects.create(player=player, rating=test_rating)
        rating = EloRating(use_current_ratings=True)
        self.assertEqual(test_rating, rating.get_rating(player))
