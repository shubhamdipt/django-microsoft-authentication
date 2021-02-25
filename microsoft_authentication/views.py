from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth import login, logout
from django.conf import settings
from microsoft_authentication.auth.auth_utils import (
    get_sign_in_flow,
    get_token_from_code,
    get_user,
    get_django_user,
    get_logout_url,
)


def microsoft_login(request):
    flow = get_sign_in_flow()
    try:
        request.session['auth_flow'] = flow
    except Exception as e:
        print(e)
    return HttpResponseRedirect(flow['auth_uri'])


def microsoft_logout(request):
    logout(request)
    return HttpResponseRedirect(get_logout_url())


def callback(request):
    result = get_token_from_code(request)
    ms_user = get_user(result['access_token'])
    user = get_django_user(email=ms_user['mail'])
    if user:
        login(request, user)
    else:
        return HttpResponseForbidden("Invalid email for this app.")
    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL or "/admin")
