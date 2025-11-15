# Binder ERP - Complete API Documentation

## Base URL
```
Development: http://localhost:8000/api/
Production (Render): https://your-backend.onrender.com/api/
Domain: https://erpbinder.com/api/ (when configured)
```

### Deployment
- **Backend**: Deployed on Render
- **Frontend**: Deployed on Vercel at https://binder-frontend-self.vercel.app/
- **Domain**: erpbinder.com
- **Production API URL**: Update `VITE_API_URL` in Vercel environment variables to point to your Render backend URL

## Authentication
All authenticated endpoints require JWT Bearer token:
```
Authorization: Bearer <your_access_token>
```

---

## 📡 API Endpoints

### 1. Authentication Endpoints

#### Register User
```http
POST /api/auth/register/
Content-Type: application/json

Request Body:
{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+91 9876543210"
}

Response (201 Created):
{
    "status": "success",
    "message": "Registration successful. Your account is ready to use.",
    "data": {
        "email": "user@example.com",
        "id": "uuid-here",
        "email_verified": true
    }
}
```

#### Verify Email
```http
POST /api/auth/verify-email/
Content-Type: application/json

Request Body:
{
    "token": "verification-token-from-email"
}

Response (200 OK):
{
    "status": "success",
    "message": "Email verified successfully. You can now login."
}
```

#### Resend Verification Email
```http
POST /api/auth/resend-verification/
Content-Type: application/json

Request Body:
{
    "email": "user@example.com"
}

Response (200 OK):
{
    "status": "success",
    "message": "Verification email sent successfully"
}
```

#### Login (Direct)
```http
POST /api/auth/login/
Content-Type: application/json

Request Body:
{
    "email": "user@example.com",
    "password": "SecurePass123!"
}

Response (200 OK):
{
    "status": "success",
    "message": "Login successful",
    "data": {
        "user": {
            "id": "uuid",
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "full_name": "John Doe",
            "role": "tenant_owner",
            "custom_role_name": null,
            "designation": "CEO",
            "tenant": "tenant-uuid",
            "tenant_details": {
                "id": "tenant-uuid",
                "company_name": "ABC Textiles",
                "logo": "https://your-backend.onrender.com/media/tenant_logos/logo.png"
            },
            "is_active": true,
            "email_verified": true,
            "permissions": []
        },
        "tokens": {
            "refresh": "refresh_token_here",
            "access": "access_token_here"
        }
    }
}
```

#### Request OTP (Step 1 of Login)
```http
POST /api/auth/login/request-otp/
Content-Type: application/json

Request Body:
{
    "email": "user@example.com",
    "password": "SecurePass123!"
}

Response (200 OK):
{
    "status": "success",
    "message": "OTP sent successfully"
}
```

#### Verify OTP (Step 2 of Login)
```http
POST /api/auth/login/verify-otp/
Content-Type: application/json

Request Body:
{
    "email": "user@example.com",
    "otp": "123456"
}

Response (200 OK):
{
    "status": "success",
    "message": "Login successful",
    "data": {
        "user": {...},
        "tokens": {
            "refresh": "refresh_token_here",
            "access": "access_token_here"
        }
    }
}
```

#### Refresh Token
```http
POST /api/auth/token/refresh/
Content-Type: application/json

Request Body:
{
    "refresh": "your_refresh_token"
}

Response (200 OK):
{
    "access": "new_access_token"
}
```

#### Logout
```http
POST /api/auth/logout/
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body:
{
    "refresh": "your_refresh_token"
}

Response (200 OK):
{
    "status": "success",
    "message": "Logged out successfully"
}
```

#### Get Current User
```http
GET /api/auth/me/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "role": "tenant_owner",
    "custom_role_name": null,
    "designation": "CEO",
    "tenant": "tenant-uuid",
    "tenant_details": {
        "id": "tenant-uuid",
        "company_name": "ABC Textiles",
        "logo": "https://your-backend.onrender.com/media/tenant_logos/logo.png"
    },
    "is_active": true,
    "email_verified": true,
    "permissions": [
        {
            "id": "permission-uuid",
            "permission_id": "role-permission-uuid",
            "category": "master_sheets",
            "action": "view",
            "resource": "buyer_master",
            "description": "View Buyer Master Sheet",
            "is_enabled": true
        }
    ],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Set Password
```http
POST /api/auth/set-password/
Content-Type: application/json

Request Body:
{
    "token": "invitation_token_here",
    "password": "newpassword123",
    "password_confirm": "newpassword123"
}

Response (200 OK):
{
    "status": "success",
    "message": "Password set successfully"
}
```

---

### 2. Member Management (Tenant Owners Only)

#### List Members
```http
GET /api/auth/members/
Authorization: Bearer <access_token>

Query Parameters:
- page: Page number (default: 1)
- page_size: Items per page (default: 50)
- search: Search by email, name

Response (200 OK):
{
    "count": 10,
    "next": "http://api/auth/members/?page=2",
    "previous": null,
    "results": [
        {
            "id": "uuid",
            "email": "member@company.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "full_name": "Jane Smith",
            "role": "supervisor",
            "custom_role_name": null,
            "designation": "Operations Supervisor",
            "is_active": true,
            "permissions": [...]
        }
    ]
}
```

#### Create Member
```http
POST /api/auth/members/
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body:
{
    "email": "newmember@company.com",
    "password": "SecurePass123!",
    "first_name": "New",
    "last_name": "Member",
    "phone": "+91 9876543210",
    "role": "supervisor",
    "custom_role_name": null,
    "designation": "Department Supervisor",
    "permissions": [
        "permission-uuid-1",
        "permission-uuid-2"
    ]
}

Response (201 Created):
{
    "status": "success",
    "message": "Member created successfully",
    "data": {
        "id": "uuid",
        "email": "newmember@company.com",
        "role": "supervisor",
        "permissions": [...],
        ...
    }
}

Error Response (400 Bad Request):
{
    "status": "error",
    "message": "User limit reached. Your plan allows 40 users."
}
```

#### Get Member Details
```http
GET /api/auth/members/{member_id}/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "id": "uuid",
    "email": "member@company.com",
    "full_name": "Jane Smith",
    "role": "supervisor",
    "custom_role_name": null,
    "permissions": [...]
}
```

#### Update Member
```http
PATCH /api/auth/members/{member_id}/
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body:
{
    "first_name": "Updated",
    "role": "accountant",
    "custom_role_name": "Custom Role Name",  // Required if role="custom"
    "is_active": true
}

Response (200 OK):
{
    "status": "success",
    "message": "Member updated successfully",
    "data": {
        "id": "uuid",
        "email": "member@company.com",
        ...updated fields
    }
}
```

#### Deactivate Member
```http
DELETE /api/auth/members/{member_id}/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "status": "success",
    "message": "Member deactivated successfully"
}
```

#### Update Member Permissions
```http
POST /api/auth/members/{member_id}/update-permissions/
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body:
{
    "permissions": [
        {
            "id": "permission-uuid",  // Permission UUID
            "permission_id": "role-permission-uuid",  // RolePermission UUID (if exists)
            "is_enabled": true
        }
    ]
}

Response (200 OK):
{
    "status": "success",
    "message": "Permissions updated successfully",
    "data": {
        "id": "uuid",
        "permissions": [...]
    }
}
```

#### Get Available Permissions for Member
```http
GET /api/auth/members/{member_id}/available-permissions/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "status": "success",
    "data": {
        "master_sheets": [
            {
                "id": "permission-uuid",
                "category": "master_sheets",
                "action": "view",
                "resource": "buyer_master",
                "description": "View Buyer Master Sheet",
                "permission_id": "role-permission-uuid",
                "is_enabled": true
            }
        ],
        "ims": [...],
        "sourcing": [...]
    }
}
```

---

### 3. Permission Management

#### Get All Permissions
```http
GET /api/auth/permissions/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "status": "success",
    "data": {
        "master_sheets": [
            {
                "id": "permission-uuid",
                "category": "master_sheets",
                "action": "view",
                "resource": "buyer_master",
                "description": "View Buyer Master Sheet"
            }
        ],
        "ims": [...],
        "sourcing": [...]
    }
}
```

#### Toggle Permission
```http
POST /api/auth/members/{user_id}/permissions/{permission_id}/toggle/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "status": "success",
    "message": "Permission enabled successfully",
    "data": {
        "id": "uuid",
        "user": "user-uuid",
        "permission": "permission-uuid",
        "is_enabled": true
    }
}
```

---

### 4. Tenant Management

#### List Tenants (Master Admin Only)
```http
GET /api/auth/tenants/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "count": 5,
    "results": [
        {
            "id": "uuid",
            "company_name": "ABC Textiles",
            "company_email": "info@abctextiles.com",
            "user_limit": 500,
            "current_user_count": 15,
            "available_slots": 485,
            "plan": "premium",
            "is_active": true,
            "logo_url": "https://your-backend.onrender.com/media/tenant_logos/logo.png"
        }
    ]
}
```

#### Create Tenant (Master Admin Only)
```http
POST /api/auth/tenants/
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body:
{
    "company_name": "New Textile Company",
    "company_email": "info@newtextile.com",
    "company_phone": "+91 1234567890",
    "company_address": "123 Textile Street, Panipat",
    "user_limit": 100,
    "plan": "standard"
}

Response (201 Created):
{
    "id": "uuid",
    "company_name": "New Textile Company",
    "user_limit": 100,
    "plan": "standard",
    ...
}
```

#### Update Tenant
```http
PATCH /api/auth/tenants/{tenant_id}/
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body (Master Admin):
{
    "user_limit": 750,
    "plan": "enterprise",
    "is_active": true
}

Request Body (Tenant Owner - Limited):
{
    "company_phone": "+91 9876543210",
    "company_address": "Updated Address"
}

Response (200 OK):
{
    "status": "success",
    "message": "Tenant updated successfully",
    "data": {...}
}
```

#### Update Tenant User Limit (Master Admin Only)
```http
POST /api/auth/tenants/{tenant_id}/update-user-limit/
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body:
{
    "user_limit": 500,
    "plan": "premium"
}

Response (200 OK):
{
    "status": "success",
    "message": "User limit updated to 500 users",
    "data": {
        "id": "tenant-uuid",
        "company_name": "ABC Textiles",
        "user_limit": 500,
        "current_user_count": 15,
        "available_slots": 485,
        "plan": "premium"
    }
}

Validation:
- user_limit must be between 1 and 1000
- Cannot be less than current_user_count
```

#### Upload Tenant Logo
```http
POST /api/auth/tenants/{tenant_id}/upload-logo/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

Request Body (Form Data):
logo: <file>

Response (200 OK):
{
    "status": "success",
    "message": "Logo uploaded successfully",
    "data": {
        "logo": "https://your-backend.onrender.com/media/tenant_logos/logo.png"
    }
}
```

---

### 5. Inventory Management (Department & Segment)

#### List Departments
```http
GET /api/ims/departments/
Authorization: Bearer <access_token>

Query Parameters:
- is_active: Filter by active status (true/false)
- search: Search by name, code, or description

Response (200 OK):
{
    "count": 10,
    "results": [
        {
            "id": "uuid",
            "code": "chd-code",
            "name": "CHD CODE CREATION",
            "description": "Department for CHD code creation",
            "display_order": 1,
            "is_active": true,
            "segments_count": 3,
            "active_segments_count": 3,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

#### Get Department Details
```http
GET /api/ims/departments/{department_id}/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "id": "uuid",
    "code": "chd-code",
    "name": "CHD CODE CREATION",
    "description": "Department for CHD code creation",
    "display_order": 1,
    "is_active": true,
    "segments_count": 3,
    "segments": [
        {
            "id": "uuid",
            "code": "buyer",
            "name": "BUYER",
            "description": "Buyer code creation",
            "display_order": 1,
            "is_active": true
        },
        {
            "id": "uuid",
            "code": "vendor",
            "name": "VENDOR",
            "description": "Vendor code creation",
            "display_order": 2,
            "is_active": true
        },
        {
            "id": "uuid",
            "code": "factory",
            "name": "FACTORY",
            "description": "Factory code creation",
            "display_order": 3,
            "is_active": true
        }
    ],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Create Department
```http
POST /api/ims/departments/
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body:
{
    "code": "chd-code",
    "name": "CHD CODE CREATION",
    "description": "Department for CHD code creation",
    "display_order": 1,
    "is_active": true,
    "segments": [
        {
            "code": "buyer",
            "name": "BUYER",
            "description": "Buyer code creation",
            "display_order": 1
        },
        {
            "code": "vendor",
            "name": "VENDOR",
            "description": "Vendor code creation",
            "display_order": 2
        },
        {
            "code": "factory",
            "name": "FACTORY",
            "description": "Factory code creation",
            "display_order": 3
        }
    ]
}

Response (201 Created):
{
    "id": "uuid",
    "code": "chd-code",
    "name": "CHD CODE CREATION",
    ...
}
```

#### Update Department
```http
PATCH /api/ims/departments/{department_id}/
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body:
{
    "name": "Updated Department Name",
    "is_active": false
}

Response (200 OK):
{
    "id": "uuid",
    "code": "chd-code",
    "name": "Updated Department Name",
    ...
}
```

#### Delete Department
```http
DELETE /api/ims/departments/{department_id}/
Authorization: Bearer <access_token>

Response (204 No Content)
```

#### Get Department Segments
```http
GET /api/ims/departments/{department_id}/segments/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "status": "success",
    "data": [
        {
            "id": "uuid",
            "code": "buyer",
            "name": "BUYER",
            "department": "uuid",
            "department_name": "CHD CODE CREATION",
            "department_code": "chd-code",
            "display_order": 1,
            "is_active": true
        }
    ]
}
```

#### Add Segment to Department
```http
POST /api/ims/departments/{department_id}/add_segment/
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body:
{
    "code": "buyer",
    "name": "BUYER",
    "description": "Buyer code creation",
    "display_order": 1,
    "is_active": true
}

Response (201 Created):
{
    "status": "success",
    "message": "Segment added successfully",
    "data": {
        "id": "uuid",
        "code": "buyer",
        "name": "BUYER",
        ...
    }
}
```

#### List Segments
```http
GET /api/ims/segments/
Authorization: Bearer <access_token>

Query Parameters:
- department: Filter by department ID
- is_active: Filter by active status
- search: Search by name, code, or description

Response (200 OK):
{
    "count": 50,
    "results": [
        {
            "id": "uuid",
            "code": "buyer",
            "name": "BUYER",
            "department": "uuid",
            "display_order": 1,
            "is_active": true,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

#### Get Segment Details
```http
GET /api/ims/segments/{segment_id}/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "id": "uuid",
    "code": "buyer",
    "name": "BUYER",
    "description": "Buyer code creation",
    "department": "uuid",
    "department_name": "CHD CODE CREATION",
    "department_code": "chd-code",
    "display_order": 1,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Create Segment
```http
POST /api/ims/segments/
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body:
{
    "code": "buyer",
    "name": "BUYER",
    "description": "Buyer code creation",
    "department": "department-uuid",
    "display_order": 1,
    "is_active": true
}

Response (201 Created):
{
    "status": "success",
    "message": "Segment created successfully",
    "data": {
        "id": "uuid",
        "code": "buyer",
        "name": "BUYER",
        "department_name": "CHD CODE CREATION",
        ...
    }
}
```

#### Update Segment
```http
PATCH /api/ims/segments/{segment_id}/
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body:
{
    "name": "Updated Segment Name",
    "is_active": false
}

Response (200 OK):
{
    "status": "success",
    "message": "Segment updated successfully",
    "data": {
        ...
    }
}
```

#### Delete Segment
```http
DELETE /api/ims/segments/{segment_id}/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "status": "success",
    "message": "Segment deleted successfully"
}
```

#### Get Menu Structure
```http
GET /api/ims/menu-structure/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "status": "success",
    "data": [
        {
            "id": "uuid",
            "code": "chd-code",
            "label": "CHD CODE CREATION",
            "hasSubMenu": true,
            "segments": [
                {
                    "id": "uuid",
                    "code": "buyer",
                    "label": "BUYER"
                },
                {
                    "id": "uuid",
                    "code": "vendor",
                    "label": "VENDOR"
                },
                {
                    "id": "uuid",
                    "code": "factory",
                    "label": "FACTORY"
                }
            ]
        }
    ]
}
```

---

### 6. Buyer Code Management

#### List Buyer Codes
```http
GET /api/ims/buyer-codes/
Authorization: Bearer <access_token>

Query Parameters:
- search: Search by buyer_name, code, retailer, contact_person

Response (200 OK):
{
    "count": 50,
    "results": [
        {
            "id": "uuid",
            "code": "101A",
            "buyer_name": "ABC Textiles",
            "retailer": "Premium Retail Store",
            "contact_person": "John Doe",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

#### Get Buyer Code Details
```http
GET /api/ims/buyer-codes/{buyer_code_id}/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "id": "uuid",
    "code": "101A",
    "buyer_name": "ABC Textiles",
    "buyer_address": "123 Main Street",
    "contact_person": "John Doe",
    "retailer": "Premium Retail Store",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Generate Buyer Code
```http
POST /api/ims/buyer-codes/
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body:
{
    "buyer_name": "ABC Textiles",
    "buyer_address": "123 Main Street, City, State, ZIP",
    "contact_person": "John Doe",
    "retailer": "Premium Retail Store"
}

Response (201 Created):
{
    "status": "success",
    "message": "Buyer code generated successfully",
    "data": {
        "id": "uuid",
        "code": "101A",
        "buyer_name": "ABC Textiles",
        "buyer_address": "123 Main Street, City, State, ZIP",
        "contact_person": "John Doe",
        "retailer": "Premium Retail Store",
        "created_at": "2024-01-01T00:00:00Z"
    }
}
```

#### Update Buyer Code
```http
PATCH /api/ims/buyer-codes/{buyer_code_id}/
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body:
{
    "buyer_name": "Updated Buyer Name",
    "contact_person": "Jane Doe"
}

Response (200 OK):
{
    "status": "success",
    "message": "Buyer code updated successfully",
    "data": {...}
}
```

#### Delete Buyer Code
```http
DELETE /api/ims/buyer-codes/{buyer_code_id}/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "status": "success",
    "message": "Buyer code 101A deleted successfully"
}
```

#### Preview Next Buyer Code
```http
GET /api/ims/buyer-codes/generate/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "status": "success",
    "data": {
        "next_code": "101A"
    }
}
```

#### Get Buyer Master Sheet
```http
GET /api/ims/buyer-codes/master-sheet/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "status": "success",
    "data": [
        {
            "code": "101A",
            "buyerName": "ABC Textiles",
            "buyerAddress": "123 Main Street",
            "contactPerson": "John Doe",
            "retailer": "Premium Retail Store",
            "createdAt": "2024-01-01T10:30:00.000Z"
        }
    ],
    "count": 10
}
```

---

### 7. Vendor Code Management

#### List Vendor Codes
```http
GET /api/ims/vendor-codes/
Authorization: Bearer <access_token>

Query Parameters:
- search: Search by vendor_name, code, gst, contact_person, email, job_work_category

Response (200 OK):
{
    "count": 50,
    "results": [
        {
            "id": "uuid",
            "code": "101",
            "vendor_name": "ABC Textiles Pvt Ltd",
            "gst": "03AABCA1234A1Z5",
            "job_work_category": "Fabric",
            "contact_person": "Rajesh Kumar",
            "email": "rajesh@abctextiles.com",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

#### Get Vendor Code Details
```http
GET /api/ims/vendor-codes/{vendor_code_id}/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "id": "uuid",
    "code": "101",
    "vendor_name": "ABC Textiles Pvt Ltd",
    "address": "123, Industrial Area",
    "gst": "03AABCA1234A1Z5",
    "bank_name": "State Bank of India",
    "account_number": "12345678901",
    "ifsc_code": "SBIN0001234",
    "job_work_category": "Fabric",
    "job_work_sub_category": "Cotton Yarn",
    "contact_person": "Rajesh Kumar",
    "whatsapp_number": "9876543210",
    "alt_whatsapp_number": "9876543211",
    "email": "rajesh@abctextiles.com",
    "payment_terms": "30 days credit after delivery",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Generate Vendor Code
```http
POST /api/ims/vendor-codes/
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body:
{
    "vendor_name": "ABC Textiles Pvt Ltd",
    "address": "123, Industrial Area, Phase-1, Chandigarh, 160002",
    "gst": "03AABCA1234A1Z5",
    "bank_name": "State Bank of India",
    "account_number": "12345678901",
    "ifsc_code": "SBIN0001234",
    "job_work_category": "Fabric",
    "job_work_sub_category": "Cotton Yarn",
    "contact_person": "Rajesh Kumar",
    "whatsapp_number": "9876543210",
    "alt_whatsapp_number": "9876543211",
    "email": "rajesh@abctextiles.com",
    "payment_terms": "30 days credit after delivery"
}

Response (201 Created):
{
    "status": "success",
    "message": "Vendor code generated successfully",
    "data": {
        "id": "uuid",
        "code": "101",
        "vendor_name": "ABC Textiles Pvt Ltd",
        ...
    }
}
```

#### Update Vendor Code
```http
PATCH /api/ims/vendor-codes/{vendor_code_id}/
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body:
{
    "vendor_name": "Updated Vendor Name",
    "contact_person": "Updated Contact"
}

Response (200 OK):
{
    "status": "success",
    "message": "Vendor code updated successfully",
    "data": {...}
}
```

#### Delete Vendor Code
```http
DELETE /api/ims/vendor-codes/{vendor_code_id}/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "status": "success",
    "message": "Vendor code 101 deleted successfully"
}
```

#### Preview Next Vendor Code
```http
GET /api/ims/vendor-codes/generate/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "status": "success",
    "data": {
        "next_code": "101"
    }
}
```

#### Get Vendor Master Sheet
```http
GET /api/ims/vendor-codes/master-sheet/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "status": "success",
    "data": [
        {
            "code": "101",
            "vendorName": "ABC Textiles Pvt Ltd",
            "address": "123, Industrial Area",
            "gst": "03AABCA1234A1Z5",
            "bankName": "State Bank of India",
            "accNo": "12345678901",
            "ifscCode": "SBIN0001234",
            "jobWorkCategory": "Fabric",
            "jobWorkSubCategory": "Cotton Yarn",
            "contactPerson": "Rajesh Kumar",
            "whatsappNo": "9876543210",
            "altWhatsappNo": "9876543211",
            "email": "rajesh@abctextiles.com",
            "paymentTerms": "30 days credit after delivery",
            "createdAt": "2024-01-01T10:30:00.000Z"
        }
    ],
    "count": 15
}
```

---

### 8. Google Sheets Integration

#### Get Departments (Legacy)
```http
GET /api/sheets/departments/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "status": "success",
    "data": [
        {
            "code": "DEPT001",
            "name": "Cutting",
            "description": "Fabric cutting department"
        }
    ]
}
```

#### Add Department (Legacy)
```http
POST /api/sheets/departments/add/
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body:
{
    "code": "DEPT003",
    "name": "Quality Check",
    "description": "Final quality inspection"
}

Response (200 OK):
{
    "status": "success",
    "message": "Department added successfully"
}
```

#### Get Accessories (Legacy)
```http
GET /api/sheets/accessories/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "status": "success",
    "data": [
        {
            "code": "ACC001",
            "name": "Buttons",
            "category": "Fasteners",
            "description": "Plastic buttons 10mm"
        }
    ]
}
```

#### Add Accessory (Legacy)
```http
POST /api/sheets/accessories/add/
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body:
{
    "code": "ACC002",
    "name": "Zipper",
    "category": "Fasteners",
    "description": "Metal zipper 15cm"
}

Response (200 OK):
{
    "status": "success",
    "message": "Accessory added successfully"
}
```

---

### 9. Health Monitoring

#### Basic Health Check
```http
GET /api/health/

Response (200 OK):
{
    "status": "healthy",
    "timestamp": 1699876543.123
}
```

#### Detailed Health Check
```http
GET /api/health/detailed/

Response (200 OK):
{
    "status": "healthy",
    "timestamp": 1699876543.123,
    "checks": {
        "database": "healthy",
        "cache": "healthy"
    }
}
```

---

## Error Responses

### Standard Error Format
```json
{
    "status": "error",
    "message": "Error description here",
    "data": {
        "field_name": ["Error detail"]
    }
}
```

### Common HTTP Status Codes
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Frontend Integration Example

```javascript
// Login
const login = async (email, password) => {
    const response = await fetch('http://localhost:8000/api/auth/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    
    if (data.status === 'success') {
        localStorage.setItem('access_token', data.data.tokens.access);
        localStorage.setItem('refresh_token', data.data.tokens.refresh);
        localStorage.setItem('user', JSON.stringify(data.data.user));
        return data;
    }
    
    throw new Error(data.message);
};

// Make authenticated request
const fetchMembers = async () => {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch('http://localhost:8000/api/auth/members/', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    return await response.json();
};

// Refresh token
const refreshToken = async () => {
    const refresh = localStorage.getItem('refresh_token');
    
    const response = await fetch('http://localhost:8000/api/auth/token/refresh/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh })
    });
    
    const data = await response.json();
    localStorage.setItem('access_token', data.access);
};
```

---

## Rate Limiting
- Authentication endpoints: 10 requests/minute per IP
- Other endpoints: 100 requests/minute per user

## API Documentation
- Swagger UI: `http://localhost:8000/api/docs/` (Development) or `https://your-backend.onrender.com/api/docs/` (Production)
- ReDoc: `http://localhost:8000/api/redoc/` (Development) or `https://your-backend.onrender.com/api/redoc/` (Production)

---

## Deployment Guide

### Backend Deployment (Render)

#### Prerequisites
1. GitHub repository with your backend code
2. Render account (sign up at https://render.com)

#### Steps

1. **Create a New Web Service on Render**
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Build Settings**
   - **Name**: Your service name (e.g., `binder-backend`)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn binder_config.wsgi:application`

3. **Set Environment Variables**
   Add the following environment variables in Render:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   DATABASE_URL=your-postgresql-database-url
   ALLOWED_HOSTS=your-app.onrender.com,erpbinder.com
   CORS_ALLOWED_ORIGINS=https://binder-frontend-self.vercel.app,https://erpbinder.com
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-gmail-app-password
   GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id
   ```

4. **Database Setup**
   - Create a PostgreSQL database on Render
   - Copy the database URL and set it as `DATABASE_URL` environment variable
   - Run migrations: Render will automatically run migrations on deploy, or you can run manually via shell

5. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your application
   - Your API will be available at `https://your-app.onrender.com/api/`

#### Post-Deployment
1. Create a superuser via Render shell:
   ```bash
   python manage.py createsuperuser
   ```
2. Create default permissions:
   ```bash
   python manage.py create_default_permissions
   ```
3. Update your frontend (Vercel) environment variable `VITE_API_URL` to point to your Render URL
4. Test the API endpoints

### Frontend Deployment (Vercel)

#### Prerequisites
1. GitHub repository with your frontend code
2. Vercel account (sign up at https://vercel.com)

#### Steps

1. **Import Project to Vercel**
   - Go to Vercel Dashboard
   - Click "Add New" → "Project"
   - Import your GitHub repository

2. **Configure Build Settings**
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build` (or `yarn build`)
   - **Output Directory**: `dist` (or your build output directory)

3. **Set Environment Variables**
   Add the following environment variables:
   ```
   VITE_API_URL=https://your-backend.onrender.com/api
   REACT_APP_API_URL=your-sheets-api-url (if applicable)
   REACT_APP_SPREADSHEET_ID=your-spreadsheet-id (if applicable)
   ```

4. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy your frontend
   - Your frontend will be available at `https://binder-frontend-self.vercel.app/`

### Important Notes

1. **CORS Configuration**: Ensure your backend CORS settings allow requests from:
   - `https://binder-frontend-self.vercel.app`
   - `https://erpbinder.com`
   - `http://localhost:5173` (development)

2. **Environment Variables**: Never commit sensitive keys to your repository. Use environment variables in both Render and Vercel

3. **Database Migrations**: Run migrations after deployment or configure Render to run them automatically

4. **Static Files**: For production, ensure static files are properly configured (WhiteNoise middleware is included)

5. **Media Files**: Configure media file serving for tenant logos and other uploads

6. **HTTPS**: Both Render and Vercel provide HTTPS by default

7. **Auto-Deploy**: Both platforms support auto-deployment on git push to main branch

---

## Available Roles

1. **master_admin** - Master Admin (Full system access)
2. **tenant_owner** - Tenant Owner (Organization owner)
3. **manager** - Manager (Department manager)
4. **general_manager** - General Manager (Cross-department)
5. **inventory_manager** - Inventory Manager (IMS specific)
6. **supervisor** - Supervisor
7. **attendant** - Attendant
8. **accountant** - Accountant
9. **vendor** - Vendor
10. **distributor** - Distributor
11. **employee** - Employee (Basic access)
12. **custom** - Custom Role (with custom_role_name)

---

## Permission Categories

1. **master_sheets** - Master Sheets (Buyer Master, Vendor Master)
2. **ims** - Inventory Management System (Departments, Segments, Buyer Codes, Vendor Codes)
3. **sourcing** - Sourcing (Yarn, Fabric, Dye, etc.)
4. **community** - Community
5. **reports** - Reports
6. **settings** - Settings
7. **members** - Member Management

---

**Last Updated**: Complete API documentation for all modules
**Version**: 2.0.0
