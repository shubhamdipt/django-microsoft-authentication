import random
import string

import msal
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

ms_settings = settings.MICROSOFT
graph_url = "https://graph.microsoft.com/v1.0"


def get_user(token):
    r = requests.get(
        url="{0}/me".format(graph_url),
        headers={"Authorization": "Bearer {0}".format(token)},
    )
    return r.json()


def load_cache(request):
    cache = msal.SerializableTokenCache()
    if request.session.get("token_cache"):
        cache.deserialize(request.session["token_cache"])
    return cache


def save_cache(request, cache):
    if cache.has_state_changed:
        request.session["token_cache"] = cache.serialize()


def get_msal_app(cache=None):
    # Initialize the MSAL confidential client
    auth_app = msal.ConfidentialClientApplication(
        ms_settings["app_id"],
        authority=ms_settings["authority"],
        client_credential=ms_settings["app_secret"],
        token_cache=cache,
    )
    return auth_app


def get_sign_in_flow():
    auth_app = get_msal_app()
    return auth_app.initiate_auth_code_flow(ms_settings["scopes"], redirect_uri=ms_settings["redirect"])


def get_token_from_code(request):
    cache = load_cache(request)
    auth_app = get_msal_app(cache)
    flow = request.session.pop("auth_flow", {})
    result = auth_app.acquire_token_by_auth_code_flow(flow, request.GET)
    save_cache(request, cache)
    return result


def get_token(request):
    cache = load_cache(request)
    auth_app = get_msal_app(cache)

    accounts = auth_app.get_accounts()
    if accounts:
        result = auth_app.acquire_token_silent(ms_settings["scopes"], account=accounts[0])
        save_cache(request, cache)
        return result["access_token"]


def remove_user_and_token(request):
    if "token_cache" in request.session:
        del request.session["token_cache"]

    if "user" in request.session:
        del request.session["user"]


def get_logout_url():
    return ms_settings["authority"] + "/oauth2/v2.0/logout" + "?post_logout_redirect_uri=" + ms_settings["logout_uri"]


# Non-microsoft related functions


def validate_email(email):
    return "@" in email and email.split("@")[1] in settings.MICROSOFT["valid_email_domains"]


def get_django_user(email, create_new=True):
    if not validate_email(email=email):
        return
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        if not create_new:
            return
        random_password = "".join(random.choice(string.ascii_letters) for i in range(32))
        user = User(username=email, email=email, password=make_password(random_password))
        user.is_staff = True
        user.save()
    return user
