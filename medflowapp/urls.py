from django.urls import path
from . import views

urlpatterns = [
    path('', views.register, name = 'register'),
    path('register/', views.register_user, name='register-user'),
    path('login/', views.login, name = 'login'),
    path('login-user/', views.login_user),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('medicine/', views.medicine, name='medicine'),
    path('add-medicine/', views.add_medicine, name='add-medicine'),
    path('delete-medicine/', views.delete_medicine, name='delete-medicine'),
    path('updation_page/<int:medicineid>', views.update_medicine_page, name='updation-page'),
    path('update-medicine/', views.update_med_info, name='update_medicine'),
    path('point-of-sale/', views.pos_billing, name='Point-of-Sale'),
    path('inventory/', views.inventory, name='inventory'),
    path('purchases/', views.purchases, name='purchases'), 
    path('reports/', views.reports_section, name='reports'),
]