from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URLs to exclude from login enforcement
        excluded_paths = [
            reverse('loansapp:login'),  # Adjust this to your login URL name
            reverse('loansapp:register'),  # Adjust this to your register URL name
            # Add other URLs you want to exclude, such as password reset, etc.
        ]
        # Ensure that `user` is available before checking authentication status
        if not request.user.is_authenticated and request.path not in excluded_paths:
            # Redirect to the login page, using `reverse` to resolve the URL correctly
            login_url = reverse('loansapp:login')
            return redirect(f"{login_url}?next={request.path}")

        return self.get_response(request)