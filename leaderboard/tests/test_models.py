from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from leaderboard.models import Player, Match


class PlayerModelTest(TestCase):

    def setUp(self):
        """Set up tests with example player."""
        self.first_name = 'Bob'
        self.last_name = 'Hope'
        self.player = Player.objects.create(first_name=self.first_name, last_name=self.last_name)

    def test_first_name(self):
        """Test that the player model has a first name field."""
        self.assertEqual(self.player.first_name, self.first_name)

    def test_last_name(self):
        """Test that the player model has a last name field."""
        self.assertEqual(self.player.last_name, self.last_name)
    
    def test_full_name(self):
        """Test that the player model has a full name property."""
        expected_full_name = f'{self.first_name} {self.last_name}'
        self.assertEqual(self.player.full_name, expected_full_name)


class MatchModelTest(TestCase):

    def setUp(self):
        """Set up tests with example match."""
        self.winner = Player.objects.create(first_name='Bob', last_name='Hope')
        self.winning_score = 21
        self.loser = Player.objects.create(first_name='Sue', last_name='Hope')
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
        self.assertAlmostEqual(
            self.match.datetime, self.current_datetime, delta=timedelta(seconds=1)
        )

    def test_score(self):
        """
        Test match model has a score property.

        Score is a hyphenated version of the score, i.e. '21-19'.
        """
        expected_score = f'{self.winning_score}-{self.losing_score}'
        self.assertEqual(self.match.score, expected_score)

    def test_description(self):
        """
        Test match model has a description property.
        
        Match description is a short summary of the match, including
        the date it was played, full name of players, winner, and score.
        i.e. "05-23-2018: Bob Hope defeated Sue Hope 21-19".
        """
        expected_description = (
            self.match.datetime.strftime('%m/%d/%Y') + ': Bob Hope defeated Sue Hope 21-19'
        )
        self.assertEqual(self.match.description, expected_description)



class GetRecentMatchesTest(TestCase):
    
    def test_get_recent_match(self):
        """Test that a match is retrieved."""
        match = Match.objects.create(
            winner=Player.objects.create(),
            winning_score=21,
            loser=Player.objects.create(),
            losing_score=19
        )
        fetched_matches = Match.get_recent_matches(num_matches=1)
        self.assertEqual(fetched_matches[0], match)

    def test_descending_order(self):
        """Test that matches are returned in descending order."""
        match1 = Match.objects.create(
            winner=Player.objects.create(),
            winning_score=21,
            loser=Player.objects.create(),
            losing_score=19
        )
        match2 = Match.objects.create(
            winner=Player.objects.create(),
            winning_score=21,
            loser=Player.objects.create(),
            losing_score=19
        )
        fetched_matches = Match.get_recent_matches(num_matches=2)
        self.assertEqual(fetched_matches[0], match2)
        self.assertEqual(fetched_matches[1], match1)

    def test_num_matches(self):
        """Test that only the specified number of matches are returned."""
        for _ in range(10):
            Match.objects.create(
                winner=Player.objects.create(),
                winning_score=21,
                loser=Player.objects.create(),
                losing_score=19
            )
        fetched_matches = Match.get_recent_matches(num_matches=5)
        self.assertEqual(len(fetched_matches), 5)
