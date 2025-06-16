import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext.jsx'
import { GoogleLogin } from '@react-oauth/google'
import '../styles/Auth.css'

// Import icons from react-icons
import { FcGoogle } from 'react-icons/fc'

function Login() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })
  const [errors, setErrors] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { login } = useAuth()

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value,
    })
    
    // Clear errors when user starts typing
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: '',
      })
    }
  }

  const handleValidateForm = () => {
    let tempErrors = {}
    if (!formData.email) {
      tempErrors.email = 'Email is required'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      tempErrors.email = 'Email is invalid'
    }
    
    if (!formData.password) {
      tempErrors.password = 'Password is required'
    }
    
    setErrors(tempErrors)
    return Object.keys(tempErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!handleValidateForm()) return
    
    try {
      setIsSubmitting(true)
      await login(formData.email, formData.password)
      // No need to navigate - login function handles redirection
    } catch (error) {
      console.error('Login failed:', error)
      // Error message is shown via toast in the login function
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      setIsSubmitting(true)
      console.log('Google login success:', credentialResponse)
      // TODO: Implement Google login with credentialResponse
      // await loginWithGoogle(credentialResponse)
    } catch (error) {
      console.error('Google login failed:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleGoogleError = () => {
    console.error('Google login failed')
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1>Welcome Back</h1>
          <p>Sign in to continue to Qaffee Point</p>
        </div>
        
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email" className="form-label">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={errors.email ? 'has-error' : ''}
              placeholder="your@email.com"
            />
            {errors.email && <span className="form-error">{errors.email}</span>}
          </div>
          
          <div className="form-group">
            <label htmlFor="password" className="form-label">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className={errors.password ? 'has-error' : ''}
              placeholder="Your password"
            />
            {errors.password && <span className="form-error">{errors.password}</span>}
          </div>
          
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="remember"
                className="h-4 w-4 text-primary-600 border-gray-300 rounded"
              />
              <label htmlFor="remember" className="ml-2 text-sm text-gray-600">
                Remember me
              </label>
            </div>
            <Link to="/forgot-password" className="text-sm text-primary-600 hover:text-primary-500">
              Forgot password?
            </Link>
          </div>
          
          <button
            type="submit"
            className="auth-submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="auth-divider">
          <span>Or continue with</span>
        </div>

                  <div className="social-buttons">
          <div className="google-login-container">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              size="large"
              width="300"
              theme="outline"
              text="continue_with"
              shape="rectangular"
              locale="en"
              useOneTap={false}
            />
          </div>
        </div>
        
        <div className="auth-footer">
          <p>
            Don't have an account?{' '}
            <Link to="/signup">Sign up</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login