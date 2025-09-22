from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Welcome/Home page view."""
    template_name = 'home.html'


# Function-based view alternative
def home_view(request):
    """Welcome/Home page view."""
    return render(request, 'home.html')
