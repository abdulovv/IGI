from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    mobile_phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    article_number = models.CharField(max_length=20, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    suppliers = models.ManyToManyField(Supplier, related_name='products')
    image = models.ImageField(upload_to='products/', default='static/images/no_image.png')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['price']

    def __str__(self):
        return self.name


class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    purchase_date = models.DateField()
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"Purchase of {self.quantity} {self.product.name} on {self.purchase_date}"


class PriceChange(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    change_date = models.DateField()
    new_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Price change for {self.product.name} on {self.change_date} to {self.new_price}"
