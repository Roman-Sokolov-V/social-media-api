from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from app.models import *
from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.ModelSerializer):
    """User Serializer"""

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
            "is_staff",
        )
        read_only_fields = ("id", "is_staff")
        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {"input_type": "password"},
            }
        }

    def create(self, validated_data):
        """Create and return a new `User` instance, given the validated data."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return an `User` instance, given the validated data."""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("Email"), write_only=True)
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    token = serializers.CharField(label=_("Token"), read_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"),
                email=email,
                password=password,
            )

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class ProfileCreateSerializer(serializers.ModelSerializer):
    """Profile Serializer"""

    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
        # validators=[
        #     UniqueValidator(
        #         queryset=get_user_model().objects.all(),
        #         message="A user with that username already exists.",
        #     )
        # ],
        ###############чому не працює?
    )

    class Meta:
        model = Profile
        fields = ("user", "picture", "bio")
        read_only_fields = ("user",)  # is it need? Can we put another user
        # exept defoult wihout this option?

    def validate(self, data):
        user = data.get("user") or self.context["request"].user

        if Profile.objects.filter(user=user).exists():
            raise serializers.ValidationError(
                "A user with that username already exists."
            )
        return data


class ProfileListSerializer(serializers.ModelSerializer):
    """Profile Serializer"""

    user = serializers.StringRelatedField(many=False, read_only=True)
    picture = serializers.URLField(read_only=True)
    bio = serializers.CharField(read_only=True)

    class Meta:
        model = Profile
        fields = ("user", "picture", "bio")


class ProfileDetailSerializer(serializers.ModelSerializer):
    """Profile Serializer"""

    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(
        source="user.first_name", read_only=True
    )
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    picture = serializers.URLField(read_only=True)
    bio = serializers.CharField(read_only=True)
    joined = serializers.DateTimeField(
        source="user.date_joined", read_only=True
    )

    class Meta:
        model = Profile
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "picture",
            "bio",
            "joined",
        )


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Profile Update Serializer"""

    class Meta:
        model = Profile
        fields = ("picture", "bio")


class FollowSerializer(serializers.ModelSerializer):
    """Add Following Serializer"""

    follower = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Follow
        fields = ("id", "follower", "followee")


class FollowListSerializer(serializers.ModelSerializer):
    """Add Following List Serializer"""

    follower = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    followee = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Follow
        fields = ("id", "follower", "followee")


class FollowersSerializer(serializers.ModelSerializer):
    """Add Followers Serializer"""

    follower = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Follow
        fields = ("id", "follower")


class MyFollowingSerializer(serializers.ModelSerializer):
    following = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = ("following",)


class MyFollowersSerializer(serializers.ModelSerializer):
    followers = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = ("followers",)


class ImageSerializer(serializers.ModelSerializer):
    """Image Serializer"""

    class Meta:
        model = Image
        fields = ("picture", "post")


class AllPostsListSerializer(serializers.ModelSerializer):
    """Post Serializer"""

    author = serializers.SlugRelatedField(
        slug_field="username", read_only=True, many=False
    )
    images = ImageSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ("id", "author", "content", "images")


class PostCreateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    images = ImageSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ("id", "author", "content", "images")

    def create(self, validated_data):
        images_data = validated_data.pop("images", None)
        post = Post.objects.create(**validated_data)
        if images_data:
            for image_data in images_data:
                Image.objects.create(post=post, **image_data)
        return post


class MyPostsSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, required=False)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Post
        fields = ("id", "author", "content", "images")

    def create(self, validated_data):
        images_data = validated_data.pop("images", None)
        post = Post.objects.create(**validated_data)
        if images_data:
            for image_data in images_data:
                Image.objects.create(post=post, **image_data)
        return post


class MyFollowingPostsListSerializer(serializers.ModelSerializer):
    """Post Serializer"""

    author = serializers.SlugRelatedField(
        slug_field="username", read_only=True, many=False
    )
    images = ImageSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ("id", "author", "content", "images")
