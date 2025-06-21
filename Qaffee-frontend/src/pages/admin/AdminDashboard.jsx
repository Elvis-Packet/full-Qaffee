import React, { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import api from '../../services/api'
import AdminSidebar from '../../components/admin/AdminSidebar.jsx'
import '../styles/Admin.css'

const AdminDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Memoize the fetch function to prevent recreation on every render
  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await api.get('/admin/dashboard')
      setDashboardData(response.data)
    } catch (err) {
      console.error('Error fetching dashboard data:', err)
      setError('Failed to load dashboard data. Please try again later.')
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }, [])

  // Use strict mode safe useEffect
  useEffect(() => {
    let mounted = true

    const loadData = async () => {
      try {
        await fetchDashboardData()
      } catch (err) {
        if (mounted) {
          console.error('Dashboard load error:', err)
        }
      }
    }

    loadData()

    return () => {
      mounted = false
    }
  }, [fetchDashboardData])

  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date)
  }

  const getStatusClass = (status) => {
    switch (status.toLowerCase()) {
      case 'pending': return 'text-yellow-800 bg-yellow-100'
      case 'processing': return 'text-blue-800 bg-blue-100'
      case 'completed': return 'text-green-800 bg-green-100'
      case 'cancelled': return 'text-red-800 bg-red-100'
      default: return 'text-gray-800 bg-gray-100'
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error) {
    return <div className="error">{error}</div>
  }

  if (!dashboardData) {
    return null
  }

  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Admin Dashboard</h1>
        <p className="mt-2 text-gray-600">Overview of your coffee shop's performance</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-medium text-gray-500">Total Orders</h3>
          <p className="mt-2 text-3xl font-bold">{dashboardData.order_stats.total_orders}</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-medium text-gray-500">Pending Orders</h3>
          <p className="mt-2 text-3xl font-bold">{dashboardData.order_stats.orders_today}</p>
          <div className="mt-2">
            <Link to="/admin/orders" className="text-sm text-primary-600 hover:text-primary-700">
              View all orders →
            </Link>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-medium text-gray-500">Total Revenue</h3>
          <p className="mt-2 text-3xl font-bold">${dashboardData.revenue_stats.total_revenue.toFixed(2)}</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-medium text-gray-500">Active Users</h3>
          <p className="mt-2 text-3xl font-bold">{dashboardData.user_stats.active_users}</p>
          <div className="mt-2">
            <Link to="/admin/users" className="text-sm text-primary-600 hover:text-primary-700">
              View all users →
            </Link>
          </div>
        </div>
      </div>

      {/* Popular Items & Recent Orders */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold mb-4">Popular Items</h2>
          {dashboardData.popular_items && dashboardData.popular_items.length > 0 ? (
            <ul className="divide-y divide-gray-200">
              {dashboardData.popular_items.map((item) => (
                <li key={item.id} className="py-3">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-medium">{item.name}</p>
                      <p className="text-sm text-gray-500">{item.total_orders} orders</p>
                    </div>
                    <p className="text-primary-600">${item.total_revenue.toFixed(2)}</p>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500 text-sm">No data available</p>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold mb-4">Recent Orders</h2>
          {dashboardData.recent_orders && dashboardData.recent_orders.length > 0 ? (
            <ul className="divide-y divide-gray-200">
              {dashboardData.recent_orders.map((order) => (
                <li key={order.id} className="py-3">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-medium">Order #{order.order_number}</p>
                      <p className="text-sm text-gray-500">{order.customer_name}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-primary-600">${order.total.toFixed(2)}</p>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusClass(order.status)}`}>
                        {order.status}
                      </span>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500 text-sm">No recent orders</p>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link to="/admin/orders" className="p-4 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow flex items-center space-x-3">
          <span className="text-primary-600">📋</span>
          <span className="font-medium">Manage Orders</span>
        </Link>
        <Link to="/admin/menu" className="p-4 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow flex items-center space-x-3">
          <span className="text-primary-600">☕</span>
          <span className="font-medium">Update Menu</span>
        </Link>
        <Link to="/admin/users" className="p-4 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow flex items-center space-x-3">
          <span className="text-primary-600">👥</span>
          <span className="font-medium">Manage Users</span>
        </Link>
        <Link to="/admin/promotions" className="p-4 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow flex items-center space-x-3">
          <span className="text-primary-600">🎯</span>
          <span className="font-medium">Promotions</span>
        </Link>
      </div>
    </div>
  )
}

export default AdminDashboard
