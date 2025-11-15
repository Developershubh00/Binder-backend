from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Department, Segment, BuyerCode, VendorCode
from .serializers import (
    DepartmentSerializer, DepartmentListSerializer, DepartmentCreateSerializer,
    SegmentSerializer, SegmentDetailSerializer,
    BuyerCodeSerializer, BuyerCodeCreateSerializer, BuyerCodeListSerializer,
    VendorCodeSerializer, VendorCodeCreateSerializer, VendorCodeListSerializer
)


class DepartmentViewSet(ModelViewSet):
    """
    ViewSet for Department CRUD operations
    """
    permission_classes = [IsAuthenticated]
    queryset = Department.objects.all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return DepartmentListSerializer
        elif self.action == 'create':
            return DepartmentCreateSerializer
        return DepartmentSerializer
    
    def get_queryset(self):
        """Filter departments based on tenant if user is not master admin"""
        queryset = Department.objects.all()
        
        # Filter by tenant if user is not master admin
        user = self.request.user
        if not user.is_master_admin and user.tenant:
            queryset = queryset.filter(
                Q(tenant=user.tenant) | Q(tenant__isnull=True)
            )
        
        # Filter by active status if requested
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.select_related('tenant', 'created_by').prefetch_related('segments')
    
    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def segments(self, request, pk=None):
        """Get all segments for a department"""
        department = self.get_object()
        segments = department.segments.all()
        serializer = SegmentDetailSerializer(segments, many=True)
        return Response({
            'status': 'success',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def add_segment(self, request, pk=None):
        """Add a segment to a department"""
        department = self.get_object()
        serializer = SegmentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(department=department, created_by=request.user)
            return Response({
                'status': 'success',
                'message': 'Segment added successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'status': 'error',
            'message': 'Failed to add segment',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class SegmentViewSet(ModelViewSet):
    """
    ViewSet for Segment CRUD operations
    """
    permission_classes = [IsAuthenticated]
    queryset = Segment.objects.all()
    serializer_class = SegmentSerializer
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve':
            return SegmentDetailSerializer
        return SegmentSerializer
    
    def get_queryset(self):
        """Filter segments based on department and tenant"""
        queryset = Segment.objects.all()
        
        # Filter by department if provided
        department_id = self.request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        # Filter by active status if requested
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by tenant if user is not master admin
        user = self.request.user
        if not user.is_master_admin and user.tenant:
            queryset = queryset.filter(
                Q(department__tenant=user.tenant) | Q(department__tenant__isnull=True)
            )
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.select_related('department', 'department__tenant', 'created_by')
    
    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Create a segment"""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'status': 'success',
                'message': 'Segment created successfully',
                'data': SegmentDetailSerializer(serializer.instance).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'status': 'error',
            'message': 'Failed to create segment',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Update a segment"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                'status': 'success',
                'message': 'Segment updated successfully',
                'data': SegmentDetailSerializer(serializer.instance).data
            })
        
        return Response({
            'status': 'error',
            'message': 'Failed to update segment',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a segment"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'status': 'success',
            'message': 'Segment deleted successfully'
        }, status=status.HTTP_200_OK)


# Additional API views for convenience
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def department_menu_structure(request):
    """
    Get complete department menu structure with segments
    Useful for frontend menu rendering
    """
    departments = Department.objects.filter(is_active=True).prefetch_related(
        'segments'
    ).order_by('display_order', 'name')
    
    menu_data = []
    for dept in departments:
        segments = dept.segments.filter(is_active=True).order_by('display_order', 'name')
        menu_data.append({
            'id': str(dept.id),
            'code': dept.code,
            'label': dept.name,
            'hasSubMenu': segments.exists(),
            'segments': [
                {
                    'id': str(seg.id),
                    'code': seg.code,
                    'label': seg.name
                }
                for seg in segments
            ]
        })
    
    return Response({
        'status': 'success',
        'data': menu_data
    })


class BuyerCodeViewSet(ModelViewSet):
    """
    ViewSet for BuyerCode CRUD operations
    Handles buyer code generation with auto-incrementing codes (101A, 102A, etc.)
    """
    permission_classes = [IsAuthenticated]
    queryset = BuyerCode.objects.all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return BuyerCodeListSerializer
        elif self.action == 'create':
            return BuyerCodeCreateSerializer
        return BuyerCodeSerializer
    
    def get_queryset(self):
        """Filter buyer codes based on tenant if user is not master admin"""
        queryset = BuyerCode.objects.all()
        
        # Filter by tenant if user is not master admin
        user = self.request.user
        if not user.is_master_admin and user.tenant:
            queryset = queryset.filter(tenant=user.tenant)
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(buyer_name__icontains=search) |
                Q(code__icontains=search) |
                Q(retailer__icontains=search) |
                Q(contact_person__icontains=search)
            )
        
        return queryset.select_related('tenant', 'created_by')
    
    def create(self, request, *args, **kwargs):
        """Create a new buyer code with auto-generated code"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create buyer code (code will be auto-generated)
        buyer_code = serializer.save()
        
        return Response({
            'status': 'success',
            'message': 'Buyer code generated successfully',
            'data': BuyerCodeSerializer(buyer_code).data
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update a buyer code (code cannot be changed)"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Remove code from request data if present (code is read-only)
        request_data = request.data.copy()
        if 'code' in request_data:
            request_data.pop('code')
        
        serializer = self.get_serializer(instance, data=request_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'status': 'success',
            'message': 'Buyer code updated successfully',
            'data': BuyerCodeSerializer(serializer.instance).data
        })
    
    def destroy(self, request, *args, **kwargs):
        """Delete a buyer code"""
        instance = self.get_object()
        code = instance.code
        self.perform_destroy(instance)
        
        return Response({
            'status': 'success',
            'message': f'Buyer code {code} deleted successfully'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def generate(self, request):
        """
        Preview the next buyer code that would be generated
        Useful for frontend to show what code will be generated
        """
        user = request.user
        tenant = user.tenant if user and not user.is_master_admin else None
        
        next_code = BuyerCode.generate_next_code(tenant=tenant)
        
        return Response({
            'status': 'success',
            'data': {
                'next_code': next_code
            }
        })
    
    @action(detail=False, methods=['get'], url_path='master-sheet')
    def master_sheet(self, request):
        """
        Get all buyer codes in master sheet format
        Returns all buyer codes formatted for frontend master sheet display
        """
        queryset = self.get_queryset()
        
        # Format data for frontend
        buyer_codes = []
        for buyer in queryset:
            buyer_codes.append({
                'code': buyer.code,
                'buyerName': buyer.buyer_name,
                'buyerAddress': buyer.buyer_address,
                'contactPerson': buyer.contact_person,
                'retailer': buyer.retailer,
                'createdAt': buyer.created_at.isoformat() if buyer.created_at else None
            })
        
        return Response({
            'status': 'success',
            'data': buyer_codes,
            'count': len(buyer_codes)
        })


class VendorCodeViewSet(ModelViewSet):
    """
    ViewSet for VendorCode CRUD operations
    Handles vendor code generation with auto-incrementing numeric codes (101, 102, etc.)
    """
    permission_classes = [IsAuthenticated]
    queryset = VendorCode.objects.all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return VendorCodeListSerializer
        elif self.action == 'create':
            return VendorCodeCreateSerializer
        return VendorCodeSerializer
    
    def get_queryset(self):
        """Filter vendor codes based on tenant if user is not master admin"""
        queryset = VendorCode.objects.all()
        
        # Filter by tenant if user is not master admin
        user = self.request.user
        if not user.is_master_admin and user.tenant:
            queryset = queryset.filter(tenant=user.tenant)
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(vendor_name__icontains=search) |
                Q(code__icontains=search) |
                Q(gst__icontains=search) |
                Q(contact_person__icontains=search) |
                Q(email__icontains=search) |
                Q(job_work_category__icontains=search)
            )
        
        return queryset.select_related('tenant', 'created_by')
    
    def create(self, request, *args, **kwargs):
        """Create a new vendor code with auto-generated code"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create vendor code (code will be auto-generated)
        vendor_code = serializer.save()
        
        return Response({
            'status': 'success',
            'message': 'Vendor code generated successfully',
            'data': VendorCodeSerializer(vendor_code).data
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update a vendor code (code cannot be changed)"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Remove code from request data if present (code is read-only)
        request_data = request.data.copy()
        if 'code' in request_data:
            request_data.pop('code')
        
        serializer = self.get_serializer(instance, data=request_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'status': 'success',
            'message': 'Vendor code updated successfully',
            'data': VendorCodeSerializer(serializer.instance).data
        })
    
    def destroy(self, request, *args, **kwargs):
        """Delete a vendor code"""
        instance = self.get_object()
        code = instance.code
        self.perform_destroy(instance)
        
        return Response({
            'status': 'success',
            'message': f'Vendor code {code} deleted successfully'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def generate(self, request):
        """
        Preview the next vendor code that would be generated
        Useful for frontend to show what code will be generated
        """
        user = request.user
        tenant = user.tenant if user and not user.is_master_admin else None
        
        next_code = VendorCode.generate_next_code(tenant=tenant)
        
        return Response({
            'status': 'success',
            'data': {
                'next_code': next_code
            }
        })
    
    @action(detail=False, methods=['get'], url_path='master-sheet')
    def master_sheet(self, request):
        """
        Get all vendor codes in master sheet format
        Returns all vendor codes formatted for frontend master sheet display
        """
        queryset = self.get_queryset()
        
        # Format data for frontend
        vendor_codes = []
        for vendor in queryset:
            vendor_codes.append({
                'code': vendor.code,
                'vendorName': vendor.vendor_name,
                'address': vendor.address,
                'gst': vendor.gst,
                'bankName': vendor.bank_name,
                'accNo': vendor.account_number,
                'ifscCode': vendor.ifsc_code,
                'jobWorkCategory': vendor.job_work_category,
                'jobWorkSubCategory': vendor.job_work_sub_category,
                'contactPerson': vendor.contact_person,
                'whatsappNo': vendor.whatsapp_number,
                'altWhatsappNo': vendor.alt_whatsapp_number or '',
                'email': vendor.email,
                'paymentTerms': vendor.payment_terms,
                'createdAt': vendor.created_at.isoformat() if vendor.created_at else None
            })
        
        return Response({
            'status': 'success',
            'data': vendor_codes,
            'count': len(vendor_codes)
        })
