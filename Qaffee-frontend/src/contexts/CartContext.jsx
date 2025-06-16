import { createContext, useContext, useState, useCallback, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { toast } from 'react-toastify'

const CartContext = createContext()

export function CartProvider({ children }) {
  const { user } = useAuth()
  const [cart, setCart] = useState({ items: [], total: 0 })
  const [promoCode, setPromoCode] = useState(null)
  const [discount, setDiscount] = useState(0)

  const getCartKey = (userId) => `cart_${userId}`

  // Load cart on user login
  useEffect(() => {
    if (user?.id) {
      const stored = localStorage.getItem(getCartKey(user.id))
      if (stored) {
        setCart(JSON.parse(stored))
      } else {
        setCart({ items: [], total: 0 })
      }
    } else {
      setCart({ items: [], total: 0 })
      setPromoCode(null)
      setDiscount(0)
    }
  }, [user])

  // Save cart to localStorage when it changes (and user is logged in)
  useEffect(() => {
    if (user?.id) {
      localStorage.setItem(getCartKey(user.id), JSON.stringify(cart))
    }
  }, [cart, user])

  const calculateTotal = useCallback((items) => {
    return items.reduce((total, item) => {
      const itemPrice = item.price * item.quantity
      const optionsPrice = item.options ? 
        Object.values(item.options).reduce((acc, opt) => acc + (opt.price || 0) * item.quantity, 0) : 0
      return total + itemPrice + optionsPrice
    }, 0)
  }, [])

  const addToCart = useCallback((item, quantity = 1, options = {}) => {
    setCart(prev => {
      const index = prev.items.findIndex(i => i.id === item.id && JSON.stringify(i.options) === JSON.stringify(options))
      let newItems = [...prev.items]

      if (index >= 0) {
        newItems[index].quantity += quantity
      } else {
        newItems.push({ ...item, quantity, options })
      }

      const newTotal = calculateTotal(newItems)
      toast.success(`Added ${item.name} to cart`)
      return { items: newItems, total: newTotal }
    })
  }, [calculateTotal])

  const updateQuantity = useCallback((itemId, quantity, options = {}) => {
    setCart(prev => {
      const index = prev.items.findIndex(i => i.id === itemId && JSON.stringify(i.options) === JSON.stringify(options))
      if (index < 0) return prev

      let newItems = [...prev.items]
      if (quantity <= 0) {
        newItems.splice(index, 1)
      } else {
        newItems[index].quantity = quantity
      }

      return { items: newItems, total: calculateTotal(newItems) }
    })
  }, [calculateTotal])

  const removeFromCart = useCallback((itemId, options = {}) => {
    setCart(prev => {
      const newItems = prev.items.filter(i => !(i.id === itemId && JSON.stringify(i.options) === JSON.stringify(options)))
      toast.info('Item removed from cart')
      return { items: newItems, total: calculateTotal(newItems) }
    })
  }, [calculateTotal])

  const clearCart = useCallback(() => {
    setCart({ items: [], total: 0 })
    setPromoCode(null)
    setDiscount(0)
    toast.info('Cart cleared')
  }, [])

  const applyPromoCode = useCallback(async (code) => {
    try {
      const res = await fetch(`/api/promo-codes/${code}`)
      const data = await res.json()

      if (data.valid) {
        setPromoCode(code)
        setDiscount(data.discount)
        toast.success(`Promo code applied: ${data.discount}% off`)
        return true
      } else {
        toast.error('Invalid promo code')
        return false
      }
    } catch (err) {
      console.error(err)
      toast.error('Error applying promo code')
      return false
    }
  }, [])

  const removePromoCode = useCallback(() => {
    setPromoCode(null)
    setDiscount(0)
    toast.info('Promo code removed')
  }, [])

  const getCartSummary = useCallback(() => {
    const subtotal = cart.total
    const discountAmount = (subtotal * discount) / 100
    const total = subtotal - discountAmount

    return {
      subtotal,
      discount: discount ? { code: promoCode, amount: discountAmount } : null,
      total
    }
  }, [cart.total, discount, promoCode])

  const value = {
    cart,
    addToCart,
    updateQuantity,
    removeFromCart,
    clearCart,
    promoCode,
    discount,
    applyPromoCode,
    removePromoCode,
    getCartSummary
  }

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  )
}

export function useCart() {
  return useContext(CartContext)
}
