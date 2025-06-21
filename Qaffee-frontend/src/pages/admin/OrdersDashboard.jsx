import React, { useState, useEffect } from 'react';
import { orderService } from '../../services/api';
import { toast } from 'react-hot-toast';
import './OrdersDashboard.css';

const OrdersDashboard = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState('all');

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const response = await orderService.getAllOrders();
      setOrders(response.data || []);
    } catch (error) {
      toast.error('Failed to fetch orders');
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateOrderStatus = async (orderId, newStatus) => {
    try {
      await orderService.updateOrderStatus(orderId, newStatus);
      toast.success('Order status updated successfully');
      fetchOrders(); // Refresh orders list
    } catch (error) {
      toast.error('Failed to update order status');
      console.error('Error updating order status:', error);
    }
  };

  const updatePaymentStatus = async (orderId, newStatus) => {
    try {
      await orderService.updateOrderPaymentStatus(orderId, newStatus);
      toast.success('Payment status updated successfully');
      fetchOrders(); // Refresh orders list
    } catch (error) {
      toast.error('Failed to update payment status');
      console.error('Error updating payment status:', error);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'PENDING': 'bg-yellow-200',
      'CONFIRMED': 'bg-blue-200',
      'PREPARING': 'bg-orange-200',
      'READY_FOR_PICKUP': 'bg-purple-200',
      'OUT_FOR_DELIVERY': 'bg-indigo-200',
      'COMPLETED': 'bg-green-200',
      'CANCELLED': 'bg-red-200'
    };
    return colors[status] || 'bg-gray-200';
  };

  const filteredOrders = selectedStatus === 'all' 
    ? orders 
    : orders.filter(order => order.status === selectedStatus);

  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Orders Dashboard</h1>
      
      <div className="mb-6">
        <select 
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
          className="p-2 border rounded"
        >
          <option value="all">All Orders</option>
          <option value="PENDING">Pending</option>
          <option value="CONFIRMED">Confirmed</option>
          <option value="PREPARING">Preparing</option>
          <option value="READY_FOR_PICKUP">Ready for Pickup</option>
          <option value="OUT_FOR_DELIVERY">Out for Delivery</option>
          <option value="COMPLETED">Completed</option>
          <option value="CANCELLED">Cancelled</option>
        </select>
      </div>

      <div className="grid gap-6">
        {filteredOrders.map((order) => (
          <div key={order.id} className="border rounded-lg p-4 shadow-sm">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold">Order #{order.id}</h3>
                <p className="text-gray-600">
                  {new Date(order.created_at).toLocaleString()}
                </p>
              </div>
              <div className="flex gap-2">
                <span className={`px-3 py-1 rounded ${getStatusColor(order.status)}`}>
                  {order.status}
                </span>
                <span className={`px-3 py-1 rounded ${order.payment_status === 'PAID' ? 'bg-green-200' : 'bg-red-200'}`}>
                  {order.payment_status}
                </span>
              </div>
            </div>

            <div className="mb-4">
              <h4 className="font-semibold mb-2">Customer Details</h4>
              <p>Name: {order.user?.name}</p>
              <p>Email: {order.user?.email}</p>
              <p>Phone: {order.user?.phone}</p>
            </div>

            <div className="mb-4">
              <h4 className="font-semibold mb-2">Order Items</h4>
              <div className="space-y-2">
                {order.items.map((item, index) => (
                  <div key={index} className="flex justify-between">
                    <span>{item.quantity}x {item.menu_item.name}</span>
                    <span>KSh {item.subtotal.toFixed(2)}</span>
                  </div>
                ))}
              </div>
              <div className="mt-2 pt-2 border-t">
                <div className="flex justify-between font-semibold">
                  <span>Total</span>
                  <span>KSh {order.total_amount.toFixed(2)}</span>
                </div>
              </div>
            </div>

            {order.is_delivery && order.delivery_address && (
              <div className="mb-4">
                <h4 className="font-semibold mb-2">Delivery Address</h4>
                <p>{order.delivery_address.address_line1}</p>
                <p>{order.delivery_address.address_line2}</p>
                <p>{order.delivery_address.city}</p>
              </div>
            )}

            <div className="flex gap-4 mt-4">
              <select
                value={order.status}
                onChange={(e) => updateOrderStatus(order.id, e.target.value)}
                className="p-2 border rounded"
              >
                <option value="PENDING">Pending</option>
                <option value="CONFIRMED">Confirmed</option>
                <option value="PREPARING">Preparing</option>
                <option value="READY_FOR_PICKUP">Ready for Pickup</option>
                <option value="OUT_FOR_DELIVERY">Out for Delivery</option>
                <option value="COMPLETED">Completed</option>
                <option value="CANCELLED">Cancelled</option>
              </select>

              <select
                value={order.payment_status}
                onChange={(e) => updatePaymentStatus(order.id, e.target.value)}
                className="p-2 border rounded"
              >
                <option value="PENDING">Payment Pending</option>
                <option value="PAID">Paid</option>
                <option value="FAILED">Failed</option>
                <option value="REFUNDED">Refunded</option>
              </select>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default OrdersDashboard; 