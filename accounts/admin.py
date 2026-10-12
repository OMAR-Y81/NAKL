
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import (
    User,
    CustomerOrganization,
    CustomerMembership,
    BrokerOffice,
    BrokerMembership,
    BrokerLicense,
    BrokerVerification,
    BrokerDocument,
)


# --------------------------------------------------
# Users
# --------------------------------------------------

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        'username',
        'full_name',
        'email',
        'phone',
        'is_active',
        'is_staff',
        'date_joined',
    )

    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
        'date_joined',
    )

    search_fields = (
        'username',
        'full_name',
        'email',
        'phone',
    )

    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        (_('بيانات إضافية'), {
            'fields': (
                'full_name',
                'phone',
                'email_verified_at',
                'phone_verified_at',
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (_('بيانات المستخدم'), {
            'fields': ('email', 'full_name', 'phone')
        }),
    )


# --------------------------------------------------
# Customer Organizations
# --------------------------------------------------

@admin.register(CustomerOrganization)
class CustomerOrganizationAdmin(admin.ModelAdmin):

    list_display = (
        'legal_name',
        'commercial_registration',
        'organization_type',
        'city',
        'verification_status',
        'created_at',
    )

    list_filter = (
        'organization_type',
        'verification_status',
        'city',
    )

    search_fields = (
        'legal_name',
        'commercial_registration',
        'vat_number',
        'contact_email',
    )

    readonly_fields = ('created_at', 'updated_at')


# --------------------------------------------------
# Customer Memberships
# --------------------------------------------------

@admin.register(CustomerMembership)
class CustomerMembershipAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'organization',
        'role',
        'can_create_requests',
        'can_approve_quotes',
        'can_view_financials',
        'is_active',
    )

    list_filter = (
        'role',
        'is_active',
    )

    search_fields = (
        'user__username',
        'user__full_name',
        'organization__legal_name',
    )

    raw_id_fields = ('user', 'organization')

    readonly_fields = ('created_at',)


# --------------------------------------------------
# Customs Broker Offices
# --------------------------------------------------

@admin.register(BrokerOffice)
class BrokerOfficeAdmin(admin.ModelAdmin):

    list_display = (
        'trade_name',
        'legal_name',
        'commercial_registration',
        'city',
        'approval_status',
        'operational_status',
        'created_at',
    )

    list_filter = (
        'approval_status',
        'operational_status',
        'city',
    )

    search_fields = (
        'trade_name',
        'legal_name',
        'commercial_registration',
        'email',
        'phone',
    )

    prepopulated_fields = {'slug': ('trade_name',)}

    readonly_fields = ('created_at', 'updated_at')

    raw_id_fields = ('approved_by',)


# --------------------------------------------------
# Broker Employees and Memberships
# --------------------------------------------------

@admin.register(BrokerMembership)
class BrokerMembershipAdmin(admin.ModelAdmin):

    list_display = (
        'broker',
        'user',
        'role',
        'can_submit_quotes',
        'can_manage_orders',
        'can_manage_staff',
        'can_manage_billing',
        'is_active',
    )

    list_filter = (
        'role',
        'is_active',
    )

    search_fields = (
        'broker__trade_name',
        'user__username',
        'user__full_name',
    )

    raw_id_fields = ('broker', 'user')


# --------------------------------------------------
# Broker Licenses
# --------------------------------------------------

@admin.register(BrokerLicense)
class BrokerLicenseAdmin(admin.ModelAdmin):

    list_display = (
        'license_number',
        'broker',
        'license_holder_name',
        'license_category',
        'issue_date',
        'expiry_date',
        'verification_status',
    )

    list_filter = (
        'license_category',
        'verification_status',
        'expiry_date',
    )

    search_fields = (
        'license_number',
        'license_holder_name',
        'broker__trade_name',
    )

    raw_id_fields = ('broker',)

    date_hierarchy = 'created_at'


# --------------------------------------------------
# Broker Verification
# --------------------------------------------------

@admin.register(BrokerVerification)
class BrokerVerificationAdmin(admin.ModelAdmin):

    list_display = (
        'broker',
        'submitted_by',
        'status',
        'reviewer',
        'submitted_at',
        'reviewed_at',
    )

    list_filter = (
        'status',
        'submitted_at',
    )

    search_fields = (
        'broker__trade_name',
        'review_notes',
    )

    raw_id_fields = (
        'broker',
        'submitted_by',
        'reviewer',
    )

    readonly_fields = ('submitted_at',)


# --------------------------------------------------
# Broker Documents
# --------------------------------------------------

@admin.register(BrokerDocument)
class BrokerDocumentAdmin(admin.ModelAdmin):

    list_display = (
        'broker',
        'document_type',
        'issue_date',
        'expiry_date',
        'is_verified',
        'created_at',
    )

    list_filter = (
        'document_type',
        'is_verified',
    )

    search_fields = (
        'broker__trade_name',
        'broker__commercial_registration',
    )

    raw_id_fields = ('broker', 'uploaded_by')

    readonly_fields = ('created_at',)
