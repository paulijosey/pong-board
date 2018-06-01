from django.shortcuts import render, redirect

from leaderboard.models import Match
from leaderboard.forms import MatchForm


def home_page(request):
    """Render view for home page."""
    recent_matches = Match.get_recent_matches(num_matches=20)
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = MatchForm()
    return render(
        request,
        'home.html',
        {'recent_matches': recent_matches, 'form': form}
    )
