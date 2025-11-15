from rest_framework import permissions

class IsTenantOwner(permissions.BasePermission):
    """Permission class for tenant owners"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_tenant_owner

class IsMasterAdmin(permissions.BasePermission):
    """Permission class for master admins"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_master_admin

class CanManageMembers(permissions.BasePermission):
    """Permission class for users who can manage members"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.can_create_members
