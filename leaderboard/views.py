from django.shortcuts import render, redirect

from leaderboard.models import Match
from leaderboard.forms import MatchForm, PlayerForm


def home_page(request):
    """Render view for home page."""
    recent_matches = Match.get_recent_matches(num_matches=20)
    match_form = MatchForm()
    player_form = PlayerForm()
    if request.method == 'POST':
        if 'winner' in request.POST:  # only occurs for match submissions
            match_form = MatchForm(request.POST)
            if match_form.is_valid():
                match_form.save()
                return redirect('/')
        elif 'first_name' in request.POST:  # only occurs for player submissions
            player_form = PlayerForm(request.POST)
            if player_form.is_valid():
                player_form.save()
                return redirect('/')
    return render(
        request,
        'home.html',
        context={
            'recent_matches': recent_matches,
            'match_form': match_form,
            'player_form': player_form
        }
    )
