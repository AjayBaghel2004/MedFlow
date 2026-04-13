from django.contrib import admin
from .models import Employee, Medicines
# Register your models here.
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'email', 'role', 'employee_ID')
admin.site.register(Employee, EmployeeAdmin)

# admin.site.register(Customers)
class MedicineAdmin(admin.ModelAdmin):
    list_display=('id','medicine_name', 'med_category', 'expiry_date', 'stock_status','price', 'quantity')
admin.site.register(Medicines, MedicineAdmin)