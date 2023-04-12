from django.conf import settings
from django.contrib.auth import login, logout
from django.http import HttpResponseForbidden, HttpResponseRedirect

from microsoft_authentication.auth.auth_utils import (
    get_django_user,
    get_logout_url,
    get_sign_in_flow,
    get_token_from_code,
    get_user,
)


def microsoft_login(request):
    request.session["next_url"] = request.GET.get("next")
    flow = get_sign_in_flow()
    try:
        request.session["auth_flow"] = flow
    except Exception as e:
        print(e)
    return HttpResponseRedirect(flow["auth_uri"])


def microsoft_logout(request):
    logout(request)
    return HttpResponseRedirect(get_logout_url())


def callback(request):
    result = get_token_from_code(request)
    next_url = request.session.pop("next_url", None)
    ms_user = get_user(result["access_token"])
    user = get_django_user(email=ms_user.get("mail") or ms_user.get("userPrincipalName"))
    if user:
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    else:
        return HttpResponseForbidden("Invalid email for this app.")
    if next_url:
        return HttpResponseRedirect(next_url)
    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL or "/admin")
