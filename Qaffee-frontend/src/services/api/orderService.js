import api from '../api';  // Use the local API configuration

export const orderService = {
  createOrder: async (orderData) => {
    const response = await api.post('/orders/checkout', orderData);
    return response.data;
  },

  getOrderById: async (orderId) => {
    const response = await api.get(`/orders/${orderId}`);
    return response.data;
  },

  getAllOrders: async (filters = {}) => {
    const response = await api.get('/orders', { params: filters });
    return response.data;
  },

  updateOrderStatus: async (orderId, status) => {
    const response = await api.patch(`/orders/${orderId}/status`, { status });
    return response.data;
  },

  updatePaymentStatus: async (orderId, paymentStatus) => {
    const response = await api.patch(`/orders/${orderId}/payment`, { status: paymentStatus });
    return response.data;
  },

  // Admin specific endpoints
  getPendingOrders: async () => {
    const response = await api.get('/orders?status=pending');
    return response.data;
  },

  approveOrder: async (orderId) => {
    const response = await api.post(`/orders/${orderId}/approve`);
    return response.data;
  },

  rejectOrder: async (orderId, reason) => {
    const response = await api.post(`/orders/${orderId}/reject`, { reason });
    return response.data;
  }
}; 