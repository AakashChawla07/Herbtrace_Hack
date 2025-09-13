from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import User, APIKey, UserSession, PasswordResetToken

admin.site.site_title = "Herbtrace"
admin.site.site_header="Herbtrace Admin Panel"
@admin.register(User)
class UserAdmin(BaseUserAdmin, OSMGeoAdmin):
    list_display = ['username', 'email', 'user_type', 'is_verified', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_verified', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'organization']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('HerbTrace Profile', {
            'fields': ('user_type', 'phone_number', 'is_verified', 'verification_token',
                      'organization', 'license_number', 'address', 'location',
                      'language', 'timezone', 'last_active')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('HerbTrace Profile', {
            'fields': ('user_type', 'phone_number', 'organization', 'license_number')
        }),
    )

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_active', 'usage_count', 'last_used', 'created_at']
    list_filter = ['is_active', 'created_at', 'last_used']
    search_fields = ['name', 'user__username', 'user__email']
    readonly_fields = ['key', 'usage_count', 'last_used', 'created_at']

@admin.register(UserSession)
class UserSessionAdmin(OSMGeoAdmin):
    list_display = ['user', 'ip_address', 'is_active', 'login_time', 'last_activity']
    list_filter = ['is_active', 'login_time']
    search_fields = ['user__username', 'ip_address']
    readonly_fields = ['session_key', 'login_time', 'last_activity']

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'expires_at', 'used_at']
    list_filter = ['created_at', 'used_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['token', 'created_at']
