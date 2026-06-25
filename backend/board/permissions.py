# board/permissions.py
from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    조회(GET)는 누구나 가능.
    수정(PUT/PATCH)·삭제(DELETE)는 작성자 본인만 가능.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author_id == request.user.id