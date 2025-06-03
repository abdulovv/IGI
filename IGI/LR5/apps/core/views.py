from django.views.generic import ListView, DetailView, View, CreateView, UpdateView, DeleteView, TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Sum, Avg, Count, F
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Product, Category, Supplier, Sale, Cart, CartItem, Order, OrderItem, Promo, PromoUsage, SupplierPurchase
from django.utils import timezone
import pytz # Добавляем импорт pytz
from decimal import Decimal
from django.contrib.auth import get_user_model
import calendar # Добавляем импорт calendar
from datetime import datetime # Добавляем импорт datetime
from django.conf import settings
from .forms import ProductQuantityUpdateForm, SupplierPurchaseForm
import matplotlib.pyplot as plt
import io
import base64
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np

class ProductListView(ListView):
    model = Product
    template_name = 'core/product_list.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация по категории
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__id=category)
        
        # Фильтрация по цене
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        # Сортировка
        sort = self.request.GET.get('sort')
        if sort:
            if sort == 'price':
                queryset = queryset.order_by('price')
            elif sort == '-price':
                queryset = queryset.order_by('-price')
            elif sort == 'name':
                queryset = queryset.order_by('name')
            elif sort == '-name':
                queryset = queryset.order_by('-name')
                
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        
        # Добавляем выбранную категорию в контекст
        category_id = self.request.GET.get('category')
        if category_id:
            context['selected_category'] = Category.objects.filter(id=category_id).first()
        
        # Добавляем информацию о типе пользователя
        user = self.request.user
        if user.is_authenticated:
            context['is_staff'] = user.is_staff
            context['is_superuser'] = user.is_superuser
            
            # Информация для сотрудников и администраторов
            if user.is_staff or user.is_superuser:
                # Получаем статистику продаж
                sales_stats = Order.objects.aggregate(
                    total_sales_count=Count('id'),
                    total_revenue=Sum('total')
                )
                context['total_sales_count'] = sales_stats['total_sales_count'] or 0
                context['total_revenue'] = sales_stats['total_revenue'] or 0

                # Получаем информацию о поставщиках
                suppliers = Supplier.objects.annotate(
                    products_count=Count('products')
                ).prefetch_related('products')
                
                context['suppliers'] = suppliers
            
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'core/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context['related_products'] = Product.objects.filter(category=product.category).exclude(id=product.id).order_by('?')[:4]
        
        user_timezone_str = self.request.session.get('user_timezone', 'Europe/Minsk')
        try:
            user_timezone = pytz.timezone(user_timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            user_timezone = pytz.timezone('Europe/Minsk') 
        context['user_timezone'] = user_timezone

        if self.request.user.is_staff or self.request.user.is_superuser:
            context['quantity_form'] = ProductQuantityUpdateForm(initial={'quantity': product.quantity})

        return context

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "У вас нет прав для изменения количества товара.")
            return redirect(product.get_absolute_url())

        form = ProductQuantityUpdateForm(request.POST)
        if form.is_valid():
            new_quantity = form.cleaned_data['quantity']
            product.quantity = new_quantity
            product.save(update_fields=['quantity'])
            messages.success(request, f"Количество товара '{product.name}' успешно обновлено до {new_quantity}.")
        else:
            messages.error(request, "Ошибка при обновлении количества. Пожалуйста, проверьте введенное значение.")
            # Чтобы форма отобразилась с ошибками, передадим ее в контекст при редиректе (не лучший способ, но для простоты)
            # Лучше было бы перерисовать страницу с ошибками формы без редиректа, но это усложнит get_context_data
            # Для простоты оставим так, ошибки будут показаны через messages

        return redirect(product.get_absolute_url())

class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'core/supplier_list.html'
    context_object_name = 'suppliers'
    login_url = 'login'

    def dispatch(self, request, *args, **kwargs):
        # Доступ для администраторов и сотрудников
        if not (request.user.is_superuser or request.user.is_staff):
            messages.warning(request, 'У вас нет доступа к списку поставщиков')
            return redirect('content:home')
        return super().dispatch(request, *args, **kwargs)

class SaleListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'core/sale_list.html'
    context_object_name = 'orders'
    login_url = 'login'
    paginate_by = 10

    def get_queryset(self):
        # Администраторы и сотрудники видят все заказы
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Order.objects.all().order_by('-created_at')
        # Обычные пользователи видят только свои заказы
        return Order.objects.filter(customer=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Статистика доступна только для администраторов и сотрудников
        if self.request.user.is_superuser or self.request.user.is_staff:
            # Используем Order для статистики, так как заказы создают Order, а не Sale
            statistics = Order.objects.aggregate(
                total_revenue=Sum('total'), 
                total_sales_count=Count('id')
            )
            context['total_revenue'] = statistics['total_revenue'] or 0
            context['total_sales_count'] = statistics['total_sales_count'] or 0
        
        # Добавляем таймзону пользователя для форматирования дат в шаблоне
        user_timezone_str = self.request.session.get('django_timezone', 'Europe/Minsk') # Минск по умолчанию
        context['user_timezone'] = user_timezone_str
        return context

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    http_referer = request.META.get('HTTP_REFERER')

    if request.method == 'POST':
        if request.user.is_staff or request.user.is_superuser:
            messages.warning(request, 'Сотрудники и администраторы не могут совершать покупки')
            return redirect(http_referer or reverse('core:product-list'))
        
        quantity_to_add = int(request.POST.get('quantity', 1))
        if quantity_to_add <= 0:
            messages.error(request, 'Количество товара должно быть положительным.')
            return redirect(http_referer or reverse('core:product-detail', kwargs={'pk': product_id}))

        cart, _ = Cart.objects.get_or_create(customer=request.user)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product,
            defaults={'quantity': 0} 
        )
        
        new_quantity_in_cart = cart_item.quantity + quantity_to_add

        if product.quantity < new_quantity_in_cart:
            messages.error(request, f'Недостаточно товара "{product.name}" на складе. Доступно: {product.quantity}, в корзине уже: {cart_item.quantity}')
        else:
            cart_item.quantity = new_quantity_in_cart
            cart_item.save()
            messages.success(request, f'Товар "{product.name}" ({quantity_to_add} шт.) добавлен в корзину.')
        
        return redirect(http_referer or reverse('core:product-detail', kwargs={'pk': product_id}))
    
    return redirect(http_referer or reverse('core:product-detail', kwargs={'pk': product_id}))

class CartView(LoginRequiredMixin, View):
    template_name = 'core/cart.html'
    login_url = 'login'

    def get(self, request):
        if request.user.is_staff or request.user.is_superuser:
            messages.warning(request, 'Сотрудники и администраторы не могут совершать покупки')
            return redirect('core:product-list')

        cart, created = Cart.objects.get_or_create(customer=request.user)
        context = {
            'cart': cart,
            'cart_items': cart.items.select_related('product').all()
        }
        return render(request, self.template_name, context)

@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.user.is_staff or request.user.is_superuser:
            return JsonResponse({
                'error': 'Сотрудники и администраторы не могут совершать покупки'
            }, status=403)

        cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
        action = request.POST.get('action')
        
        if action == 'increase':
            if cart_item.product.quantity > cart_item.quantity:
                cart_item.quantity += 1
                cart_item.save()
            else:
                return JsonResponse({
                    'error': 'Недостаточно товара на складе'
                }, status=400)
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        elif action == 'remove':
            cart_item.delete()
        
        cart = cart_item.cart
        context = {
            'cart': cart,
            'cart_items': cart.items.select_related('product').all()
        }
        cart_html = render_to_string('core/cart_items.html', context, request=request)
        
        return JsonResponse({
            'cart_html': cart_html,
            'cart_total': str(cart.total_price),
            'cart_items_count': cart.total_items
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def apply_promo(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.user.is_staff or request.user.is_superuser:
            return JsonResponse({
                'error': 'Сотрудники и администраторы не могут использовать промокоды'
            }, status=403)

        code = request.POST.get('code')
        cart = get_object_or_404(Cart, customer=request.user)
        
        try:
            promo = Promo.objects.get(code=code)
            if not promo.is_valid(cart.total_price, request.user):
                error_message = 'Промокод недействителен, истек срок действия, не достигнута минимальная сумма заказа или уже был использован.'
                if PromoUsage.objects.filter(promo=promo, customer=request.user).exists():
                    error_message = 'Вы уже использовали этот промокод.'
                elif not promo.is_active:
                    error_message = 'Промокод неактивен.'
                elif promo.valid_from and timezone.now() < promo.valid_from:
                    error_message = 'Срок действия промокода еще не начался.'
                elif promo.valid_until and timezone.now() > promo.valid_until:
                    error_message = 'Срок действия промокода истек.'
                elif cart.total_price < promo.min_order_amount:
                    error_message = f'Минимальная сумма заказа для этого промокода: {promo.min_order_amount} руб.'
                
                return JsonResponse({
                    'error': error_message
                }, status=400)
            
            discount = promo.calculate_discount(cart.total_price)
            request.session['applied_promo_code'] = promo.code
            request.session['promo_discount_amount'] = str(discount)
            
            return JsonResponse({
                'success': True,
                'discount': str(discount),
                'total_with_discount': str(cart.total_price - discount),
                'message': f'Промокод "{promo.code}" применен. Скидка: {discount} руб.'
            })
        except Promo.DoesNotExist:
            return JsonResponse({
                'error': 'Промокод не найден'
            }, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

class CheckoutView(LoginRequiredMixin, View):
    template_name = 'core/checkout.html'
    login_url = 'login'

    def get(self, request):
        if request.user.is_staff or request.user.is_superuser:
            messages.warning(request, 'Сотрудники и администраторы не могут оформлять заказы')
            return redirect('core:product-list')

        cart = get_object_or_404(Cart, customer=request.user)
        if not cart.items.exists():
            messages.warning(request, 'Ваша корзина пуста')
            return redirect('core:cart')

        context = {
            'cart': cart,
            'cart_items': cart.items.select_related('product').all(),
            'applied_promo_code': request.session.get('applied_promo_code'),
            'promo_discount_amount': request.session.get('promo_discount_amount')
        }
        if context['applied_promo_code'] and context['promo_discount_amount']:
            try:
                promo = Promo.objects.get(code=context['applied_promo_code'])
                discount = Decimal(context['promo_discount_amount'])
                if promo.is_valid(cart.total_price, request.user):
                    context['total_with_discount'] = cart.total_price - discount
                else:
                    del request.session['applied_promo_code']
                    del request.session['promo_discount_amount']
                    messages.warning(request, 'Примененный промокод больше не действителен.')
            except Promo.DoesNotExist:
                del request.session['applied_promo_code']
                del request.session['promo_discount_amount']
                messages.error(request, 'Произошла ошибка с промокодом.')

        return render(request, self.template_name, context)

    def post(self, request):
        if request.user.is_staff or request.user.is_superuser:
            messages.warning(request, 'Сотрудники и администраторы не могут оформлять заказы')
            return redirect('core:product-list')

        cart = get_object_or_404(Cart, customer=request.user)
        if not cart.items.exists():
            messages.warning(request, 'Ваша корзина пуста')
            return redirect('core:cart')

        # Проверяем наличие товаров
        for item in cart.items.all():
            if item.quantity > item.product.quantity:
                messages.error(
                    request,
                    f'Товара "{item.product.name}" недостаточно на складе. '
                    f'Доступно: {item.product.quantity} шт.'
                )
                return redirect('core:cart')

        order_subtotal = cart.total_price
        order_discount = Decimal('0.00')
        applied_promo_instance = None

        # Check for promo code from session (applied in cart)
        session_promo_code = request.session.get('applied_promo_code')
        session_discount_str = request.session.get('promo_discount_amount')

        if session_promo_code and session_discount_str:
            try:
                promo = Promo.objects.get(code=session_promo_code)
                # Re-validate promo at checkout, especially for usage
                if promo.is_valid(order_subtotal, request.user):
                    potential_discount = promo.calculate_discount(order_subtotal)
                    # Ensure session discount matches calculated discount to prevent tampering
                    if Decimal(session_discount_str) == potential_discount:
                        order_discount = potential_discount
                        applied_promo_instance = promo
                    else:
                        messages.error(request, "Ошибка применения промокода. Пожалуйста, примените его снова в корзине.")
                        # Clear potentially tampered session data
                        if 'applied_promo_code' in request.session: del request.session['applied_promo_code']
                        if 'promo_discount_amount' in request.session: del request.session['promo_discount_amount']
                        return redirect('core:cart') # Send back to cart to re-apply
                else:
                    messages.warning(request, f'Промокод "{promo.code}" больше не действителен или уже использован.')
                    # Clear invalid promo from session
                    if 'applied_promo_code' in request.session: del request.session['applied_promo_code']
                    if 'promo_discount_amount' in request.session: del request.session['promo_discount_amount']

            except Promo.DoesNotExist:
                messages.error(request, 'Промокод не найден.')
                # Clear invalid promo from session
                if 'applied_promo_code' in request.session: del request.session['applied_promo_code']
                if 'promo_discount_amount' in request.session: del request.session['promo_discount_amount']

        order_total = order_subtotal - order_discount # Assuming shipping_cost is 0 for now

        client_timezone_str = request.POST.get('client_timezone') # Get timezone from form

        # Логика для установки Europe/Minsk по умолчанию или принудительной замены
        if not client_timezone_str or client_timezone_str == "Europe/Moscow":
            final_client_timezone_to_save = "Europe/Minsk"
        else:
            final_client_timezone_to_save = client_timezone_str

        order = Order.objects.create(
            customer=request.user,
            shipping_address=request.POST.get('shipping_address', 'Не указан'), # Added defaults
            phone=request.POST.get('phone', 'Не указан'),
            email=request.POST.get('email', request.user.email),
            comment=request.POST.get('comment', ''),
            client_timezone=final_client_timezone_to_save, # Используем обработанное значение
            subtotal=order_subtotal,
            promo=applied_promo_instance,
            discount=order_discount,
            shipping_cost=Decimal('0.00'), # Assuming 0 for now
            total=order_total
        )

        if applied_promo_instance:
            PromoUsage.objects.create(promo=applied_promo_instance, customer=request.user)
            # Clear promo from session after successful order creation and usage logging
            if 'applied_promo_code' in request.session: del request.session['applied_promo_code']
            if 'promo_discount_amount' in request.session: del request.session['promo_discount_amount']

        # Создаем позиции заказа и уменьшаем количество товаров на складе
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price # Use current product price at time of order
            )
            item.product.quantity -= item.quantity
            item.product.save()

        # Очищаем корзину
        cart.items.all().delete()

        messages.success(request, f'Заказ #{order.id} успешно оформлен')
        return redirect('core:order-detail', pk=order.id)

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'core/order_detail.html'
    context_object_name = 'order'
    login_url = 'login'

    def dispatch(self, request, *args, **kwargs):
        order = self.get_object()
        # Проверяем, что заказ принадлежит текущему пользователю
        # или пользователь является администратором/сотрудником
        if not (order.customer == request.user or request.user.is_staff or request.user.is_superuser):
            messages.warning(request, 'У вас нет доступа к этому заказу')
            return redirect('core:product-list')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_items'] = self.object.items.select_related('product').all()
        
        # Добавляем таймзону пользователя для форматирования дат в шаблоне
        user_timezone_str = self.request.session.get('django_timezone', 'Europe/Minsk') # Минск по умолчанию
        context['user_timezone'] = user_timezone_str
            
        return context

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'core/order_list.html'
    context_object_name = 'orders'
    login_url = 'login'
    paginate_by = 10

    def get_queryset(self):
        # Администраторы и сотрудники видят все заказы
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Order.objects.all().order_by('-created_at')
        # Обычные пользователи видят только свои заказы
        return Order.objects.filter(customer=self.request.user).order_by('-created_at')

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def update_order_status(request, pk):
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Статус заказа #{order.id} обновлен')
        else:
            messages.error(request, 'Некорректный статус заказа')
            
    return redirect('core:order-detail', pk=pk)

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

class PromoListView(StaffRequiredMixin, ListView):
    model = Promo
    template_name = 'core/promo_list.html'
    context_object_name = 'promos'
    paginate_by = 10
    login_url = 'login'

    def get_queryset(self):
        queryset = Promo.objects.all().order_by('-created_at')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) |
                Q(description__icontains=search)
            )
        return queryset

class PromoCreateView(StaffRequiredMixin, CreateView):
    model = Promo
    template_name = 'core/promo_form.html'
    fields = ['code', 'description', 'discount_amount', 
              'min_order_amount', 'valid_from', 'valid_until', 'is_active']
    success_url = reverse_lazy('core:promo-list')
    login_url = 'login'

    def form_valid(self, form):
        messages.success(self.request, 'Промокод успешно создан')
        return super().form_valid(form)

class PromoUpdateView(StaffRequiredMixin, UpdateView):
    model = Promo
    template_name = 'core/promo_form.html'
    fields = ['code', 'description', 'discount_amount', 
              'min_order_amount', 'valid_from', 'valid_until', 'is_active']
    success_url = reverse_lazy('core:promo-list')
    login_url = 'login'

    def form_valid(self, form):
        messages.success(self.request, 'Промокод успешно обновлен')
        return super().form_valid(form)

class PromoDeleteView(StaffRequiredMixin, DeleteView):
    model = Promo
    template_name = 'core/promo_confirm_delete.html'
    success_url = reverse_lazy('core:promo-list')
    login_url = 'login'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Промокод успешно удален.')
        return super().delete(request, *args, **kwargs)

def generate_bar_chart(labels, data, title, ylabel):
    """Генерирует столбчатую диаграмму"""
    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    
    # Создаем столбчатую диаграмму
    bars = ax.bar(range(len(data)), data)
    
    # Настраиваем внешний вид
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    
    # Добавляем значения над столбцами
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:,.0f}',
                ha='center', va='bottom')
    
    # Автоматически регулируем размещение подписей
    fig.tight_layout()
    
    # Сохраняем график в байтовый поток
    buf = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buf)
    plt.close(fig)
    
    # Кодируем в base64
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'

def generate_pie_chart(labels, data, title):
    """Генерирует круговую диаграмму"""
    fig = Figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    
    # Создаем круговую диаграмму
    wedges, texts, autotexts = ax.pie(data, labels=labels, autopct='%1.1f%%',
                                     textprops={'fontsize': 8})
    
    # Добавляем заголовок
    ax.set_title(title)
    
    # Делаем диаграмму круглой
    ax.axis('equal')
    
    # Добавляем легенду
    ax.legend(wedges, labels,
             title="Категории",
             loc="center left",
             bbox_to_anchor=(1, 0, 0.5, 1))
    
    # Автоматически регулируем размещение подписей
    fig.tight_layout()
    
    # Сохраняем график в байтовый поток
    buf = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buf)
    plt.close(fig)
    
    # Кодируем в base64
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'

class StatisticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'core/statistics.html'
    login_url = reverse_lazy('accounts:login')

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Статистика'

        # --- Таймзоны и Даты ---
        user_timezone_str = self.request.session.get('user_timezone', 'Europe/Minsk')
        try:
            user_tz = pytz.timezone(user_timezone_str)
        except pytz.UnknownTimeZoneError:
            user_tz = pytz.timezone('Europe/Minsk')
            user_timezone_str = 'Europe/Minsk'
            self.request.session['user_timezone'] = user_timezone_str

        now_utc = timezone.now()
        now_local = now_utc.astimezone(user_tz)

        context['user_timezone'] = str(user_tz)
        context['current_time_utc'] = now_utc
        context['current_time_local'] = now_local

        # --- Топ-3 продаваемых товара ---
        # По количеству
        top_products_qty_query = OrderItem.objects.values(
            'product__id', 'product__name'
        ).annotate(
            total_quantity_sold_agg=Sum('quantity')
        ).filter(total_quantity_sold_agg__gt=0).order_by('-total_quantity_sold_agg')[:3]
        
        top_products_by_quantity = [
            {'id':p['product__id'], 'name':p['product__name'], 'total_quantity_sold':p['total_quantity_sold_agg']}
            for p in top_products_qty_query
        ]
        labels = [p['name'] for p in top_products_by_quantity]
        data = [p['total_quantity_sold'] for p in top_products_by_quantity]
        context['top_products_quantity_chart'] = generate_bar_chart(
            labels, data, 
            'Топ-3 продаваемых товара (по количеству)', 
            'Количество продаж'
        )

        # По сумме выручки
        top_products_rev_query = OrderItem.objects.values(
            'product__id', 'product__name'
        ).annotate(
            total_revenue_generated_agg=Sum(F('price') * F('quantity'))
        ).filter(total_revenue_generated_agg__gt=0).order_by('-total_revenue_generated_agg')[:3]

        top_products_by_revenue = [
            {'id':p['product__id'], 'name':p['product__name'], 'total_revenue_generated':p['total_revenue_generated_agg']}
            for p in top_products_rev_query
        ]
        labels = [p['name'] for p in top_products_by_revenue]
        data = [float(p['total_revenue_generated']) for p in top_products_by_revenue]
        context['top_products_revenue_chart'] = generate_bar_chart(
            labels, data,
            'Топ-3 продаваемых товара (по выручке)',
            'Выручка (руб.)'
        )

        # --- Популярность категорий ---
        category_popularity_query = OrderItem.objects.values(
            'product__category__id', 'product__category__name'
        ).annotate(
            total_sold_quantity_agg=Sum('quantity')
        ).filter(total_sold_quantity_agg__isnull=False).order_by('-total_sold_quantity_agg')

        category_popularity = [
            {'id': item['product__category__id'], 'name': item['product__category__name'], 'total_sold_quantity': item['total_sold_quantity_agg']}
            for item in category_popularity_query
        ]
        labels = [cat['name'] for cat in category_popularity]
        data = [cat['total_sold_quantity'] for cat in category_popularity]
        context['category_popularity_chart'] = generate_pie_chart(
            labels, data,
            'Популярность категорий (кол-во)'
        )

        # --- Прибыльность категорий ---
        category_profitability_query = OrderItem.objects.values(
            'product__category__id', 'product__category__name'
        ).annotate(
            total_revenue_agg=Sum(F('price') * F('quantity'))
        ).filter(total_revenue_agg__isnull=False).order_by('-total_revenue_agg')

        category_profitability = [
            {'id': item['product__category__id'], 'name': item['product__category__name'], 'total_revenue_from_category': item['total_revenue_agg']}
            for item in category_profitability_query
        ]
        labels = [cat['name'] for cat in category_profitability]
        data = [float(cat['total_revenue_from_category']) for cat in category_profitability]
        context['category_profitability_chart'] = generate_pie_chart(
            labels, data,
            'Прибыльность категорий (сумма)'
        )

        # --- Распределение товаров по всем категориям ---
        all_categories_data = Category.objects.annotate(product_count=Count('products')).order_by('-product_count')
        labels = [cat.name for cat in all_categories_data if cat.product_count > 0]
        data = [cat.product_count for cat in all_categories_data if cat.product_count > 0]
        context['all_category_product_chart'] = generate_pie_chart(
            labels, data,
            'Распределение товаров по всем категориям'
        )

        return context

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def update_product_quantity(request, product_id):
    if not request.method == 'POST':
        return redirect('core:product-list')
    
    product = get_object_or_404(Product, id=product_id)
    try:
        new_quantity = int(request.POST.get('quantity', 0))
        if new_quantity < 0:
            raise ValueError("Количество не может быть отрицательным")
        
        product.quantity = new_quantity
        product.save(update_fields=['quantity'])
        messages.success(request, f"Количество товара '{product.name}' успешно обновлено до {new_quantity}.")
    except (ValueError, TypeError) as e:
        messages.error(request, "Ошибка при обновлении количества. Пожалуйста, введите корректное значение.")
    
    return redirect('core:product-list')

class ProductPurchaseView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'core/product_purchase.html'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_context_data(self, product):
        context = {
            'product': product,
            'form': SupplierPurchaseForm(product=product),
            'purchase_history': product.purchase_history.select_related('supplier').order_by('-purchase_date')[:10]
        }
        
        if self.request.user.is_superuser:
            # Для суперпользователя - полная информация о всех поставщиках
            context['suppliers'] = product.suppliers.prefetch_related(
                'supplierproduct_set__product',
                'purchases'
            ).all()
        elif self.request.user.is_staff:
            # Для сотрудника - статистика продаж и поставщики, с которыми он работал
            from django.db.models import Avg
            staff_supplier_ids = product.suppliers.values_list('id', flat=True)
            
            context['staff_suppliers'] = Supplier.objects.filter(id__in=staff_supplier_ids)
            
            sales_stats = Order.objects.aggregate(
                total_sales_count=Count('id'),
                total_revenue=Sum('total'),
                average_sale=Avg('total')
            )
            context['total_sales_count'] = sales_stats['total_sales_count'] or 0
            context['total_revenue'] = sales_stats['total_revenue'] or 0
            context['average_sale'] = sales_stats['average_sale'] or 0
            
        return context
    
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        context = self.get_context_data(product)
        return render(request, self.template_name, context)
    
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        form = SupplierPurchaseForm(product=product, data=request.POST)
        
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.product = product
            purchase.save()
            messages.success(request, f'Закупка товара "{product.name}" успешно оформлена')
            return redirect('core:product-list')
        
        context = self.get_context_data(product)
        context['form'] = form
        return render(request, self.template_name, context)
