# accounts/views.py
from django.shortcuts import render

def not_cleared_view(request):
    return render(request, 'account/not_cleared.html')
