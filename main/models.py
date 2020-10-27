import sys
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


def get_models_for_count(*model_names):
    return [models.Count(model_name) for model_name in model_names]


def get_product_url(obj, viewname):
    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})


class LatestProductsManager:
    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)

        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(
                        products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to), reverse=True
                    )

        return products


class LatestProducts:
    objects = LatestProductsManager()


class CategoryManager(models.Manager):
    CATEGORY_NAMES = {
        'Notebook': 'notebook__count',
        'Smartphone': 'smartphone__count'
    }

    def get_queryset(self):
        return super().get_queryset()

    def get_categories_for_left_sidebar(self):
        models = get_models_for_count('notebook', 'smartphone')
        qs = list(self.get_queryset().annotate(*models))
        data = [
            dict(name=c.name, url=c.get_absolute_url(), count=getattr(c, self.CATEGORY_NAMES[c.name]))
            for c in qs
        ]

        return data


class MinResolutionError(Exception):
    pass


class MaxResolutionError(Exception):
    pass


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Category Name')
    slug = models.SlugField(unique=True)
    objects = CategoryManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    MIN_RESOLUTION = (400, 400)
    MAX_RESOLUTION = (3000, 3000)

    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='Category', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Title')
    description = models.TextField(verbose_name='Description', null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Price')
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Image')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # image = self.image
        # img = Image.open(image)
        #
        # min_height, min_width = Product.MIN_RESOLUTION
        # max_height, max_width = Product.MAX_RESOLUTION
        #
        # if img.height > max_height or img.width > max_height:
        #     raise MaxResolutionError('The loaded image is too big')
        #
        # if img.height < min_height or img.width < min_width:
        #     raise MinResolutionError('The loaded image is too small')

        image = self.image
        # The system of trim images
        img = Image.open(image)
        new_image = img.convert('RGB')
        resized_image = new_image.resize((600, 600), Image.ANTIALIAS)
        filestream = BytesIO()
        resized_image.save(filestream, 'JPEG', qulity=98)
        filestream.seek(0)

        self.image = InMemoryUploadedFile(
            filestream, 'ImageField', self.image.name, 'jpeg/image', sys.getsizeof(filestream), None
        )

        super().save(*args, **kwargs)

    def get_model_name(self):
        return self.__class__.__name__.lower()


class Notebook(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Diagonal')
    display_type = models.CharField(max_length=255, verbose_name='Display type')
    processor_frq = models.CharField(max_length=255, verbose_name='Processor frequency')
    ram = models.CharField(max_length=255, verbose_name='RAM')
    video = models.CharField(max_length=255, verbose_name='Video card')
    time_without_charge = models.CharField(max_length=255, verbose_name='Time without charge')

    def __str__(self):
        return f'{self.category.name} : title {self.title}'

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class Smartphone(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Diagonal')
    display_type = models.CharField(max_length=255, verbose_name='Display type')
    resolution = models.CharField(max_length=255, verbose_name='Resolution')
    sd = models.BooleanField(default=True)
    accum_volume = models.CharField(max_length=255, verbose_name='Accumulator volume')
    ram = models.CharField(max_length=255, verbose_name='RAM')
    sd_volume_max = models.CharField(max_length=255, verbose_name='Max volume of memory')
    main_cam_mp = models.CharField(max_length=255, verbose_name='Main camera')
    front_cam_mp = models.CharField(max_length=255, verbose_name='Front camera')

    def __str__(self):
        return f'{self.category.name} : {self.title}'

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class CartProduct(models.Model):
    customer = models.ForeignKey('Customer', verbose_name='Customer', on_delete=models.CASCADE, null=True, blank=True)
    cart = models.ForeignKey('Cart', verbose_name='Cart', on_delete=models.CASCADE, related_name='related_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1, verbose_name='Number of products')
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Full price')

    def __str__(self):
        return self.content_object.title

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)


class Cart(models.Model):
    user = models.ForeignKey('Customer', null=True, verbose_name='Customer', on_delete=models.CASCADE)
    user_agent = models.CharField(max_length=200, verbose_name='User-Agent', null=True, blank=True)

    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart', null=True)
    total_products = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=10, default=0, decimal_places=2, verbose_name='Final price')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='User', on_delete=models.CASCADE)
    phone = models.CharField(max_length=13, verbose_name='Phone number', null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name='Address', null=True, blank=True)
    orders = models.ManyToManyField('Order', verbose_name='Customer`s orders', null=True, blank=True)

    def __str__(self):
        return f"User: {self.user.first_name}, {self.user.last_name}"


class Order(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'New order'),
        (STATUS_IN_PROGRESS, 'Order is in progress'),
        (STATUS_READY, 'Order is ready'),
        (STATUS_COMPLETED, 'Order is completed'),
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Self delivery'),
        (BUYING_TYPE_DELIVERY, 'Delivery'),
    )

    owner = models.ForeignKey(Customer, verbose_name='Customer', on_delete=models.CASCADE, blank=True, null=True)
    cart = models.ForeignKey(Cart, verbose_name='Cart', on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=255, verbose_name='First name')
    last_name = models.CharField(max_length=255, verbose_name='Last name')
    phone = models.CharField(max_length=20, verbose_name='Phone')
    address = models.CharField(max_length=1024, verbose_name='Address', blank=True, null=True)
    status = models.CharField(max_length=100, verbose_name='Order status', choices=STATUS_CHOICES, default=STATUS_NEW)
    buying_type = models.CharField(max_length=100, verbose_name='Buying type', choices=BUYING_TYPE_CHOICES,
                                   default=BUYING_TYPE_SELF)
    comment = models.TextField(max_length=1000, verbose_name='Comment for order', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='The time of ordering')
    order_date = models.DateField(verbose_name='Date of the ordering', default=timezone.now)

    def __str__(self):
        return f'The order {self.id}'
