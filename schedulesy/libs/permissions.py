from functools import reduce

from rest_framework import permissions


class IsOwnerPermission(permissions.BasePermission):
    """Object-level permission to only allow owners of an object to edit it."""

    def __init__(self, username_field='username'):
        self.username_field = username_field

    def has_object_permission(self, request, view, obj):
        value = reduce(lambda a, b: getattr(a, b), self.username_field.split('__'), obj)
        return request.user.is_superuser or value == request.user.username
