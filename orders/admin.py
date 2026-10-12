
from django.contrib import admin

from .models import (
    ClearanceRequest,
    Shipment,
    ShipmentItem,
    RequestDocument,
    DocumentReview,
    QuoteInvitation,
    BrokerQuote,
    QuoteItem,
    QuoteRevision,
    Order,
    OrderAssignment,
    OrderStatusHistory,
    OrderMilestone,
    CustomsAuthorization,
    OrderChangeRequest,
    PaymentRecord,
    PaymentProof,
    BrokerInvoice,
    CommissionRule,
    Commission,
    CommissionInvoice,
    CommissionInvoiceItem,
    CommissionPayment,
    Conversation,
    Message,
    MessageAttachment,
    Notification,
    Review,
    Dispute,
    DisputeEvidence,
    DisputeHistory,
    AuditLog,
    SystemEvent,
)


# --------------------------------------------------
# Clearance Requests
# --------------------------------------------------

@admin.register(ClearanceRequest)
class ClearanceRequestAdmin(admin.ModelAdmin):

    list_display = (
        'request_number',
        'title',
        'requester',
        'organization',
        'service',
        'port',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'service',
        'port',
        'created_at',
    )

    search_fields = (
        'request_number',
        'title',
        'requester__username',
        'organization__legal_name',
    )

    raw_id_fields = (
        'requester',
        'organization',
        'service',
        'port',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    ordering = ('-created_at',)
    date_hierarchy = 'created_at'


# --------------------------------------------------
# Shipments
# --------------------------------------------------

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'request',
        'shipment_number',
        'transport_mode',
        'origin_country',
        'destination_country',
        'estimated_arrival',
    )

    list_filter = (
        'transport_mode',
        'origin_country',
    )

    search_fields = (
        'shipment_number',
        'bill_of_lading_number',
        'request__request_number',
    )

    raw_id_fields = ('request',)


@admin.register(ShipmentItem)
class ShipmentItemAdmin(admin.ModelAdmin):

    list_display = (
        'shipment',
        'description',
        'hs_code',
        'quantity',
        'unit',
        'declared_value',
        'currency',
    )

    search_fields = (
        'description',
        'hs_code',
        'shipment__shipment_number',
    )

    raw_id_fields = ('shipment',)


# --------------------------------------------------
# Request Documents
# --------------------------------------------------

@admin.register(RequestDocument)
class RequestDocumentAdmin(admin.ModelAdmin):

    list_display = (
        'request',
        'document_type',
        'uploaded_by',
        'verification_status',
        'visibility_level',
        'created_at',
    )

    list_filter = (
        'verification_status',
        'visibility_level',
    )

    search_fields = (
        'request__request_number',
        'document_type',
    )

    raw_id_fields = (
        'request',
        'shipment',
        'uploaded_by',
    )

    readonly_fields = ('created_at',)


# --------------------------------------------------
# Quotation Invitations
# --------------------------------------------------

@admin.register(QuoteInvitation)
class QuoteInvitationAdmin(admin.ModelAdmin):

    list_display = (
        'request',
        'broker',
        'status',
        'invited_at',
        'expires_at',
    )

    list_filter = ('status',)

    search_fields = (
        'request__request_number',
        'broker__trade_name',
    )

    raw_id_fields = ('request', 'broker')


# --------------------------------------------------
# Broker Quotations
# --------------------------------------------------

@admin.register(BrokerQuote)
class BrokerQuoteAdmin(admin.ModelAdmin):

    list_display = (
        'quote_number',
        'request',
        'broker',
        'subtotal',
        'tax_amount',
        'total_amount',
        'currency',
        'status',
        'valid_until',
    )

    list_filter = (
        'status',
        'currency',
        'created_at',
    )

    search_fields = (
        'quote_number',
        'request__request_number',
        'broker__trade_name',
    )

    raw_id_fields = (
        'invitation',
        'request',
        'broker',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    ordering = ('-created_at',)


@admin.register(QuoteItem)
class QuoteItemAdmin(admin.ModelAdmin):

    list_display = (
        'quote',
        'description',
        'item_type',
        'quantity',
        'unit_price',
        'total_price',
        'tax_amount',
    )

    list_filter = ('item_type',)

    search_fields = (
        'description',
        'quote__quote_number',
    )

    raw_id_fields = ('quote',)


# --------------------------------------------------
# Orders
# --------------------------------------------------

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'order_number',
        'request',
        'broker',
        'customer',
        'status',
        'accepted_at',
        'completed_at',
    )

    list_filter = (
        'status',
        'accepted_at',
        'created_at',
    )

    search_fields = (
        'order_number',
        'request__request_number',
        'broker__trade_name',
        'customer__username',
    )

    raw_id_fields = (
        'request',
        'accepted_quote',
        'broker',
        'customer',
        'organization',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    ordering = ('-created_at',)


# --------------------------------------------------
# Order Assignments
# --------------------------------------------------

@admin.register(OrderAssignment)
class OrderAssignmentAdmin(admin.ModelAdmin):

    list_display = (
        'order',
        'broker_membership',
        'assigned_by',
        'status',
        'assigned_at',
    )

    list_filter = ('status',)

    search_fields = (
        'order__order_number',
        'broker_membership__user__username',
    )

    raw_id_fields = (
        'order',
        'broker_membership',
        'assigned_by',
    )


# --------------------------------------------------
# Customer Payments
# --------------------------------------------------

@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):

    list_display = (
        'order',
        'broker',
        'amount',
        'currency',
        'payment_method',
        'status',
        'paid_at',
    )

    list_filter = (
        'status',
        'currency',
        'payment_method',
    )

    search_fields = (
        'order__order_number',
        'broker__trade_name',
        'reference_number',
    )

    raw_id_fields = ('order', 'broker')

    readonly_fields = ('created_at',)


# --------------------------------------------------
# Broker Invoices
# --------------------------------------------------

@admin.register(BrokerInvoice)
class BrokerInvoiceAdmin(admin.ModelAdmin):

    list_display = (
        'invoice_number',
        'broker',
        'order',
        'amount',
        'tax_amount',
        'currency',
        'issued_at',
    )

    list_filter = (
        'currency',
        'issued_at',
    )

    search_fields = (
        'invoice_number',
        'broker__trade_name',
        'order__order_number',
    )

    raw_id_fields = ('order', 'broker')


# --------------------------------------------------
# Commission Rules
# --------------------------------------------------

@admin.register(CommissionRule)
class CommissionRuleAdmin(admin.ModelAdmin):

    list_display = (
        'broker',
        'service',
        'commission_type',
        'commission_value',
        'effective_from',
        'effective_until',
        'is_active',
    )

    list_filter = (
        'commission_type',
        'is_active',
    )

    raw_id_fields = ('broker', 'service')


# --------------------------------------------------
# Commissions
# --------------------------------------------------

@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):

    list_display = (
        'order',
        'broker',
        'base_amount',
        'rate',
        'commission_amount',
        'status',
        'earned_at',
    )

    list_filter = ('status',)

    search_fields = (
        'order__order_number',
        'broker__trade_name',
    )

    raw_id_fields = (
        'order',
        'broker',
        'rule',
    )

    readonly_fields = ('created_at',)


# --------------------------------------------------
# Commission Invoices
# --------------------------------------------------

@admin.register(CommissionInvoice)
class CommissionInvoiceAdmin(admin.ModelAdmin):

    list_display = (
        'invoice_number',
        'broker',
        'period_start',
        'period_end',
        'subtotal',
        'tax_amount',
        'total',
        'status',
    )

    list_filter = ('status',)

    search_fields = (
        'invoice_number',
        'broker__trade_name',
    )

    raw_id_fields = ('broker',)


# --------------------------------------------------
# Commission Payments
# --------------------------------------------------

@admin.register(CommissionPayment)
class CommissionPaymentAdmin(admin.ModelAdmin):

    list_display = (
        'invoice',
        'amount',
        'payment_method',
        'payment_reference',
        'paid_at',
    )

    search_fields = (
        'invoice__invoice_number',
        'payment_reference',
    )

    raw_id_fields = ('invoice',)


# --------------------------------------------------
# Conversations and Messages
# --------------------------------------------------

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'request',
        'broker',
        'order',
        'is_active',
        'created_at',
    )

    list_filter = ('is_active',)

    search_fields = (
        'request__request_number',
        'broker__trade_name',
    )

    raw_id_fields = (
        'request',
        'order',
        'broker',
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'conversation',
        'sender',
        'sent_at',
        'is_internal',
    )

    list_filter = ('is_internal',)

    search_fields = (
        'sender__username',
        'body',
    )

    raw_id_fields = (
        'conversation',
        'sender',
    )

    readonly_fields = ('sent_at',)


# --------------------------------------------------
# Notifications
# --------------------------------------------------

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        'recipient',
        'notification_type',
        'title',
        'created_at',
        'read_at',
    )

    list_filter = ('notification_type',)

    search_fields = (
        'recipient__username',
        'title',
        'body',
    )

    raw_id_fields = ('recipient',)

    readonly_fields = ('created_at',)


# --------------------------------------------------
# Reviews
# --------------------------------------------------

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        'order',
        'broker',
        'customer',
        'rating',
        'status',
        'created_at',
    )

    list_filter = (
        'rating',
        'status',
    )

    search_fields = (
        'order__order_number',
        'broker__trade_name',
    )

    raw_id_fields = (
        'order',
        'broker',
        'customer',
    )


# --------------------------------------------------
# Disputes
# --------------------------------------------------

@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'order',
        'dispute_type',
        'opened_by',
        'status',
        'assigned_to',
        'created_at',
    )

    list_filter = (
        'status',
        'dispute_type',
    )

    search_fields = (
        'order__order_number',
        'description',
    )

    raw_id_fields = (
        'order',
        'opened_by',
        'assigned_to',
    )


# --------------------------------------------------
# Additional Models
# Register all remaining supporting models
# --------------------------------------------------

additional_models = [
    DocumentReview,
    QuoteRevision,
    OrderStatusHistory,
    OrderMilestone,
    CustomsAuthorization,
    OrderChangeRequest,
    PaymentProof,
    CommissionInvoiceItem,
    MessageAttachment,
    DisputeEvidence,
    DisputeHistory,
    AuditLog,
    SystemEvent,
]

for model in additional_models:
    admin.site.register(model)
