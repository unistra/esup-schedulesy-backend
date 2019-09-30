from rest_framework import permissions


class IsOwnerPermission(permissions.BasePermission):
    """Object-level permission to only allow owners of an object to edit it.
    """

    def __init__(self, username_field='username'):
        self.username_field = username_field

    def has_object_permission(self, request, view, obj):
        # TODO: timeit user.username vs getattr(user, 'username')
        return (
            request.user.is_superuser or
            obj.username == getattr(request.user, self.username_field)
        )

    # TODO: def has_permission(self, request, view) ?????
