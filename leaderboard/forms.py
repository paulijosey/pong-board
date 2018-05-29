from django import forms
from django.core.exceptions import ValidationError

from leaderboard.models import Match


class MatchForm(forms.ModelForm):
    """Form to submit a match result."""
    
    def __init__(self, *args, **kwargs):
        """Initialize form with initial winning score of 21."""
        super().__init__(*args, **kwargs)
        self.fields['winning_score'].initial = 21

    class Meta:
        model = Match
        fields = ['winner', 'winning_score', 'loser', 'losing_score']
        widgets = {
            'winning_score': forms.NumberInput(attrs={'min': 21}),
            'losing_score': forms.NumberInput(attrs={'min': 0}),
        }

    def clean(self):
        """Validate winning and losing scores."""
        cleaned_data = super().clean()
        winning_score = cleaned_data.get('winning_score')
        losing_score = cleaned_data.get('losing_score')
        if winning_score < 21:
            raise ValidationError('Winning score must be 21 or greater.')
        if losing_score < 0:
            raise ValidationError('Losing score must be 0 or greater.')
        if winning_score - losing_score < 2:
            raise ValidationError(
                'Losing score must be less than the winning score by at least 2 points.'
            )
        if winning_score > 21 and winning_score - losing_score != 2:
            raise ValidationError(
                'Deuce game! Winner must win by exactly 2 points when above 21.'
            )
