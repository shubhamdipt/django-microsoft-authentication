from django.http import HttpResponseForbidden
from django.contrib.auth.models import Group
from django.shortcuts import redirect


def is_member(user, group_names):
    return user.groups.filter(name__in=group_names).exists() if user else False


def microsoft_login_required(groups=None):
    """
    A user can only access page if
    the user belongs to the given group.
    """
    def _wrapper(view_func):
        def _view_wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("/microsoft_authentication/login")
            if groups:
                if is_member(
                    user=request.user,
                    group_names=groups
                ):
                    return view_func(request, *args, **kwargs)
                else:
                    return HttpResponseForbidden("Not authorized. Contact Admin")
            return view_func(request, *args, **kwargs)
        return _view_wrapper
    return _wrapper
