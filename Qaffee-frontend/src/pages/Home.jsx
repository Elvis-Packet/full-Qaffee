import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api.js'
import Loader from '../components/ui/Loader.jsx'
import './Home.css'

function Home() {
  const [menuItems, setMenuItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [currentPromoIndex, setCurrentPromoIndex] = useState(0)
  const [isPaused, setIsPaused] = useState(false)

  useEffect(() => {
    const fetchHomeData = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // Fetch all menu items from backend
        const response = await api.get('/menu/items')
        const items = response.data.items || []
        
        // Only set menu items if we have valid data
        if (Array.isArray(items) && items.length > 0) {
          setMenuItems(items)
        } else {
          // Fallback to mock data if API returns empty or invalid data
          setMenuItems([
            {
              id: 1,
              name: 'Hummus & Pita',
              description: 'Creamy chickpea dip with warm pita bread',
              price: 450.0,
              image_url: 'https://images.unsplash.com/photo-1633945274309-2c16cf9687a4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1470&q=80',
            },
            {
              id: 2,
              name: 'Falafel Plate',
              description: 'Crispy chickpea fritters with tahini sauce',
              price: 550.0,
              image_url: 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1470&q=80',
            },
            {
              id: 3,
              name: 'Shawarma Wrap',
              description: 'Tender spiced meat with vegetables in flatbread',
              price: 650.0,
              image_url: 'https://images.unsplash.com/photo-1601050690597-df0568f70950?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1470&q=80',
            },
            {
              id: 4,
              name: 'Classic Beef Burger',
              description: 'Juicy beef patty with fresh toppings',
              price: 750.0,
              image_url: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1598&q=80',
            },
          ])
        }
        
        setLoading(false)
      } catch (err) {
        console.error('Error fetching home data:', err)
        setError('Failed to load data. Please try again later.')
        setLoading(false)
      }
    }
    
    fetchHomeData()
  }, [])

  // Auto-rotate menu highlights
  useEffect(() => {
    if (menuItems.length > 0 && !isPaused) {
      const interval = setInterval(() => {
        setCurrentPromoIndex((prevIndex) => 
          (prevIndex + 1) % menuItems.length
        )
      }, 3000) // Rotate every 3 seconds
      
      return () => clearInterval(interval)
    }
  }, [menuItems.length, isPaused])

  // Ensure currentPromoIndex is valid
  useEffect(() => {
    if (currentPromoIndex >= menuItems.length) {
      setCurrentPromoIndex(0)
    }
  }, [menuItems.length, currentPromoIndex])

  if (loading) {
    return (
      <div className="home-page">
        <div className="container">
          <Loader />
        </div>
      </div>
    )
  }

  // Get current menu item safely
  const getCurrentMenuItem = () => {
    if (!Array.isArray(menuItems) || menuItems.length === 0) {
      return null
    }
    return menuItems[currentPromoIndex] || null
  }

  const currentItem = getCurrentMenuItem()

  return (
    <div className="home-page">
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">Experience Premium Coffee & Cuisine</h1>
          <p className="hero-subtitle">Handcrafted with love, served with passion</p>
          <div className="hero-cta">
            <Link to="/menu" className="btn btn-primary">Explore Menu</Link>
            <Link to="/signup" className="btn btn-outline">Join Loyalty Program</Link>
          </div>
        </div>
      </section>
      
      {error && (
        <div className="container">
          <div className="alert alert-error">
            {error}
          </div>
        </div>
      )}
      
      <section className="menu-highlights-section">
        <div className="container">
          <h2 className="section-title">Our Menu Highlights</h2>
          
          {currentItem ? (
            <div 
              className="highlights-container"
              onMouseEnter={() => setIsPaused(true)}
              onMouseLeave={() => setIsPaused(false)}
            >
              <div className="highlight-card">
                <div className="highlight-image">
                  <img 
                    src={currentItem.image_url || currentItem.image || '/images/placeholder-food.jpg'} 
                    alt={currentItem.name || 'Menu item'} 
                  />
                </div>
                <div className="highlight-content">
                  <h3 className="highlight-title">{currentItem.name || 'Menu item'}</h3>
                  <p className="highlight-description">{currentItem.description || 'No description available'}</p>
                  <div className="highlight-price">
                    {typeof currentItem.price === 'number'
                      ? `KSh ${currentItem.price.toFixed(2)}`
                      : 'Price not available'}
                  </div>
                  <div className="highlight-indicator">
                    {menuItems.map((_, index) => (
                      <span 
                        key={index}
                        className={`indicator-dot ${index === currentPromoIndex ? 'active' : ''}`}
                        onClick={() => setCurrentPromoIndex(index)}
                      />
                    ))}
                  </div>
                  {currentItem.id && (
                    <Link 
                      to={`/menu/item/${currentItem.id}`} 
                      className="btn btn-secondary"
                    >
                      View Details
                    </Link>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <p className="no-items">No menu items available</p>
          )}
        </div>
      </section>
      
      <section className="app-promo-section">
        <div className="container">
          <div className="app-promo-content">
            <h2>Get the full experience</h2>
            <p>Download our app for exclusive deals, faster ordering, and easy pickup</p>
            <div className="app-buttons">
              <a href="#" className="app-button">
                <span className="app-icon">📱</span>
                <span className="app-text">
                  <span className="app-store-text">Download on the</span>
                  <span className="app-store-name">App Store</span>
                </span>
              </a>
              <a href="#" className="app-button">
                <span className="app-icon">🤖</span>
                <span className="app-text">
                  <span className="app-store-text">GET IT ON</span>
                  <span className="app-store-name">Google Play</span>
                </span>
              </a>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Home