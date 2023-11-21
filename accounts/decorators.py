# accounts/decorators.py
from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

def is_cleared(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_cleared:
            return function(request, *args, **kwargs)
        else:
            # Handle the response if the user is not cleared.
            # You can redirect to a different page or return an error response.
            # For example, return HttpResponseForbidden("You are not cleared to access this page.")
            # or redirect to a 'not cleared' page.
            return redirect('not_cleared_url')  # Replace 'not_cleared_url' with the name of your url
    return wrap
