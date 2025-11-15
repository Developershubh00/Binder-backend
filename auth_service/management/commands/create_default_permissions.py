"""
Management command to create default permissions for Master Sheets, IMS, and Sourcing
Run: python manage.py create_default_permissions
"""
from django.core.management.base import BaseCommand
from auth_service.models import Permission


class Command(BaseCommand):
    help = 'Create default permissions for Master Sheets, IMS, and Sourcing'

    def handle(self, *args, **options):
        # Define default permissions
        default_permissions = [
            # Master Sheets Permissions
            {'category': 'master_sheets', 'action': 'view', 'resource': 'buyer_master', 'description': 'View Buyer Master Sheet'},
            {'category': 'master_sheets', 'action': 'create', 'resource': 'buyer_master', 'description': 'Create Buyer Codes'},
            {'category': 'master_sheets', 'action': 'edit', 'resource': 'buyer_master', 'description': 'Edit Buyer Master Sheet'},
            {'category': 'master_sheets', 'action': 'delete', 'resource': 'buyer_master', 'description': 'Delete Buyer Codes'},
            {'category': 'master_sheets', 'action': 'export', 'resource': 'buyer_master', 'description': 'Export Buyer Master Sheet'},
            
            {'category': 'master_sheets', 'action': 'view', 'resource': 'vendor_master', 'description': 'View Vendor Master Sheet'},
            {'category': 'master_sheets', 'action': 'create', 'resource': 'vendor_master', 'description': 'Create Vendor Codes'},
            {'category': 'master_sheets', 'action': 'edit', 'resource': 'vendor_master', 'description': 'Edit Vendor Master Sheet'},
            {'category': 'master_sheets', 'action': 'delete', 'resource': 'vendor_master', 'description': 'Delete Vendor Codes'},
            {'category': 'master_sheets', 'action': 'export', 'resource': 'vendor_master', 'description': 'Export Vendor Master Sheet'},
            
            # IMS (Inventory Management System) Permissions
            {'category': 'ims', 'action': 'view', 'resource': 'departments', 'description': 'View Departments'},
            {'category': 'ims', 'action': 'create', 'resource': 'departments', 'description': 'Create Departments'},
            {'category': 'ims', 'action': 'edit', 'resource': 'departments', 'description': 'Edit Departments'},
            {'category': 'ims', 'action': 'delete', 'resource': 'departments', 'description': 'Delete Departments'},
            
            {'category': 'ims', 'action': 'view', 'resource': 'segments', 'description': 'View Segments'},
            {'category': 'ims', 'action': 'create', 'resource': 'segments', 'description': 'Create Segments'},
            {'category': 'ims', 'action': 'edit', 'resource': 'segments', 'description': 'Edit Segments'},
            {'category': 'ims', 'action': 'delete', 'resource': 'segments', 'description': 'Delete Segments'},
            
            {'category': 'ims', 'action': 'view', 'resource': 'buyer_codes', 'description': 'View Buyer Codes'},
            {'category': 'ims', 'action': 'create', 'resource': 'buyer_codes', 'description': 'Create Buyer Codes'},
            {'category': 'ims', 'action': 'edit', 'resource': 'buyer_codes', 'description': 'Edit Buyer Codes'},
            {'category': 'ims', 'action': 'delete', 'resource': 'buyer_codes', 'description': 'Delete Buyer Codes'},
            
            {'category': 'ims', 'action': 'view', 'resource': 'vendor_codes', 'description': 'View Vendor Codes'},
            {'category': 'ims', 'action': 'create', 'resource': 'vendor_codes', 'description': 'Create Vendor Codes'},
            {'category': 'ims', 'action': 'edit', 'resource': 'vendor_codes', 'description': 'Edit Vendor Codes'},
            {'category': 'ims', 'action': 'delete', 'resource': 'vendor_codes', 'description': 'Delete Vendor Codes'},
            
            # Sourcing Permissions
            {'category': 'sourcing', 'action': 'view', 'resource': 'yarn', 'description': 'View Yarn Sourcing'},
            {'category': 'sourcing', 'action': 'create', 'resource': 'yarn', 'description': 'Create Yarn Sourcing'},
            {'category': 'sourcing', 'action': 'edit', 'resource': 'yarn', 'description': 'Edit Yarn Sourcing'},
            {'category': 'sourcing', 'action': 'delete', 'resource': 'yarn', 'description': 'Delete Yarn Sourcing'},
            
            {'category': 'sourcing', 'action': 'view', 'resource': 'fabric', 'description': 'View Fabric Sourcing'},
            {'category': 'sourcing', 'action': 'create', 'resource': 'fabric', 'description': 'Create Fabric Sourcing'},
            {'category': 'sourcing', 'action': 'edit', 'resource': 'fabric', 'description': 'Edit Fabric Sourcing'},
            {'category': 'sourcing', 'action': 'delete', 'resource': 'fabric', 'description': 'Delete Fabric Sourcing'},
            
            {'category': 'sourcing', 'action': 'view', 'resource': 'dye', 'description': 'View Dye Sourcing'},
            {'category': 'sourcing', 'action': 'create', 'resource': 'dye', 'description': 'Create Dye Sourcing'},
            {'category': 'sourcing', 'action': 'edit', 'resource': 'dye', 'description': 'Edit Dye Sourcing'},
            {'category': 'sourcing', 'action': 'delete', 'resource': 'dye', 'description': 'Delete Dye Sourcing'},
            
            # Add more sourcing resources as needed
        ]
        
        created_count = 0
        skipped_count = 0
        
        for perm_data in default_permissions:
            permission, created = Permission.objects.get_or_create(
                category=perm_data['category'],
                action=perm_data['action'],
                resource=perm_data['resource'],
                defaults={'description': perm_data['description']}
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created permission: {permission}')
                )
            else:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Skipped (already exists): {permission}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Created {created_count} permissions, skipped {skipped_count} existing permissions.'
            )
        )

