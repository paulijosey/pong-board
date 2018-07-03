from datetime import timedelta, datetime
import pytz

from django.test import TestCase
from django.utils import timezone

from leaderboard.models import Player, Match, PlayerRating
from leaderboard.rankings import DEFAULT_K_FACTOR, DEFAULT_ELO_RATING


class PlayerModelTest(TestCase):

    def setUp(self):
        """Set up tests with example player."""
        self.first_name = 'Bob'
        self.last_name = 'Hope'
        self.full_name = f'{self.first_name} {self.last_name}'
        self.player = Player.objects.create(first_name=self.first_name, last_name=self.last_name)

    def test_first_name(self):
        """Test that the player model has a first name field."""
        self.assertEqual(self.player.first_name, self.first_name)

    def test_last_name(self):
        """Test that the player model has a last name field."""
        self.assertEqual(self.player.last_name, self.last_name)
    
    def test_full_name(self):
        """Test that the player model has a full name property."""
        self.assertEqual(self.player.full_name, self.full_name)

    def test_str_representation(self):
        """Test that the string representation is the full name."""
        self.assertEqual(str(self.player), self.full_name)


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

    def test_date(self):
        """
        Test match model has a date property.

        Date is a truncated version of the datetime with only
        the date part.
        """
        expected_date = self.match.datetime.strftime('%m/%d/%Y')
        self.assertEqual(self.match.date, expected_date)

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

    def setUp(self):
        """Set up tests with players."""
        self.player1 = Player.objects.create(first_name='Bob', last_name='Hope')
        self.player2 = Player.objects.create(first_name='Sue', last_name='Hope')
    
    def test_get_recent_match(self):
        """Test that a match is retrieved."""
        match = Match.objects.create(
            winner=self.player1,
            winning_score=21,
            loser=self.player2,
            losing_score=19
        )
        fetched_matches = Match.get_recent_matches(num_matches=1)
        self.assertEqual(fetched_matches[0], match)

    def test_descending_order(self):
        """Test that matches are returned in descending order."""
        match1 = Match.objects.create(
            winner=self.player1,
            winning_score=21,
            loser=self.player2,
            losing_score=19
        )
        match2 = Match.objects.create(
            winner=self.player1,
            winning_score=21,
            loser=self.player2,
            losing_score=19
        )
        fetched_matches = Match.get_recent_matches(num_matches=2)
        self.assertEqual(fetched_matches[0], match2)
        self.assertEqual(fetched_matches[1], match1)

    def test_num_matches(self):
        """Test that only the specified number of matches are returned."""
        for _ in range(10):
            Match.objects.create(
                winner=self.player1,
                winning_score=21,
                loser=self.player2,
                losing_score=19
            )
        fetched_matches = Match.get_recent_matches(num_matches=5)
        self.assertEqual(len(fetched_matches), 5)


class PlayerRatingTest(TestCase):

    def setUp(self):
        """Set up tests with example match."""
        self.player1 = Player.objects.create(first_name='Bob', last_name='Hope')
        self.player2 = Player.objects.create(first_name='Sue', last_name='Hope')

    def test_foreign_key_player(self):
        """Test ranking has a player field foreign key."""
        with self.assertRaises(ValueError):
            PlayerRating.objects.create(player='Joe Hope')
        PlayerRating.objects.create(player=self.player1, rating=1000)  # should not raise error

    def test_player_primary_key(self):
        """Test ranking's player field is primary key."""
        ranking = PlayerRating.objects.create(player=self.player2, rating=1000)
        self.assertEqual(ranking.pk, ranking.player.id)
        self.assertNotEqual(ranking.pk, 1)  # assert keys aren't equal coincidentally

    def test_rating(self):
        """Test that the ranking model has a rating field."""
        ranking = PlayerRating.objects.create(player=self.player1, rating=1000.5145)
        self.assertEqual(ranking.rating, 1000.5145)

    def test_match_adds_player_ranking(self):
        """Test that match submission adds player rankings."""
        Match.objects.create(
            winner=self.player1,
            loser=self.player2,
            winning_score=21,
            losing_score=19
        )
        PlayerRating.objects.get(pk=self.player1.id)  # should not raise error
        PlayerRating.objects.get(pk=self.player2.id)  # should not raise error

    def test_player_ratings(self):
        """Test that player ratings are saved properly after match."""
        Match.objects.create(
            winner=self.player1,
            loser=self.player2,
            winning_score=21,
            losing_score=19
        )
        ranking1 = PlayerRating.objects.get(pk=self.player1.id)
        ranking2 = PlayerRating.objects.get(pk=self.player2.id)
        self.assertEqual(ranking1.rating, DEFAULT_ELO_RATING + DEFAULT_K_FACTOR / 2)
        self.assertEqual(ranking2.rating, DEFAULT_ELO_RATING - DEFAULT_K_FACTOR / 2)

    def test_generate_ratings_in_order(self):
        """
        Test that ratings are generated in correct match order.
        
        If player 1 wins against player 2 first, then player 2 wins
        against player 1, player 2 will have a higher rating (i.e.
        it's dependent on the order of the matches)
        """
        Match.objects.create(
            winner=self.player2,
            loser=self.player1,
            winning_score=21,
            losing_score=19,
            datetime=pytz.utc.localize(datetime(2010, 1, 1)) 
        )
        Match.objects.create(
            winner=self.player1,
            loser=self.player2,
            winning_score=21,
            losing_score=19,
            datetime=pytz.utc.localize(datetime(2000, 1, 1))
        )
        PlayerRating.generate_ratings()
        ranking1 = PlayerRating.objects.get(pk=self.player1.id)
        ranking2 = PlayerRating.objects.get(pk=self.player2.id)
        self.assertGreater(ranking2.rating, ranking1.rating)

    def test_games_played(self):
        """Test property for number of games played."""
        Match.objects.create(
            winner=self.player2,
            loser=self.player1,
            winning_score=21,
            losing_score=19,
            datetime=pytz.utc.localize(datetime(2010, 1, 1)) 
        )
        Match.objects.create(
            winner=self.player1,
            loser=self.player2,
            winning_score=21,
            losing_score=19,
            datetime=pytz.utc.localize(datetime(2000, 1, 1))
        )
        ranking1 = PlayerRating.objects.get(pk=self.player1.id)
        self.assertEqual(ranking1.games_played, 2)

    def test_losses(self):
        """Test property for number of losses."""
        Match.objects.create(
            winner=self.player2,
            loser=self.player1,
            winning_score=21,
            losing_score=19,
            datetime=pytz.utc.localize(datetime(2010, 1, 1)) 
        )
        ranking1 = PlayerRating.objects.get(pk=self.player1.id)
        self.assertEqual(ranking1.losses, 1)
    
    def test_wins(self):
        """Test property for number of wins."""
        Match.objects.create(
            winner=self.player2,
            loser=self.player1,
            winning_score=21,
            losing_score=19,
            datetime=pytz.utc.localize(datetime(2010, 1, 1)) 
        )
        ranking1 = PlayerRating.objects.get(pk=self.player2.id)
        self.assertEqual(ranking1.wins, 1)

    def test_points_won(self):
        """Test property for total points won."""
        Match.objects.create(
            winner=self.player2,
            loser=self.player1,
            winning_score=21,
            losing_score=19,
            datetime=pytz.utc.localize(datetime(2010, 1, 1)) 
        )
        Match.objects.create(
            winner=self.player1,
            loser=self.player2,
            winning_score=21,
            losing_score=19,
            datetime=pytz.utc.localize(datetime(2000, 1, 1))
        )
        ranking1 = PlayerRating.objects.get(pk=self.player1.id)
        self.assertEqual(ranking1.points_won, 40)

    def test_points_lost(self):
        """Test property for total points lost."""
        Match.objects.create(
            winner=self.player2,
            loser=self.player1,
            winning_score=21,
            losing_score=19,
            datetime=pytz.utc.localize(datetime(2010, 1, 1)) 
        )
        Match.objects.create(
            winner=self.player1,
            loser=self.player2,
            winning_score=21,
            losing_score=19,
            datetime=pytz.utc.localize(datetime(2000, 1, 1))
        )
        ranking1 = PlayerRating.objects.get(pk=self.player1.id)
        self.assertEqual(ranking1.points_lost, 40)

    def test_points_per_game(self):
        """Test property for total points lost."""
        Match.objects.create(
            winner=self.player2,
            loser=self.player1,
            winning_score=21,
            losing_score=19,
            datetime=pytz.utc.localize(datetime(2010, 1, 1)) 
        )
        Match.objects.create(
            winner=self.player1,
            loser=self.player2,
            winning_score=21,
            losing_score=19,
            datetime=pytz.utc.localize(datetime(2000, 1, 1))
        )
        ranking1 = PlayerRating.objects.get(pk=self.player1.id)
        self.assertEqual(ranking1.points_per_game, 20)

    def test_point_differential(self):
        """Test property for point differential."""
        Match.objects.create(
            winner=self.player2,
            loser=self.player1,
            winning_score=21,
            losing_score=19,
            datetime=pytz.utc.localize(datetime(2010, 1, 1)) 
        )
        ranking1 = PlayerRating.objects.get(pk=self.player1.id)
        self.assertEqual(ranking1.point_differential, -2)

    def test_avg_point_differential(self):
        """Test property for average point differential."""
        Match.objects.create(
            winner=self.player2,
            loser=self.player1,
            winning_score=21,
            losing_score=19,
            datetime=pytz.utc.localize(datetime(2010, 1, 1)) 
        )
        Match.objects.create(
            winner=self.player2,
            loser=self.player1,
            winning_score=21,
            losing_score=19,
            datetime=pytz.utc.localize(datetime(2000, 1, 1))
        )
        ranking1 = PlayerRating.objects.get(pk=self.player1.id)
        self.assertEqual(ranking1.avg_point_differential, -2)

    def test_win_percent(self):
        """Test property for win percentage."""
        Match.objects.create(
            winner=self.player2,
            loser=self.player1,
            winning_score=21,
            losing_score=19,
            datetime=pytz.utc.localize(datetime(2010, 1, 1)) 
        )
        Match.objects.create(
            winner=self.player1,
            loser=self.player2,
            winning_score=21,
            losing_score=19,
            datetime=pytz.utc.localize(datetime(2000, 1, 1))
        )
        ranking1 = PlayerRating.objects.get(pk=self.player1.id)
        self.assertEqual(ranking1.win_percent, 0.5)
