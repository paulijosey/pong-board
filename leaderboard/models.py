from typing import Any
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from leaderboard.rankings import EloRating


class Player(models.Model):
    """Table for keeping player information."""
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    rating = models.IntegerField(default=1450, blank=True, null=True)

    class Meta:
        unique_together = ('first_name', 'last_name')

    def __str__(self):
        """Display player's full name as string object representation."""
        return self.full_name

    @property
    def full_name(self):
        """The players full name, first plus last name."""
        full_name = f'{self.first_name} {self.last_name}'
        return full_name

    def set_rating(self, rating: int):
        """Set the rating of the specified player."""
        self.rating = rating
        self.save_without_elo_update()

    def save_without_elo_update(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        elo_rating = EloRating(use_current_ratings=True)
        elo_rating.set_rating(player=self, rating=self.rating)
        PlayerRating.add_ratings(elo_rating)

class Match(models.Model):
    """Table for keeping track of game scores and winners."""
    winner = models.ForeignKey(Player, default=None, related_name='won_matches')
    winning_score = models.IntegerField(default=None)
    loser = models.ForeignKey(Player, default=None, related_name='lost_matches')
    losing_score = models.IntegerField(default=None)
    datetime = models.DateTimeField(default=timezone.now)
    draw = models.BooleanField(default=False)

    def __str__(self):
        """Display match description as string object representation."""
        return self.description

    @staticmethod
    def get_recent_matches(num_matches: int):
        """Get specified number of recent matches in descending date."""
        recent_matches = Match.objects.order_by('-datetime')[0:num_matches]
        return recent_matches

    @property
    def score(self):
        """Hyphenated version of match score, i.e. 21-19"""
        score = f'{self.winning_score}-{self.losing_score}'
        return score

    @property
    def date(self):
        """Date part of match datetime."""
        date = self.datetime.strftime('%m/%d/%Y')
        return date
    
    @property
    def description(self):
        """Description of who defeated who and what the score was."""
        if self.winning_score == self.losing_score:
            description = (
                f'{self.date}: {self.winner} drew {self.loser} {self.score}'
            )
            return description
        else:
            description = (
                f'{self.date}: {self.winner} defeated {self.loser} {self.score}'
            )
            return description

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.id:  # occurs when the match already exists and is being updated
            PlayerRating.generate_ratings()
        else:  # occurs when it's a new match being added
            elo_rating = EloRating(use_current_ratings=True)
            elo_rating.update_ratings(self.winner, self.loser, self.winning_score == self.losing_score)
            PlayerRating.add_ratings(elo_rating)


class PlayerRating(models.Model):
    """Table for keeping track of a player's rating."""
    player = models.OneToOneField(Player, default=None, primary_key=True)
    rating = models.IntegerField(default=None, blank=False)
    
    @staticmethod
    def add_ratings(elo_rating: EloRating):
        """Add ratings to database given EloRating object."""
        PlayerRating.objects.all().delete()
        for player, rating in elo_rating.ratings.items():
            PlayerRating.objects.create(player=player, rating=rating)
            player.set_rating(rating)

    @staticmethod
    def generate_ratings():
        """Generate ratings from scratch based on all previous matches."""
        elo_rating = EloRating()
        matches = Match.objects.all().order_by('datetime')
        for match in matches:
            draw = match.winning_score == match.losing_score
            elo_rating.update_ratings(match.winner, match.loser, draw=draw)
        PlayerRating.add_ratings(elo_rating)

    @property
    def games_played(self):
        """Returns the number of games played."""
        games_played = self.wins + self.losses + self.draws
        return games_played
        
    @property
    def losses(self):
        """Returns the number of losses."""
        # check for games where the player is the loser and its not a draw
        losses = Match.objects.filter(loser=self.player).exclude(draw=True).count()
        return losses

    @property
    def wins(self):
        """Returns the number of wins."""
        wins = Match.objects.filter(winner=self.player).exclude(draw=True).count()
        return wins

    @property
    def draws(self):
        """Returns the number of wins."""
        # draws = Match.objects.filter(winner=self.player, draw=True).count()
        wins_draw = Match.objects.filter(winner=self.player).exclude(draw=False).count()
        losses_draw = Match.objects.filter(loser=self.player).exclude(draw=False).count()
        draws = wins_draw + losses_draw
        return draws

    @property
    def points_won(self):
        """Returns the number of points won."""
        winning_matches = Match.objects.filter(winner=self.player)
        losing_matches = Match.objects.filter(loser=self.player)
        points_won = (
            winning_matches.aggregate(points=Coalesce(Sum('winning_score'), 0))['points']
            + losing_matches.aggregate(points=Coalesce(Sum('losing_score'), 0))['points']
        )
        return points_won

    @property
    def points_lost(self):
        """Returns the number of points lost."""
        winning_matches = Match.objects.filter(winner=self.player)
        losing_matches = Match.objects.filter(loser=self.player)
        points_lost = (
            winning_matches.aggregate(points=Coalesce(Sum('losing_score'), 0))['points']
            + losing_matches.aggregate(points=Coalesce(Sum('winning_score'), 0))['points']
        )
        return points_lost

    @property
    def points_per_game(self):
        """Returns the number of wins."""
        if self.games_played == 0:
            points_per_game = 0
        else:
            points_per_game = self.points_won / self.games_played
        return points_per_game

    @property
    def point_differential(self):
        """Return the points won minus points lost."""
        point_differential = self.points_won - self.points_lost
        return point_differential

    @property
    def avg_point_differential(self):
        """Return the average point differential."""
        if self.games_played == 0:
            avg_point_differential = 0
        else:
            avg_point_differential = self.point_differential / self.games_played
        return avg_point_differential

    @property
    def win_percent(self):
        """Return the win percentage."""
        if self.games_played == 0:
            win_percent = 0
        else:
            win_percent = self.wins / self.games_played
        return win_percent
