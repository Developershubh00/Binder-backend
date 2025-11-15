from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, SegmentViewSet, department_menu_structure,
    BuyerCodeViewSet, VendorCodeViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'segments', SegmentViewSet, basename='segment')
router.register(r'buyer-codes', BuyerCodeViewSet, basename='buyer-code')
router.register(r'vendor-codes', VendorCodeViewSet, basename='vendor-code')

urlpatterns = [
    # Router URLs for ViewSets
    path('', include(router.urls)),
    
    # Additional endpoints
    path('menu-structure/', department_menu_structure, name='department-menu-structure'),
]
