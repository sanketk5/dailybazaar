from django.contrib import admin
from .models import Products, Order, OrderProduct, Payment, Address, Refund
# Register your models here.


def make_refund_accepted(modeladmin, request, quesryset):
    quesryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = "Update orders to refund granted"


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_title', 'product_price',
                    'product_discount_price', 'delievery_charges')
    list_editable = ('product_price', 'product_discount_price',
                     'delievery_charges')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_product', 'start_date', 'ordered',
                    'payment')
    list_display_links = ('user', 'get_product', 'start_date')
    list_editable = ('ordered', )
    list_filter = ('ordered',)

    search_fields = ('user__username',)
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'room_no', 'wing_name', 'address_type', 'default',)
    list_filter = ('user', 'address_type', 'default',)
    search_fields = ['user', ]


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'timestamp',
                    'payment_option', 'payment_sender_name')


admin.site.site_header = "Daily Bazaar"
admin.site.register(Products, ProductAdmin)
admin.site.register(OrderProduct)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Refund)
