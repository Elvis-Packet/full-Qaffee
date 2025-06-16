import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import './OrderHistory.css'; // CSS import

const OrderHistory = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        // Mock implementation
        setOrders([
          {
            id: '12345',
            date: '2024-03-15',
            total: 25.50,
            status: 'completed',
            items: [
              { name: 'Cappuccino', quantity: 2, price: 8.00 },
              { name: 'Croissant', quantity: 1, price: 9.50 }
            ]
          },
          {
            id: '12346',
            date: '2024-03-14',
            total: 18.00,
            status: 'completed',
            items: [
              { name: 'Latte', quantity: 2, price: 9.00 }
            ]
          }
        ]);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching orders:', error);
        toast.error('Failed to fetch order history');
        setLoading(false);
      }
    };

    fetchOrders();
  }, []);

  if (loading) {
    return (
      <div className="spinner-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="order-history-container">
      <div className="order-history-card">
        <div className="order-history-header">
          <h1>Order History</h1>
          <div className="header-actions">
            <button className="action-button">Filter</button>
            <button className="action-button">Sort</button>
          </div>
        </div>
        
        {orders.length === 0 ? (
          <div className="empty-state">
            <h2>No orders found</h2>
            <p>You haven't placed any orders yet</p>
            <Link to="/menu" className="browse-button">
              Browse Menu
            </Link>
          </div>
        ) : (
          <div className="orders-list">
            {orders.map(order => (
              <div key={order.id} className="order-card">
                <div className="order-header">
                  <div>
                    <div className="order-title">
                      <h3>Order #{order.id}</h3>
                      <span className={`status-badge ${order.status}`}>
                        {order.status}
                      </span>
                    </div>
                    <p className="order-date">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      {new Date(order.date).toLocaleDateString('en-US', { 
                        year: 'numeric', 
                        month: 'short', 
                        day: 'numeric' 
                      })}
                    </p>
                  </div>
                  <div className="order-total">
                    <p>${order.total.toFixed(2)}</p>
                  </div>
                </div>

                <div className="order-items">
                  <h4>Items</h4>
                  <ul>
                    {order.items.map((item, index) => (
                      <li key={index} className="order-item">
                        <div className="item-info">
                          <div className="item-thumbnail"></div>
                          <div>
                            <span className="item-name">{item.name}</span>
                            <p className="item-quantity">x{item.quantity}</p>
                          </div>
                        </div>
                        <span className="item-price">${(item.price * item.quantity).toFixed(2)}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="order-actions">
                  <Link to={`/orders/${order.id}`} className="view-details">
                    View Details
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                      <path d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                  </Link>
                </div>

                <div className="decorative-element"></div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default OrderHistory;