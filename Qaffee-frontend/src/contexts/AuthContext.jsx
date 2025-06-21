import { createContext, useContext, useState, useCallback, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import { toast } from 'react-toastify'

const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const [authChecked, setAuthChecked] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  // Initialize auth state on mount
  useEffect(() => {
    let isMounted = true
    
    const initializeAuth = async () => {
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          if (isMounted) {
            setIsAuthenticated(false)
            setUser(null)
            setLoading(false)
            setAuthChecked(true)
          }
          return
        }

        // Set token in API headers
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        
        // Verify token with backend
        const { data } = await api.get('/auth/me')
        if (data.user && isMounted) {
          setUser(data.user)
          setIsAuthenticated(true)
        }
      } catch (err) {
        console.error('Auth initialization failed:', err)
        if (isMounted) {
          // Clear invalid tokens
          localStorage.removeItem('token')
          localStorage.removeItem('refresh_token')
          delete api.defaults.headers.common['Authorization']
          setUser(null)
          setIsAuthenticated(false)
          setError(err)
        }
      } finally {
        if (isMounted) {
          setAuthChecked(true)
          setLoading(false)
        }
      }
    }

    initializeAuth()

    return () => {
      isMounted = false
    }
  }, [])

  const login = useCallback(async (email, password, isAdmin = false) => {
    try {
      setLoading(true)
      setError(null)
      const endpoint = isAdmin ? '/auth/admin-login' : '/auth/login'
      const { data } = await api.post(endpoint, { email, password })
      
      if (!data.token) {
        throw new Error('No token received from server')
      }
      
      // Store tokens
      localStorage.setItem('token', data.token)
      if (data.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token)
      }
      
      // Update auth state
      setUser(data.user)
      setIsAuthenticated(true)
      
      // Configure API with new token
      api.defaults.headers.common['Authorization'] = `Bearer ${data.token}`
      
      // Redirect based on role
      if (data.user.role === 'admin') {
        navigate('/admin/dashboard')
      } else if (data.user.role === 'staff') {
        navigate('/staff/orders')
      } else {
        navigate('/')
      }
      
      toast.success(`Welcome back, ${data.user.first_name}!`)
      return data
    } catch (error) {
      console.error('Login failed:', error)
      setError(error)
      const message = error.response?.data?.message || 'Login failed. Please try again.'
      toast.error(message)
      throw error
    } finally {
      setLoading(false)
    }
  }, [navigate])

  const signup = useCallback(async (userData) => {
    try {
      setLoading(true)
      setError(null)
      const { data } = await api.post('/auth/signup', userData)
      
      if (!data.token) {
        throw new Error('No token received from server')
      }
      
      // Store tokens and user data
      localStorage.setItem('token', data.token)
      if (data.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token)
      }
      
      // Configure API with new token
      api.defaults.headers.common['Authorization'] = `Bearer ${data.token}`
      
      setUser(data.user)
      setIsAuthenticated(true)
      
      navigate('/')
      toast.success('Account created successfully!')
      return data
    } catch (error) {
      console.error('Signup failed:', error)
      setError(error)
      toast.error(error.response?.data?.message || 'Signup failed. Please try again.')
      throw error
    } finally {
      setLoading(false)
    }
  }, [navigate])

  const logout = useCallback(() => {
    // Clear all auth data
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    delete api.defaults.headers.common['Authorization']
    setUser(null)
    setIsAuthenticated(false)
    setError(null)
    navigate('/login')
    toast.info('You have been logged out.')
  }, [navigate])

  const checkAuthStatus = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const token = localStorage.getItem('token')
      
      if (!token) {
        setIsAuthenticated(false)
        setUser(null)
        return false
      }
      
      // Set token in API headers
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      
      // Verify token with backend
      const { data } = await api.get('/auth/me')
      if (!data.user) {
        throw new Error('Invalid user data received')
      }
      
      setUser(data.user)
      setIsAuthenticated(true)
      return true
    } catch (error) {
      console.error('Auth check failed:', error)
      setError(error)
      // Clear invalid tokens
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      delete api.defaults.headers.common['Authorization']
      setUser(null)
      setIsAuthenticated(false)
      return false
    } finally {
      setAuthChecked(true)
      setLoading(false)
    }
  }, [])

  const updateProfile = useCallback(async (userData) => {
    try {
      setLoading(true)
      setError(null)
      const { data } = await api.put('/users/profile', userData)
      setUser(data.user)
      toast.success('Profile updated successfully!')
      return data
    } catch (error) {
      console.error('Profile update failed:', error)
      setError(error)
      toast.error(error.response?.data?.message || 'Failed to update profile. Please try again.')
      throw error
    } finally {
      setLoading(false)
    }
  }, [])

  const value = {
    user,
    isAuthenticated,
    loading,
    authChecked,
    error,
    login,
    signup,
    logout,
    checkAuthStatus,
    updateProfile
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}