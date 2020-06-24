from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from datetime import datetime
from django.db.models import Sum
# Create your models here.

CATEGORY_CHOICES = (
    ('BD', 'BREAD'),
    ('MK', 'MILK'),
    ('EG', 'EGG'),
)
LABEL_CHOICES = (
    ('NW', 'NEW'),
    ('BS', 'BEST-SELLER'),
)
ADDRESS_CHOICES = (
    ('S', 'SHIPPING'),
    ('B', 'BILLING'),
)


class Products(models.Model):
    product_no = models.CharField(max_length=15)
    product_title = models.CharField(max_length=30)
    product_brand = models.CharField(max_length=30, default='.')
    product_image1 = models.ImageField(upload_to='propics')
    product_discount_price = models.IntegerField(blank=True, null=True)
    product_price = models.IntegerField(default=0)
    product_description = models.TextField(max_length=150)
    product_offer = models.BooleanField(default=False)
    product_category = models.CharField(
        choices=CATEGORY_CHOICES, max_length=4, default='..')
    product_label = models.CharField(
        choices=LABEL_CHOICES, max_length=4, default='..')
    delievery_charges = models.IntegerField(blank=True, null=True)
    slug = models.SlugField(default='test-product')
    total_orders = models.IntegerField(default=0)

    def __str__(self):
        return self.product_title

    class Meta:
        verbose_name_plural = 'Products'

    def get_absolute_url(self):
        return reverse("products:product", kwargs={
            'slug': self.slug
        })

    def add_to_cart_url(self):
        return reverse("products:add-to-cart", kwargs={
            'slug': self.slug
        })

    def remove_from_cart_url(self):
        return reverse("products:remove-from-cart", kwargs={
            'slug': self.slug
        })


class OrderProduct(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    product_quantity = models.IntegerField(default=1)
    # This is for product_price * product quantity (khali)
    pro_price = models.IntegerField(default=1)
    # This is for product total delievery charges (khali)
    pro_delievery_charges = models.IntegerField(default=1)
    # This is for sum of pro_price and pro_delievery_charges (khali)
    pro_total_price = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.product.product_title} - {self.product_quantity}"

    def get_pro_price(self):
        return self.product_quantity * self.product.product_price

    def get_pro_discount_price(self):
        return self.product_quantity * self.product.product_discount_price

    def get_pro_total_price(self):
        return self.get_delievery_charges() + self.get_pro_price()    

    def get_delievery_charges(self):
        if self.product.product_category == 'EG':
            if self.product_quantity > 0 and self.product_quantity <= 10:
                return 5
            elif self.product_quantity > 10 and self.product_quantity <= 24:
                return 10

        if self.product.product_category == 'BD':
            if self.product_quantity > 0 and self.product_quantity <= 2:
                return 5
            elif self.product_quantity > 2 and self.product_quantity <= 5:
                return 10

        if self.product.product_category == 'MK':
            if self.product_quantity > 0 and self.product_quantity <= 4:
                return 5
            elif self.product_quantity > 4 and self.product_quantity <= 8:
                return 10

    def get_total_cart_price(self):
        return (self.product_quantity * self.product.product_price) + self.get_delievery_charges()

    def get_total_cart_discount_price(self):
        return self.product_quantity * self.product.product_discount_price + self.get_delievery_charges()

    def get_amount_saved(self):
        return self.get_total_cart_price() - self.get_total_cart_discount_price()

    def get_final_price(self):
        if self.product.product_discount_price:
            return self.get_total_cart_discount_price()
        return self.get_total_cart_price()

    def get_total_quantity(self):
        return self.product_quantity


class Order(models.Model):
    order_id = models.CharField(
        null=True, blank=True, max_length=15)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    products = models.ManyToManyField(OrderProduct)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    being_delieverd = models.BooleanField(default=False)
    recieved = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    delievery_address = models.ForeignKey(
        'Address', on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username

    def get_product(self):
        return ", ".join([str(p) for p in self.products.all()])

    def get_total(self):
        total = 0
        for order_product in self.products.all():
            total += order_product.get_final_price()
        return total

    def get_total_quantity(self):
        total = 0
        for order_product in self.products.all():
            total += order_product.get_total_quantity()
        return total

    def get_total_delievery_charges(self):
        total = 0
        for a in self.products.all():
            total += a.get_delievery_charges()
        return total


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)
    payment_option = models.CharField(blank=True, null=True, max_length=20)
    payment_sender_name = models.CharField(blank=True, max_length=50)

    def __str__(self):
        return self.payment_sender_name


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    room_no = models.CharField(max_length=10)
    wing_name = models.CharField(max_length=10)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Adresses'


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    email = models.EmailField()
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.pk}"
