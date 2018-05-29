from django.shortcuts import render

from leaderboard.models import Match
from leaderboard.forms import MatchForm


def home_page(request):
    """Render view for home page."""
    recent_matches = Match.get_recent_matches(num_matches=20)
    return render(
        request,
        'home.html',
        {'recent_matches': recent_matches, 'form': MatchForm()}
    )
