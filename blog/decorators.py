from functools import wraps
from django.http import HttpResponseForbidden


# Dekorator sprawdzający uprawnienia superusera
def superuser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('home')

    return _wrapped_view
