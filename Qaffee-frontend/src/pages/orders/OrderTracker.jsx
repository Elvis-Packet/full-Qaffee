import { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import api from '../../services/api';
import './OrderTracker.css';

const OrderTracker = () => {
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const { orderId } = useParams();
  const intervalRef = useRef(null);
  
  // Map backend statuses to frontend timeline
  const mapStatusToTimeline = (status) => {
    const statusMap = {
      'pending': 'placed',
      'awaiting_payment': 'placed',
      'confirmed': 'confirmed',
      'preparing': 'preparing',
      'ready_for_pickup': 'ready',
      'out_for_delivery': 'ready',
      'completed': 'completed'
    };
    return statusMap[status] || 'placed';
  };

  const orderStatuses = [
    { id: 'placed', label: 'Order Placed' },
    { id: 'confirmed', label: 'Order Confirmed' },
    { id: 'preparing', label: 'Preparing' },
    { id: 'ready', label: order?.is_delivery ? 'Out for Delivery' : 'Ready for Pickup' },
    { id: 'completed', label: 'Completed' }
  ];

  const fetchOrderStatus = async () => {
    try {
      const response = await api.get(`/order/${orderId}`);
      
      // Transform backend data to frontend format
      const orderData = response.data;
      const transformedOrder = {
        id: orderData.id,
        status: mapStatusToTimeline(orderData.status),
        items: orderData.items.map(item => ({
          name: item.menu_item_name || 'Item',
          quantity: item.quantity
        })),
        estimatedTime: 'Calculating...', // You can implement actual ETA logic
        is_delivery: orderData.is_delivery
      };
      
      setOrder(transformedOrder);
      setLoading(false);
      
      // Stop polling if order is completed or cancelled
      if (['completed', 'cancelled_by_user', 'cancelled_by_admin', 'failed'].includes(orderData.status)) {
        clearInterval(intervalRef.current);
      }
    } catch (error) {
      console.error('Error fetching order:', error);
      if (error.response?.status === 404) {
        setOrder(null);
      }
      toast.error('Failed to fetch order status');
      setLoading(false);
      clearInterval(intervalRef.current);
    }
  };

  useEffect(() => {
    fetchOrderStatus();
    
    // Set up polling every 30 seconds
    intervalRef.current = setInterval(fetchOrderStatus, 30000);
    
    return () => {
      clearInterval(intervalRef.current);
    };
  }, [orderId]);

  if (loading) {
    return (
      <div className="spinner-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="not-found-container">
        <h2 className="not-found-title">No order found</h2>
        <p className="not-found-message">Please check your order ID and try again</p>
      </div>
    );
  }

  const currentStatusIndex = orderStatuses.findIndex(s => s.id === order.status);

  return (
    <div className="order-tracker-container">
      <div className="order-tracker-card">
        <h1 className="order-tracker-title">Order Status</h1>
        
        <div className="order-header">
          <div className="order-id">Order #{order.id}</div>
          <div className="estimated-time">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Est. Time: {order.estimatedTime}
          </div>
        </div>

        {/* Status Timeline */}
        <div className="timeline-container">
          <div className="timeline-track">
            <div 
              className="timeline-progress" 
              style={{ width: `${(currentStatusIndex / (orderStatuses.length - 1)) * 100}%` }}
            ></div>
          </div>
          
          <div className="timeline-steps">
            {orderStatuses.map((status, index) => {
              const statusClass = 
                index < currentStatusIndex ? 'completed' :
                index === currentStatusIndex ? 'active' : 'inactive';
                
              return (
                <div 
                  key={status.id} 
                  className={`timeline-step ${statusClass}`}
                >
                  <div className={`timeline-marker ${statusClass}`}>
                    {index < currentStatusIndex ? '✓' : index === currentStatusIndex ? '•' : index + 1}
                  </div>
                  <div className="timeline-label">{status.label}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Order Items */}
        <div className="order-items-container">
          <h3 className="order-items-title">Order Items</h3>
          <ul className="order-items-list">
            {order.items.map((item, index) => (
              <li key={index} className="order-item">
                <span className="item-name">{item.name}</span>
                <span className="item-quantity">x{item.quantity}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default OrderTracker;