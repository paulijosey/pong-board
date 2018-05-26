from django.shortcuts import render


def home_page(request):
    """Render view for home page."""
    return render(request, 'home.html')
