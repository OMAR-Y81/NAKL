
from django.contrib import admin

from .models import (
    ServiceCategory,
    Service,
    ServiceImage,
    CustomsPort,
    ServiceRequirement,
    BrokerService,
    BrokerCoverage,
    BrokerPricing,
)


# --------------------------------------------------
# Service Categories
# --------------------------------------------------

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'sort_order',
        'is_active',
        'created_at',
    )

    list_filter = ('is_active',)

    search_fields = ('name',)

    list_editable = (
        'sort_order',
        'is_active',
    )

    ordering = ('sort_order', 'name')


# --------------------------------------------------
# Customs Services
# --------------------------------------------------

class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1
    fields = ('image', 'caption', 'sort_order')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):

    inlines = (ServiceImageInline,)

    list_display = (
        'name',
        'code',
        'category',
        'is_active',
        'created_at',
    )

    list_filter = (
        'category',
        'is_active',
    )

    search_fields = (
        'name',
        'code',
        'description',
    )

    prepopulated_fields = {'code': ('name',)}

    list_editable = ('is_active',)

    raw_id_fields = ('category',)


# --------------------------------------------------
# Customs Ports
# --------------------------------------------------

@admin.register(CustomsPort)
class CustomsPortAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'code',
        'port_type',
        'city',
        'region',
        'is_active',
    )

    list_filter = (
        'port_type',
        'region',
        'is_active',
    )

    search_fields = (
        'name',
        'code',
        'city',
    )

    list_editable = ('is_active',)


# --------------------------------------------------
# Service Requirements
# --------------------------------------------------

@admin.register(ServiceRequirement)
class ServiceRequirementAdmin(admin.ModelAdmin):

    list_display = (
        'service',
        'document_type',
        'is_required',
        'sort_order',
    )

    list_filter = ('is_required',)

    search_fields = (
        'service__name',
        'document_type',
    )

    raw_id_fields = ('service',)

    list_editable = (
        'is_required',
        'sort_order',
    )


# --------------------------------------------------
# Broker Services
# --------------------------------------------------

@admin.register(BrokerService)
class BrokerServiceAdmin(admin.ModelAdmin):

    list_display = (
        'broker',
        'service',
        'is_available',
        'created_at',
    )

    list_filter = ('is_available',)

    search_fields = (
        'broker__trade_name',
        'service__name',
    )

    raw_id_fields = ('broker', 'service')

    list_editable = ('is_available',)


# --------------------------------------------------
# Broker Coverage
# --------------------------------------------------

@admin.register(BrokerCoverage)
class BrokerCoverageAdmin(admin.ModelAdmin):

    list_display = (
        'broker_service',
        'port',
        'is_available',
        'created_at',
    )

    list_filter = (
        'is_available',
        'port__port_type',
    )

    search_fields = (
        'broker_service__broker__trade_name',
        'broker_service__service__name',
        'port__name',
    )

    raw_id_fields = ('broker_service', 'port')

    list_editable = ('is_available',)


# --------------------------------------------------
# Broker Pricing
# --------------------------------------------------

@admin.register(BrokerPricing)
class BrokerPricingAdmin(admin.ModelAdmin):

    list_display = (
        'broker_service',
        'port',
        'pricing_type',
        'starting_price',
        'currency',
        'valid_from',
        'valid_until',
        'is_active',
    )

    list_filter = (
        'pricing_type',
        'currency',
        'is_active',
    )

    search_fields = (
        'broker_service__broker__trade_name',
        'broker_service__service__name',
        'port__name',
    )

    raw_id_fields = ('broker_service', 'port')

    list_editable = ('is_active',)

    date_hierarchy = 'valid_from'
