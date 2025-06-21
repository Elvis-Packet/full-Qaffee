import api from './api';

// Order Management
export const getOrders = async (params) => {
  const response = await api.get('/admin/orders', { params });
  return response.data;
};

export const updateOrderStatus = async (orderId, status) => {
  const response = await api.patch(`/admin/orders/${orderId}/status`, { status });
  return response.data;
};

export const assignDeliveryStaff = async (orderId, staffId) => {
  const response = await api.post(`/admin/orders/${orderId}/assign`, { staff_id: staffId });
  return response.data;
};

// Menu Management
export const getCategories = async () => {
  const response = await api.get('/admin/categories');
  return response.data;
};

export const createCategory = async (categoryData) => {
  const response = await api.post('/admin/categories', categoryData);
  return response.data;
};

export const updateCategory = async (categoryId, categoryData) => {
  const response = await api.put(`/admin/categories/${categoryId}`, categoryData);
  return response.data;
};

export const deleteCategory = async (categoryId) => {
  const response = await api.delete(`/admin/categories/${categoryId}`);
  return response.data;
};

export const getMenuItems = async (params) => {
  const response = await api.get('/admin/menu-items', { params });
  return response.data;
};

export const createMenuItem = async (itemData) => {
  const response = await api.post('/admin/menu-items', itemData);
  return response.data;
};

export const updateMenuItem = async (itemId, itemData) => {
  const response = await api.put(`/admin/menu-items/${itemId}`, itemData);
  return response.data;
};

export const deleteMenuItem = async (itemId) => {
  const response = await api.delete(`/admin/menu-items/${itemId}`);
  return response.data;
};

export const uploadItemImage = async (itemId, imageFile) => {
  const formData = new FormData();
  formData.append('image', imageFile);
  const response = await api.post(`/admin/menu-items/${itemId}/image`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

// Promotions Management
export const getPromotions = async (params) => {
  const response = await api.get('/admin/promotions', { params });
  return response.data;
};

export const createPromotion = async (promotionData) => {
  const response = await api.post('/admin/promotions', promotionData);
  return response.data;
};

export const updatePromotion = async (promotionId, promotionData) => {
  const response = await api.put(`/admin/promotions/${promotionId}`, promotionData);
  return response.data;
};

export const deletePromotion = async (promotionId) => {
  const response = await api.delete(`/admin/promotions/${promotionId}`);
  return response.data;
};

export const togglePromotionStatus = async (promotionId, isActive) => {
  const response = await api.patch(`/admin/promotions/${promotionId}/status`, { is_active: isActive });
  return response.data;
};

// Analytics
export const getAnalytics = async (params) => {
  const response = await api.get('/admin/analytics', { params });
  return response.data;
};

export const exportAnalytics = async (params) => {
  const response = await api.get('/admin/analytics/export', {
    params,
    responseType: 'blob'
  });
  return response.data;
};

// User Management
export const getUsers = async (params) => {
  const response = await api.get('/admin/users', { params });
  return response.data;
};

export const updateUserStatus = async (userId, isActive) => {
  const response = await api.patch(`/admin/users/${userId}/status`, { is_active: isActive });
  return response.data;
};

export const updateUserRole = async (userId, role) => {
  const response = await api.patch(`/admin/users/${userId}/role`, { role });
  return response.data;
};

// Staff Management
export const getStaff = async (params) => {
  const response = await api.get('/admin/staff', { params });
  return response.data;
};

export const createStaff = async (staffData) => {
  const response = await api.post('/admin/staff', staffData);
  return response.data;
};

export const updateStaff = async (staffId, staffData) => {
  const response = await api.put(`/admin/staff/${staffId}`, staffData);
  return response.data;
};

export const deleteStaff = async (staffId) => {
  const response = await api.delete(`/admin/staff/${staffId}`);
  return response.data;
};

// Branch Management
export const getBranches = async () => {
  const response = await api.get('/admin/branches');
  return response.data;
};

export const createBranch = async (branchData) => {
  const response = await api.post('/admin/branches', branchData);
  return response.data;
};

export const updateBranch = async (branchId, branchData) => {
  const response = await api.put(`/admin/branches/${branchId}`, branchData);
  return response.data;
};

export const deleteBranch = async (branchId) => {
  const response = await api.delete(`/admin/branches/${branchId}`);
  return response.data;
};

// Support Tools
export const getTickets = async (params) => {
  const response = await api.get('/admin/support/tickets', { params });
  return response.data;
};

export const updateTicket = async (ticketId, ticketData) => {
  const response = await api.patch(`/admin/support/tickets/${ticketId}`, ticketData);
  return response.data;
};

export const respondToTicket = async (ticketId, message) => {
  const response = await api.post(`/admin/support/tickets/${ticketId}/respond`, { message });
  return response.data;
};

// Settings
export const getSettings = async () => {
  const response = await api.get('/admin/settings');
  return response.data;
};

export const updateSettings = async (settings) => {
  const response = await api.put('/admin/settings', settings);
  return response.data;
};

// Testing Tools
export const toggleTestMode = async (isEnabled) => {
  const response = await api.post('/admin/testing/mode', { enabled: isEnabled });
  return response.data;
};

export const createTestData = async (type) => {
  const response = await api.post('/admin/testing/data', { type });
  return response.data;
};

export const clearTestData = async () => {
  const response = await api.delete('/admin/testing/data');
  return response.data;
}; 