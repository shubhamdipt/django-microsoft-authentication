from django.http import HttpResponse
from microsoft_authentication.auth.auth_decorators import microsoft_login_required


@microsoft_login_required()
def home(request):
    return HttpResponse("Logged in")


@microsoft_login_required(groups=("SpecificGroup1", "SpecificGroup2"))
def specific_group_access(request):
    return HttpResponse("You are accessing page which is accessible only to users belonging to SpecificGroup1 or SpecificGroup2")