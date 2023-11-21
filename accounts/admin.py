from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

# accounts/admin.py
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username', 'is_cleared']  # Add 'is_cleared' here

    # Add 'is_cleared' to the fieldsets
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_cleared',)}),
    )

    # If you want 'is_cleared' to be editable when creating a user
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_cleared',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
