import sys

from PIL import Image

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.files.uploadedfile import InMemoryUploadedFile

from io import BytesIO

User = get_user_model()


class MinResolutionError(Exception):
    pass


class MaxResolutionError(Exception):
    pass


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Category Name')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


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
        image = self.image
        img = Image.open(image)

        min_height, min_width = Product.MIN_RESOLUTION
        max_height, max_width = Product.MAX_RESOLUTION

        if img.height > max_height or img.width > max_height:
            raise MaxResolutionError('The loaded image is too big')

        if img.height < min_height or img.width < min_width:
            raise MinResolutionError('The loaded image is too small')
        # The system of trim images
        # image = self.image
        # img = Image.open(image)
        # new_image = img.convert('RGB')
        # resized_image = new_image.resize((200, 200), Image.ANTIALIAS)
        # filestream = BytesIO()
        # resized_image.save(filestream, 'JPEG', qulity=98)
        # filestream.seek(0)
        #
        # self.image = InMemoryUploadedFile(
        #     filestream, 'ImageField', self.image.name, 'jpeg/image', sys.getsizeof(filestream), None
        # )

        super().save(*args, **kwargs)


class Notebook(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Diagonal')
    display_type = models.CharField(max_length=255, verbose_name='Display type')
    processor_frq = models.CharField(max_length=255, verbose_name='Processor frequency')
    ram = models.CharField(max_length=255, verbose_name='RAM')
    video = models.CharField(max_length=255, verbose_name='Video card')
    time_without_charge = models.CharField(max_length=255, verbose_name='Time without charge')
    
    def __str__(self):
        return f'{self.category.name} : title {self.title}'


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


class CartProduct(models.Model):
    customer = models.ForeignKey('Customer', verbose_name='Customer', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Cart', on_delete=models.CASCADE, related_name='related_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1, verbose_name='Number of products')
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Full price')

    def __str__(self):
        return self.product.name


class Cart(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Customer', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=8)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Final price')

    def __str__(self):
        return str(self.id)


class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='User', on_delete=models.CASCADE)
    phone = models.CharField(max_length=13, verbose_name='Phone number')
    address = models.CharField(max_length=255, verbose_name='Address')

    def __str__(self):
        return f"User: {self.user.first_name}, {self.user.last_name}"







