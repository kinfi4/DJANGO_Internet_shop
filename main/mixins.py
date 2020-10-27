from django.views.generic.detail import SingleObjectMixin, View

from main.models import Category, Cart, Customer, Notebook, Smartphone


class CategoryDetailMixin(SingleObjectMixin):
    CATEGORY_SLUG2PRODUCT_MODEL = {
        'notebooks': Notebook,
        'smartphones': Smartphone
    }

    def get_context_data(self, **kwargs):
        if isinstance(self.get_object(), Category):
            model = self.CATEGORY_SLUG2PRODUCT_MODEL[self.get_object().slug]
            context = super().get_context_data(**kwargs)
            context['categories'] = Category.objects.get_categories_for_left_sidebar()
            context['category_products'] = model.objects.all()
        else:
            context = super().get_context_data(**kwargs)
            context['categories'] = Category.objects.get_categories_for_left_sidebar()

        return context


class CartMixin(View):
    def dispatch(self, request, *args, **kwargs):
        self.is_aut = request.user.is_authenticated

        if self.is_aut:
            customer = Customer.objects.filter(user=request.user).first()

            if not customer:
                customer = Customer.objects.create(
                    user=request.user
                )

            cart = Cart.objects.filter(user=customer, in_order=False).first()
            if not cart:
                cart = Cart.objects.create(user=customer)

        else:
            cart = Cart.objects.filter(user_agent=request.headers['User-Agent'], for_anonymous_user=True).first()
            if not cart:
                cart = Cart(user_agent=request.headers['User-Agent'], for_anonymous_user=True)

        self.cart = cart
        self.cart.save()
        return super().dispatch(request, *args, **kwargs)
