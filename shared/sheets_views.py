from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .google_sheets import sheets_service
from datetime import datetime

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_buyers(request):
    """Get all buyers from Google Sheets"""
    try:
        records = sheets_service.get_buyers(settings.GOOGLE_SHEETS_SPREADSHEET_ID)
        return Response({
            'status': 'success',
            'data': records
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_buyer(request):
    """Add buyer to Google Sheets"""
    try:
        data = request.data
        data['created_at'] = datetime.now().isoformat()
        
        success = sheets_service.add_buyer(
            settings.GOOGLE_SHEETS_SPREADSHEET_ID,
            data
        )
        
        if success:
            return Response({
                'status': 'success',
                'message': 'Buyer added successfully',
                'data': data
            })
        else:
            return Response({
                'status': 'error',
                'message': 'Failed to add buyer'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_vendors(request):
    """Get all vendors from Google Sheets"""
    try:
        records = sheets_service.get_vendors(settings.GOOGLE_SHEETS_SPREADSHEET_ID)
        return Response({
            'status': 'success',
            'data': records
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_vendor(request):
    """Add vendor to Google Sheets"""
    try:
        data = request.data
        data['created_at'] = datetime.now().isoformat()
        
        success = sheets_service.add_vendor(
            settings.GOOGLE_SHEETS_SPREADSHEET_ID,
            data
        )
        
        if success:
            return Response({
                'status': 'success',
                'message': 'Vendor added successfully',
                'data': data
            })
        else:
            return Response({
                'status': 'error',
                'message': 'Failed to add vendor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_factories(request):
    """Get all factories from Google Sheets"""
    try:
        records = sheets_service.get_factories(settings.GOOGLE_SHEETS_SPREADSHEET_ID)
        return Response({
            'status': 'success',
            'data': records
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_factory(request):
    """Add factory to Google Sheets"""
    try:
        data = request.data
        data['created_at'] = datetime.now().isoformat()
        
        success = sheets_service.add_factory(
            settings.GOOGLE_SHEETS_SPREADSHEET_ID,
            data
        )
        
        if success:
            return Response({
                'status': 'success',
                'message': 'Factory added successfully',
                'data': data
            })
        else:
            return Response({
                'status': 'error',
                'message': 'Failed to add factory'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_master_sheet(request):
    """Get master sheet data (tenant-only access)"""
    user = request.user
    
    # Check if user is tenant owner
    if user.role not in ['tenant_owner', 'master_admin']:
        return Response({
            'status': 'error',
            'message': 'Access denied. Only tenant owners can view master sheet.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        records = sheets_service.get_master_sheet(
            settings.GOOGLE_SHEETS_SPREADSHEET_ID
        )
        return Response({
            'status': 'success',
            'data': records
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)