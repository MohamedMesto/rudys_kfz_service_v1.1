# invoices/forms_user_create.py
from django import forms
from django.contrib.auth import get_user_model

from .models import Profile

User = get_user_model()

class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Repeat password")
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, label="Role")

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = True
        if commit:
            user.save()
        return user
