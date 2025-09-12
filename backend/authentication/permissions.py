from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user.user_type == 'ADMIN':
            return True
        
        # Check if object has a user field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if object is the user itself
        if hasattr(obj, 'username'):
            return obj == request.user
        
        return False

class IsCollectorOrAdmin(permissions.BasePermission):
    """
    Permission for collector-specific actions
    """
    
    def has_permission(self, request, view):
        return request.user.user_type in ['COLLECTOR', 'ADMIN']

class IsProcessorOrAdmin(permissions.BasePermission):
    """
    Permission for processor-specific actions
    """
    
    def has_permission(self, request, view):
        return request.user.user_type in ['PROCESSOR', 'ADMIN']

class IsQualityInspectorOrAdmin(permissions.BasePermission):
    """
    Permission for quality inspector actions
    """
    
    def has_permission(self, request, view):
        return request.user.user_type in ['QUALITY_INSPECTOR', 'ADMIN']

class IsVerifiedUser(permissions.BasePermission):
    """
    Permission for verified users only
    """
    
    def has_permission(self, request, view):
        return request.user.is_verified

class CanCreateBatch(permissions.BasePermission):
    """
    Permission to create batches - only collectors and admins
    """
    
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.user_type in ['COLLECTOR', 'ADMIN'] and request.user.is_verified
        return True

class CanProcessBatch(permissions.BasePermission):
    """
    Permission to add processing events - processors and admins
    """
    
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.user_type in ['PROCESSOR', 'ADMIN'] and request.user.is_verified
        return True

class CanQualityTest(permissions.BasePermission):
    """
    Permission to add quality tests - quality inspectors and admins
    """
    
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.user_type in ['QUALITY_INSPECTOR', 'ADMIN'] and request.user.is_verified
        return True
