# invoices/forms_users.py
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Profile

User = get_user_model()


class AdminCreateUserForm(UserCreationForm):
    email = forms.EmailField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    profile_role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=True)
    profile_phone = forms.CharField(required=False)
    profile_address = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))
    profile_photo = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Bootstrap styling
        for name, field in self.fields.items():
            # selects vs inputs
            if name == "profile_role":
                field.widget.attrs.setdefault("class", "form-select")
            else:
                # file inputs, text, password, email...
                css = "form-control"
                if isinstance(field.widget, forms.Textarea):
                    css = "form-control"
                field.widget.attrs.setdefault("class", css)

        # small UX improvements
        self.fields["username"].widget.attrs.setdefault("placeholder", "username")
        self.fields["email"].widget.attrs.setdefault("placeholder", "email@example.com")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email", "")
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")

        if commit:
            user.save()

            profile, _ = Profile.objects.get_or_create(
                profile_user_id=user,
                defaults={"profile_role": self.cleaned_data["profile_role"]},
            )

            profile.profile_role = self.cleaned_data["profile_role"]
            profile.profile_phone = self.cleaned_data.get("profile_phone") or ""
            profile.profile_address = self.cleaned_data.get("profile_address") or ""
            if self.cleaned_data.get("profile_photo"):
                profile.profile_photo = self.cleaned_data["profile_photo"]
            profile.save()

            # Optional: let Admin role access staff-only pages
            if profile.profile_role == "Admin":
                user.is_staff = True
                user.save(update_fields=["is_staff"])

        return user
