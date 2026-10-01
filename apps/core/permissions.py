from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    message = "شما مالک این منبع نیستید."

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "owner_id", None) == request.user.id


class IsOwnerOrReadOnlyPublic(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return getattr(obj, "owner_id", None) == request.user.id
