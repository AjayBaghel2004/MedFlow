from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=100)
    email=models.EmailField(max_length=50)
    # ADMIN='Admin'
    # STAFF='Staff'
    roles_choices={
        "Administrator":"Administrator",
        "Staff":"Staff"
    }
    role=models.CharField(choices=roles_choices)
    employee_ID=models.PositiveIntegerField()
    password=models.CharField(max_length=100)

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
    price=models.FloatField()
    quantity = models.IntegerField()
