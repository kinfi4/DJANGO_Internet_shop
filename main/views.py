from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse_lazy
from django.views.generic import DetailView, View
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.core.handlers.wsgi import WSGIRequest

from .models import Notebook, Smartphone, Category, LatestProducts, Customer, Cart, CartProduct
from main.mixins import CategoryDetailMixin, CartMixin
from main.forms import OrderForm
from main.utils import recalc_cart


class BaseView(CartMixin):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_left_sidebar()
        products = LatestProducts.objects.get_products_for_main_page('notebook', 'smartphone')
        context = {
            'categories': categories,
            'products': products,
            'cart': self.cart

        }

        return render(request, 'base.html', context)


class ProductDetailView(CartMixin, CategoryDetailMixin, DetailView):
    CT_MODEL_CLASS = {
        'notebook': Notebook,
        'smartphone': Smartphone,
    }

    def dispatch(self, request: WSGIRequest, *args, **kwargs):

        self.model = self.CT_MODEL_CLASS[kwargs.get('ct_model')]
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)

    context_object_name = 'product'
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ct_model'] = self.model._meta.model_name
        context['cart'] = self.cart

        return context


class CategoryDetailView(CartMixin, CategoryDetailMixin, DetailView):
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart

        return context


class AddToCartView(CartMixin, View):
    def get(self, request, *args, **kwargs):

        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)

        cart_product, created = CartProduct.objects.get_or_create(
            customer=self.cart.user, cart=self.cart, content_type=content_type, object_id=product.id
        )

        if created:
            self.cart.products.add(cart_product)
            messages.add_message(request, messages.INFO, 'Product added successfully')
        else:
            messages.add_message(request, messages.WARNING, 'Product has already been added')

        recalc_cart(self.cart)

        return HttpResponseRedirect('/cart/')


class DeleteFromCartView(CartMixin, View):
    def get(self, request, *args, **kwargs):

        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            customer=self.cart.user, cart=self.cart, content_type=content_type, object_id=product.id,
        )
        self.cart.products.remove(cart_product)
        cart_product.delete()

        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, 'Product removed successfully')
        return HttpResponseRedirect('/cart/')


class ChangeQTYView(CartMixin, View):
    def post(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            customer=self.cart.user, cart=self.cart, content_type=content_type, object_id=product.id,
        )

        cart_product.qty = int(request.POST.get('qty'))
        cart_product.save()

        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, 'Amount was changed successfully')
        return HttpResponseRedirect('/cart/')


class CartView(CartMixin, View):
    def get(self, request: WSGIRequest, *args, **kwargs):
        categories = Category.objects.get_categories_for_left_sidebar()
        context = {
            'categories': categories,
            'cart': self.cart
        }

        return render(request, 'cart.html', context)


class CheckoutView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_left_sidebar()
        form = OrderForm(request.POST or None)
        context = {
            'categories': categories,
            'cart': self.cart,
            'form': form
        }

        return render(request, 'checkout.html', context)


class MakeOrderView(CartMixin, View):
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        if form.is_valid():
            new_order = form.save(commit=False)

            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['first_name']
            new_order.buying_type = form.cleaned_data['buying_type']
            new_order.order_date = form.cleaned_data['order_date']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()
            self.cart.in_order = True
            new_order.cart = self.cart
            new_order.save()

            self.cart.delete()
            messages.add_message(request, messages.INFO, 'Thank you for your order, but its not actually a shop :(')
            return HttpResponseRedirect('/')

        return HttpResponseRedirect('/checkout/')


# class LogInView(LoginView):
#     template_name = 'login.html'
#     form_class = AuthUserForm
#     success_url = reverse_lazy('/')
