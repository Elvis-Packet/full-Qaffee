import axios from 'axios'
import { toast } from 'react-toastify'

// API base URL
const BASE_URL = import.meta.env.VITE_API_URL || 'http://143.198.224.163'

// Rate limiting configuration
const MAX_RETRIES = 3;
const BASE_DELAY = 1000; // 1 second
const MAX_DELAY = 10000; // 10 seconds

// Request deduplication and caching
const pendingRequests = new Map();
const responseCache = new Map();
const CACHE_TTL = 5000; // 5 seconds cache TTL

// Helper to get request key
const getRequestKey = (config) => {
  const params = config.params ? JSON.stringify(config.params) : '';
  const data = config.data ? JSON.stringify(config.data) : '';
  return `${config.method}:${config.url}:${params}:${data}`;
};

// Helper to check if a request should use cache
const shouldUseCache = (config) => {
  // Only cache GET requests
  if (config.method?.toLowerCase() !== 'get') return false;
  
  // List of cacheable endpoints
  const cacheableEndpoints = ['/auth/me', '/admin/dashboard', '/admin/promotions'];
  return cacheableEndpoints.some(endpoint => config.url?.endsWith(endpoint));
};

// Helper to check if cache is valid
const isCacheValid = (cacheEntry) => {
  return cacheEntry && Date.now() - cacheEntry.timestamp < CACHE_TTL;
};

// Calculate delay with exponential backoff
const getRetryDelay = (retryCount) => {
  return Math.min(Math.pow(2, retryCount) * BASE_DELAY, MAX_DELAY);
};

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true
});

// Request interceptor
api.interceptors.request.use(
  async (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    const requestKey = getRequestKey(config);

    // Check if there's already a pending request
    if (pendingRequests.has(requestKey)) {
      return Promise.reject({
        __DUPLICATE_REQUEST__: true,
        promise: pendingRequests.get(requestKey)
      });
    }

    if (shouldUseCache(config)) {
      // Check cache first
      const cachedResponse = responseCache.get(requestKey);
      if (isCacheValid(cachedResponse)) {
        return Promise.reject({
          __CACHE_HIT__: true,
          cachedData: cachedResponse.data
        });
      }
    }

    // Create a new promise for this request
    const promise = new Promise((resolve) => {
      config.__resolveRequest = resolve;
    });
    pendingRequests.set(requestKey, promise);

    config.metadata = { startTime: new Date() };
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    const requestKey = getRequestKey(response.config);

    if (shouldUseCache(response.config)) {
      // Update cache
      responseCache.set(requestKey, {
        data: response.data,
        timestamp: Date.now()
      });
    }

    // Clean up pending request
    pendingRequests.delete(requestKey);

    // Resolve any pending duplicate requests
    if (response.config.__resolveRequest) {
      response.config.__resolveRequest(response);
    }

    return response;
  },
  async (error) => {
    // Handle cache hits
    if (error.__CACHE_HIT__) {
      return Promise.resolve({ data: error.cachedData });
    }

    // Handle duplicate requests
    if (error.__DUPLICATE_REQUEST__) {
      try {
        const response = await error.promise;
        return response;
      } catch (err) {
        return Promise.reject(err);
      }
    }

    const originalRequest = error.config;
    const requestKey = originalRequest ? getRequestKey(originalRequest) : null;

    // Clean up pending request on any error
    if (requestKey) {
      pendingRequests.delete(requestKey);
    }

    // Handle rate limiting (429)
    if (error.response?.status === 429 && originalRequest) {
      const retryCount = (originalRequest.__retryCount || 0) + 1;
      
      if (retryCount <= MAX_RETRIES) {
        originalRequest.__retryCount = retryCount;
        
        const retryAfter = parseInt(error.response.headers['retry-after'], 10) || 2;
        const delayMs = retryAfter * 1000;
        
        // Add jitter to prevent thundering herd
        const jitter = Math.random() * 1000;
        const totalDelay = delayMs + jitter;

        await new Promise(resolve => setTimeout(resolve, totalDelay));
        
        // Create a new request instead of retrying the original to avoid stale state
        const newRequest = { ...originalRequest };
        delete newRequest.__retryCount;
        
        return api(newRequest);
      }
    }

    // Handle authentication errors
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');

      if (refreshToken) {
        try {
          const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
          const newAccessToken = response.data.access_token;
          localStorage.setItem('token', newAccessToken);
          api.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;
          originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
          return api(originalRequest);
        } catch (refreshError) {
          localStorage.removeItem('token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          toast.error('Session expired. Please log in again.');
          return Promise.reject(refreshError);
        }
      } else {
        localStorage.removeItem('token');
        window.location.href = '/login';
        toast.error('Session expired. Please log in again.');
      }
    }

    // Handle server errors
    if (error.response?.status === 500) {
      toast.error('Something went wrong. Please try again later.');
    }

    return Promise.reject(error);
  }
);

// Menu Service
export const menuService = {
  getItems: () => api.get('/admin/menu'),
  getItem: (id) => api.get(`/menu/item/${id}`),
  createItem: (data) => {
    // If the data contains an image URL, use FormData
    if (data.image_url && data.image_url.startsWith('http')) {
      const formData = new FormData();
      Object.keys(data).forEach(key => {
        if (key === 'ingredients' || key === 'add_ons') {
          formData.append(key, JSON.stringify(data[key]));
        } else if (key === 'image_url') {
          formData.append('image_url', data[key]);
        } else if (typeof data[key] === 'boolean') {
          formData.append(key, data[key].toString());
        } else {
          formData.append(key, data[key] || '');
        }
      });
      return api.post('/admin/menu', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    }
    
    // Otherwise, send as JSON
    const cleanData = {
      name: String(data.name || ''),
      description: String(data.description || ''),
      price: Number(data.price),
      category_id: Number(data.category_id),
      image_url: String(data.image_url || ''),
      is_available: Boolean(data.is_available),
      is_featured: Boolean(data.is_featured)
    };
    
    return api.post('/admin/menu', cleanData);
  },
  updateItem: (id, data) => {
    const formData = new FormData();
    Object.keys(data).forEach(key => {
      if (key === 'ingredients' || key === 'add_ons') {
        formData.append(key, JSON.stringify(data[key]));
      } else if (key === 'image_url' && data[key] && data[key].startsWith('http')) {
        // If image_url is a URL, pass it directly
        formData.append('image_url', data[key]);
      } else if (key === 'image' && data[key]) {
        // If image is a file, append it to formData
        formData.append('image', data[key]);
      } else if (typeof data[key] === 'boolean') {
        // Convert boolean values to strings
        formData.append(key, data[key].toString());
      } else {
        formData.append(key, data[key] || '');
      }
    });
    return api.put(`/admin/item/${id}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  deleteItem: (id) => api.delete(`/admin/item/${id}`),
  getCategories: () => api.get('/admin/categories'),
  getCategory: (id) => api.get(`/admin/categories/${id}`),
  createCategory: (data) => api.post('/admin/categories', data),
  updateCategory: (id, data) => api.put(`/admin/categories/${id}`, data),
  deleteCategory: (id) => api.delete(`/admin/categories/${id}`),
  toggleItemAvailability: (id, isAvailable) => 
    api.patch(`/admin/menu/items/${id}/availability`, { is_available: isAvailable }),
  toggleItemFeatured: (id, isFeatured) => 
    api.patch(`/admin/menu/items/${id}/featured`, { is_featured: isFeatured }),
  
  // Add-ons
  getAddOns: () => api.get('/menu/add-ons'),
  createAddOn: (data) => api.post('/admin/menu/add-ons', data),
  updateAddOn: (id, data) => api.put(`/admin/menu/add-ons/${id}`, data),
  deleteAddOn: (id) => api.delete(`/admin/menu/add-ons/${id}`),
  
  // Bulk Operations
  bulkUpdateAvailability: (itemIds, isAvailable) => 
    api.patch('/admin/menu/items/bulk-availability', { item_ids: itemIds, is_available: isAvailable }),
  bulkUpdateFeatured: (itemIds, isFeatured) => 
    api.patch('/admin/menu/items/bulk-featured', { item_ids: itemIds, is_featured: isFeatured }),
  bulkDeleteItems: (itemIds) => 
    api.post('/admin/menu/items/bulk-delete', { item_ids: itemIds }),
  
  // Menu Stats
  getMenuStats: () => api.get('/admin/menu/stats'),
  
  // Search and Filters
  searchItems: (query) => api.get('/menu/items/search', { params: { q: query } }),
  filterItems: (filters) => api.get('/menu/items/filter', { params: filters })
};

// Promotion Service
const promotionService = {
  getAdminPromotions: (signal) => api.get('/admin/promotions', { signal }),
  createAdminPromotion: (data) => api.post('/admin/promotion', data),
  updateAdminPromotion: (id, data) => api.put(`/admin/promotion/${id}`, data),
  deleteAdminPromotion: (id) => api.delete(`/admin/promotion/${id}`),
  validatePromotion: (code) => api.post('/promotions/validate', { code }),
  getActivePromotions: () => api.get('/promotions/active')
};

// Order Service
const orderService = {
  getAllOrders: () => api.get('/admin/orders'),
  getOrderDetails: (id) => api.get(`/admin/orders/${id}`),
  updateOrderStatus: (id, status) => api.put(`/admin/orders/${id}/status`, { status }),
  updateOrderPaymentStatus: (id, payment_status) => api.put(`/admin/orders/${id}/payment`, { payment_status }),
  createOrder: (data) => api.post('/orders', data),
  getUserOrders: () => api.get('/orders/user'),
  cancelOrder: (id) => api.post(`/orders/${id}/cancel`),
  getOrderTracking: (id) => api.get(`/orders/${id}/tracking`)
};

export { api as default, promotionService, orderService };
