# import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.conf import settings
import os

class GoogleSheetsService:
    """Service for Google Sheets integration"""
    
    def __init__(self):
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        self.credentials = None
        self.client = None
        self.initialize()
    
    def initialize(self):
        """Initialize Google Sheets client"""
        try:
            # Skip if credentials file doesn't exist
            if not os.path.exists(settings.GOOGLE_SHEETS_CREDENTIALS_FILE):
                print("Google Sheets: credentials.json not found, skipping")
                return
                
            self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
                settings.GOOGLE_SHEETS_CREDENTIALS_FILE,
                self.scope
            )
            self.client = gspread.authorize(self.credentials)
        except Exception as e:
            print(f"Error initializing Google Sheets: {e}")
    
    def get_sheet(self, spreadsheet_id, sheet_name='Sheet1'):
        """Get worksheet"""
        try:
            if not self.client:
                raise Exception("Google Sheets client not initialized")
                
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            return worksheet
        except Exception as e:
            print(f"Error getting sheet: {e}")
            return None
    
    def get_all_records(self, spreadsheet_id, sheet_name='Sheet1'):
        """Get all records from sheet"""
        worksheet = self.get_sheet(spreadsheet_id, sheet_name)
        if worksheet:
            return worksheet.get_all_records()
        return []
    
    def append_row(self, spreadsheet_id, values, sheet_name='Sheet1'):
        """Append row to sheet"""
        worksheet = self.get_sheet(spreadsheet_id, sheet_name)
        if worksheet:
            worksheet.append_row(values)
            return True
        return False
    
    def update_cell(self, spreadsheet_id, row, col, value, sheet_name='Sheet1'):
        """Update specific cell"""
        worksheet = self.get_sheet(spreadsheet_id, sheet_name)
        if worksheet:
            worksheet.update_cell(row, col, value)
            return True
        return False
    
    def get_buyers(self, spreadsheet_id):
        """Get all buyers from Buyers sheet"""
        return self.get_all_records(spreadsheet_id, 'Buyers')
    
    def add_buyer(self, spreadsheet_id, buyer_data):
        """Add buyer to Buyers sheet"""
        values = [
            buyer_data.get('code', ''),
            buyer_data.get('buyer_name', ''),
            buyer_data.get('buyer_address', ''),
            buyer_data.get('contact_person', ''),
            buyer_data.get('retailer', ''),
            buyer_data.get('created_at', '')
        ]
        return self.append_row(spreadsheet_id, values, 'Buyers')
    
    def get_vendors(self, spreadsheet_id):
        """Get all vendors from Vendors sheet"""
        return self.get_all_records(spreadsheet_id, 'Vendors')
    
    def add_vendor(self, spreadsheet_id, vendor_data):
        """Add vendor to Vendors sheet"""
        values = [
            vendor_data.get('code', ''),
            vendor_data.get('vendor_name', ''),
            vendor_data.get('address', ''),
            vendor_data.get('gst', ''),
            vendor_data.get('bank_name', ''),
            vendor_data.get('account_no', ''),
            vendor_data.get('ifsc_code', ''),
            vendor_data.get('job_work_category', ''),
            vendor_data.get('job_work_sub_category', ''),
            vendor_data.get('contact_person', ''),
            vendor_data.get('whatsapp_no', ''),
            vendor_data.get('email', ''),
            vendor_data.get('payment_terms', ''),
            vendor_data.get('created_at', '')
        ]
        return self.append_row(spreadsheet_id, values, 'Vendors')
    
    def get_factories(self, spreadsheet_id):
        """Get all factories from Factories sheet"""
        return self.get_all_records(spreadsheet_id, 'Factories')
    
    def add_factory(self, spreadsheet_id, factory_data):
        """Add factory to Factories sheet"""
        values = [
            factory_data.get('code', ''),
            factory_data.get('factory_name', ''),
            factory_data.get('address', ''),
            factory_data.get('contact_person', ''),
            factory_data.get('phone', ''),
            factory_data.get('email', ''),
            factory_data.get('capacity', ''),
            factory_data.get('specialization', ''),
            factory_data.get('created_at', '')
        ]
        return self.append_row(spreadsheet_id, values, 'Factories')
    
    def get_master_sheet(self, spreadsheet_id):
        """Get all data from Master Sheet (tenant-only)"""
        return self.get_all_records(spreadsheet_id, 'MasterSheet')

# Singleton instance
sheets_service = GoogleSheetsService()