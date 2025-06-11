from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product-list'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('product/<int:product_id>/purchase/', views.ProductPurchaseView.as_view(), name='product-purchase'),
    path('suppliers/', views.SupplierListView.as_view(), name='supplier-list'),
    path('sales/', views.SaleListView.as_view(), name='sales-list'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add-to-cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update-cart-item'),
    path('cart/apply-promo/', views.apply_promo, name='apply-promo'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('order/<int:pk>/update-status/', views.update_order_status, name='update-order-status'),
    path('product/<int:product_id>/update-quantity/', views.update_product_quantity, name='update-product-quantity'),
    # Управление промокодами
    path('promos/', views.PromoListView.as_view(), name='promo-list'),
    path('promos/create/', views.PromoCreateView.as_view(), name='promo-create'),
    path('promos/<int:pk>/update/', views.PromoUpdateView.as_view(), name='promo-update'),
    path('promos/<int:pk>/delete/', views.PromoDeleteView.as_view(), name='promo-delete'),
    # Статистика
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
]
