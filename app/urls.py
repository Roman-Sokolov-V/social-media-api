from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from app.views import CreateUserView, LoginUserView, LogoutUserView

app_name = "app"

# router = DefaultRouter()
# router.register(r"airplane-type", AirplaneTypeViewSet)


urlpatterns = [
    path("register/", CreateUserView.as_view(), name="user-register"),
    path("login/", LoginUserView.as_view(), name="take-token"),
    path("logout/", LogoutUserView.as_view(), name="logout"),
]
