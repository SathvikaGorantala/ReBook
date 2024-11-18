from django.contrib import admin
from .models import Description, Category, Wishlist, Review, Transaction
# Register your models here.
admin.site.register(Description)

admin.site.register(Category)
admin.site.register(Wishlist)
admin.site.register(Review)
admin.site.register(Transaction)