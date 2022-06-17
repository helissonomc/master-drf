from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email


class CustomUserManager(BaseUserManager):
    """
    Custom user manager to deal with email as username.
    """

    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError(
                _('%(email)s is not a valid email address.'),
                params={'email': email},
            )

    def create_user(self, username, first_name, last_name, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not username:
            raise ValueError(_("Users must have a username"))

        if not first_name:
            raise ValueError(_("Users must have a first name"))

        if not last_name:
            raise ValueError(_("Users must have a last name"))

        if email:
            email =  self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError(_("Users must have an email address"))

        user = self.model(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            **extra_fields
        )

        user.set_password(password)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, first_name, last_name, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_("Superuser must have is_staff=True."))

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        if not password:
            raise ValueError(_("Superuser must have a password"))


        user = self.create_user(username, first_name, last_name, email, password, **extra_fields)
        user.save(using=self._db)

        return user