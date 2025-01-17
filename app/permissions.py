from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrAuthenticatedReadOnly(BasePermission):
    """
    The request user is authenticated and he is object owner.,
     or request is authenticated as user is a read-only request.
    """

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS
            and request.user.is_authenticated
            or obj.user == request.user
        )
