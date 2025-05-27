from rest_framework import serializers
from .models import Category, Supplier, Product, Sale, Cart, CartItem, Order, OrderItem, ProductReview, Promo, PromoUsage

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'address', 'phone', 'email']

class ProductReviewSerializer(serializers.ModelSerializer):
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    
    class Meta:
        model = ProductReview
        fields = [
            'id', 'product', 'customer', 'customer_username',
            'rating', 'text', 'created_at', 'updated_at',
            'is_moderated'
        ]
        read_only_fields = ['customer', 'is_moderated']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    suppliers = SupplierSerializer(many=True, read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        source='category'
    )
    supplier_ids = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        write_only=True,
        many=True,
        source='suppliers'
    )
    rating = serializers.DecimalField(
        max_digits=3,
        decimal_places=2,
        read_only=True
    )
    reviews_count = serializers.IntegerField(read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'article', 'category', 'category_id',
            'description', 'price', 'quantity', 'suppliers',
            'supplier_ids', 'image', 'created_at', 'updated_at',
            'rating', 'reviews_count', 'reviews'
        ]

class SaleSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        source='product'
    )

    class Meta:
        model = Sale
        fields = [
            'id', 'product', 'product_id', 'quantity',
            'price_per_unit', 'total_price', 'date', 'customer'
        ]
        read_only_fields = ['total_price', 'customer']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        source='product'
    )
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            'id', 'cart', 'product', 'product_id',
            'quantity', 'added_at', 'total_price'
        ]
        read_only_fields = ['cart']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Количество товара должно быть больше 0")
        return value

    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity', 1)
        
        if product and product.quantity < quantity:
            raise serializers.ValidationError(
                f"Недостаточно товара на складе. В наличии: {product.quantity}"
            )
        return data

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = [
            'id', 'customer', 'items', 'created_at',
            'updated_at', 'total_price', 'total_items'
        ]
        read_only_fields = ['customer']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        source='product'
    )
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'product', 'product_id',
            'quantity', 'price', 'total_price'
        ]
        read_only_fields = ['order', 'price']

class PromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promo
        fields = [
            'id', 'code', 'discount_amount',
            'description', 'valid_from', 'valid_until',
            'min_order_amount', 'is_active'
        ]

class PromoUsageSerializer(serializers.ModelSerializer):
    promo_code = serializers.CharField(source='promo.code', read_only=True)
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    
    class Meta:
        model = PromoUsage
        fields = [
            'id', 'promo', 'promo_code', 
            'customer', 'customer_username', 'used_at'
        ]
        read_only_fields = ['promo', 'customer', 'used_at']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items_count = serializers.IntegerField(read_only=True)
    promo_applied_code = serializers.CharField(source='promo.code', read_only=True, allow_null=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'status', 'status_display',
            'created_at', 'updated_at', 'shipping_address',
            'phone', 'email', 'comment', 'items', 'items_count',
            'subtotal', 'shipping_cost', 'discount', 'total',
            'promo', 'promo_applied_code'
        ]
        read_only_fields = [
            'customer', 'subtotal', 'total', 'discount',
            'promo', 'promo_applied_code'
        ]

class CreateOrderFromCartSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    comment = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        user = self.context['request'].user
        cart = Cart.objects.get(customer=user)
        
        if not cart.items.exists():
            raise serializers.ValidationError("Корзина пуста")

        # Создаем заказ
        order = Order.objects.create(
            customer=user,
            shipping_address=validated_data['shipping_address'],
            phone=validated_data['phone'],
            email=validated_data['email'],
            comment=validated_data.get('comment', ''),
            subtotal=cart.total_price,
            shipping_cost=0,  # Можно добавить расчет стоимости доставки
            total=cart.total_price  # + стоимость доставки
        )

        # Переносим товары из корзины в заказ
        for cart_item in cart.items.all():
            if cart_item.quantity > cart_item.product.quantity:
                raise serializers.ValidationError(
                    f"Недостаточно товара '{cart_item.product.name}' на складе"
                )
            
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            
            # Уменьшаем количество товара на складе
            cart_item.product.quantity -= cart_item.quantity
            cart_item.product.save()

        # Очищаем корзину
        cart.items.all().delete()

        return order 