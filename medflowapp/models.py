from django.db import models
from django.utils import timezone

class Employee(models.Model):
    name = models.CharField(max_length=100)
    email=models.EmailField(max_length=50)
    roles_choices={
        "Administrator":"Administrator",
        "Staff":"Staff"
    }
    role=models.CharField(choices=roles_choices)
    employee_ID=models.PositiveIntegerField()
    password=models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now())

class Customers(models.Model):
    customer_name = models.CharField(max_length=100)
    customer_phone = models.IntegerField()
    customer_email = models.EmailField(max_length=100)
    customer_address = models.TextField()
    created_at = models.DateTimeField(default=timezone.now())

class Medicines(models.Model):
    medicine_name = models.CharField(max_length=50)
    expiry_date = models.DateField()
    category={
        '------':'-----',
        'TAB':'TAB',
        'SYR': 'SYRUP',
        'CAP':'CAP',
        'INJ': 'INJ'
    }
    status = {
        "Out-of-Stock": "Out-of-Stock",
        "In-stock":"In-stock",
    }
    med_category = models.CharField(choices=category, default="----")
    stock_status = models.CharField(choices=status, default='Overstock')
    price=models.DecimalField(max_digits=11, decimal_places=2)
    quantity = models.IntegerField()

class Suppliers(models.Model):
    supplier_name=models.CharField(max_length=50)
    supplier_contact = models.IntegerField()
    supplier_person = models.CharField()
    supplier_address=models.TextField()

class Purchases(models.Model):
    supplier_ID = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    medicine_ID = models.ForeignKey(Medicines, on_delete=models.CASCADE)
    quantity_received = models.IntegerField()
    cost_price=models.FloatField()
    purchase_date=models.DateTimeField(default=timezone.now())

class Sales(models.Model):
    invoice_number=models.CharField()
    employee_id = models.ForeignKey(Employee, on_delete=models.CASCADE)
    subtotal=models.DecimalField(max_digits=11, decimal_places=2)
    gst_amount = models.DecimalField(max_digits=11, decimal_places=2)
    total_amount=models.DecimalField(max_digits=11, decimal_places=2)
    sale_date = models.DateTimeField(default=timezone.now())

class SalesItems(models.Model):
    medicine_ID = models.ForeignKey(Medicines, on_delete=models.CASCADE)
    sale_ID = models.ForeignKey(Sales, on_delete=models.CASCADE)
    quantity_sold = models.IntegerField()
    unit_price=models.DecimalField(max_digits=11, decimal_places=2)
    total_price = models.DecimalField(max_digits=11, decimal_places=2)
