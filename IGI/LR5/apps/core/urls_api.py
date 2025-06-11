from rest_framework.routers import DefaultRouter
from .views_api import (
    CategoryViewSet, SupplierViewSet,
    ProductViewSet, SaleViewSet, CartViewSet,
    OrderViewSet, PromoViewSet
)

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('suppliers', SupplierViewSet)
router.register('products', ProductViewSet)
router.register('sales', SaleViewSet)
router.register('carts', CartViewSet, basename='cart')
router.register('orders', OrderViewSet, basename='order')
router.register('promos', PromoViewSet, basename='promo')

urlpatterns = router.urls 