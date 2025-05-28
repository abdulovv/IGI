from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import pytz

# Function for default valid_until value
def get_default_valid_until():
    return timezone.now() + timedelta(days=7)

class Category(models.Model):
    name = models.CharField('Название категории', max_length=100)
    description = models.TextField('Описание', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories', verbose_name='Родительская категория')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField('Название компании', max_length=100)
    address = models.CharField('Адрес', max_length=255)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email')
    # ManyToManyField - связь с товарами через промежуточную модель
    products = models.ManyToManyField('Product', through='SupplierProduct', related_name='supplier_products', verbose_name='Поставляемые товары')

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'

    def __str__(self):
        return self.name

# Промежуточная модель для связи многие-ко-многим между Supplier и Product
class SupplierProduct(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name='Поставщик')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name='Товар')
    is_main_supplier = models.BooleanField('Основной поставщик', default=False)
    supply_price = models.DecimalField('Цена поставки', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    last_supply_date = models.DateTimeField('Дата последней поставки', null=True, blank=True)

    class Meta:
        verbose_name = 'Поставщик товара'
        verbose_name_plural = 'Поставщики товара'
        unique_together = ['supplier', 'product']  # Уникальная связь

    def __str__(self):
        return f"{self.supplier.name} - {self.product.name}"

class Product(models.Model):
    # ForeignKey - связь с категорией (один ко многим)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категория')
    name = models.CharField('Название товара', max_length=200)
    article = models.CharField('Артикул', max_length=50, unique=True)
    description = models.TextField('Описание')
    price = models.DecimalField('Цена продажи', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quantity = models.PositiveIntegerField('Количество на складе', default=0)
    image = models.ImageField('Изображение', upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    suppliers = models.ManyToManyField(Supplier, related_name='product_suppliers', verbose_name='Поставщики')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (Арт. {self.article})"

    @property
    def current_supplier(self):
        """Получить основного поставщика товара"""
        supplier_product = self.supplierproduct_set.filter(is_main_supplier=True).first()
        return supplier_product.supplier if supplier_product else None

    @property
    def current_supply_price(self):
        """Получить текущую цену поставки"""
        supplier_product = self.supplierproduct_set.filter(is_main_supplier=True).first()
        return supplier_product.supply_price if supplier_product else None

    def calculate_rating(self):
        reviews = self.reviews.filter(is_moderated=True)
        if reviews.exists():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return None

    def reviews_count(self):
        return self.reviews.filter(is_moderated=True).count()

    rating = property(calculate_rating)
    reviews_count = property(reviews_count)

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales', verbose_name='Товар')
    quantity = models.PositiveIntegerField('Количество')
    price_per_unit = models.DecimalField('Цена за единицу', max_digits=10, decimal_places=2)
    total_price = models.DecimalField('Общая стоимость', max_digits=10, decimal_places=2)
    date = models.DateTimeField('Дата продажи', auto_now_add=True)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='purchases', verbose_name='Покупатель')

    class Meta:
        verbose_name = 'Продажа'
        verbose_name_plural = 'Продажи'
        ordering = ['-date']

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.price_per_unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Продажа {self.product.name} ({self.date.strftime('%d.%m.%Y %H:%M')})"

class Cart(models.Model):
    customer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', verbose_name='Покупатель')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f"Корзина пользователя {self.customer.username}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='Корзина')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField('Количество', default=1, validators=[MinValueValidator(1)])
    added_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.product.name} ({self.quantity} шт.) в корзине {self.cart.customer.username}"

    @property
    def total_price(self):
        return self.quantity * self.product.price

class Order(models.Model):
    STATUS_CHOICES = [
        # ('pending', 'Ожидает оплаты'), # Можно закомментировать или удалить
        ('paid', 'Оплачен'), # Оставим, если вдруг понадобится
        ('processing', 'Заказ оформлен'), # Изменен текст
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Покупатель')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='processing') # Изменен default
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    shipping_address = models.TextField('Адрес доставки')
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email')
    comment = models.TextField('Комментарий к заказу', blank=True)
    client_timezone = models.CharField('Часовой пояс клиента', max_length=50, blank=True, null=True) # New field
    
    # Для сохранения информации о ценах на момент заказа
    subtotal = models.DecimalField('Сумма товаров', max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField('Стоимость доставки', max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField('Итоговая сумма', max_digits=10, decimal_places=2, default=0)
    promo = models.ForeignKey(
        'Promo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Примененный промокод'
    )
    discount = models.DecimalField(
        'Сумма скидки',
        max_digits=10,
        decimal_places=2,
        default=0
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.id} ({self.get_status_display()})"

    def get_created_at_in_client_timezone(self):
        if self.client_timezone:
            try:
                tz = timezone.pytz.timezone(self.client_timezone)
                return self.created_at.astimezone(tz)
            except Exception: # Handle invalid timezone string or missing pytz
                pass
        return self.created_at # Fallback to server time

    def save(self, *args, **kwargs):
        if not self.total:
            self.total = self.subtotal + self.shipping_cost
        super().save(*args, **kwargs)

    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Товар')
    quantity = models.PositiveIntegerField('Количество', validators=[MinValueValidator(1)])
    price = models.DecimalField('Цена на момент заказа', max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

    def __str__(self):
        return f"{self.product.name} ({self.quantity} шт.) в заказе #{self.order.id}"

    @property
    def total_price(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        # Если цена не установлена, берем текущую цену товара
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='Товар')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_reviews', verbose_name='Покупатель')
    rating = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Оценка от 1 до 5'
    )
    text = models.TextField('Текст отзыва')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    is_moderated = models.BooleanField('Прошел модерацию', default=False)

    class Meta:
        verbose_name = 'Отзыв о товаре'
        verbose_name_plural = 'Отзывы о товарах'
        ordering = ['-created_at']
        unique_together = ['product', 'customer']

    def __str__(self):
        return f"Отзыв на {self.product.name} от {self.customer.username}"

class Promo(models.Model):
    code = models.CharField('Промокод', max_length=20, unique=True)
    discount_amount = models.DecimalField(
        'Сумма скидки',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        default=Decimal('0.00')
    )
    description = models.TextField('Описание', blank=True)
    valid_from = models.DateTimeField('Действителен с', default=timezone.now)
    valid_until = models.DateTimeField('Действителен до', default=get_default_valid_until)
    min_order_amount = models.DecimalField(
        'Минимальная сумма заказа',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'
        ordering = ['-created_at']

    def __str__(self):
        return self.code

    def is_valid(self, order_amount, user):
        if not self.is_active:
            return False
        if self.valid_from and timezone.now() < self.valid_from:
            return False
        if self.valid_until and timezone.now() > self.valid_until:
            return False
        if order_amount < self.min_order_amount:
            return False
        if PromoUsage.objects.filter(promo=self, customer=user).exists():
            return False
        return True

    def calculate_discount(self, order_amount):
        # For fixed amount, the discount is simply the discount_amount
        # Ensure discount doesn't exceed order_amount
        return min(self.discount_amount, order_amount)

class PromoUsage(models.Model):
    promo = models.ForeignKey(Promo, on_delete=models.CASCADE, related_name='usages', verbose_name='Промокод')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='promo_usages', verbose_name='Покупатель')
    used_at = models.DateTimeField('Дата использования', auto_now_add=True)

    class Meta:
        verbose_name = 'Использование промокода'
        verbose_name_plural = 'Использования промокодов'
        ordering = ['-used_at']
        unique_together = ['promo', 'customer'] # Each customer can use a promo only once

    def __str__(self):
        return f"{self.customer.username} использовал {self.promo.code}"

class SupplierPurchase(models.Model):
    # ForeignKey - связи с поставщиком и товаром (один ко многим)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchases', verbose_name='Поставщик')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='purchase_history', verbose_name='Товар')
    quantity = models.PositiveIntegerField('Количество', validators=[MinValueValidator(1)])
    price_per_unit = models.DecimalField('Цена за единицу', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_price = models.DecimalField('Общая стоимость', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    purchase_date = models.DateTimeField('Дата закупки', default=timezone.now)
    created_at = models.DateTimeField('Дата создания записи', auto_now_add=True)
    
    class Meta:
        ordering = ['-purchase_date']
        verbose_name = 'Закупка у поставщика'
        verbose_name_plural = 'Закупки у поставщиков'
    
    def save(self, *args, **kwargs):
        # Рассчитываем общую стоимость
        self.total_price = self.quantity * self.price_per_unit
        
        # Обновляем связь поставщик-товар
        supplier_product, created = SupplierProduct.objects.get_or_create(
            supplier=self.supplier,
            product=self.product,
            defaults={'supply_price': self.price_per_unit}
        )
        
        # Обновляем информацию о поставке
        supplier_product.supply_price = self.price_per_unit
        supplier_product.last_supply_date = self.purchase_date
        supplier_product.save()
        
        # Увеличиваем количество товара
        self.product.quantity += self.quantity
        self.product.save()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Закупка {self.product.name} ({self.quantity} шт.) у {self.supplier.name} от {self.purchase_date.strftime('%d.%m.%Y')}"
