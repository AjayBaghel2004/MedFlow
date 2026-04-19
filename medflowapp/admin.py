from django.contrib import admin
from .models import Employee, Medicines, Customers,  Suppliers, Purchases, Sales, SalesItems
# Register your models here.
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'email', 'role', 'employee_ID', 'password', 'created_at')
admin.site.register(Employee, EmployeeAdmin)

class CustomerAdmin(admin.ModelAdmin):
    list_display=('id', 'customer_name', 'customer_phone', 'customer_address', 'created_at')
admin.site.register(Customers, CustomerAdmin)

class MedicineAdmin(admin.ModelAdmin):
    list_display=('id','medicine_name', 'med_category', 'expiry_date', 'stock_status','price', 'quantity')
admin.site.register(Medicines, MedicineAdmin)

class SuppliersAdmin(admin.ModelAdmin):
    list_display =('id', 'supplier_name', 'supplier_contact', 'supplier_person', 'supplier_address')
admin.site.register(Suppliers, SuppliersAdmin)

class PurchasesAdmin(admin.ModelAdmin):
    list_display=('id', 'supplier_ID','medicine_ID', 'quantity_received', 'cost_price', 'purchase_date')
admin.site.register(Purchases, PurchasesAdmin)

class SalesAdmin(admin.ModelAdmin):
    list_display=('id', 'invoice_number', 'employee_id', 'subtotal', 'gst_amount', 'total_amount', 'sale_date')
admin.site.register(Sales, SalesAdmin)

class SalesItemsAdmin(admin.ModelAdmin):
    list_display = ('id','medicine_ID', 'sale_ID', 'quantity_sold', 'unit_price', 'total_price')
admin.site.register(SalesItems, SalesItemsAdmin)