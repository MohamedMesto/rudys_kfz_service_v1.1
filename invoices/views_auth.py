from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from .forms_auth import RegisterForm, LoginForm
from .models import Profile

def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # create Profile for the new user (default role)
            Profile.objects.get_or_create(profile_user_id=user, defaults={"profile_role": "User"})

            messages.success(request, _("Account created. You can now log in."))
            return redirect("auth:login")
    else:
        form = RegisterForm()

    return render(request, "auth/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, _("Welcome back!"))
            return redirect("home")
    else:
        form = LoginForm()

    return render(request, "auth/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, _("You have been logged out."))
    return redirect("auth:login")


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(
        profile_user_id=request.user,
        defaults={"profile_role": "User"},
    )
    return render(request, "auth/profile.html", {"profile": profile})
