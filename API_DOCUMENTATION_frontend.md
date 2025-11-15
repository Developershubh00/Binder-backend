# Binder Frontend - Backend API Documentation

This document provides comprehensive documentation for all backend API endpoints used by the Binder frontend application.

## Table of Contents
- [Base URLs](#base-urls)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [Authentication Endpoints](#authentication-endpoints)
  - [Sheets API Endpoints](#sheets-api-endpoints)
  - [External APIs](#external-apis)

---

## Base URLs

### Main Backend API
- **Development**: `http://127.0.0.1:8000/api`
- **Production (Render)**: Set via `VITE_API_URL` environment variable
- **Default**: `http://127.0.0.1:8000/api`

### Sheets API
- **Base URL**: Set via `REACT_APP_API_URL` environment variable
- **Default**: `http://localhost:3000`

### External APIs
- **Google Gemini AI**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`

### Deployment
- **Frontend**: Deployed on Vercel
- **Backend**: Deployed on Render
- **Production API URL**: Update `VITE_API_URL` in Vercel environment variables to point to your Render backend URL

---

## Authentication

The application uses JWT (JSON Web Token) authentication with access and refresh tokens.

### Token Storage
- **Access Token**: Stored in `localStorage` as `access_token`
- **Refresh Token**: Stored in `localStorage` as `refresh_token`
- **User Data**: Stored in `localStorage` as `user`

### Authorization Header Format
```
Authorization: Bearer <access_token>
```

---

## API Endpoints

### Authentication Endpoints

#### 1. Request OTP (Step 1 of Login)

**Endpoint**: `POST /auth/login/request-otp/`

**Description**: Validates user credentials and sends OTP to user's email.

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "userpassword123"
}
```

**Request Body Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| email | string | Yes | User's email address |
| password | string | Yes | User's password |

**Success Response** (200 OK):
```json
{
  "message": "OTP sent successfully",
  "data": {
    // Additional data if needed
  }
}
```

**Error Response** (400/401):
```json
{
  "message": "Failed to send OTP" // or specific error message
}
```

**Example Request**:
```javascript
const response = await fetch(`${API_BASE_URL}/auth/login/request-otp/`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'userpassword123'
  })
});
```

---

#### 2. Verify OTP (Step 2 of Login)

**Endpoint**: `POST /auth/login/verify-otp/`

**Description**: Verifies the OTP and completes the login process, returning access and refresh tokens.

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Request Body Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| email | string | Yes | User's email address |
| otp | string | Yes | One-time password received via email |

**Success Response** (200 OK):
```json
{
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "role": "manager",
      // ... other user fields
    },
    "tokens": {
      "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
  }
}
```

**Response Data Structure**:
| Field | Type | Description |
|-------|------|-------------|
| user | object | User object with profile information |
| tokens.access | string | JWT access token (short-lived) |
| tokens.refresh | string | JWT refresh token (long-lived) |

**Error Response** (400/401):
```json
{
  "message": "Invalid OTP" // or specific error message
}
```

**Example Request**:
```javascript
const response = await fetch(`${API_BASE_URL}/auth/login/verify-otp/`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    otp: '123456'
  })
});
```

---

#### 3. Get Current User

**Endpoint**: `GET /auth/me/`

**Description**: Retrieves the current authenticated user's information.

**Request Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "role": "manager",
  "created_at": "2024-01-01T00:00:00Z",
  // ... other user fields
}
```

**Error Response** (401 Unauthorized):
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Example Request**:
```javascript
const response = await fetch(`${API_BASE_URL}/auth/me/`, {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});
```

---

#### 4. Refresh Access Token

**Endpoint**: `POST /auth/token/refresh/`

**Description**: Refreshes an expired access token using a valid refresh token.

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Request Body Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| refresh | string | Yes | Valid refresh token |

**Success Response** (200 OK):
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response Data Structure**:
| Field | Type | Description |
|-------|------|-------------|
| access | string | New JWT access token |

**Error Response** (401 Unauthorized):
```json
{
  "detail": "Token is invalid or expired"
}
```

**Example Request**:
```javascript
const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    refresh: refreshToken
  })
});
```

---

#### 5. Logout

**Endpoint**: `POST /auth/logout/`

**Description**: Logs out the current user and invalidates the refresh token.

**Request Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Request Body Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| refresh | string | Yes | Refresh token to invalidate |

**Success Response** (200 OK):
```json
{
  "message": "Logout successful"
}
```

**Example Request**:
```javascript
const response = await fetch(`${API_BASE_URL}/auth/logout/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    refresh: refreshToken
  })
});
```

---

#### 6. Set Password

**Endpoint**: `POST /auth/set-password/`

**Description**: Sets a password for a new user (typically used during initial account setup).

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "token": "invitation_token_here",
  "password": "newpassword123",
  "password_confirm": "newpassword123"
}
```

**Request Body Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| token | string | Yes | Invitation or setup token |
| password | string | Yes | New password |
| password_confirm | string | Yes | Password confirmation (must match password) |

**Success Response** (200 OK):
```json
{
  "message": "Password set successfully"
}
```

**Error Response** (400):
```json
{
  "message": "Failed to set password" // or specific validation error
}
```

**Example Request**:
```javascript
const response = await fetch(`${API_BASE_URL}/auth/set-password/`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    token: 'invitation_token',
    password: 'newpassword123',
    password_confirm: 'newpassword123'
  })
});
```

---

### Inventory Management Endpoints

#### Department Management

##### 1. List Departments

**Endpoint**: `GET /api/ims/departments/`

**Description**: Retrieves a list of all departments with their segments.

**Request Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| is_active | boolean | No | Filter by active status (true/false) |
| search | string | No | Search by name, code, or description |

**Success Response** (200 OK):
```json
{
  "count": 10,
  "next": null,
  "previous": null,
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

**Example Request**:
```javascript
const response = await fetch(`${API_BASE_URL}/ims/departments/`, {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});
```

---

##### 2. Get Department Details

**Endpoint**: `GET /api/ims/departments/{department_id}/`

**Description**: Retrieves detailed information about a specific department including all its segments.

**Request Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Success Response** (200 OK):
```json
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
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "uuid",
      "code": "vendor",
      "name": "VENDOR",
      "description": "Vendor code creation",
      "display_order": 2,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "uuid",
      "code": "factory",
      "name": "FACTORY",
      "description": "Factory code creation",
      "display_order": 3,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

##### 3. Create Department

**Endpoint**: `POST /api/ims/departments/`

**Description**: Creates a new department. Optionally, segments can be created along with the department.

**Request Body**:
```json
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
```

**Success Response** (201 Created):
```json
{
  "id": "uuid",
  "code": "chd-code",
  "name": "CHD CODE CREATION",
  ...
}
```

---

##### 4. Get Department Segments

**Endpoint**: `GET /api/ims/departments/{department_id}/segments/`

**Description**: Retrieves all segments for a specific department.

**Success Response** (200 OK):
```json
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

---

##### 5. Add Segment to Department

**Endpoint**: `POST /api/ims/departments/{department_id}/add_segment/`

**Description**: Adds a new segment to an existing department.

**Request Body**:
```json
{
  "code": "buyer",
  "name": "BUYER",
  "description": "Buyer code creation",
  "display_order": 1,
  "is_active": true
}
```

**Success Response** (201 Created):
```json
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

---

#### Segment Management

##### 1. List Segments

**Endpoint**: `GET /api/ims/segments/`

**Description**: Retrieves a list of all segments.

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| department | uuid | No | Filter by department ID |
| is_active | boolean | No | Filter by active status |
| search | string | No | Search by name, code, or description |

**Success Response** (200 OK):
```json
{
  "count": 50,
  "next": null,
  "previous": null,
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

---

##### 2. Get Segment Details

**Endpoint**: `GET /api/ims/segments/{segment_id}/`

**Description**: Retrieves detailed information about a specific segment.

**Success Response** (200 OK):
```json
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

---

#### Menu Structure

##### Get Complete Menu Structure

**Endpoint**: `GET /api/ims/menu-structure/`

**Description**: Retrieves the complete department menu structure with all active segments. This endpoint is optimized for frontend menu rendering.

**Success Response** (200 OK):
```json
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

**Example Request**:
```javascript
const response = await fetch(`${API_BASE_URL}/ims/menu-structure/`, {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});
const menuData = await response.json();
// Use menuData.data to render your menu structure
```

---

### Sheets API Endpoints

**Note**: These endpoints require a `SPREADSHEET_ID` which should be set via the `REACT_APP_SPREADSHEET_ID` environment variable.

#### 1. Fetch Sheet Data (GET)

**Endpoint**: `GET /api/sheets/{SPREADSHEET_ID}/json`

**Description**: Retrieves data from a Google Sheet in JSON format.

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| range | string | No | `Sheet1!A1:Z1000` | A1 notation range (e.g., `Sheet1!A1:Z1000`) |

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": [
    ["Header1", "Header2", "Header3"],
    ["Value1", "Value2", "Value3"],
    ["Value4", "Value5", "Value6"]
  ]
}
```

**Response Data Structure**:
| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Indicates if the request was successful |
| data | array | 2D array of sheet data (rows and columns) |

**Error Response**:
```json
{
  "success": false,
  "error": "Error message here"
}
```

**Example Request**:
```javascript
const response = await fetch(
  `${API_BASE_URL}/api/sheets/${SPREADSHEET_ID}/json?range=Sheet1!A1:Z1000`
);
const data = await response.json();
```

---

#### 2. Add Row to Sheet (POST)

**Endpoint**: `POST /api/sheets/{SPREADSHEET_ID}/append`

**Description**: Appends a new row to the specified Google Sheet.

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "range": "Sheet1!A:Z",
  "values": [
    ["Value1", "Value2", "Value3", "Value4"]
  ]
}
```

**Request Body Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| range | string | Yes | A1 notation range for where to append (e.g., `Sheet1!A:Z`) |
| values | array | Yes | Array of arrays, where each inner array represents a row |

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Row added successfully"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Error message here"
}
```

**Example Request**:
```javascript
const response = await fetch(
  `${API_BASE_URL}/api/sheets/${SPREADSHEET_ID}/append`,
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      range: 'Sheet1!A:Z',
      values: [['Value1', 'Value2', 'Value3']]
    })
  }
);
```

---

#### 3. Update Row in Sheet (PUT)

**Endpoint**: `PUT /api/sheets/{SPREADSHEET_ID}/update`

**Description**: Updates an existing row in the Google Sheet.

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "range": "Sheet1!A2:Z2",
  "values": [
    ["UpdatedValue1", "UpdatedValue2", "UpdatedValue3"]
  ]
}
```

**Request Body Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| range | string | Yes | A1 notation range for the row to update (e.g., `Sheet1!A2:Z2`) |
| values | array | Yes | Array containing one array with updated row values |

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Row updated successfully"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Error message here"
}
```

**Example Request**:
```javascript
const response = await fetch(
  `${API_BASE_URL}/api/sheets/${SPREADSHEET_ID}/update`,
  {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      range: 'Sheet1!A2:Z2',
      values: [['UpdatedValue1', 'UpdatedValue2', 'UpdatedValue3']]
    })
  }
);
```

---

#### 4. Clear/Delete Row in Sheet (DELETE)

**Endpoint**: `DELETE /api/sheets/{SPREADSHEET_ID}/clear`

**Description**: Clears/deletes data from a specified range in the Google Sheet.

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "range": "Sheet1!A2:Z2"
}
```

**Request Body Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| range | string | Yes | A1 notation range to clear (e.g., `Sheet1!A2:Z2`) |

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Row cleared successfully"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Error message here"
}
```

**Example Request**:
```javascript
const response = await fetch(
  `${API_BASE_URL}/api/sheets/${SPREADSHEET_ID}/clear`,
  {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      range: 'Sheet1!A2:Z2'
    })
  }
);
```

---

### External APIs

#### Google Gemini AI API

**Endpoint**: `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`

**Description**: Used for chatbot functionality to generate AI responses.

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| key | string | Yes | Google Gemini API key |

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "contents": [
    {
      "parts": [
        {
          "text": "User question or context here"
        }
      ]
    }
  ],
  "generationConfig": {
    "temperature": 0.7,
    "topK": 40,
    "topP": 0.95,
    "maxOutputTokens": 500
  }
}
```

**Request Body Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| contents | array | Yes | Array of content objects with parts containing text |
| generationConfig | object | No | Configuration for response generation |
| generationConfig.temperature | number | No | Controls randomness (0.0-1.0) |
| generationConfig.topK | number | No | Limits token selection |
| generationConfig.topP | number | No | Nucleus sampling parameter |
| generationConfig.maxOutputTokens | number | No | Maximum tokens in response |

**Success Response** (200 OK):
```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "AI generated response text here"
          }
        ]
      }
    }
  ]
}
```

**Example Request**:
```javascript
const response = await fetch(
  `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}`,
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      contents: [{
        parts: [{
          text: 'User question here'
        }]
      }],
      generationConfig: {
        temperature: 0.7,
        topK: 40,
        topP: 0.95,
        maxOutputTokens: 500
      }
    })
  }
);
```

---

## Error Handling

### Common HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Invalid or missing authentication |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |

### Error Response Format

Most endpoints return errors in the following format:
```json
{
  "message": "Error description",
  "detail": "Detailed error information (optional)"
}
```

---

## Authentication Flow

1. **Step 1**: User submits email and password → `POST /auth/login/request-otp/`
2. **Step 2**: User receives OTP via email
3. **Step 3**: User submits email and OTP → `POST /auth/login/verify-otp/`
4. **Step 4**: Frontend receives access and refresh tokens
5. **Step 5**: Access token is used for authenticated requests
6. **Step 6**: When access token expires, use refresh token → `POST /auth/token/refresh/`
7. **Step 7**: On logout → `POST /auth/logout/` to invalidate refresh token

---

## Environment Variables

The following environment variables should be configured:

### Frontend (Vite) - Vercel Deployment

#### Required Variables:
- `VITE_API_URL`: Backend API base URL
  - **Development**: `http://127.0.0.1:8000/api`
  - **Production**: Your Render backend URL (e.g., `https://your-app.onrender.com/api`)

#### Vercel Configuration:
1. Go to your Vercel project settings
2. Navigate to "Environment Variables"
3. Add `VITE_API_URL` with your Render backend URL for production
4. Add the same variable for Preview and Development environments if needed

### Sheets API
- `REACT_APP_API_URL`: Sheets API base URL (default: `http://localhost:3000`)
- `REACT_APP_SPREADSHEET_ID`: Google Sheets spreadsheet ID

### External Services
- Google Gemini API Key: Should be stored in Vercel environment variables (not hardcoded)

---

## Notes

1. **Token Expiration**: Access tokens are short-lived. The frontend automatically refreshes them using the refresh token when they expire.

2. **CORS**: Ensure the backend has CORS configured to allow requests from the frontend origin.

3. **Sheets API**: The Sheets API endpoints require proper Google Sheets API credentials and permissions.

4. **Security**: 
   - Never expose API keys in client-side code
   - Use environment variables for sensitive configuration
   - Always validate and sanitize user input
   - Use HTTPS in production

5. **Rate Limiting**: Be aware of any rate limits on the backend API and implement appropriate retry logic.

---

## Support

For questions or issues regarding the API, please contact the development team or refer to the backend API documentation.

---

**Last Updated**: Generated from frontend codebase analysis
**Version**: 1.0.0

