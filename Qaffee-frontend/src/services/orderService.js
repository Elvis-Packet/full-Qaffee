import api from './api';

const orderService = {
  createOrder: async (orderData) => {
    try {
      const response = await api.post('/api/orders', orderData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  getOrder: async (orderId) => {
    try {
      const response = await api.get(`/api/orders/${orderId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  updateOrder: async (orderId, updateData) => {
    try {
      const response = await api.put(`/api/orders/${orderId}`, updateData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  getOrderStatus: async (orderId) => {
    try {
      const response = await api.get(`/api/orders/${orderId}/status`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default orderService; 