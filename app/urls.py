from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from app.views import (
    CreateUserView,
    LoginUserView,
    LogoutUserView,
    ProfileViewSet,
    # AddFollowView,
    FollowViewSet,
    FollowersViewSet,
    MyFollowingSet,
    MyFollowersSet,
    # UnfollowViewSet,
    PostViewSet,
    MyPostsSet,
    MyFollowingPostsSet,
    ImageViewSet,
)

app_name = "app"

router = DefaultRouter()
router.register(r"profile", ProfileViewSet)
# router.register(r"following", FollowViewSet)
# router.register(r"followers", FollowersViewSet, basename="followers")
router.register(r"following", MyFollowingSet, basename="following")
router.register(r"followers", MyFollowersSet, basename="followers")
router.register(r"post", PostViewSet, basename="post")
router.register(r"my-posts", MyPostsSet, basename="my-posts")
router.register(
    r"following-posts", MyFollowingPostsSet, basename="following-posts"
)
router.register(r"image", ImageViewSet, basename="image")


urlpatterns = [
    path("register/", CreateUserView.as_view(), name="user-register"),
    path("login/", LoginUserView.as_view(), name="take-token"),
    path("logout/", LogoutUserView.as_view(), name="logout"),
    path("", include(router.urls)),
    # path("follow/", AddFollowView.as_view(), name="add-follow"),
]
