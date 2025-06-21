import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import './OrderDetails.css';

const OrderDetails = () => {
  const { id } = useParams();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOrderDetails = async () => {
      try {
        setOrder({
          id,
          date: '2024-03-15T14:30:00',
          status: 'completed',
          items: [
            { name: 'Cappuccino', quantity: 2, price: 8.00, notes: 'Extra hot' },
            { name: 'Croissant', quantity: 1, price: 9.50, notes: 'Butter on side' }
          ],
          subtotal: 25.50,
          tax: 2.55,
          total: 28.05,
          paymentMethod: 'Credit Card',
          deliveryAddress: '123 Coffee Street, Bean City, BC 12345',
          specialInstructions: 'Please ring doorbell on delivery'
        });
        setLoading(false);
      } catch (error) {
        console.error('Error fetching order details:', error);
        toast.error('Failed to fetch order details');
        setLoading(false);
      }
    };

    if (id) {
      fetchOrderDetails();
    }
  }, [id]);

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
        <h2 className="not-found-title">Order not found</h2>
        <p className="not-found-message">The order you're looking for doesn't exist</p>
        <Link
          to="/orders/history"
          className="back-button"
        >
          Back to Orders
        </Link>
      </div>
    );
  }

  return (
    <div className="order-details-container">
      <div className="order-details-card">
        <div className="order-details-header">
          <h1>Order Details</h1>
          <Link
            to="/orders/history"
            className="back-link"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Orders
          </Link>
        </div>

        <div className="info-grid">
          <div className="info-section">
            <h2>Order Information</h2>
            <div className="detail-item">
              <span className="detail-label">Order ID:</span>
              <span className="detail-value">#{order.id}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Date:</span>
              <span className="detail-value">
                {new Date(order.date).toLocaleString('en-US', {
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Status:</span>
              <span className="detail-value">
                <span className={`status-badge ${order.status}`}>
                  {order.status}
                </span>
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Payment Method:</span>
              <span className="detail-value">{order.paymentMethod}</span>
            </div>
          </div>

          <div className="info-section">
            <h2>Delivery Information</h2>
            <div className="detail-item">
              <span className="detail-label">Delivery Address:</span>
              <span className="detail-value">{order.deliveryAddress}</span>
            </div>
            {order.specialInstructions && (
              <div className="detail-item">
                <span className="detail-label">Special Instructions:</span>
                <span className="detail-value">{order.specialInstructions}</span>
              </div>
            )}
          </div>
        </div>

        <div className="items-section">
          <h2>Order Items</h2>
          <div className="space-y-2">
            {order.items.map((item, index) => (
              <div key={index} className="item-card">
                <div className="item-info">
                  <p className="item-name">{item.name}</p>
                  <div className="item-meta">
                    <p>Quantity: {item.quantity}</p>
                    {item.notes && <p>Notes: {item.notes}</p>}
                  </div>
                </div>
                <p className="item-price">${(item.price * item.quantity).toFixed(2)}</p>
              </div>
            ))}
          </div>

          <div className="summary-section">
            <div className="summary-item">
              <span className="summary-label">Subtotal</span>
              <span className="summary-value">${order.subtotal.toFixed(2)}</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Tax</span>
              <span className="summary-value">${order.tax.toFixed(2)}</span>
            </div>
            <div className="summary-total">
              <span>Total</span>
              <span>${order.total.toFixed(2)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderDetails;