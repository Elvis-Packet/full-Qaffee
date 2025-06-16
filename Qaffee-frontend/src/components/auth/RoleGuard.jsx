import React, { Suspense } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext.jsx'
import Loader from '../ui/Loader.jsx'
import PropTypes from 'prop-types'

const LoadingFallback = () => (
  <div className="min-h-screen flex items-center justify-center">
    <Loader />
  </div>
)

export const RoleGuard = ({ roles, children, fallback = '/login' }) => {
  const { isAuthenticated, user, loading, authChecked } = useAuth()
  const location = useLocation()

  // Wait until the authentication check is complete
  if (loading || !authChecked) {
    return <LoadingFallback />
  }

  // Redirect if not authenticated
  if (!isAuthenticated || !user) {
    return <Navigate to={fallback} state={{ from: location }} replace />
  }

  // Check if user has required role
  if (roles && !roles.includes(user.role)) {
    let redirectPath = fallback

    if (user.role === 'admin') {
      redirectPath = '/admin/dashboard'
    } else if (user.role === 'staff') {
      redirectPath = '/staff/orders'
    } else {
      redirectPath = '/'
    }

    return <Navigate to={redirectPath} replace />
  }

  // Wrap children in Suspense to handle any lazy-loaded components
  return (
    <Suspense fallback={<LoadingFallback />}>
      {children}
    </Suspense>
  )
}

RoleGuard.propTypes = {
  roles: PropTypes.arrayOf(PropTypes.string).isRequired,
  children: PropTypes.node.isRequired,
  fallback: PropTypes.string
}

export default RoleGuard
