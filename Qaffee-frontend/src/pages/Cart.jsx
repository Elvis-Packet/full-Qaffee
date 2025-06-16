import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useCart } from '../contexts/CartContext'
import './Cart.css'

function Cart() {
  const { cart, updateQuantity, removeFromCart, clearCart, applyPromoCode, removePromoCode, getCartSummary } = useCart()
  const [promoInput, setPromoInput] = useState('')
  const [isApplyingPromo, setIsApplyingPromo] = useState(false)
  const navigate = useNavigate()
  
  const handleQuantityChange = (item, newQuantity) => {
    updateQuantity(item.id, newQuantity, item.options)
  }
  
  const handleRemoveItem = (item) => {
    removeFromCart(item.id, item.options)
  }
  
  const handleApplyPromo = async () => {
    if (!promoInput.trim()) return
    
    setIsApplyingPromo(true)
    try {
      const success = await applyPromoCode(promoInput)
      if (!success) {
        setPromoInput('')
      }
    } finally {
      setIsApplyingPromo(false)
    }
  }
  
  const handleRemovePromo = () => {
    removePromoCode()
    setPromoInput('')
  }
  
  const handleCheckout = () => {
    navigate('/checkout')
  }
  
  const summary = getCartSummary()

  return (
    <div className="cart-page">
      <div className="container">
        <h1>Your Cart</h1>
        
        {cart.items.length === 0 ? (
          <div className="empty-cart">
            <div className="empty-cart-icon">🛒</div>
            <h2>Your cart is empty</h2>
            <p>Looks like you haven't added any items to your cart yet.</p>
            <Link to="/menu" className="btn btn-primary">
              Explore Menu
            </Link>
          </div>
        ) : (
          <div className="cart-content">
            <div className="cart-items">
              <div className="cart-header">
                <h2>Items ({cart.items.reduce((sum, item) => sum + item.quantity, 0)})</h2>
                <button className="clear-cart-btn" onClick={clearCart}>
                  Clear Cart
                </button>
              </div>
              
              {cart.items.map((item) => (
                <div className="cart-item" key={`${item.id}-${JSON.stringify(item.options)}`}>
                  <div className="cart-item-image">
                    <img src={item.image} alt={item.name} />
                  </div>
                  
                  <div className="cart-item-details">
                    <h3>{item.name}</h3>
                    <p className="item-price">KSh{item.price.toFixed(2)}</p>
                    
                    {item.options && Object.keys(item.options).length > 0 && (
                      <div className="item-options">
                        {Object.entries(item.options).map(([key, value]) => (
                          <span key={key} className="item-option">
                            {key}: {typeof value === 'object' ? value.label : value}
                            {value.price && ` (KSh${value.price.toFixed(2)})`}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  <div className="cart-item-actions">
                    <div className="quantity-selector">
                      <button 
                        className="quantity-btn"
                        onClick={() => handleQuantityChange(item, Math.max(0, item.quantity - 1))}
                      >
                        -
                      </button>
                      <span className="quantity">{item.quantity}</span>
                      <button 
                        className="quantity-btn"
                        onClick={() => handleQuantityChange(item, item.quantity + 1)}
                      >
                        +
                      </button>
                    </div>
                    
                    <button 
                      className="remove-item-btn"
                      onClick={() => handleRemoveItem(item)}
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="cart-summary">
              <h2>Order Summary</h2>
              
              <div className="summary-row">
                <span>Subtotal</span>
                <span>Ksh{summary.subtotal.toFixed(2)}</span>
              </div>
              
              {summary.discount && (
                <div className="summary-row discount">
                  <span>
                    Discount ({summary.discount.code})
                    <button className="remove-promo" onClick={handleRemovePromo}>
                      ×
                    </button>
                  </span>
                  <span>-KSh{summary.discount.amount.toFixed(2)}</span>
                </div>
              )}
              
              <div className="summary-row total">
                <span>Total</span>
                <span>KSh{summary.total.toFixed(2)}</span>
              </div>
              
              {!summary.discount && (
                <div className="promo-code-form">
                  <div className="promo-input-group">
                    <input
                      type="text"
                      placeholder="Promo Code"
                      value={promoInput}
                      onChange={(e) => setPromoInput(e.target.value)}
                    />
                    <button 
                      className="btn btn-outline"
                      onClick={handleApplyPromo}
                      disabled={isApplyingPromo}
                    >
                      {isApplyingPromo ? 'Applying...' : 'Apply'}
                    </button>
                  </div>
                </div>
              )}
              
              <button 
                className="btn btn-primary checkout-btn"
                onClick={handleCheckout}
              >
                Proceed to Checkout
              </button>
              
              <div className="continue-shopping">
                <Link to="/menu">
                  ← Continue Shopping
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Cart