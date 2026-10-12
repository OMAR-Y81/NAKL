
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from cloudinary.models import CloudinaryField


# ==================================================
# Service Category
# ==================================================

class ServiceCategory(models.Model):

    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="اسم التصنيف"
    )

    description = models.TextField(
        blank=True,
        verbose_name="الوصف"
    )

    sort_order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "تصنيف خدمة"
        verbose_name_plural = "تصنيفات الخدمات"

    def __str__(self):
        return self.name


# ==================================================
# Service
# ==================================================

class Service(models.Model):

    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.PROTECT,
        related_name="services"
    )

    name = models.CharField(max_length=200)

    code = models.SlugField(
        max_length=100,
        unique=True
    )

    description = models.TextField(blank=True)

    image = CloudinaryField(
        resource_type="image",
        folder="media/services/main",
        blank=True,
        verbose_name="الصورة الرئيسية",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "خدمة جمركية"
        verbose_name_plural = "الخدمات الجمركية"

    def __str__(self):
        return self.name


# ==================================================
# Service Images
# ==================================================

class ServiceImage(models.Model):

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="الخدمة",
    )

    image = CloudinaryField(
        resource_type="image",
        folder="media/services/gallery",
        verbose_name="الصورة",
    )

    caption = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="وصف الصورة",
    )

    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتيب العرض",
    )

    class Meta:
        ordering = ["sort_order", "pk"]
        verbose_name = "صورة خدمة"
        verbose_name_plural = "صور الخدمة"

    def __str__(self):
        return self.caption or f"صورة {self.service}"


# ==================================================
# Customs Port
# ==================================================

class CustomsPort(models.Model):

    class PortType(models.TextChoices):
        SEA = "sea", "بحري"
        AIR = "air", "جوي"
        LAND = "land", "بري"

    name = models.CharField(
        max_length=200,
        verbose_name="اسم المنفذ"
    )

    code = models.CharField(
        max_length=50,
        unique=True
    )

    port_type = models.CharField(
        max_length=10,
        choices=PortType.choices
    )

    city = models.CharField(max_length=100, blank=True)

    region = models.CharField(max_length=100, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "منفذ جمركي"
        verbose_name_plural = "المنافذ الجمركية"

    def __str__(self):
        return self.name


# ==================================================
# Service Requirement
# ==================================================

class ServiceRequirement(models.Model):

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="requirements"
    )

    document_type = models.CharField(
        max_length=150,
        verbose_name="نوع المستند"
    )

    description = models.TextField(blank=True)

    is_required = models.BooleanField(default=True)

    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "متطلب خدمة"
        verbose_name_plural = "متطلبات الخدمات"

    def __str__(self):
        return f"{self.service} - {self.document_type}"


# ==================================================
# Broker Service
# ==================================================

class BrokerService(models.Model):

    broker = models.ForeignKey(
        "accounts.BrokerOffice",
        on_delete=models.PROTECT,
        related_name="broker_services"
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name="broker_services"
    )

    description = models.TextField(blank=True)

    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "خدمة مكتب"
        verbose_name_plural = "خدمات المكاتب"
        constraints = [
            models.UniqueConstraint(
                fields=["broker", "service"],
                name="unique_broker_service"
            )
        ]

    def __str__(self):
        return f"{self.broker} - {self.service}"


# ==================================================
# Broker Coverage
# ==================================================

class BrokerCoverage(models.Model):

    broker_service = models.ForeignKey(
        BrokerService,
        on_delete=models.CASCADE,
        related_name="coverages"
    )

    port = models.ForeignKey(
        CustomsPort,
        on_delete=models.PROTECT,
        related_name="broker_coverages"
    )

    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تغطية منفذ"
        verbose_name_plural = "تغطية المنافذ"
        constraints = [
            models.UniqueConstraint(
                fields=["broker_service", "port"],
                name="unique_broker_port_coverage"
            )
        ]

    def __str__(self):
        return f"{self.broker_service} - {self.port}"


# ==================================================
# Broker Pricing
# ==================================================

class BrokerPricing(models.Model):

    class PricingType(models.TextChoices):
        FIXED = "fixed", "سعر ثابت"
        STARTING = "starting", "يبدأ من"
        QUOTATION = "quotation", "حسب عرض السعر"

    broker_service = models.ForeignKey(
        BrokerService,
        on_delete=models.CASCADE,
        related_name="prices"
    )

    port = models.ForeignKey(
        CustomsPort,
        on_delete=models.PROTECT,
        related_name="service_prices"
    )

    pricing_type = models.CharField(
        max_length=20,
        choices=PricingType.choices,
        default=PricingType.QUOTATION
    )

    starting_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))]
    )

    currency = models.CharField(
        max_length=3,
        default="SAR"
    )

    valid_from = models.DateField(
        null=True,
        blank=True
    )

    valid_until = models.DateField(
        null=True,
        blank=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تسعيرة مكتب"
        verbose_name_plural = "تسعيرات المكاتب"

    def __str__(self):
        return f"{self.broker_service} - {self.get_pricing_type_display()}"
