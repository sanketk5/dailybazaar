from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import FormView
from .models import Products, Order, OrderProduct
from django.views.generic import ListView, DetailView, View
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from datetime import datetime
from django.utils import timezone
from .forms import CheckoutForm, PaymentForm, RefundForm
from .models import Products, Order, OrderProduct, Address, Payment, Refund
from itertools import zip_longest


# Create your views here.

def home(request):
    pro = Products.objects.all()
    return render(request, 'base.html', {'pro': pro})


def product(request):
    products = Products.objects.all()
    return render(request, "product.html", {'products': products})

def about(request):
    return render(request, "about.html")


i = 00


def get_id(self):
    global i
    i += 1
    now = datetime.now()
    date = now.strftime("%d%m%Y")
    a = "OD" + date + str(i)
    return a


class ProductDetailView(DetailView):
    model = Products
    template_name = "plp.html"

    # form_class = ProductForm
    # return render("plp.html", {'form':form})
a=list()
class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(
                user=self.request.user, ordered=False)            
            context = {
                'object': order
            }
            print(order)
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "Your cart is empty.")
            return redirect("/")


class Checkoutview(View):
    def get(self, *args, **kwargs):
        # form
        form = CheckoutForm()
        order = Order.objects.get(user=self.request.user, ordered=False)
        # payment = Payment.objects.get(user = self.request.user)
        context = {
            'form': form,
            'order': order
        }
        # delievery_address_qs = Address.objects.filter(user = request.user, )
        return render(self.request, "checkout.html", context)

    def post(self, *args, **kwargs):
        # form
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            # payment = Payment.objects.get(user = self.request.user)
            if form.is_valid():
                room_no = form.cleaned_data.get('room_no')
                wing_name = form.cleaned_data.get('wing_name')
                # TODO : add functionality to these option
                save_info = form.cleaned_data.get('save-info')
                payment_option = form.cleaned_data.get('payment_option')
                print(form.cleaned_data)
                delievery_address = Address(
                    user=self.request.user,
                    room_no=room_no,
                    wing_name=wing_name,
                    # default = save_info,
                    address_type='B',
                )
                delievery_address.save()
                order.delievery_address = delievery_address
                # order.payment.payment_option = payment_option
                order.save()
                # TODO : add redirect to the selected payment options
                if payment_option == 'UPI':
                    return redirect('products:payment', payment_option='UPI')
                elif payment_option == 'COD':
                    return redirect('products:payment', payment_option='Cash on delievery')
                else:
                    messages.warning(
                        self.request, "Invalid payment option is selected.")
                    return redirect("products:checkout")
            else:
                messages.warning(
                    self.request, "Invalid option is selected.")
                return redirect("products:checkout")

        except ObjectDoesNotExist:
            messages.warning(self.request, "Your cart is empty.")
            return redirect("products:order-summary")


c = list()

class MyorderView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.filter(
                user_id=self.request.user.id, ordered=True, recieved=False)
            print(len(order))
            for i in range(0, len(order), 1):
                global c
                b = order[i]
                c += b.products.all()
            mylist = zip_longest(list(set(c)), order)
            context = {
                'mylist': mylist,  # LIst of c and order                
            }
            print(f'Diff : {list(set(c))}')
            return render(self.request, 'my_ord1.html', context)
        except len(order)==0:
            messages.warning(self.request, "Your cart is empty.")
            return redirect("/")


class PaymentView(View):
    def get(self, *args, **kwargs):
        # Form
        form = PaymentForm()
        # Order
        order = Order.objects.get(user=self.request.user, ordered=False)
        pro = Products.objects.all()
        context = {
            'form': form,
            'order': order,
            'pro': pro
        }
        return render(self.request, 'payment.html', context)

    def post(self, *args, **kwargs):
        # Form
        form = PaymentForm(self.request.POST)
        # payment = Payment()
        # Order
        order = Order.objects.get(user=self.request.user, ordered=False)
        # pro = Products.objects.all()
        try:
            if form.is_valid():
                payment_sender_name = form.cleaned_data.get(
                    'payment_sender_name')
                chv = Checkoutview()
                # payment_option = Checkoutview.post.pmnt(self)
                print(f"Payment Sender Name :- {payment_sender_name}")
                payment = Payment(
                    user=self.request.user,
                    amount=order.get_total(),
                    # payment_option=payment_option,
                    payment_sender_name=payment_sender_name
                )
                # Create payment here.
                payment.save()
                # Assign the payment to the order.
                order.payment = payment

                order.order_id = get_id(self)
                # pro.total_orders += order.products.product_quantity
                # order.i += 1
                order_products = order.products.all()
                order_products.update(ordered=True)

                order.ordered = True
                order.save()
                messages.info(self.request, "Order is placed.")
                return redirect("products:home")
            else:
                messages.warning(self.request, "Form is not filled properly.")
                return redirect("/")

        except ObjectDoesNotExist:
            messages.warning(self.request, "Invalid Credentials.")
            return redirect("products:checkout")


class RefundRequestView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            order_id = form.cleaned_data.get('order_id')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # Edit the order
            try:
                order = Order.objects.get(order_id=order_id)
                order.refund_requested = True
                order.save()
                # Store the refund
                # refund = Refund()
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()
                messages.info(self.request, "This request was recieved.")
                return redirect("products:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order is not exist.")
                return redirect("products:request-refund")


@csrf_protect
def add_to_cart(request, slug):
    if request.user.is_authenticated:
        product = get_object_or_404(Products, slug=slug)
        print(request.method)
        pro_quantity = int(request.POST.get('qnt', False))
        # pro_quantity = request.POST['qnt']
        print(pro_quantity)
        order_product, created = OrderProduct.objects.get_or_create(
            product=product,
            user=request.user,
            ordered=False,
            product_quantity=pro_quantity
        )
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # Check if the order item is in the order
            if order.products.filter(product__slug=product.slug).exists():
                order_product.product_quantity += pro_quantity
                order_product.save()
                messages.info(request, "The product quantity is updated.")
            else:
                order.products.add(order_product)
                messages.info(
                    request, "This product is added to your cart succesfully.")

        else:
            ordered_date = timezone.now()
            product_quantity = pro_quantity
            order = Order.objects.create(
                user=request.user, ordered_date=ordered_date)
            order.products.add(order_product)
            messages.info(
                request, "This product is added to your cart succesfully.")
        # "products:product" is saying products is the name of main url of app
        # product is the name of url who is calling the function (add_to_cart)
        return redirect("products:product", slug=slug)
    else:
        messages.info(
            request, "Login first.")
        return redirect("products:home")


@login_required
def remove_from_cart(request, slug):
    product = get_object_or_404(Products, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # Check if the order item is in the order
        if order.products.filter(product__slug=product.slug).exists():
            order_product = OrderProduct.objects.filter(
                product=product,
                user=request.user,
                ordered=False
            )[0]
            # order_product.product_quantity -= 1
            # order_product.product_quantity = 0
            order.products.remove(order_product)
            # order_product.save()
            # order.products.save()
            messages.info(
                request, "This product is removed from your cart succesfully.")
            return redirect("products:product", slug=slug)
        else:
            # Add a message saying the order does not contain the item
            messages.info(request, "This product is not in your cart .")
            return redirect("products:product", slug=slug)
    else:
        # Add a message saying the user doesn't have an order
        messages.info(request, "Your cart is empty.")
        return redirect("products:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    product = get_object_or_404(Products, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # Check if the order item is in the order
        if order.products.filter(product__slug=product.slug).exists():
            order_product = OrderProduct.objects.filter(
                product=product,
                user=request.user,
                ordered=False
            )[0]
            if order_product.product_quantity > 1:
                order_product.product_quantity -= 1
                order_product.save()
            else:
                order.products.remove(order_product)
            return redirect("products:order-summary")
        else:
            return redirect("products:order-summary")
    else:
        return redirect("products:order-summary")


@login_required
def add_single_item_to_cart(request, slug):
    if request.user.is_authenticated:
        product = get_object_or_404(Products, slug=slug)

        order_product, created = OrderProduct.objects.get_or_create(
            product=product,
            user=request.user,
            ordered=False
        )
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # Check if the order item is in the order
            if order.products.filter(product__slug=product.slug).exists():
                order_product.product_quantity += 1
                order_product.save()
                return redirect("products:order-summary")
            else:
                order.products.add(order_product)
                return redirect("products:order-summary")
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=request.user, ordered_date=ordered_date)
            order.products.add(order_product)
        return redirect("products:order-summary")
    else:
        return redirect("products:home")
