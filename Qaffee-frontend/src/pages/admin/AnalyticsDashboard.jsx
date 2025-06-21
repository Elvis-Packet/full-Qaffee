import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import api from '../../services/api';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';

const AnalyticsDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('week');
  const [metrics, setMetrics] = useState({
    salesData: [],
    orderData: [],
    topProducts: [],
    customerMetrics: {
      totalCustomers: 0,
      newCustomers: 0,
      returningCustomers: 0,
      averageOrderValue: 0
    }
  });

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const [dashboardRes, salesRes, menuRes, customersRes] = await Promise.all([
          api.get('/analytics/dashboard'),
          api.get('/analytics/sales/daily?days=7'),
          api.get('/analytics/items/popular?limit=5'),
          api.get('/analytics/users/activity')
        ]);

        const dashboardData = dashboardRes.data;
        const salesData = salesRes.data;
        const topProducts = menuRes.data;
        const customerActivity = customersRes.data;

        setMetrics({
          salesData: salesData.map(item => ({
            date: item.date,
            sales: item.value,
            orders: 0 // You might need another endpoint for orders by day
          })),
          orderData: [], // You might need to fetch this separately
          topProducts: topProducts.map(item => ({
            name: item.name,
            sales: item.total_orders,
            revenue: item.total_revenue
          })),
          customerMetrics: {
            totalCustomers: customerActivity.total_users,
            newCustomers: 0, // You might need another endpoint for new customers
            returningCustomers: customerActivity.active_users,
            averageOrderValue: customerActivity.average_orders_per_user
          }
        });
        setLoading(false);
      } catch (error) {
        console.error('Error fetching analytics:', error);
        toast.error('Failed to fetch analytics data');
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [timeRange]);

  // ... rest of the component remains the same ...
};

export default AnalyticsDashboard;