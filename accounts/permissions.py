# accounts/permissions.py

from rest_framework import permissions


class IsOwnerSuperuser(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            return view.kwargs.get('pk', None) == str(request.user.id)
        
        return False

    def has_object_permission(self, request, view, obj):
        
        if request.user.is_superuser:
            return True

        return view.kwargs.get('pk', None) == str(request.user.id) == str(obj.id)


class IsOwnerUserOrSuperuser(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            return view.kwargs.get('user_pk', None) == str(request.user.id)
        
        return False

    def has_object_permission(self, request, view, obj):
        
        if request.user.is_superuser:
            return True

        return view.kwargs.get('user_pk', None) == str(request.user.id) == str(obj.user.id)