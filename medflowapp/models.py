from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class Employee(AbstractUser):
    roles_choices={
        "Administrator":"Administrator",
        "Staff":"Staff"
    }
    role=models.CharField(choices=roles_choices)
    created_at = models.DateTimeField(default=timezone.now)

class Customer(models.Model):
    phone_regex=RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Format: '+999999999'")
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

class Medicine(models.Model):
    medicine_name = models.CharField(max_length=50)
    expiry_date = models.DateField()
    category={
        '------':'-----',
        'TAB':'TAB',
        'SYR': 'SYRUP',
        'CAP':'CAP',
        'INJ': 'INJ'
    }
    med_category = models.CharField(choices=category, default="----")
    price=models.DecimalField(max_digits=11, decimal_places=2, default=0.00)
    quantity = models.PositiveIntegerField(default=0)
    @property
    def is_stock_available(self):
        return "In-stock" if self.quantity > 0 else "Out-of-stock"

    @property
    def is_expired(self):
        return self.expiry_date < timezone.now().date()

    def __str__(self):
        return self.medicine_name


class Supplier(models.Model):
    phone_regex=RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Format: '+999999999'")
    supplier_name=models.CharField(max_length=50)
    supplier_contact = models.CharField(validators=[phone_regex],max_length=17, unique=True)
    supplier_person = models.CharField()
    supplier_address=models.TextField()

class Purchase(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    batch_number=models.CharField(max_length=50)
    quantity_received = models.PositiveIntegerField(default=0)
    cost_price=models.DecimalField(max_digits=11, decimal_places=2)
    purchase_date=models.DateTimeField(default=timezone.now)

class Sale(models.Model):
    invoice_number=models.IntegerField()
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    subtotal=models.DecimalField(max_digits=11, decimal_places=2, default=0.00)
    gst_amount = models.DecimalField(max_digits=5,decimal_places=2, default=12.00)
    total_amount=models.DecimalField(max_digits=11, decimal_places=2, editable=False)
    created_at = models.DateTimeField(default = timezone.now)

    def save(self, *args, **kwargs):
        # Automatically calculate total based on subtotal and GST
        tax_multiplier = 1 + (self.gst_amount / 100)
        self.total_amount = self.subtotal * tax_multiplier
        super().save(*args, **kwargs)

class SaleItem(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    sale = models.ForeignKey(Sale, related_name="items", on_delete=models.PROTECT)
    quantity_sold = models.IntegerField(default=0)
    unit_price=models.DecimalField(max_digits=11, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity_sold
        super().save(*args, **kwargs)
