from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Profile', {'fields': ('role', 'profile_picture', 'bio', 'phone_number', 'date_of_birth')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role & Profile', {'fields': ('role', 'email', 'first_name', 'last_name')}),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'academic_year', 'subject_specialization', 'institution')
    list_filter = ('academic_year', 'subject_specialization', 'institution')
    search_fields = ('user__username', 'user__email', 'institution')
