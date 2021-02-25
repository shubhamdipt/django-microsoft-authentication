from django.urls import re_path, path
from microsoft_authentication.views import (
    microsoft_login,
    microsoft_logout,
    callback,
)

app_name = 'microsoft_authentication'
urlpatterns = [
    path('login', microsoft_login, name="microsoft_authentication_login"),
    path('logout', microsoft_logout, name="microsoft_authentication_logout"),
    path('callback', callback, name="microsoft_authentication_callback"),
]