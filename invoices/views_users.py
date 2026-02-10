# # invoices/views_users.py

# invoices/views_users.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect

from .forms_users import AdminCreateUserForm


def is_admin_user(u):
    return u.is_authenticated and (u.is_superuser or u.is_staff)


@login_required
@user_passes_test(is_admin_user)
def user_create_view(request):
    if request.method == "POST":
        form = AdminCreateUserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"User '{user.username}' created.")
            return redirect("users:create")
    else:
        form = AdminCreateUserForm()

    return render(request, "users/user_create.html", {"form": form})

# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.contrib.auth import get_user_model
# from django.shortcuts import render, redirect
# from django.contrib import messages

# from .models import Profile
# from .forms_user_create import UserCreateForm

# User = get_user_model()

# def is_admin(user):
#     return user.is_authenticated and (user.is_superuser or user.is_staff)

# @login_required
# @user_passes_test(is_admin)
# def user_list(request):
#     users = User.objects.all().order_by("username")
#     return render(request, "users/user_list.html", {"users": users})

# @login_required
# @user_passes_test(is_admin)
# def user_create(request):
#     if request.method == "POST":
#         form = UserCreateForm(request.POST, request.FILES)
#         if form.is_valid():
#             user = form.save()  # creates user
#             role = form.cleaned_data["role"]
#             # profile already created by signal, but safe:
#             Profile.objects.update_or_create(
#                 profile_user_id=user,
#                 defaults={"profile_role": role}
#             )
#             messages.success(request, "User created successfully.")
#             return redirect("users:list")
#     else:
#         form = UserCreateForm()

#     return render(request, "users/user_form.html", {"form": form})
