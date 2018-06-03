from django.db import models
from django.utils import timezone

from leaderboard.rankings import EloRating


class Player(models.Model):
    """Table for keeping player information."""
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)

    class Meta:
        unique_together = ('first_name', 'last_name',)

    def __str__(self):
        """Display player's full name as string object representation."""
        return self.full_name

    @property
    def full_name(self):
        """The players full name, first plus last name."""
        full_name = f'{self.first_name} {self.last_name}'
        return full_name


class Match(models.Model):
    """Table for keeping track of game scores and winners."""
    winner = models.ForeignKey(Player, default=None, related_name='won_matches')
    winning_score = models.IntegerField(default=None)
    loser = models.ForeignKey(Player, default=None, related_name='lost_matches')
    losing_score = models.IntegerField(default=None)
    datetime = models.DateTimeField(default=timezone.now)

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
    def description(self):
        match_date = self.datetime.strftime('%m/%d/%Y')
        description = (
            f'{match_date}: {self.winner} defeated {self.loser} {self.score}'
        )
        return description

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        PlayerRating.generate_ratings()


class PlayerRating(models.Model):
    """Table for keeping track of a player's rating."""
    player = models.OneToOneField(Player, default=None, primary_key=True)
    rating = models.IntegerField(default=None, blank=False)

    @staticmethod
    def generate_ratings():
        PlayerRating.objects.all().delete()
        matches = Match.objects.all().order_by('datetime')
        elo_rating = EloRating()
        for match in matches:
            elo_rating.update_ratings(match.winner, match.loser)
        for player, rating in elo_rating.ratings.items():
            PlayerRating.objects.create(player=player, rating=rating)

