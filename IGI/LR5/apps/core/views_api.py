from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Count
from decimal import Decimal, InvalidOperation
from .models import Category, Supplier, Product, Sale, Cart, CartItem, Order, OrderItem, Promo, PromoUsage
from .serializers import (
    CategorySerializer, SupplierSerializer,
    ProductSerializer, SaleSerializer,
    CartSerializer, CartItemSerializer,
    OrderSerializer, OrderItemSerializer,
    CreateOrderFromCartSerializer, PromoSerializer,
    PromoUsageSerializer
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
    ordering_fields = ['name', 'price', 'created_at']

    def perform_create(self, serializer):
        serializer.save()

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
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id:
            return Response(
                {"error": "Product ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        product = get_object_or_404(Product, pk=product_id)
        
        if product.quantity < quantity:
            return Response(
                {"error": "Not enough items in stock"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity, 'price': product.price}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def remove_item(self, request, pk=None):
        cart = self.get_object()
        item_id = request.data.get('item_id')

        if not item_id:
            return Response(
                {"error": "Item ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            item = cart.items.get(pk=item_id)
            item.delete()
            serializer = self.get_serializer(cart)
            return Response(serializer.data)
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Item not found in cart"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def update_item(self, request, pk=None):
        cart = self.get_object()
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')

        if not item_id or quantity is None:
            return Response(
                {"error": "Item ID and quantity are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)
        except ValueError:
            return Response(
                {"error": "Quantity must be a number"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            item = cart.items.get(pk=item_id)
            if quantity <= 0:
                item.delete()
            else:
                if item.product.quantity < quantity:
                    return Response(
                        {"error": "Not enough items in stock"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                item.quantity = quantity
                item.save()
            
            serializer = self.get_serializer(cart)
            return Response(serializer.data)
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Item not found in cart"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        cart = self.get_object()
        cart.items.all().delete()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'total']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer=user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    @action(detail=False, methods=['post'])
    def create_from_cart(self, request):
        serializer = CreateOrderFromCartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = Cart.objects.get(customer=request.user)
            if not cart.items.exists():
                return Response(
                    {"error": "Cart is empty"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create order
            order = Order.objects.create(
                customer=request.user,
                shipping_address=serializer.validated_data['shipping_address'],
                phone=serializer.validated_data['phone'],
                email=serializer.validated_data['email'],
                comment=serializer.validated_data.get('comment', ''),
                subtotal=cart.total_price,
                total=cart.total_price
            )

            # Create order items
            for cart_item in cart.items.all():
                if cart_item.product.quantity < cart_item.quantity:
                    order.delete()
                    return Response(
                        {
                            "error": f"Not enough {cart_item.product.name} in stock. "
                                    f"Available: {cart_item.product.quantity}"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )

                # Update product quantity
                cart_item.product.quantity -= cart_item.quantity
                cart_item.product.save()

            # Clear cart
            cart.items.all().delete()

            # Apply promo code if provided
            promo_code = serializer.validated_data.get('promo_code')
            if promo_code:
                try:
                    promo = Promo.objects.get(code=promo_code)
                    if promo.is_valid(order.subtotal, request.user):
                        discount = promo.calculate_discount(order.subtotal)
                        order.promo = promo
                        order.discount = discount
                        order.total = order.subtotal - discount
                        order.save()

                        # Record promo usage
                        PromoUsage.objects.create(
                            promo=promo,
                            customer=request.user,
                            order=order,
                            discount_amount=discount
                        )

                        # Update promo uses count
                        promo.uses_count += 1
                        promo.save()
                except Promo.DoesNotExist:
                    pass

            return Response(
                OrderSerializer(order).data,
                status=status.HTTP_201_CREATED
            )

        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')

        if not new_status:
            return Response(
                {"error": "Status is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {"error": "Invalid status"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()
        return Response(OrderSerializer(order).data)

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
                {"error": "Invalid order amount"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            promo = Promo.objects.get(code=code)
        except Promo.DoesNotExist:
            return Response(
                {"error": "Promo code not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not promo.is_valid(amount, request.user):
            error_message = "Promo code is invalid or cannot be applied."
            if PromoUsage.objects.filter(promo=promo, customer=request.user).exists():
                error_message = "You have already used this promo code."
            return Response(
                {"error": error_message},
                status=status.HTTP_400_BAD_REQUEST
            )

        discount = promo.calculate_discount(amount)
        return Response({
            "message": "Promo code is valid",
            "discount": discount,
            "final_amount": amount - discount,
            "promo_code": promo.code
        }) 