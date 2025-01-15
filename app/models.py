from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext as _

from PIL import Image as PILImage
import uuid
from pathlib import Path

from api_config.settings import AUTH_USER_MODEL


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""

        if not email:
            raise ValueError("The given email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model"""

    username = None
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()


def upload_picture(instance: "Profile", filename: str) -> Path:
    filename = (
        f"{slugify(instance.owner.email)}-{uuid.uuid4()}"
        + Path(filename).suffix
    )
    return Path("profile_pictures") / Path(filename)


class Profile(models.Model):
    """Profile model"""

    owner = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE)
    picture = models.ImageField(
        blank=True, null=True, upload_to=upload_picture
    )
    bio = models.TextField(blank=True, null=True)


class Follow(models.Model):
    """Model representing user follow relationships."""

    follower = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followee",
    )
    followee = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "followee"], name="unique_follow"
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F("followee")),
                name="follower_not_followee",
            ),
        ]

    @staticmethod
    def check_not_me(follower, followee, error):
        """Validate that a user cannot follow themselves."""
        if follower == followee:
            raise error("You cannot follow yourself.")

    def clean(self):
        """Validate Follow instance."""
        self.check_not_me(
            follower=self.follower,
            followee=self.followee,
            error=ValidationError,
        )


class Post(models.Model):
    """Post model"""

    author = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


def upload_image(instance: "Image", filename: str) -> Path:
    today = timezone.now().strftime("%Y/%m/%d")
    filename = (
        f"{slugify(instance.post)}-{uuid.uuid4()}" + Path(filename).suffix
    )
    return Path(today) / Path(filename)


class Image(models.Model):
    """Image model"""

    picture = models.ImageField(upload_to=upload_image)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="images"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = PILImage.open(self.picture.path)
        if img.height > 1080 or img.width > 1920:
            img.thumbnail((1080, 1920))
            img.save(self.picture.path)


class Feedback(models.Model):
    """Feedback model"""

    reviewer = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="feedbacks"
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="feedbacks"
    )
    comment = models.TextField(blank=True, null=True)
    likes = models.BooleanField(blank=True, null=True)

    @staticmethod
    def feedback_not_empty(comment, likes, error):
        if not comment and not likes:
            raise error(
                "Feedback cannot be empty. Leave comment or/and likes."
            )

    def clean(self):
        """Validate Feedback instance."""
        self.feedback_not_empty(
            comment=self.comment, likes=self.likes, error=ValidationError
        )
