import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export const orderService = {
  createOrder: async (orderData) => {
    const response = await axios.post(`${API_URL}/orders/checkout`, orderData);
    return response.data;
  },

  getOrderById: async (orderId) => {
    const response = await axios.get(`${API_URL}/orders/${orderId}`);
    return response.data;
  },

  getAllOrders: async (filters = {}) => {
    const response = await axios.get(`${API_URL}/orders`, { params: filters });
    return response.data;
  },

  updateOrderStatus: async (orderId, status) => {
    const response = await axios.patch(`${API_URL}/orders/${orderId}/status`, { status });
    return response.data;
  },

  updatePaymentStatus: async (orderId, paymentStatus) => {
    const response = await axios.patch(`${API_URL}/orders/${orderId}/payment`, { status: paymentStatus });
    return response.data;
  },

  // Admin specific endpoints
  getPendingOrders: async () => {
    const response = await axios.get(`${API_URL}/orders?status=pending`);
    return response.data;
  },

  approveOrder: async (orderId) => {
    const response = await axios.post(`${API_URL}/orders/${orderId}/approve`);
    return response.data;
  },

  rejectOrder: async (orderId, reason) => {
    const response = await axios.post(`${API_URL}/orders/${orderId}/reject`, { reason });
    return response.data;
  }
}; 