from django.db.models.signals import post_save
from djanog.dispatch import receiver
from .models import Purchase, SaleItem

@receiver(post_save, sender=Purchase)
def add_stock_on_purchase(sender, instance, created, **kwargs):
    if created:
        medicine = instance.medicine
        medicine.quantity += instance.quantity_received
        medicine.save()

@receiver(post_save, sender=SaleItem)
def subtract_stock_on_sale(sender, instance, created, **kwargs):
    if created:
        medicine = instance.medicine
        medicine.quantity -= instance.quantity_sold
        medicine.save()

