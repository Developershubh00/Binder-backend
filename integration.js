/**
 * Binder ERP - Frontend API Integration File
 * React + Vite Frontend Integration
 * 
 * This file contains all API integration functions for the frontend.
 * Copy these functions to your React frontend project.
 * 
 * Base URL Configuration:
 * - Development: http://localhost:8000/api/
 * - Production: https://your-backend.onrender.com/api/
 * - Domain: https://erpbinder.com/api/
 * 
 * Frontend Deployment: https://binder-frontend-self.vercel.app/
 */

// ============================================================================
// CONFIGURATION
// ============================================================================

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/';

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Get access token from localStorage
 */
const getAccessToken = () => {
  return localStorage.getItem('access_token');
};

/**
 * Get refresh token from localStorage
 */
const getRefreshToken = () => {
  return localStorage.getItem('refresh_token');
};

/**
 * Set tokens in localStorage
 */
const setTokens = (accessToken, refreshToken) => {
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
};

/**
 * Clear tokens from localStorage
 */
const clearTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
};

/**
 * Get user from localStorage
 */
const getUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

/**
 * Set user in localStorage
 */
const setUser = (user) => {
  localStorage.setItem('user', JSON.stringify(user));
};

/**
 * Make authenticated API request
 */
const apiRequest = async (endpoint, options = {}) => {
  const token = getAccessToken();
  
  // Don't set Content-Type for FormData, browser will set it with boundary
  const isFormData = options.body instanceof FormData;
  
  const defaultHeaders = {};
  
  if (!isFormData) {
    defaultHeaders['Content-Type'] = 'application/json';
  }
  
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }
  
  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };
  
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    
    // Handle 401 Unauthorized - try to refresh token
    if (response.status === 401 && token) {
      const refreshed = await refreshToken();
      if (refreshed) {
        // Retry request with new token
        config.headers['Authorization'] = `Bearer ${getAccessToken()}`;
        return await fetch(`${API_BASE_URL}${endpoint}`, config);
      }
    }
    
    return response;
  } catch (error) {
    console.error('API Request Error:', error);
    throw error;
  }
};

/**
 * Refresh access token
 */
const refreshToken = async () => {
  const refresh = getRefreshToken();
  if (!refresh) {
    clearTokens();
    return false;
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}auth/token/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh }),
    });
    
    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('access_token', data.access);
      return true;
    } else {
      clearTokens();
      return false;
    }
  } catch (error) {
    console.error('Token refresh error:', error);
    clearTokens();
    return false;
  }
};

// ============================================================================
// AUTHENTICATION APIs
// ============================================================================

/**
 * Register new user
 */
export const register = async (userData) => {
  const response = await apiRequest('auth/register/', {
    method: 'POST',
    body: JSON.stringify({
      email: userData.email,
      password: userData.password,
      password_confirm: userData.passwordConfirm,
      first_name: userData.firstName,
      last_name: userData.lastName,
      phone: userData.phone,
    }),
  });
  
  return await response.json();
};

/**
 * Login user (direct login)
 */
export const login = async (email, password) => {
  const response = await apiRequest('auth/login/', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  
  const data = await response.json();
  
  if (data.status === 'success') {
    setTokens(data.data.tokens.access, data.data.tokens.refresh);
    setUser(data.data.user);
  }
  
  return data;
};

/**
 * Request OTP for login (Step 1)
 */
export const requestOTP = async (email, password) => {
  const response = await apiRequest('auth/login/request-otp/', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  
  return await response.json();
};

/**
 * Verify OTP and login (Step 2)
 */
export const verifyOTP = async (email, otp) => {
  const response = await apiRequest('auth/login/verify-otp/', {
    method: 'POST',
    body: JSON.stringify({ email, otp }),
  });
  
  const data = await response.json();
  
  if (data.status === 'success') {
    setTokens(data.data.tokens.access, data.data.tokens.refresh);
    setUser(data.data.user);
  }
  
  return data;
};

/**
 * Logout user
 */
export const logout = async () => {
  const refresh = getRefreshToken();
  
  if (refresh) {
    try {
      await apiRequest('auth/logout/', {
        method: 'POST',
        body: JSON.stringify({ refresh }),
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
  }
  
  clearTokens();
};

/**
 * Get current user
 */
export const getCurrentUser = async () => {
  const response = await apiRequest('auth/me/');
  const data = await response.json();
  
  if (data.id) {
    setUser(data);
  }
  
  return data;
};

/**
 * Verify email
 */
export const verifyEmail = async (token) => {
  const response = await apiRequest('auth/verify-email/', {
    method: 'POST',
    body: JSON.stringify({ token }),
  });
  
  return await response.json();
};

/**
 * Resend verification email
 */
export const resendVerification = async (email) => {
  const response = await apiRequest('auth/resend-verification/', {
    method: 'POST',
    body: JSON.stringify({ email }),
  });
  
  return await response.json();
};

/**
 * Set password (for new users)
 */
export const setPassword = async (token, password, passwordConfirm) => {
  const response = await apiRequest('auth/set-password/', {
    method: 'POST',
    body: JSON.stringify({
      token,
      password,
      password_confirm: passwordConfirm,
    }),
  });
  
  return await response.json();
};

// ============================================================================
// MEMBER MANAGEMENT APIs
// ============================================================================

/**
 * List members
 */
export const getMembers = async (params = {}) => {
  const queryParams = new URLSearchParams(params);
  const response = await apiRequest(`auth/members/?${queryParams}`);
  return await response.json();
};

/**
 * Get member details
 */
export const getMember = async (memberId) => {
  const response = await apiRequest(`auth/members/${memberId}/`);
  return await response.json();
};

/**
 * Create member
 */
export const createMember = async (memberData) => {
  const response = await apiRequest('auth/members/', {
    method: 'POST',
    body: JSON.stringify({
      email: memberData.email,
      password: memberData.password,
      first_name: memberData.firstName,
      last_name: memberData.lastName,
      phone: memberData.phone,
      role: memberData.role,
      custom_role_name: memberData.role === 'custom' ? memberData.customRoleName : null,
      designation: memberData.designation,
      permissions: memberData.permissions || [],
    }),
  });
  
  return await response.json();
};

/**
 * Update member
 */
export const updateMember = async (memberId, updates) => {
  const response = await apiRequest(`auth/members/${memberId}/`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
  
  return await response.json();
};

/**
 * Deactivate member
 */
export const deactivateMember = async (memberId) => {
  const response = await apiRequest(`auth/members/${memberId}/`, {
    method: 'DELETE',
  });
  
  return await response.json();
};

/**
 * Update member permissions
 */
export const updateMemberPermissions = async (memberId, permissions) => {
  const response = await apiRequest(`auth/members/${memberId}/update-permissions/`, {
    method: 'POST',
    body: JSON.stringify({ permissions }),
  });
  
  return await response.json();
};

/**
 * Get available permissions for member
 */
export const getMemberAvailablePermissions = async (memberId) => {
  const response = await apiRequest(`auth/members/${memberId}/available-permissions/`);
  return await response.json();
};

// ============================================================================
// PERMISSION APIs
// ============================================================================

/**
 * Get all permissions grouped by category
 */
export const getAllPermissions = async () => {
  const response = await apiRequest('auth/permissions/');
  return await response.json();
};

/**
 * Toggle permission for user
 */
export const togglePermission = async (userId, permissionId) => {
  const response = await apiRequest(`auth/members/${userId}/permissions/${permissionId}/toggle/`, {
    method: 'POST',
  });
  
  return await response.json();
};

// ============================================================================
// TENANT MANAGEMENT APIs
// ============================================================================

/**
 * List tenants (Master Admin only)
 */
export const getTenants = async (params = {}) => {
  const queryParams = new URLSearchParams(params);
  const response = await apiRequest(`auth/tenants/?${queryParams}`);
  return await response.json();
};

/**
 * Get tenant details
 */
export const getTenant = async (tenantId) => {
  const response = await apiRequest(`auth/tenants/${tenantId}/`);
  return await response.json();
};

/**
 * Create tenant (Master Admin only)
 */
export const createTenant = async (tenantData) => {
  const response = await apiRequest('auth/tenants/', {
    method: 'POST',
    body: JSON.stringify({
      company_name: tenantData.companyName,
      company_email: tenantData.companyEmail,
      company_phone: tenantData.companyPhone,
      company_address: tenantData.companyAddress,
      user_limit: tenantData.userLimit,
      plan: tenantData.plan,
    }),
  });
  
  return await response.json();
};

/**
 * Update tenant
 */
export const updateTenant = async (tenantId, updates) => {
  const response = await apiRequest(`auth/tenants/${tenantId}/`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
  
  return await response.json();
};

/**
 * Update tenant user limit (Master Admin only)
 */
export const updateTenantUserLimit = async (tenantId, userLimit, plan) => {
  const response = await apiRequest(`auth/tenants/${tenantId}/update-user-limit/`, {
    method: 'POST',
    body: JSON.stringify({
      user_limit: userLimit,
      plan: plan,
    }),
  });
  
  return await response.json();
};

/**
 * Upload tenant logo
 */
export const uploadTenantLogo = async (tenantId, logoFile) => {
  const formData = new FormData();
  formData.append('logo', logoFile);
  
  const response = await apiRequest(`auth/tenants/${tenantId}/upload-logo/`, {
    method: 'POST',
    body: formData,
  });
  
  return await response.json();
};

// ============================================================================
// DEPARTMENT MANAGEMENT APIs
// ============================================================================

/**
 * List departments
 */
export const getDepartments = async (params = {}) => {
  const queryParams = new URLSearchParams(params);
  const response = await apiRequest(`ims/departments/?${queryParams}`);
  return await response.json();
};

/**
 * Get department details
 */
export const getDepartment = async (departmentId) => {
  const response = await apiRequest(`ims/departments/${departmentId}/`);
  return await response.json();
};

/**
 * Create department
 */
export const createDepartment = async (departmentData) => {
  const response = await apiRequest('ims/departments/', {
    method: 'POST',
    body: JSON.stringify({
      code: departmentData.code,
      name: departmentData.name,
      description: departmentData.description,
      display_order: departmentData.displayOrder,
      is_active: departmentData.isActive,
      segments: departmentData.segments || [],
    }),
  });
  
  return await response.json();
};

/**
 * Update department
 */
export const updateDepartment = async (departmentId, updates) => {
  const response = await apiRequest(`ims/departments/${departmentId}/`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
  
  return await response.json();
};

/**
 * Delete department
 */
export const deleteDepartment = async (departmentId) => {
  const response = await apiRequest(`ims/departments/${departmentId}/`, {
    method: 'DELETE',
  });
  
  return response.status === 204 ? { status: 'success' } : await response.json();
};

/**
 * Get department segments
 */
export const getDepartmentSegments = async (departmentId) => {
  const response = await apiRequest(`ims/departments/${departmentId}/segments/`);
  return await response.json();
};

/**
 * Add segment to department
 */
export const addSegmentToDepartment = async (departmentId, segmentData) => {
  const response = await apiRequest(`ims/departments/${departmentId}/add_segment/`, {
    method: 'POST',
    body: JSON.stringify({
      code: segmentData.code,
      name: segmentData.name,
      description: segmentData.description,
      display_order: segmentData.displayOrder,
      is_active: segmentData.isActive,
    }),
  });
  
  return await response.json();
};

/**
 * Get menu structure
 */
export const getMenuStructure = async () => {
  const response = await apiRequest('ims/menu-structure/');
  return await response.json();
};

// ============================================================================
// SEGMENT MANAGEMENT APIs
// ============================================================================

/**
 * List segments
 */
export const getSegments = async (params = {}) => {
  const queryParams = new URLSearchParams(params);
  const response = await apiRequest(`ims/segments/?${queryParams}`);
  return await response.json();
};

/**
 * Get segment details
 */
export const getSegment = async (segmentId) => {
  const response = await apiRequest(`ims/segments/${segmentId}/`);
  return await response.json();
};

/**
 * Create segment
 */
export const createSegment = async (segmentData) => {
  const response = await apiRequest('ims/segments/', {
    method: 'POST',
    body: JSON.stringify({
      code: segmentData.code,
      name: segmentData.name,
      description: segmentData.description,
      department: segmentData.departmentId,
      display_order: segmentData.displayOrder,
      is_active: segmentData.isActive,
    }),
  });
  
  return await response.json();
};

/**
 * Update segment
 */
export const updateSegment = async (segmentId, updates) => {
  const response = await apiRequest(`ims/segments/${segmentId}/`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
  
  return await response.json();
};

/**
 * Delete segment
 */
export const deleteSegment = async (segmentId) => {
  const response = await apiRequest(`ims/segments/${segmentId}/`, {
    method: 'DELETE',
  });
  
  return await response.json();
};

// ============================================================================
// BUYER CODE APIs
// ============================================================================

/**
 * List buyer codes
 */
export const getBuyerCodes = async (params = {}) => {
  const queryParams = new URLSearchParams(params);
  const response = await apiRequest(`ims/buyer-codes/?${queryParams}`);
  return await response.json();
};

/**
 * Get buyer code details
 */
export const getBuyerCode = async (buyerCodeId) => {
  const response = await apiRequest(`ims/buyer-codes/${buyerCodeId}/`);
  return await response.json();
};

/**
 * Generate buyer code
 */
export const createBuyerCode = async (buyerData) => {
  const response = await apiRequest('ims/buyer-codes/', {
    method: 'POST',
    body: JSON.stringify({
      buyer_name: buyerData.buyerName,
      buyer_address: buyerData.buyerAddress,
      contact_person: buyerData.contactPerson,
      retailer: buyerData.retailer,
    }),
  });
  
  return await response.json();
};

/**
 * Update buyer code
 */
export const updateBuyerCode = async (buyerCodeId, updates) => {
  const response = await apiRequest(`ims/buyer-codes/${buyerCodeId}/`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
  
  return await response.json();
};

/**
 * Delete buyer code
 */
export const deleteBuyerCode = async (buyerCodeId) => {
  const response = await apiRequest(`ims/buyer-codes/${buyerCodeId}/`, {
    method: 'DELETE',
  });
  
  return await response.json();
};

/**
 * Preview next buyer code
 */
export const previewNextBuyerCode = async () => {
  const response = await apiRequest('ims/buyer-codes/generate/');
  return await response.json();
};

/**
 * Get buyer master sheet
 */
export const getBuyerMasterSheet = async () => {
  const response = await apiRequest('ims/buyer-codes/master-sheet/');
  return await response.json();
};

// ============================================================================
// VENDOR CODE APIs
// ============================================================================

/**
 * List vendor codes
 */
export const getVendorCodes = async (params = {}) => {
  const queryParams = new URLSearchParams(params);
  const response = await apiRequest(`ims/vendor-codes/?${queryParams}`);
  return await response.json();
};

/**
 * Get vendor code details
 */
export const getVendorCode = async (vendorCodeId) => {
  const response = await apiRequest(`ims/vendor-codes/${vendorCodeId}/`);
  return await response.json();
};

/**
 * Generate vendor code
 */
export const createVendorCode = async (vendorData) => {
  const response = await apiRequest('ims/vendor-codes/', {
    method: 'POST',
    body: JSON.stringify({
      vendor_name: vendorData.vendorName,
      address: vendorData.address,
      gst: vendorData.gst,
      bank_name: vendorData.bankName,
      account_number: vendorData.accountNumber,
      ifsc_code: vendorData.ifscCode,
      job_work_category: vendorData.jobWorkCategory,
      job_work_sub_category: vendorData.jobWorkSubCategory,
      contact_person: vendorData.contactPerson,
      whatsapp_number: vendorData.whatsappNumber,
      alt_whatsapp_number: vendorData.altWhatsappNumber,
      email: vendorData.email,
      payment_terms: vendorData.paymentTerms,
    }),
  });
  
  return await response.json();
};

/**
 * Update vendor code
 */
export const updateVendorCode = async (vendorCodeId, updates) => {
  const response = await apiRequest(`ims/vendor-codes/${vendorCodeId}/`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
  
  return await response.json();
};

/**
 * Delete vendor code
 */
export const deleteVendorCode = async (vendorCodeId) => {
  const response = await apiRequest(`ims/vendor-codes/${vendorCodeId}/`, {
    method: 'DELETE',
  });
  
  return await response.json();
};

/**
 * Preview next vendor code
 */
export const previewNextVendorCode = async () => {
  const response = await apiRequest('ims/vendor-codes/generate/');
  return await response.json();
};

/**
 * Get vendor master sheet
 */
export const getVendorMasterSheet = async () => {
  const response = await apiRequest('ims/vendor-codes/master-sheet/');
  return await response.json();
};

// ============================================================================
// HEALTH CHECK APIs
// ============================================================================

/**
 * Basic health check
 */
export const healthCheck = async () => {
  const response = await fetch(`${API_BASE_URL}health/`);
  return await response.json();
};

/**
 * Detailed health check
 */
export const detailedHealthCheck = async () => {
  const response = await fetch(`${API_BASE_URL}health/detailed/`);
  return await response.json();
};

// ============================================================================
// GOOGLE SHEETS APIs (Legacy)
// ============================================================================

/**
 * Get departments (Legacy)
 */
export const getSheetsDepartments = async () => {
  const response = await apiRequest('sheets/departments/');
  return await response.json();
};

/**
 * Add department (Legacy)
 */
export const addSheetsDepartment = async (departmentData) => {
  const response = await apiRequest('sheets/departments/add/', {
    method: 'POST',
    body: JSON.stringify(departmentData),
  });
  
  return await response.json();
};

/**
 * Get accessories (Legacy)
 */
export const getSheetsAccessories = async () => {
  const response = await apiRequest('sheets/accessories/');
  return await response.json();
};

/**
 * Add accessory (Legacy)
 */
export const addSheetsAccessory = async (accessoryData) => {
  const response = await apiRequest('sheets/accessories/add/', {
    method: 'POST',
    body: JSON.stringify(accessoryData),
  });
  
  return await response.json();
};

