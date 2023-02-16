# Django microsoft authentication

It is a very simple app which uses Microsoft authentication for user login and 
admin panel login. It uses the Microsoft authentication library for Python (msal).


## Installation

Standard pip install:

```bash
pip install django-microsoft-authentication
```


## Configuration

* First create an App in https://portal.azure.com/#home. There one needs to create set up for authentication. The details can be found here: 
  * https://docs.microsoft.com/en-us/azure/api-management/api-management-howto-protect-backend-with-aad
  * https://docs.microsoft.com/en-us/azure/app-service/configure-authentication-provider-microsoft
* Add the following microsoft app authentication configuration to settings.py file. (e.g. below, please replace redirect and logout_uri with correct domain)


```python
MICROSOFT = {
    "app_id": "YOUR_APP_ID_HERE",
    "app_secret": "YOUR_APP_SECRET_HERE",
    "redirect": "http://localhost:8000/microsoft_authentication/callback",
    "scopes": ["user.read"],
    "authority": "https://login.microsoftonline.com/common",  # or using tenant "https://login.microsoftonline.com/{tenant}",
    "valid_email_domains": ["<list_of_valid_domains>"],
    "logout_uri": "http://localhost:8000/admin/logout"
}
```


* Add the following line to settings.py to change the LOGIN_URL and LOGIN_REDIRECT_URL settings. 

```python
LOGIN_URL = "/microsoft_authentication/login"
LOGIN_REDIRECT_URL = "/admin"  # optional and can be changed to any other url


# True: creates new Django User after valid microsoft authentication. 
# False: it will only allow those users which are already created in Django User model and 
# will validate the email using Microsoft.
MICROSOFT_CREATE_NEW_DJANGO_USER = True  # Optional, default value is True
```


* Add 'microsoft_authentication' to INSTALLED_APPS
* Add the following to the project/urls.py

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Add the following line
    path('microsoft_authentication/', include('microsoft_authentication.urls'))
]
```

* In templates \
  Use "{% url 'microsoft_authentication:microsoft_authentication_login' %}" as login url \
  Use "{% url 'microsoft_authentication:microsoft_authentication_logout' %}" as logout url


## How it works?

1. It authenticates the user using their microsoft email and microsoft authentication.
2. It also verifies if the domain of the microsoft authenticated email is also in MICROSOFT["valid_email_domains"] 
3. After the first two steps of authentication, if the user is not found, it creates a new user but with no access to any apps in admin panel.
4. Superusers can assign User Groups to the users for Group based access to views.


## Quickstart

This app provides a decorator which can be used as follows:

```python
from django.http import HttpResponse
from microsoft_authentication.auth.auth_decorators import microsoft_login_required


@microsoft_login_required()
def home(request):
    return HttpResponse("Logged in")

# If pages need to be restricted to certain groups of users.
@microsoft_login_required(groups=("SpecificGroup1", "SpecificGroup2"))  # Add here the list of Group names
def specific_group_access(request):
    return HttpResponse("You are accessing page which is accessible only to users belonging to SpecificGroup1 or SpecificGroup2")

```

### Troubleshooting during development

* Use http://localhost:8000 instead of http://127.0.0.1:8000 because session cookies 
  are set differently for these urls.
