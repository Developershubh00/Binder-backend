#!/usr/bin/env python3
"""
Automated Unfold Admin Migration Script
This script migrates an existing Django project to use Unfold Admin UI
"""

import os
import re
import sys
from pathlib import Path


class UnfoldMigrator:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.changes_made = []
        self.warnings = []
        
    def find_settings_file(self):
        """Find settings.py file in the project"""
        possible_locations = [
            self.project_root / "settings.py",
            self.project_root / "config" / "settings.py",
        ]
        
        # Search for settings.py in common Django project structures
        for root, dirs, files in os.walk(self.project_root):
            if "settings.py" in files:
                return Path(root) / "settings.py"
        
        return None
    
    def backup_file(self, filepath):
        """Create a backup of the file before modifying"""
        backup_path = Path(str(filepath) + ".backup")
        if filepath.exists():
            with open(filepath, 'r') as f:
                content = f.read()
            with open(backup_path, 'w') as f:
                f.write(content)
            return backup_path
        return None
    
    def update_settings_installed_apps(self, settings_path):
        """Update INSTALLED_APPS in settings.py"""
        with open(settings_path, 'r') as f:
            content = f.read()
        
        # Check if unfold is already added
        if '"unfold"' in content or "'unfold'" in content:
            self.warnings.append("⚠️  Unfold already in INSTALLED_APPS")
            return False
        
        # Find INSTALLED_APPS and add unfold before django.contrib.admin
        pattern = r'(INSTALLED_APPS\s*=\s*\[)\s*'
        
        unfold_apps = '''    # Unfold Admin - Must be before django.contrib.admin
    "unfold",
    "unfold.contrib.filters",  # optional, for advanced filters
    "unfold.contrib.forms",  # optional, for better forms
    "unfold.contrib.import_export",  # optional, for import/export
    '''
        
        replacement = r'\1\n' + unfold_apps + '\n    '
        new_content = re.sub(pattern, replacement, content)
        
        if new_content != content:
            with open(settings_path, 'w') as f:
                f.write(new_content)
            self.changes_made.append(f"✅ Updated INSTALLED_APPS in {settings_path}")
            return True
        
        return False
    
    def add_unfold_settings(self, settings_path):
        """Add UNFOLD configuration to settings.py"""
        with open(settings_path, 'r') as f:
            content = f.read()
        
        # Check if UNFOLD settings already exist
        if 'UNFOLD = {' in content:
            self.warnings.append("⚠️  UNFOLD settings already exist")
            return False
        
        unfold_config = '''

# Unfold Admin Configuration
UNFOLD = {
    "SITE_TITLE": "Binder ERP Admin",
    "SITE_HEADER": "Binder ERP",
    "SITE_URL": "/",
    # "SITE_ICON": {
    #     "light": lambda request: static("icon-light.svg"),
    #     "dark": lambda request: static("icon-dark.svg"),
    # },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Navigation",
                "separator": True,
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": lambda request: "/admin/",
                    },
                ],
            },
        ],
    },
    "TABS": [
        {
            "models": [
                "auth.user",
                "auth.group",
            ],
            "items": [
                {
                    "title": "Users",
                    "link": lambda request: "/admin/auth/user/",
                },
                {
                    "title": "Groups",
                    "link": lambda request: "/admin/auth/group/",
                },
            ],
        },
    ],
}
'''
        
        with open(settings_path, 'a') as f:
            f.write(unfold_config)
        
        self.changes_made.append(f"✅ Added UNFOLD configuration to {settings_path}")
        return True
    
    def ensure_request_context_processor(self, settings_path):
        """Ensure request context processor is in TEMPLATES"""
        with open(settings_path, 'r') as f:
            content = f.read()
        
        if '"django.template.context_processors.request"' in content or \
           "'django.template.context_processors.request'" in content:
            return False
        
        # Try to add it to context_processors
        pattern = r'("context_processors"\s*:\s*\[)'
        replacement = r'\1\n                "django.template.context_processors.request",  # Required by Unfold'
        new_content = re.sub(pattern, replacement, content)
        
        if new_content != content:
            with open(settings_path, 'w') as f:
                f.write(new_content)
            self.changes_made.append(f"✅ Added request context processor to TEMPLATES")
            return True
        
        self.warnings.append("⚠️  Could not automatically add request context processor. Please add manually.")
        return False
    
    def find_admin_files(self):
        """Find all admin.py files in the project"""
        admin_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Skip virtual environments and common non-app directories
            if any(skip in root for skip in ['venv', 'env', 'node_modules', '.git', 'migrations']):
                continue
            if "admin.py" in files:
                admin_files.append(Path(root) / "admin.py")
        return admin_files
    
    def update_admin_file(self, admin_path):
        """Update a single admin.py file to use Unfold"""
        with open(admin_path, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Check if already using unfold
        if 'from unfold.admin import ModelAdmin' in content:
            return False
        
        # Import replacement patterns
        replacements = [
            # Replace django.contrib admin imports with unfold
            (r'from django\.contrib import admin\n',
             'from django.contrib import admin\nfrom unfold.admin import ModelAdmin\n'),
            
            # Replace admin.ModelAdmin with ModelAdmin
            (r'\badmin\.ModelAdmin\b', 'ModelAdmin'),
            
            # Replace admin.TabularInline with TabularInline
            (r'from django\.contrib import admin(?!\n.*from unfold)',
             'from django.contrib import admin\nfrom unfold.admin import ModelAdmin, TabularInline, StackedInline'),
            (r'\badmin\.TabularInline\b', 'TabularInline'),
            (r'\badmin\.StackedInline\b', 'StackedInline'),
        ]
        
        # Apply replacements
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        # If content changed, write it back
        if content != original_content:
            with open(admin_path, 'w') as f:
                f.write(content)
            self.changes_made.append(f"✅ Updated {admin_path}")
            return True
        
        return False
    
    def create_requirements_update(self):
        """Create a requirements file addition"""
        requirements_addition = """
# Unfold Admin UI
django-unfold>=0.30.0
"""
        
        req_file = self.project_root / "unfold_requirements.txt"
        with open(req_file, 'w') as f:
            f.write(requirements_addition.strip())
        
        self.changes_made.append(f"✅ Created {req_file} - Add this to your requirements.txt")
        return req_file
    
    def run_migration(self):
        """Run the complete migration process"""
        print("🚀 Starting Unfold Admin Migration...\n")
        
        # Find settings.py
        settings_path = self.find_settings_file()
        if not settings_path:
            print("❌ Could not find settings.py file")
            return False
        
        print(f"📁 Found settings.py at: {settings_path}\n")
        
        # Backup settings
        backup = self.backup_file(settings_path)
        if backup:
            print(f"💾 Created backup: {backup}\n")
        
        # Update settings.py
        self.update_settings_installed_apps(settings_path)
        self.ensure_request_context_processor(settings_path)
        self.add_unfold_settings(settings_path)
        
        # Find and update admin files
        print("\n🔍 Finding admin.py files...")
        admin_files = self.find_admin_files()
        print(f"Found {len(admin_files)} admin.py file(s)\n")
        
        for admin_file in admin_files:
            backup = self.backup_file(admin_file)
            if backup:
                print(f"💾 Backed up: {admin_file}")
            self.update_admin_file(admin_file)
        
        # Create requirements update
        self.create_requirements_update()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 MIGRATION SUMMARY")
        print("="*60)
        
        if self.changes_made:
            print("\n✅ Changes Made:")
            for change in self.changes_made:
                print(f"  {change}")
        
        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  {warning}")
        
        print("\n" + "="*60)
        print("📝 NEXT STEPS:")
        print("="*60)
        print("1. Install unfold: pip install django-unfold")
        print("2. Run migrations: python manage.py migrate")
        print("3. Collect static files: python manage.py collectstatic")
        print("4. Restart your Django server")
        print("5. Visit /admin/ to see the new Unfold UI")
        print("\n💡 All original files have been backed up with .backup extension")
        print("="*60)
        
        return True


def main():
    # Get project root from command line or use current directory
    project_root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    
    migrator = UnfoldMigrator(project_root)
    success = migrator.run_migration()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
