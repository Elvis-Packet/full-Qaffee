import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useCart } from '../contexts/CartContext.jsx'
import Loader from '../components/ui/Loader.jsx'
import FoodCarousel from '../components/FoodCarousel'
import api from '../services/api.js'
import '../styles/Menu.css'

const Menu = () => {
  const [categories, setCategories] = useState([])
  const [menuItems, setMenuItems] = useState([])
  const [activeCategory, setActiveCategory] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const { addToCart } = useCart()

  useEffect(() => {
    const fetchMenuData = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // Fetch categories - using the Flask RESTX endpoint
        const categoriesResponse = await api.get('/menu/categories')
        // The RESTX endpoint returns an array directly
        const categoriesData = categoriesResponse.data || []
        setCategories(categoriesData)
        
        // Set first category as active if categories exist
        if (categoriesData.length > 0) {
          setActiveCategory(categoriesData[0].id)
        }
        
        // Fetch all menu items - using the Flask RESTX endpoint
        const itemsResponse = await api.get('/menu/items')
        // The RESTX endpoint returns an array directly
        const itemsData = itemsResponse.data || []
        setMenuItems(itemsData)
        
      } catch (err) {
        console.error('Error fetching menu data:', err)
        setError('Failed to load menu. Please try again later.')
        // Set empty arrays to prevent undefined errors
        setCategories([])
        setMenuItems([])
      } finally {
        setLoading(false)
      }
    }

    fetchMenuData()
  }, [])

  const handleCategoryChange = (categoryId) => {
    setActiveCategory(categoryId)
  }

  const handleAddToCart = (item) => {
    addToCart({
      id: item.id,
      name: item.name,
      price: item.price,
      image: item.image_url,
      description: item.description
    })
  }

  const getItemsByCategory = (categoryId) => {
    return menuItems.filter(item => item.category_id === categoryId)
  }

  if (loading) {
    return (
      <div className="menu-section container">
        <Loader />
      </div>
    )
  }

  if (error) {
    return (
      <div className="menu-section container">
        <div className="alert alert-error">
          {error}
        </div>
      </div>
    )
  }

  return (
    <div className="menu-section container">
      <h2 className="section-title">Our Menu</h2>
      
      {categories.length > 0 ? (
        <>
          <div className="category-tabs">
            {categories.map(category => (
              <button
                key={category.id}
                className={`category-tab ${activeCategory === category.id ? 'active' : ''}`}
                onClick={() => handleCategoryChange(category.id)}
              >
                {category.name}
              </button>
            ))}
          </div>
          
          <div className="menu-items">
            {categories.map(category => (
              <div 
                key={category.id} 
                className={`menu-category ${activeCategory === category.id ? 'active' : ''}`}
              >
                <FoodCarousel category={category.id} />
                <div className="menu-grid">
                  {getItemsByCategory(category.id).length > 0 ? (
                    getItemsByCategory(category.id).map(item => (
                      <div className="menu-item card" key={item.id}>
                        {item.is_available && <span className="popular-badge">Available</span>}
                        <Link to={`/menu/item/${item.id}`} className="menu-item-image">
                          <img src={item.image_url || '/placeholder-food.jpg'} alt={item.name} />
                        </Link>
                        <div className="menu-item-content">
                          <Link to={`/menu/item/${item.id}`} className="menu-item-name">{item.name}</Link>
                          <p className="menu-item-description">{item.description}</p>
                          <div className="menu-item-footer">
                            <span className="menu-item-price">KSh {item.price.toFixed(2)}</span>
                            <button 
                              className="btn-add-to-cart"
                              onClick={() => handleAddToCart(item)}
                              disabled={!item.is_available}
                            >
                              {item.is_available ? 'Add to Cart' : 'Not Available'}
                            </button>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="no-items">No items available in this category</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      ) : (
        <p className="no-categories">No menu categories available</p>
      )}
      
      <div className="menu-note">
        <p>* All our dishes are prepared fresh daily with high-quality ingredients</p>
        <p>* Special dietary requirements can be accommodated upon request</p>
      </div>
    </div>
  )
}

export default Menu