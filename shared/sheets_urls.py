from django.urls import path
from . import sheets_views

urlpatterns = [
    # Buyers
    path('buyers/', sheets_views.list_buyers, name='list-buyers'),
    path('buyers/add/', sheets_views.add_buyer, name='add-buyer'),
    
    # Vendors
    path('vendors/', sheets_views.list_vendors, name='list-vendors'),
    path('vendors/add/', sheets_views.add_vendor, name='add-vendor'),
    
    # Factories
    path('factories/', sheets_views.list_factories, name='list-factories'),
    path('factories/add/', sheets_views.add_factory, name='add-factory'),
    
    # Master Sheet (Tenant-only)
    path('master/', sheets_views.get_master_sheet, name='get-master-sheet'),
    
    # Legacy endpoints
    path('departments/', sheets_views.list_buyers, name='list-departments'),
    path('departments/add/', sheets_views.add_buyer, name='add-department'),
    path('accessories/', sheets_views.list_vendors, name='list-accessories'),
    path('accessories/add/', sheets_views.add_vendor, name='add-accessory'),
]