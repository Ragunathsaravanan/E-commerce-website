from django.contrib import admin
from .models import Product
from .models import Order

admin.site.register(Product)    # register the database here to access the database in admin panel
admin.site.register(Order)