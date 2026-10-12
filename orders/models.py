
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


# --------------------------------------------------
# Common Choices
# --------------------------------------------------

class Currency(models.TextChoices):
    SAR = "SAR", "ريال سعودي"
    USD = "USD", "دولار أمريكي"
    EUR = "EUR", "يورو"


class VerificationStatus(models.TextChoices):
    PENDING = "pending", "بانتظار المراجعة"
    VERIFIED = "verified", "تم التحقق"
    REJECTED = "rejected", "مرفوض"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "بانتظار السداد"
    REPORTED = "reported", "تم الإبلاغ عن السداد"
    CONFIRMED = "confirmed", "تم تأكيد السداد"
    REJECTED = "rejected", "مرفوض"
    REFUNDED = "refunded", "مسترد"


# ==================================================
# A. Clearance Requests and Shipments
# ==================================================

class ClearanceRequest(models.Model):

    class Status(models.TextChoices):
        DRAFT = "draft", "مسودة"
        PUBLISHED = "published", "منشور للمكاتب"
        QUOTING = "quoting", "استقبال عروض الأسعار"
        AWARDED = "awarded", "تم اختيار مكتب"
        EXPIRED = "expired", "انتهت المنافسة"
        CANCELLED = "cancelled", "ملغي"

    request_number = models.CharField(
        max_length=40,
        unique=True
    )

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="clearance_requests"
    )

    organization = models.ForeignKey(
        "accounts.CustomerOrganization",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="clearance_requests"
    )

    service = models.ForeignKey(
        "catalog.Service",
        on_delete=models.PROTECT,
        related_name="clearance_requests"
    )

    port = models.ForeignKey(
        "catalog.CustomsPort",
        on_delete=models.PROTECT,
        related_name="clearance_requests"
    )

    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    bidding_deadline = models.DateTimeField(
        null=True,
        blank=True
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "طلب تخليص"
        verbose_name_plural = "طلبات التخليص"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["port", "service"]),
        ]

    def __str__(self):
        return self.request_number


class Shipment(models.Model):

    class TransportMode(models.TextChoices):
        SEA = "sea", "بحري"
        AIR = "air", "جوي"
        LAND = "land", "بري"

    request = models.ForeignKey(
        ClearanceRequest,
        on_delete=models.CASCADE,
        related_name="shipments"
    )

    shipment_number = models.CharField(
        max_length=100,
        blank=True
    )

    bill_of_lading_number = models.CharField(
        max_length=100,
        blank=True
    )

    transport_mode = models.CharField(
        max_length=10,
        choices=TransportMode.choices
    )

    origin_country = models.CharField(max_length=100)
    destination_country = models.CharField(max_length=100)

    estimated_arrival = models.DateField(
        null=True,
        blank=True
    )

    gross_weight = models.DecimalField(
        max_digits=14,
        decimal_places=3,
        null=True,
        blank=True
    )

    container_count = models.PositiveIntegerField(default=0)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "شحنة"
        verbose_name_plural = "الشحنات"

    def __str__(self):
        return self.shipment_number or f"Shipment #{self.pk}"


class ShipmentItem(models.Model):

    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name="items"
    )

    description = models.CharField(max_length=500)

    hs_code = models.CharField(
        max_length=20,
        blank=True
    )

    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=3
    )

    unit = models.CharField(max_length=50)

    declared_value = models.DecimalField(
        max_digits=16,
        decimal_places=2
    )

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.SAR
    )

    country_of_origin = models.CharField(max_length=100)

    class Meta:
        verbose_name = "صنف شحنة"
        verbose_name_plural = "أصناف الشحنات"
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name="shipment_item_positive_quantity"
            ),
            models.CheckConstraint(
                condition=Q(declared_value__gte=0),
                name="shipment_item_nonnegative_value"
            ),
        ]

    def __str__(self):
        return self.description


class RequestDocument(models.Model):

    class Visibility(models.TextChoices):
        CUSTOMER = "customer", "العميل والإدارة"
        INVITED = "invited", "المكاتب المدعوة والمخولون"
        AWARDED = "awarded", "المكتب الفائز والمخولون"

    request = models.ForeignKey(
        ClearanceRequest,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="documents"
    )

    document_type = models.CharField(max_length=150)

    file = models.FileField(
        upload_to="clearance/documents/"
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )

    visibility_level = models.CharField(
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.CUSTOMER
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.shipment_id and self.request_id:
            if self.shipment.request_id != self.request_id:
                raise ValidationError(
                    "يجب أن تتبع الشحنة الطلب المرتبط بالمستند."
                )

    class Meta:
        verbose_name = "مستند طلب"
        verbose_name_plural = "مستندات الطلبات"

    def __str__(self):
        return self.document_type


class DocumentReview(models.Model):

    document = models.ForeignKey(
        RequestDocument,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    review_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices
    )

    comments = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "مراجعة مستند"
        verbose_name_plural = "مراجعات المستندات"


# ==================================================
# B. Quotations and Competition
# ==================================================

class QuoteInvitation(models.Model):

    class Status(models.TextChoices):
        INVITED = "invited", "تمت الدعوة"
        VIEWED = "viewed", "تم الاطلاع"
        RESPONDED = "responded", "تم تقديم عرض"
        DECLINED = "declined", "اعتذر المكتب"
        EXPIRED = "expired", "منتهية"

    request = models.ForeignKey(
        ClearanceRequest,
        on_delete=models.PROTECT,
        related_name="invitations"
    )

    broker = models.ForeignKey(
        "accounts.BrokerOffice",
        on_delete=models.PROTECT,
        related_name="quote_invitations"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INVITED
    )

    invited_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "دعوة تقديم عرض"
        verbose_name_plural = "دعوات تقديم العروض"
        constraints = [
            models.UniqueConstraint(
                fields=["request", "broker"],
                name="unique_request_broker_invitation"
            )
        ]

    def __str__(self):
        return f"{self.request} - {self.broker}"


class BrokerQuote(models.Model):

    class Status(models.TextChoices):
        DRAFT = "draft", "مسودة"
        SUBMITTED = "submitted", "مقدم"
        REVISED = "revised", "معدل"
        ACCEPTED = "accepted", "مقبول"
        REJECTED = "rejected", "غير مختار"
        WITHDRAWN = "withdrawn", "مسحوب"
        EXPIRED = "expired", "منتهي"

    invitation = models.OneToOneField(
        QuoteInvitation,
        on_delete=models.PROTECT,
        related_name="quote"
    )

    request = models.ForeignKey(
        ClearanceRequest,
        on_delete=models.PROTECT,
        related_name="quotes"
    )

    broker = models.ForeignKey(
        "accounts.BrokerOffice",
        on_delete=models.PROTECT,
        related_name="quotes"
    )

    quote_number = models.CharField(
        max_length=40,
        unique=True
    )

    subtotal = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    tax_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.SAR
    )

    valid_until = models.DateTimeField()
    estimated_days = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    notes = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.invitation_id:
            if self.request_id != self.invitation.request_id:
                raise ValidationError("الطلب لا يطابق الدعوة.")
            if self.broker_id != self.invitation.broker_id:
                raise ValidationError("المكتب لا يطابق الدعوة.")

    class Meta:
        verbose_name = "عرض سعر"
        verbose_name_plural = "عروض الأسعار"
        constraints = [
            models.UniqueConstraint(
                fields=["request"],
                condition=Q(status="accepted"),
                name="one_accepted_quote_per_request"
            ),
            models.CheckConstraint(
                condition=Q(total_amount__gte=0),
                name="quote_nonnegative_total"
            ),
        ]

    def __str__(self):
        return self.quote_number


class QuoteItem(models.Model):

    class ItemType(models.TextChoices):
        BROKER_FEE = "broker_fee", "أتعاب المكتب"
        GOVERNMENT = "government", "رسوم حكومية تقديرية"
        THIRD_PARTY = "third_party", "تكاليف طرف ثالث"
        OTHER = "other", "أخرى"

    quote = models.ForeignKey(
        BrokerQuote,
        on_delete=models.CASCADE,
        related_name="items"
    )

    description = models.CharField(max_length=250)

    item_type = models.CharField(
        max_length=20,
        choices=ItemType.choices
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=1
    )

    unit_price = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    total_price = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    tax_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    class Meta:
        verbose_name = "بند عرض سعر"
        verbose_name_plural = "بنود عروض الأسعار"
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name="quote_item_positive_quantity"
            ),
            models.CheckConstraint(
                condition=Q(unit_price__gte=0),
                name="quote_item_nonnegative_unit_price"
            ),
        ]

    def __str__(self):
        return self.description


class QuoteRevision(models.Model):

    quote = models.ForeignKey(
        BrokerQuote,
        on_delete=models.PROTECT,
        related_name="revisions"
    )

    revision_number = models.PositiveIntegerField()

    revised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    reason = models.TextField(blank=True)
    snapshot = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "نسخة عرض سعر"
        verbose_name_plural = "نسخ عروض الأسعار"
        constraints = [
            models.UniqueConstraint(
                fields=["quote", "revision_number"],
                name="unique_quote_revision"
            )
        ]


# ==================================================
# C. Orders and Execution
# ==================================================

class Order(models.Model):

    class Status(models.TextChoices):
        ACCEPTED = "accepted", "تم قبول العرض"
        AUTHORIZATION = "authorization", "بانتظار التفويض"
        READY = "ready", "جاهز للتنفيذ"
        PROCESSING = "processing", "قيد التخليص"
        ON_HOLD = "on_hold", "معلق"
        COMPLETED = "completed", "مكتمل"
        CLOSED = "closed", "مغلق"
        CANCELLED = "cancelled", "ملغي"

    order_number = models.CharField(
        max_length=40,
        unique=True
    )

    request = models.OneToOneField(
        ClearanceRequest,
        on_delete=models.PROTECT,
        related_name="order"
    )

    accepted_quote = models.OneToOneField(
        BrokerQuote,
        on_delete=models.PROTECT,
        related_name="order"
    )

    broker = models.ForeignKey(
        "accounts.BrokerOffice",
        on_delete=models.PROTECT,
        related_name="orders"
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="customer_orders"
    )

    organization = models.ForeignKey(
        "accounts.CustomerOrganization",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACCEPTED
    )

    accepted_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.accepted_quote_id and self.request_id:
            if self.accepted_quote.request_id != self.request_id:
                raise ValidationError("العرض لا ينتمي إلى هذا الطلب.")
            if self.broker_id != self.accepted_quote.broker_id:
                raise ValidationError("المكتب لا يطابق العرض المقبول.")

        if self.request_id:
            if self.customer_id != self.request.requester_id:
                raise ValidationError("العميل لا يطابق مقدم الطلب.")
            if self.organization_id != self.request.organization_id:
                raise ValidationError("المنشأة لا تطابق منشأة الطلب.")

    class Meta:
        verbose_name = "أمر تنفيذ"
        verbose_name_plural = "أوامر التنفيذ"
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number


class OrderAssignment(models.Model):

    class Status(models.TextChoices):
        ASSIGNED = "assigned", "مسند"
        ACCEPTED = "accepted", "تم قبول التكليف"
        COMPLETED = "completed", "مكتمل"
        CANCELLED = "cancelled", "ملغي"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="assignments"
    )

    broker_membership = models.ForeignKey(
        "accounts.BrokerMembership",
        on_delete=models.PROTECT,
        related_name="order_assignments"
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assigned_orders"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ASSIGNED
    )

    assigned_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.order_id and self.broker_membership_id:
            if self.order.broker_id != self.broker_membership.broker_id:
                raise ValidationError(
                    "لا يمكن إسناد الطلب إلى موظف من مكتب آخر."
                )

    class Meta:
        verbose_name = "إسناد طلب"
        verbose_name_plural = "إسنادات الطلبات"


class OrderStatusHistory(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="status_history"
    )

    old_status = models.CharField(max_length=30, blank=True)
    new_status = models.CharField(max_length=30)

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    notes = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "سجل حالة طلب"
        verbose_name_plural = "سجل حالات الطلبات"
        ordering = ["-changed_at"]


class OrderMilestone(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "لم يبدأ"
        IN_PROGRESS = "in_progress", "قيد التنفيذ"
        COMPLETED = "completed", "مكتمل"
        BLOCKED = "blocked", "متعثر"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="milestones"
    )

    milestone_type = models.CharField(max_length=100)
    title = models.CharField(max_length=200)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    evidence_document = models.ForeignKey(
        RequestDocument,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "مرحلة تنفيذ"
        verbose_name_plural = "مراحل التنفيذ"


class CustomsAuthorization(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="authorizations"
    )

    broker_license = models.ForeignKey(
        "accounts.BrokerLicense",
        on_delete=models.PROTECT
    )

    authorization_reference = models.CharField(
        max_length=150
    )

    port = models.ForeignKey(
        "catalog.CustomsPort",
        on_delete=models.PROTECT
    )

    authorization_scope = models.CharField(max_length=250)

    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)

    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تفويض جمركي"
        verbose_name_plural = "التفويضات الجمركية"

    def clean(self):
        if self.order_id and self.broker_license_id:
            if self.broker_license.broker_id != self.order.broker_id:
                raise ValidationError(
                    "يجب أن تتبع الرخصة مكتب تنفيذ الطلب."
                )


class OrderChangeRequest(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "بانتظار الموافقة"
        APPROVED = "approved", "معتمد"
        REJECTED = "rejected", "مرفوض"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="change_requests"
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="requested_order_changes"
    )

    reason = models.TextField()

    financial_impact = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="approved_order_changes"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "طلب تغيير"
        verbose_name_plural = "طلبات التغيير"


# ==================================================
# D. Direct Payments and Commissions
# ==================================================

class PaymentRecord(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments"
    )

    broker = models.ForeignKey(
        "accounts.BrokerOffice",
        on_delete=models.PROTECT,
        related_name="customer_payments"
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.SAR
    )

    payment_method = models.CharField(max_length=100)
    reference_number = models.CharField(max_length=150, blank=True)

    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )

    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.order_id and self.broker_id:
            if self.order.broker_id != self.broker_id:
                raise ValidationError("المكتب لا يطابق أمر التنفيذ.")

    class Meta:
        verbose_name = "سداد عميل"
        verbose_name_plural = "مدفوعات العملاء"
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="customer_payment_positive"
            )
        ]


class PaymentProof(models.Model):

    payment = models.ForeignKey(
        PaymentRecord,
        on_delete=models.PROTECT,
        related_name="proofs"
    )

    file = models.FileField(
        upload_to="payments/proofs/"
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "إثبات سداد"
        verbose_name_plural = "إثباتات السداد"


class BrokerInvoice(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="broker_invoices"
    )

    broker = models.ForeignKey(
        "accounts.BrokerOffice",
        on_delete=models.PROTECT
    )

    invoice_number = models.CharField(max_length=100)

    issued_at = models.DateTimeField()

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    tax_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    currency = models.CharField(max_length=3, default="SAR")

    file = models.FileField(
        upload_to="invoices/brokers/",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "فاتورة مكتب للعميل"
        verbose_name_plural = "فواتير المكاتب للعملاء"
        constraints = [
            models.UniqueConstraint(
                fields=["broker", "invoice_number"],
                name="unique_broker_invoice_number"
            )
        ]


class CommissionRule(models.Model):

    class CommissionType(models.TextChoices):
        PERCENTAGE = "percentage", "نسبة مئوية"
        FIXED = "fixed", "مبلغ ثابت"

    broker = models.ForeignKey(
        "accounts.BrokerOffice",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="commission_rules"
    )

    service = models.ForeignKey(
        "catalog.Service",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    commission_type = models.CharField(
        max_length=20,
        choices=CommissionType.choices,
        default=CommissionType.PERCENTAGE
    )

    commission_value = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    effective_from = models.DateField()
    effective_until = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "قاعدة عمولة"
        verbose_name_plural = "قواعد العمولات"
        constraints = [
            models.CheckConstraint(
                condition=Q(commission_value__gte=0),
                name="commission_rule_nonnegative"
            ),
        ]


class Commission(models.Model):

    class Status(models.TextChoices):
        EXPECTED = "expected", "متوقعة"
        DUE = "due", "مستحقة"
        INVOICED = "invoiced", "مفوترة"
        PAID = "paid", "مدفوعة"
        REVERSED = "reversed", "معكوسة"

    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name="commission"
    )

    broker = models.ForeignKey(
        "accounts.BrokerOffice",
        on_delete=models.PROTECT,
        related_name="commissions"
    )

    rule = models.ForeignKey(
        CommissionRule,
        on_delete=models.PROTECT
    )

    base_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    rate = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    commission_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.EXPECTED
    )

    earned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "عمولة منصة"
        verbose_name_plural = "عمولات المنصة"
        constraints = [
            models.CheckConstraint(
                condition=Q(commission_amount__gte=0),
                name="commission_nonnegative"
            )
        ]


class CommissionInvoice(models.Model):

    class Status(models.TextChoices):
        DRAFT = "draft", "مسودة"
        ISSUED = "issued", "صادرة"
        PARTIAL = "partial", "مدفوعة جزئيًا"
        PAID = "paid", "مدفوعة"
        CANCELLED = "cancelled", "ملغاة"

    broker = models.ForeignKey(
        "accounts.BrokerOffice",
        on_delete=models.PROTECT,
        related_name="commission_invoices"
    )

    invoice_number = models.CharField(
        max_length=100,
        unique=True
    )

    period_start = models.DateField()
    period_end = models.DateField()

    subtotal = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    tax_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    total = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    issued_at = models.DateTimeField(null=True, blank=True)
    due_at = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "فاتورة عمولة"
        verbose_name_plural = "فواتير العمولات"


class CommissionInvoiceItem(models.Model):

    invoice = models.ForeignKey(
        CommissionInvoice,
        on_delete=models.PROTECT,
        related_name="items"
    )

    commission = models.OneToOneField(
        Commission,
        on_delete=models.PROTECT,
        related_name="invoice_item"
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    class Meta:
        verbose_name = "بند فاتورة عمولة"
        verbose_name_plural = "بنود فواتير العمولات"

    def clean(self):
        if self.invoice_id and self.commission_id:
            if self.invoice.broker_id != self.commission.broker_id:
                raise ValidationError(
                    "لا يمكن إضافة عمولة مكتب إلى فاتورة مكتب آخر."
                )


class CommissionPayment(models.Model):

    invoice = models.ForeignKey(
        CommissionInvoice,
        on_delete=models.PROTECT,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    payment_method = models.CharField(max_length=100)

    payment_reference = models.CharField(
        max_length=150,
        blank=True
    )

    paid_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "سداد عمولة"
        verbose_name_plural = "مدفوعات العمولات"
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="commission_payment_positive"
            )
        ]


# ==================================================
# E. Conversations and Notifications
# ==================================================

class Conversation(models.Model):

    request = models.ForeignKey(
        ClearanceRequest,
        on_delete=models.PROTECT,
        related_name="conversations"
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="conversations"
    )

    broker = models.ForeignKey(
        "accounts.BrokerOffice",
        on_delete=models.PROTECT,
        related_name="conversations"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "محادثة"
        verbose_name_plural = "المحادثات"
        constraints = [
            models.UniqueConstraint(
                fields=["request", "broker"],
                name="unique_request_broker_conversation"
            )
        ]

    def clean(self):
        if self.order_id:
            if self.order.request_id != self.request_id:
                raise ValidationError("المحادثة لا تطابق الطلب.")
            if self.order.broker_id != self.broker_id:
                raise ValidationError("المحادثة لا تطابق المكتب.")


class Message(models.Model):

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.PROTECT,
        related_name="messages"
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    body = models.TextField()
    is_internal = models.BooleanField(default=False)

    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "رسالة"
        verbose_name_plural = "الرسائل"
        ordering = ["sent_at"]


class MessageAttachment(models.Model):

    message = models.ForeignKey(
        Message,
        on_delete=models.PROTECT,
        related_name="attachments"
    )

    file = models.FileField(
        upload_to="messages/attachments/"
    )

    file_type = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "مرفق رسالة"
        verbose_name_plural = "مرفقات الرسائل"


class Notification(models.Model):

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    notification_type = models.CharField(max_length=100)
    title = models.CharField(max_length=250)
    body = models.TextField()

    related_object_type = models.CharField(
        max_length=100,
        blank=True
    )

    related_object_id = models.CharField(
        max_length=100,
        blank=True
    )

    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "إشعار"
        verbose_name_plural = "الإشعارات"
        ordering = ["-created_at"]


# ==================================================
# F. Reviews and Disputes
# ==================================================

class Review(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "قيد المراجعة"
        PUBLISHED = "published", "منشور"
        HIDDEN = "hidden", "مخفي"

    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name="review"
    )

    broker = models.ForeignKey(
        "accounts.BrokerOffice",
        on_delete=models.PROTECT,
        related_name="reviews"
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="submitted_reviews"
    )

    rating = models.PositiveSmallIntegerField()

    comment = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تقييم مكتب"
        verbose_name_plural = "تقييمات المكاتب"
        constraints = [
            models.CheckConstraint(
                condition=Q(rating__gte=1) & Q(rating__lte=5),
                name="review_rating_between_1_and_5"
            )
        ]

    def clean(self):
        if self.order_id:
            if self.broker_id != self.order.broker_id:
                raise ValidationError("المكتب لا يطابق الطلب.")
            if self.customer_id != self.order.customer_id:
                raise ValidationError("العميل لا يطابق الطلب.")


class Dispute(models.Model):

    class Status(models.TextChoices):
        OPEN = "open", "مفتوحة"
        INVESTIGATING = "investigating", "قيد الدراسة"
        RESOLVED = "resolved", "تم الحل"
        CLOSED = "closed", "مغلقة"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="disputes"
    )

    opened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="opened_disputes"
    )

    dispute_type = models.CharField(max_length=100)
    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_disputes"
    )

    resolution = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "نزاع"
        verbose_name_plural = "النزاعات"


class DisputeEvidence(models.Model):

    dispute = models.ForeignKey(
        Dispute,
        on_delete=models.PROTECT,
        related_name="evidence"
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    file = models.FileField(
        upload_to="disputes/evidence/"
    )

    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "مستند نزاع"
        verbose_name_plural = "مستندات النزاعات"


class DisputeHistory(models.Model):

    dispute = models.ForeignKey(
        Dispute,
        on_delete=models.PROTECT,
        related_name="history"
    )

    old_status = models.CharField(max_length=30, blank=True)
    new_status = models.CharField(max_length=30)

    action_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "سجل نزاع"
        verbose_name_plural = "سجل النزاعات"
        ordering = ["-created_at"]


# ==================================================
# G. Audit and System Events
# ==================================================

class AuditLog(models.Model):

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    action = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=100)

    previous_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "سجل تدقيق"
        verbose_name_plural = "سجلات التدقيق"
        ordering = ["-created_at"]


class SystemEvent(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "بانتظار المعالجة"
        PROCESSED = "processed", "تمت المعالجة"
        FAILED = "failed", "فشلت المعالجة"

    event_type = models.CharField(max_length=150)

    related_entity_type = models.CharField(
        max_length=100,
        blank=True
    )

    related_entity_id = models.CharField(
        max_length=100,
        blank=True
    )

    payload = models.JSONField(default=dict)

    processing_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "حدث نظام"
        verbose_name_plural = "أحداث النظام"
        ordering = ["created_at"]
