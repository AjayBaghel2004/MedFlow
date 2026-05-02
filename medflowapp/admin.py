from django.contrib import admin
from .models import Employee, Medicine, Customer, Supplier, Purchase, Sale, SaleItem
# Register your models here.
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'password', 'created_at')
admin.site.register(Employee, EmployeeAdmin)

class CustomerAdmin(admin.ModelAdmin):
    list_display=('id', 'customer_name', 'customer_phone', 'created_at')
admin.site.register(Customer, CustomerAdmin)

class MedicineAdmin(admin.ModelAdmin):
    list_display=('id','medicine_name', 'med_category', 'expiry_date','price', 'quantity')
admin.site.register(Medicine, MedicineAdmin)

class SuppliersAdmin(admin.ModelAdmin):
    list_display =('id', 'supplier_name', 'supplier_contact', 'supplier_person', 'supplier_address')
admin.site.register(Supplier, SuppliersAdmin)

class PurchasesAdmin(admin.ModelAdmin):
    list_display=('id', 'supplier','medicine', 'quantity_received', 'cost_price', 'purchase_date')
admin.site.register(Purchase, PurchasesAdmin)

class SalesAdmin(admin.ModelAdmin):
    list_display=('id', 'invoice_number', 'customer', 'employee', 'subtotal', 'gst_amount', 'total_amount', 'created_at')
admin.site.register(Sale, SalesAdmin)

class SalesItemsAdmin(admin.ModelAdmin):
    list_display = ('id','medicine', 'sale', 'quantity_sold', 'unit_price', 'total_price')
admin.site.register(SaleItem, SalesItemsAdmin)