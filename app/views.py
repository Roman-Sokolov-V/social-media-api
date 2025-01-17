from datetime import datetime

from django.shortcuts import render, get_object_or_404

from rest_framework import viewsets, generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from app.permissions import IsOwnerOrAuthenticatedReadOnly
from app.serializers import (
    UserSerializer,
    ProfileListSerializer,
    ProfileCreateSerializer,
    ProfileDetailSerializer,
    ProfileUpdateSerializer,
)
from app.models import Profile


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class LoginUserView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


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
        if self.action in ("list",):
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
