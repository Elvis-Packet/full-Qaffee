import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';

const StaffOrders = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('pending');

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        // TODO: Replace with actual API call
        // Mock data for demonstration
        const mockOrders = [
          {
            id: 1,
            orderNumber: 'ORD-001',
            customerName: 'John Doe',
            items: [
              { name: 'Cappuccino', quantity: 2, notes: 'Extra hot' },
              { name: 'Croissant', quantity: 1, notes: '' }
            ],
            status: 'pending',
            total: 15.50,
            createdAt: '2024-03-16T10:30:00Z',
            estimatedPickupTime: '2024-03-16T10:45:00Z'
          },
          {
            id: 2,
            orderNumber: 'ORD-002',
            customerName: 'Jane Smith',
            items: [
              { name: 'Latte', quantity: 1, notes: 'Soy milk' },
              { name: 'Blueberry Muffin', quantity: 1, notes: '' }
            ],
            status: 'in-progress',
            total: 12.00,
            createdAt: '2024-03-16T10:25:00Z',
            estimatedPickupTime: '2024-03-16T10:40:00Z'
          }
        ];

        setOrders(mockOrders);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching orders:', error);
        toast.error('Failed to fetch orders');
        setLoading(false);
      }
    };

    fetchOrders();
    // Set up polling for new orders
    const pollInterval = setInterval(fetchOrders, 30000);
    return () => clearInterval(pollInterval);
  }, []);

  const handleUpdateStatus = async (orderId, newStatus) => {
    try {
      // TODO: Implement actual API call to update order status
      setOrders(orders.map(order =>
        order.id === orderId ? { ...order, status: newStatus } : order
      ));
      toast.success(`Order ${orderId} status updated to ${newStatus}`);
    } catch (error) {
      console.error('Error updating order status:', error);
      toast.error('Failed to update order status');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'in-progress':
        return 'bg-blue-100 text-blue-800';
      case 'ready':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const filteredOrders = orders.filter(order => 
    filter === 'all' ? true : order.status === filter
  );

  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Staff Orders Dashboard</h1>
        <p className="mt-2 text-gray-600">Manage and track customer orders</p>
      </div>

      {/* Filter Controls */}
      <div className="mb-6">
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
        >
          <option value="all">All Orders</option>
          <option value="pending">Pending</option>
          <option value="in-progress">In Progress</option>
          <option value="ready">Ready for Pickup</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      {/* Orders List */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Order Details
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Items
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Time
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredOrders.map((order) => (
                <tr key={order.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">#{order.orderNumber}</div>
                    <div className="text-sm text-gray-500">{order.customerName}</div>
                    <div className="text-sm text-gray-500">${order.total.toFixed(2)}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">
                      {order.items.map((item, index) => (
                        <div key={index} className="mb-1">
                          {item.quantity}x {item.name}
                          {item.notes && (
                            <span className="text-gray-500 text-xs ml-2">({item.notes})</span>
                          )}
                        </div>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(order.status)}`}>
                      {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div>Created: {new Date(order.createdAt).toLocaleTimeString()}</div>
                    <div>Pickup: {new Date(order.estimatedPickupTime).toLocaleTimeString()}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {order.status === 'pending' && (
                      <button
                        onClick={() => handleUpdateStatus(order.id, 'in-progress')}
                        className="text-primary-600 hover:text-primary-900 mr-2"
                      >
                        Start
                      </button>
                    )}
                    {order.status === 'in-progress' && (
                      <button
                        onClick={() => handleUpdateStatus(order.id, 'ready')}
                        className="text-green-600 hover:text-green-900 mr-2"
                      >
                        Mark Ready
                      </button>
                    )}
                    {order.status === 'ready' && (
                      <button
                        onClick={() => handleUpdateStatus(order.id, 'completed')}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        Complete
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default StaffOrders; 