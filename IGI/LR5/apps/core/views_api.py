from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Count
from decimal import Decimal, InvalidOperation
from .models import Category, Supplier, Product, Sale, Cart, CartItem, Order, OrderItem, ProductReview, Promo, PromoUsage
from .serializers import (
    CategorySerializer, SupplierSerializer,
    ProductSerializer, SaleSerializer,
    CartSerializer, CartItemSerializer,
    OrderSerializer, OrderItemSerializer,
    CreateOrderFromCartSerializer, ProductReviewSerializer,
    PromoSerializer, PromoUsageSerializer
)
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'address', 'email']
    ordering_fields = ['name']

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'suppliers']
    search_fields = ['name', 'article', 'description']
    ordering_fields = ['name', 'price', 'created_at', 'rating']

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def add_review(self, request, pk=None):
        product = self.get_object()
        
        # Проверяем, покупал ли пользователь товар
        if not Order.objects.filter(
            customer=request.user,
            items__product=product,
            status='delivered'
        ).exists():
            return Response(
                {"error": "Вы можете оставить отзыв только после покупки товара"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Проверяем, не оставлял ли пользователь уже отзыв
        if ProductReview.objects.filter(product=product, customer=request.user).exists():
            return Response(
                {"error": "Вы уже оставили отзыв на этот товар"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ProductReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                product=product,
                customer=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True)
    def reviews(self, request, pk=None):
        product = self.get_object()
        reviews = product.reviews.filter(is_moderated=True)
        page = self.paginate_queryset(reviews)
        
        if page is not None:
            serializer = ProductReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductReviewSerializer(reviews, many=True)
        return Response(serializer.data)

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['product', 'customer', 'date']
    ordering_fields = ['date', 'total_price']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Sale.objects.all()
        return Sale.objects.filter(customer=user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def statistics(self, request):
        total_sales = Order.objects.aggregate(total_revenue=Sum('total'), count=Count('id'))
        return Response({
            'total_revenue': total_sales['total_revenue'] or 0,
            'total_sales_count': total_sales['count'] or 0,
        })

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        cart = self.get_object()
        serializer = CartItemSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(cart=cart)
            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def remove_item(self, request, pk=None):
        cart = self.get_object()
        try:
            item = cart.items.get(id=request.data.get('item_id'))
            item.delete()
            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data)
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Товар не найден в корзине"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def update_quantity(self, request, pk=None):
        cart = self.get_object()
        try:
            item = cart.items.get(id=request.data.get('item_id'))
            serializer = CartItemSerializer(
                item,
                data={'quantity': request.data.get('quantity')},
                partial=True
            )
            
            if serializer.is_valid():
                serializer.save()
                cart_serializer = CartSerializer(cart)
                return Response(cart_serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Товар не найден в корзине"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        cart = self.get_object()
        cart.items.all().delete()
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data)

class PromoViewSet(viewsets.ModelViewSet):
    queryset = Promo.objects.all()
    serializer_class = PromoSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['code', 'description']
    ordering_fields = ['created_at', 'valid_from', 'valid_until']

    @action(detail=True, methods=['get'])
    def usages(self, request, pk=None):
        promo = self.get_object()
        usages = promo.usages.all()
        page = self.paginate_queryset(usages)
        
        if page is not None:
            serializer = PromoUsageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PromoUsageSerializer(usages, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def validate(self, request):
        code = request.data.get('code')
        amount_str = request.data.get('amount', '0')
        try:
            amount = Decimal(amount_str)
        except InvalidOperation:
            return Response(
                {"error": "Неверная сумма заказа"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            promo = Promo.objects.get(code=code)
        except Promo.DoesNotExist:
            return Response(
                {"error": "Промокод не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not promo.is_valid(amount, request.user):
            error_message = "Промокод недействителен или не может быть применен."
            if PromoUsage.objects.filter(promo=promo, customer=request.user).exists():
                error_message = "Вы уже использовали этот промокод."
            return Response(
                {"error": error_message},
                status=status.HTTP_400_BAD_REQUEST
            )

        discount = promo.calculate_discount(amount)
        return Response({
            "message": "Промокод действителен",
            "discount": discount,
            "final_amount": amount - discount,
            "promo_code": promo.code
        })

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'updated_at', 'total']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer=user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    @action(detail=False, methods=['post'])
    def create_from_cart(self, request):
        serializer = CreateOrderFromCartSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            order = serializer.save()
            return Response(
                OrderSerializer(order).data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status != 'pending':
            return Response(
                {"error": "Можно отменить только заказ в статусе 'Ожидает оплаты'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Возвращаем товары на склад
        for item in order.items.all():
            item.product.quantity += item.quantity
            item.product.save()
        
        order.status = 'cancelled'
        order.save()
        
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def apply_promo(self, request, pk=None):
        order = self.get_object()
        code = request.data.get('code')

        if not code:
            return Response(
                {"error": "Не указан промокод"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            promo = Promo.objects.get(code=code)
        except Promo.DoesNotExist:
            return Response(
                {"error": "Промокод не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Проверяем валидность промокода
        is_valid, message = promo.is_valid(order.subtotal)
        if not is_valid:
            return Response(
                {"error": message},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Применяем промокод
        discount = promo.calculate_discount(order.subtotal)
        order.promo = promo
        order.discount = discount
        order.total = order.subtotal + order.shipping_cost - discount
        order.save()

        # Создаем запись об использовании промокода
        PromoUsage.objects.create(
            promo=promo,
            order=order,
            customer=request.user,
            discount_amount=discount
        )

        # Увеличиваем счетчик использований
        promo.uses_count += 1
        promo.save()

        return Response(OrderSerializer(order).data)

class ProductReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['product', 'rating', 'is_moderated']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        # By default, users see all moderated reviews
        # For list view, allow seeing all moderated reviews
        if self.action == 'list':
            return ProductReview.objects.filter(is_moderated=True)
        # For other actions (retrieve, update, delete), users should only see their own if not moderated
        # Or if they are staff/admin they can see all for moderation purposes (handled by separate admin panel ideally)
        # For this specific update/delete, we will restrict to owner.
        return ProductReview.objects.all() # Base queryset, permissions handle access

    def perform_create(self, serializer):
        # Ensure product exists and user has not already reviewed it (unless policy changes)
        product_id = self.request.data.get('product')
        if not product_id:
            raise serializers.ValidationError({"product": "Product ID is required."}) # Use DRF validation
        product = get_object_or_404(Product, pk=product_id)

        if ProductReview.objects.filter(product=product, customer=self.request.user).exists():
            raise serializers.ValidationError({"detail": "Вы уже оставили отзыв на этот товар"})
        
        serializer.save(customer=self.request.user, product=product)

    def perform_update(self, serializer):
        review = self.get_object()
        if review.customer != self.request.user:
            raise PermissionDenied("Вы не можете редактировать чужой отзыв.")
        serializer.save()

    def perform_destroy(self, serializer):
        review = self.get_object()
        if review.customer != self.request.user:
            raise PermissionDenied("Вы не можете удалить чужой отзыв.")
        review.delete() # Changed from serializer.delete() to review.delete() 