from django.apps import apps
from django.contrib import auth
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.auth.models import AbstractUser
from mybank import apps


# Create your models here.

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument.'
                )
        elif not isinstance(backend, str):
            raise TypeError(
                'backend must be a dotted import path string (got %r).'
                % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, 'with_perm'):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=120)
    age = models.CharField(max_length=10)
    objects = CustomUserManager()


class Account(models.Model):
    account_number = models.CharField(max_length=30, unique=True)
    balance = models.FloatField()
    types = (
        ("savings", "savings"),
        ("current", "current"),
        ("credit", "credit")
    )
    ac_type = models.CharField(max_length=12, choices=types, default="savings")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = (
        ("active", "active"),
        ("inactive", "inactive")
    )
    active_status = models.CharField(max_length=12, choices=status, default="inactive")

    def __str__(self):
        return self.account_number


class Transactions(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    amount=models.IntegerField()
    to_accno=models.CharField(max_length=120)
    date=models.DateTimeField(auto_now=True)
    remarks=models.CharField(max_length=120)

    def __str__(self):
        return self.user