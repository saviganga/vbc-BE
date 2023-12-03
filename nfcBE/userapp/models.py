from django.db import models

# Create your models here.
from datetime import datetime
from email.policy import default
from pickle import TRUE
from pyexpat import model
from socket import send_fds

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import jwt
from userapp.managers import MyUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings

from decimal import Decimal

import time
from django.utils import timezone

# from user import enums as user_enums

import uuid


# Create your models here.


class CustomUser(AbstractBaseUser, PermissionsMixin):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_name = models.CharField(
        _("username"),
        max_length=254,
        help_text=_("The prefereed username"),
        unique=True,
        null=False,
        blank=False
    )
    username = None
    email = models.EmailField(_("email address"), max_length=254, unique=True)
    first_name = models.CharField(
        _("first name"),
        max_length=254,
        help_text=_("The first name as it appears on ID or passport"),
    )
    last_name = models.CharField(
        _("last name"),
        max_length=254,
        help_text=_("The first name as it appears on ID or passport"),
    )
    is_business = models.BooleanField(default=False)
    is_business_member = models.BooleanField(default=False)
    # businesses = models.JSONField(default=list)

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."),
    )

    is_verified = models.BooleanField(
        _("user verified"),
        default=False,
        help_text=_("Designates whether the user is a verified user"),
    )

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as "
            "active. Unselect this instead of deleting accounts."
        ),
    )
    
    # picture = models.ImageField(
    #     blank=True, null=True, upload_to=file_services.renameProfilePicture, help_text=_("User picture")
    # )

    updated_on = models.DateTimeField(_("updated on"), auto_now=True)
    added_on = models.DateTimeField(_("date joined"), default=timezone.now)
    is_blocked = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "user_name"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-added_on"]

    def __unicode__(self):
        return f"{self.user_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        first_name = self.first_name.strip()
        last_name = self.last_name.strip()
        full_name = f"{first_name} {last_name}"
        return full_name

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True


# class AppPermissions(models.Model):

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=100, null=False, blank=False)
#     slug = models.CharField(max_length=100, null=False, blank=False)
#     description = models.TextField(null=False, blank=False)
#     added_on = models.DateTimeField(auto_now_add=True)
#     updated_on = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ["-added_on"]

# class PermissionRoles(models.Model):

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     role = models.CharField(max_length=100, null=False, blank=False)
#     permissions = models.ForeignKey(AppPermissions, on_delete=models.CASCADE, related_name='role_map')

# class PermissionRolesMap(models.Model):
    