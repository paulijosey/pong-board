import leaderboard.models

DEFAULT_ELO_RATING = 1450
DEFAULT_K_FACTOR = 30


class EloRating(object):
    """Uses Elo rating system to rate players."""

    def __init__(self, use_current_ratings=False):
        self.ratings = {}
        if use_current_ratings:
            rated_players = leaderboard.models.PlayerRating.objects.all()
            for rated_player in rated_players:
                self.ratings[rated_player.player] = rated_player.rating
        
    def get_rating(self, player):
        """Return the rating of the specified player."""
        try:
            rating = self.ratings[player]
        except KeyError:  # ocurrs when no rating for that player is present
            rating = player.rating
        return rating
    
    def set_rating(self, player, rating):
        """Set the rating of the specified player."""
        self.ratings[player] = rating
    
    @staticmethod
    def calculate_expected_score(player_rating, opponent_rating):
        """Return the expected score given player ratings."""
        rating_differential = opponent_rating - player_rating
        expected_score = 1 / (1 + 10 ** (rating_differential / 400))
        return expected_score
    
    def get_expected_score(self, player, opponent):
        """Return the expected score for player against opponent."""
        player_rating = self.get_rating(player)
        opponent_rating = self.get_rating(opponent)
        return self.calculate_expected_score(player_rating, opponent_rating)

    def calculate_new_ratings(self, winner_rating, loser_rating, draw=False):
        """Return the new ratings given the prior ratings."""
        draw_var = 0.5 if draw else 0
        winner_expected_score = self.calculate_expected_score(winner_rating, loser_rating)
        loser_expected_score = self.calculate_expected_score(loser_rating, winner_rating)
        new_winner_rating = round(winner_rating + DEFAULT_K_FACTOR * (1 - draw_var - winner_expected_score))
        new_loser_rating  = round(loser_rating  + DEFAULT_K_FACTOR * (0 + draw_var - loser_expected_score))
        winner_rating_delta = new_winner_rating - winner_rating
        loser_rating_delta = new_loser_rating - loser_rating
        return new_winner_rating, new_loser_rating, winner_rating_delta, loser_rating_delta

    def update_ratings(self, winner, loser, draw=False):
        """Update the Elo ratings based on match outcome."""
        winner_rating = self.get_rating(winner)
        loser_rating = self.get_rating(loser)
        new_winner_rating, new_loser_rating, winner_rating_delta, loser_rating_delta = self.calculate_new_ratings(
            winner_rating,
            loser_rating,
            draw=draw
        )
        self.ratings[winner] = new_winner_rating
        self.ratings[loser] = new_loser_rating
        return new_winner_rating, new_loser_rating, winner_rating_delta, loser_rating_delta
    