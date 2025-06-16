import { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext.jsx'
import { useCart } from '../../contexts/CartContext.jsx'
import './Navbar.css'

function Navbar() {
  const { isAuthenticated, user, logout } = useAuth()
  const { cart } = useCart()
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  // Toggle mobile menu
  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen)
  }

  // Close mobile menu when changing routes
  useEffect(() => {
    setMobileMenuOpen(false)
  }, [location.pathname])

  // Change navbar style on scroll
  useEffect(() => {
    const handleScroll = () => {
      const isScrolled = window.scrollY > 50
      if (isScrolled !== scrolled) {
        setScrolled(isScrolled)
      }
    }

    window.addEventListener('scroll', handleScroll)
    return () => {
      window.removeEventListener('scroll', handleScroll)
    }
  }, [scrolled])

  // Determine if we're on the home page
  const isHomePage = location.pathname === '/'

  // Get cart item count
  const cartItemCount = cart?.items?.reduce((count, item) => count + item.quantity, 0) || 0

  return (
    <nav className={`navbar ${scrolled || !isHomePage ? 'navbar-scrolled' : ''}`}>
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <img src="/images/qaffee-logo.svg" alt="Qaffee Point" className="logo-img" />
          <span className="logo-text">Qaffee Point</span>
        </Link>
        
        <div className="navbar-mobile-toggle" onClick={toggleMobileMenu}>
          <div className={`hamburger ${mobileMenuOpen ? 'open' : ''}`}>
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
        
        <div className={`navbar-menu ${mobileMenuOpen ? 'open' : ''}`}>
          <div className="navbar-links">
            <Link to="/" className={location.pathname === '/' ? 'active' : ''}>
              Home
            </Link>
            <Link to="/menu" className={location.pathname.startsWith('/menu') ? 'active' : ''}>
              Menu
            </Link>
            <Link to="/branches" className={location.pathname === '/branches' ? 'active' : ''}>
              Locations
            </Link>
          </div>
          
          <div className="navbar-actions">
            {isAuthenticated ? (
              <>
                {user?.role === 'customer' && (
                  <Link to="/cart" className="cart-link">
                    <span className="cart-icon">🛒</span>
                    {cartItemCount > 0 && (
                      <span className="cart-count">{cartItemCount}</span>
                    )}
                  </Link>
                )}
                
                <div className="user-menu">
                  <div className="user-menu-trigger">
                    <span className="user-name">{user?.name || 'User'}</span>
                    <span className="user-arrow">▼</span>
                  </div>
                  
                  <div className="user-dropdown">
                    {user?.role === 'admin' && (
                      <Link to="/admin/dashboard" className="dropdown-item">Dashboard</Link>
                    )}
                    {user?.role === 'staff' && (
                      <Link to="/staff/orders" className="dropdown-item">Orders</Link>
                    )}
                    {user?.role === 'customer' && (
                      <>
                        <Link to="/account" className="dropdown-item">My Profile</Link>
                        <Link to="/orders/history" className="dropdown-item">Order History</Link>
                      </>
                    )}
                    <button onClick={logout} className="dropdown-item logout-btn">
                      Logout
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <>
                <Link to="/login" className="nav-login-btn">
                  Login
                </Link>
                <Link to="/signup" className="nav-signup-btn btn btn-primary">
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar