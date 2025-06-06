from django.shortcuts import render

# Create your views here.

def index(request):
    """The home page for bjj app."""
    return render(request, 'bjj/index.html')