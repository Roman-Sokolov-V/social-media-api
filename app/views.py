from datetime import datetime

from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404

from rest_framework import viewsets, generics, mixins, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action

from app.permissions import IsOwnerOrAuthenticatedReadOnly
from app.serializers import (
    UserSerializer,
    AuthTokenSerializer,
    ProfileListSerializer,
    ProfileCreateSerializer,
    ProfileDetailSerializer,
    ProfileUpdateSerializer,
    FollowSerializer,
    FollowListSerializer,
    FollowersSerializer,
    MyFollowingSerializer,
    MyFollowersSerializer,
    # FollowDetailSerializer,
    # UnfollowingSerializer,
    AllPostsListSerializer,
    PostCreateSerializer,
    # MyPostsSerializer,
    MyFollowingPostsListSerializer,
    ImageCreateSerializer,
    CommentCreateSerializer,
    CommentListSerializer,
    LikePostSerializer,
)
from app.models import Profile, Follow, Post, Image


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class LoginUserView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


class LogoutUserView(APIView):
    """API for logging out the user by deleting their token."""

    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()  # Видалення токену користувача
        return Response({"detail": "Successfully logged out."})


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileCreateSerializer
    queryset = Profile.objects.all().select_related("user")
    permission_classes = (IsOwnerOrAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return ProfileListSerializer
        elif self.action == "retrieve":
            return ProfileDetailSerializer
        elif self.action in ("update", "partial_update"):
            return ProfileUpdateSerializer
        return self.serializer_class

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)
    #  what is beter this option or serializers.HiddenFielddefault=serializers.CurrentUserDefault(),

    def get_queryset(self):
        user_id = self.request.query_params.get("id")
        username = self.request.query_params.get("username")
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")
        joined = self.request.query_params.get("joined")

        queryset = self.queryset

        if user_id:
            try:
                user_id = int(user_id)
                return queryset.filter(user_id=user_id)
            except ValueError:
                queryset = queryset.none()
                # raise ValidationError("Invalid user ID format.")

        if username:
            queryset = queryset.filter(user__username__icontains=username)

        if first_name:
            queryset = queryset.filter(user__first_name__icontains=first_name)

        if last_name:
            queryset = queryset.filter(user__last_name__icontains=last_name)

        if joined:
            try:
                start, end = joined.split(",")
                start = datetime.strptime(start.strip(), "%Y-%m-%d")
                end = datetime.strptime(end.strip(), "%Y-%m-%d")
                return queryset.filter(user__date_joined__range=(start, end))
            except ValueError:
                queryset = queryset.none()
                # raise ValidationError(
                #     "Invalid date range format. Use 'YYYY-MM-DD,YYYY-MM-DD'."
                # )
        return queryset


class FollowViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return FollowListSerializer
        elif self.action == "retrieve":
            return FollowListSerializer
        return self.serializer_class

    def get_queryset(self):
        return self.queryset.filter(follower_id=self.request.user.id)


class FollowersViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Follow.objects.all()
    serializer_class = FollowersSerializer

    def get_queryset(self):
        return self.queryset.filter(followee_id=self.request.user.id)


class MyFollowingSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = MyFollowingSerializer
    queryset = get_user_model().objects.all()

    def get_queryset(self):
        return self.queryset.filter(id=self.request.user.id)


class MyFollowersSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = MyFollowersSerializer
    queryset = get_user_model().objects.all()

    def get_queryset(self):
        return self.queryset.filter(id=self.request.user.id)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().filter(is_published=True)
    serializer_class = AllPostsListSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return PostCreateSerializer
        elif self.action == "upload_image":
            return ImageCreateSerializer
        elif self.action == "comments":
            return CommentCreateSerializer
        elif self.action == "like":
            return LikePostSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset
        tags = self.request.query_params.get("tags")
        author = self.request.query_params.get("author")
        content = self.request.query_params.get("content")
        if tags:
            tags = tags.split(",")
            queryset = queryset.filter(hashtags__text__in=tags)
        if author:
            queryset = queryset.filter(author__username__icontains=author)
        if content:
            queryset = queryset.filter(content__icontains=content)

        return queryset.distinct()

    @action(detail=False, methods=["GET"])
    def my_posts(self, request, *args, **kwargs):
        posts = Post.objects.all().filter(author_id=self.request.user.id)
        serialiser = self.get_serializer(posts, many=True)
        return Response(serialiser.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def my_following(self, request, *args, **kwargs):
        posts = Post.objects.all().filter(
            author__in=self.request.user.following.all()
        )
        serialiser = self.get_serializer(posts, many=True)
        return Response(serialiser.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])  # в формі є можливість обрати
    # будьякий пост, не дивлячись на це використаний буде саме поточний
    # пост, хотілось би видалити можливість обирати пост
    def upload_image(self, request, *args, **kwargs):
        post = self.get_object()
        data = request.data
        data["post"] = post.id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post", "get"])  # чи варто робити два
    # методи в одному екшені, і взагалі чи не краще робити окремий ендпоінт?
    def comments(self, request, *args, **kwargs):
        post = self.get_object()
        # data = request.data.copy()
        # data["post"] = post.id
        # serializer = self.get_serializer(data=data)

        if request.method == "GET":
            comments = post.comments.all()
            serializer = CommentListSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == "POST":
            serializer = self.get_serializer(
                data=request.data,
                context={"request": request, "post": post},
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def like(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request, "post": post},  # як це працює
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False)
    def liked(self, request, *args, **kwargs):
        queryset = self.queryset.filter(
            likes__reviewer=self.request.user.id, likes__is_likes=True
        ).prefetch_related("likes__reviewer")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 76  203  216 249
