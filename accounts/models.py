
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from cloudinary.models import CloudinaryField


# ==================================================
# Validators
# ==================================================

phone_validator = RegexValidator(
    regex=r"^\+?[0-9]{9,15}$",
    message="يرجى إدخال رقم جوال صحيح."
)


# ==================================================
# User
# ==================================================

class User(AbstractUser):

    full_name = models.CharField(
        max_length=200,
        verbose_name="الاسم الكامل"
    )

    email = models.EmailField(
        unique=True,
        verbose_name="البريد الإلكتروني"
    )

    phone = models.CharField(
        max_length=16,
        unique=True,
        null=True,
        blank=True,
        validators=[phone_validator],
        verbose_name="رقم الجوال"
    )

    email_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاريخ توثيق البريد"
    )

    phone_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاريخ توثيق الجوال"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمون"

    def __str__(self):
        return self.full_name or self.username


# ==================================================
# Customer Organization
# ==================================================

class CustomerOrganization(models.Model):

    class OrganizationType(models.TextChoices):
        COMPANY = "company", "شركة"
        ESTABLISHMENT = "establishment", "مؤسسة"

    class VerificationStatus(models.TextChoices):
        PENDING = "pending", "بانتظار التحقق"
        VERIFIED = "verified", "موثقة"
        REJECTED = "rejected", "مرفوضة"

    legal_name = models.CharField(
        max_length=255,
        verbose_name="الاسم النظامي"
    )

    organization_type = models.CharField(
        max_length=20,
        choices=OrganizationType.choices
    )

    commercial_registration = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="رقم السجل التجاري"
    )

    vat_number = models.CharField(
        max_length=30,
        blank=True
    )

    contact_email = models.EmailField(blank=True)

    contact_phone = models.CharField(
        max_length=16,
        blank=True,
        validators=[phone_validator]
    )

    city = models.CharField(max_length=100, blank=True)

    national_address = models.TextField(blank=True)

    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "منشأة عميل"
        verbose_name_plural = "منشآت العملاء"

    def __str__(self):
        return self.legal_name


# ==================================================
# Customer Membership
# ==================================================

class CustomerMembership(models.Model):

    class Role(models.TextChoices):
        OWNER = "owner", "مالك"
        MANAGER = "manager", "مدير"
        REQUESTER = "requester", "مقدم طلب"
        FINANCE = "finance", "مسؤول مالي"
        VIEWER = "viewer", "مشاهد"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="customer_memberships"
    )

    organization = models.ForeignKey(
        CustomerOrganization,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.REQUESTER
    )

    can_create_requests = models.BooleanField(default=True)
    can_approve_quotes = models.BooleanField(default=False)
    can_view_financials = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "عضوية منشأة"
        verbose_name_plural = "عضويات المنشآت"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization"],
                name="unique_customer_membership"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.organization}"


# ==================================================
# Broker Office
# ==================================================

class BrokerOffice(models.Model):

    class ApprovalStatus(models.TextChoices):
        PENDING = "pending", "بانتظار الاعتماد"
        UNDER_REVIEW = "under_review", "قيد المراجعة"
        APPROVED = "approved", "معتمد"
        REJECTED = "rejected", "مرفوض"

    class OperationalStatus(models.TextChoices):
        ACTIVE = "active", "نشط"
        SUSPENDED = "suspended", "موقوف"
        INACTIVE = "inactive", "غير نشط"

    legal_name = models.CharField(max_length=255)

    trade_name = models.CharField(max_length=255)

    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True
    )

    commercial_registration = models.CharField(
        max_length=30,
        unique=True
    )

    vat_number = models.CharField(
        max_length=30,
        blank=True
    )

    description = models.TextField(blank=True)

    logo = CloudinaryField(
        resource_type="image",
        folder="media/brokers/logos",
        null=True,
        blank=True
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=16,
        validators=[phone_validator]
    )

    city = models.CharField(max_length=100)

    national_address = models.TextField(blank=True)

    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING
    )

    operational_status = models.CharField(
        max_length=20,
        choices=OperationalStatus.choices,
        default=OperationalStatus.INACTIVE
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_brokers"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "مكتب تخليص"
        verbose_name_plural = "مكاتب التخليص"

    def __str__(self):
        return self.trade_name


# ==================================================
# Broker Membership
# ==================================================

class BrokerMembership(models.Model):

    class Role(models.TextChoices):
        OWNER = "owner", "مالك المكتب"
        MANAGER = "manager", "مدير المكتب"
        QUOTATIONS = "quotations", "مسؤول عروض الأسعار"
        OPERATIONS = "operations", "مسؤول العمليات"
        BROKER = "broker", "مخلص جمركي"
        FINANCE = "finance", "محاسب"

    broker = models.ForeignKey(
        BrokerOffice,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="broker_memberships"
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices
    )

    can_submit_quotes = models.BooleanField(default=False)
    can_manage_orders = models.BooleanField(default=False)
    can_manage_staff = models.BooleanField(default=False)
    can_manage_billing = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "عضو مكتب"
        verbose_name_plural = "أعضاء المكاتب"
        constraints = [
            models.UniqueConstraint(
                fields=["broker", "user"],
                name="unique_broker_membership"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.broker}"


# ==================================================
# Broker License
# ==================================================

class BrokerLicense(models.Model):

    class VerificationStatus(models.TextChoices):
        PENDING = "pending", "بانتظار التحقق"
        VERIFIED = "verified", "تم التحقق"
        REJECTED = "rejected", "مرفوض"

    broker = models.ForeignKey(
        BrokerOffice,
        on_delete=models.PROTECT,
        related_name="licenses"
    )

    license_number = models.CharField(max_length=100)

    license_holder_name = models.CharField(max_length=255)

    license_category = models.CharField(
        max_length=100,
        blank=True
    )

    license_type = models.CharField(
        max_length=100,
        blank=True
    )

    issue_date = models.DateField(
        null=True,
        blank=True
    )

    expiry_date = models.DateField(
        null=True,
        blank=True
    )

    license_document = models.FileField(
        upload_to="brokers/licenses/",
        null=True,
        blank=True
    )

    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "رخصة تخليص جمركي"
        verbose_name_plural = "رخص التخليص الجمركي"
        constraints = [
            models.UniqueConstraint(
                fields=["broker", "license_number"],
                name="unique_broker_license"
            )
        ]

    def __str__(self):
        return self.license_number


# ==================================================
# Broker Verification
# ==================================================

class BrokerVerification(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "بانتظار المراجعة"
        NEEDS_INFO = "needs_info", "يتطلب استكمال"
        APPROVED = "approved", "معتمد"
        REJECTED = "rejected", "مرفوض"

    broker = models.ForeignKey(
        BrokerOffice,
        on_delete=models.PROTECT,
        related_name="verifications"
    )

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="submitted_broker_verifications"
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_broker_verifications"
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    review_notes = models.TextField(blank=True)

    rejection_reason = models.TextField(blank=True)

    class Meta:
        verbose_name = "طلب اعتماد مكتب"
        verbose_name_plural = "طلبات اعتماد المكاتب"

    def __str__(self):
        return f"{self.broker} - {self.get_status_display()}"


# ==================================================
# Broker Document
# ==================================================

class BrokerDocument(models.Model):

    class DocumentType(models.TextChoices):
        COMMERCIAL_REGISTRATION = "commercial_reg", "السجل التجاري"
        CUSTOMS_LICENSE = "customs_license", "رخصة التخليص"
        VAT_CERTIFICATE = "vat_certificate", "الشهادة الضريبية"
        OTHER = "other", "مستند آخر"

    broker = models.ForeignKey(
        BrokerOffice,
        on_delete=models.PROTECT,
        related_name="documents"
    )

    document_type = models.CharField(
        max_length=30,
        choices=DocumentType.choices
    )

    file = models.FileField(
        upload_to="brokers/documents/"
    )

    issue_date = models.DateField(
        null=True,
        blank=True
    )

    expiry_date = models.DateField(
        null=True,
        blank=True
    )

    is_verified = models.BooleanField(default=False)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "مستند مكتب"
        verbose_name_plural = "مستندات المكاتب"

    def __str__(self):
        return f"{self.broker} - {self.get_document_type_display()}"
