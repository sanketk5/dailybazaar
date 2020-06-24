from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'product'

urlpatterns = [
    #path('', views.product, name='one'),
    path('', views.product, name='home'),
    path('home/', views.product, name='home'),
    #path('one/', views.product, name='one'),
    path('about/', views.about, name='about'),
    path('checkout/', views.Checkoutview.as_view(), name='checkout'),
    path('payment/<payment_option>/', views.PaymentView.as_view(), name='payment'),
    path('request-refund/', views.RefundRequestView.as_view(), name='request-refund'),
    path('product/<slug>/', views.ProductDetailView.as_view(), name='product'),
    path('order-summary/', views.OrderSummaryView.as_view(), name='order-summary'),
    path('my-orders/', views.MyorderView.as_view(), name='my-orders'),
    path('add-to-cart/<slug>', views.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>',
         views.remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>', views.remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('add-item-to-cart/<slug>',
         views.add_single_item_to_cart, name='add-item-to-cart'),
]
