import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { useCart } from '../contexts/CartContext';
import { config } from '../config';
import PaymentSimulator from '../components/PaymentSimulator';
import PaymentForm from '../components/PaymentForm';
import MpesaPayment from '../components/payment/MpesaPayment';
import DeliveryLocationPicker from '../components/DeliveryLocationPicker';
import orderService from '../services/orderService';
import './Checkout.css'; 

const BRANCH_HOURS = {
  weekday: '7:00 AM - 11:00 PM',
  weekend: '8:00 AM - 11:00 PM'
};

function Checkout() {
  const { user } = useAuth();
  const { cart, getCartSummary, clearCart } = useCart();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [deliveryMethod, setDeliveryMethod] = useState('delivery');
  const [selectedBranch, setSelectedBranch] = useState(null);
  const [branches] = useState([
    {
      id: 1,
      name: 'Qaffee Point - Mombasa',
      address: 'Nyerere Avenue, Mombasa, Kenya',
      phone: '+254 758 222222',
      coordinates: {
        lat: -4.0435,
        lng: 39.6682
      },
      features: ['Dine-in', 'Takeaway', 'WiFi']
    },
    {
      id: 2,
      name: 'Qaffee Point - Nairobi Westlands',
      address: 'THE OVAL BUILDING, RING ROAD, PRR4+G5H, Nairobi',
      phone: '+254 759 111111',
      coordinates: {
        lat: -1.2648,
        lng: 36.8050
      },
      features: ['Dine-in', 'Takeaway', 'WiFi', 'Outdoor Seating']
    }
  ]);
  const [customizations, setCustomizations] = useState({});
  const [promoCode, setPromoCode] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('');
  const [deliveryLocation, setDeliveryLocation] = useState('');
  const [locationData, setLocationData] = useState(null);
  const [mpesaNumber, setMpesaNumber] = useState('');
  const [cardDetails, setCardDetails] = useState({
    number: '',
    expiry: '',
    cvc: '',
    name: ''
  });
  const [orderId, setOrderId] = useState(null);
  const [mapsLoaded, setMapsLoaded] = useState(false);

  // Load Google Maps script
  useEffect(() => {
    const initializeMaps = async () => {
      try {
        await loadGoogleMapsApi();
        setMapsLoaded(true);
      } catch (error) {
        console.error('Failed to load Google Maps:', error);
        toast.error('Failed to load location services');
      }
    };

    if (deliveryMethod === 'delivery') {
      initializeMaps();
    }
  }, [deliveryMethod]);

  // Initialize autocomplete when maps are loaded
  useEffect(() => {
    if (mapsLoaded && deliveryMethod === 'delivery') {
      const input = document.getElementById('delivery-location-input');
      if (input) {
        const autocomplete = new window.google.maps.places.Autocomplete(input, config.googleMaps.options);

        autocomplete.addListener('place_changed', () => {
          const place = autocomplete.getPlace();
          if (place.formatted_address) {
            setDeliveryLocation(place.formatted_address);
          }
        });
      }
    }
  }, [mapsLoaded, deliveryMethod]);

  const summary = getCartSummary();

  const handleOrderCreation = async (paymentDetails) => {
    try {
      setLoading(true);

      // Create order data
      const orderData = {
        items: cart.items.map(item => ({
          menu_item_id: item.id,
          quantity: item.quantity,
          customization: customizations[item.id] || {}
        })),
        delivery_method: deliveryMethod,
        payment_method: paymentMethod,
        total_amount: summary.total,
        is_delivery: deliveryMethod === 'delivery',
        delivery_location: deliveryMethod === 'delivery' ? locationData : null,
        pickup_branch: deliveryMethod === 'pickup' ? selectedBranch : null,
        payment_details: paymentDetails,
        status: 'pending'
      };

      // Create the order
      const response = await orderService.createOrder(orderData);
      
      if (!response.id) {
        throw new Error('Invalid response from server');
      }

      // Set the order ID
      setOrderId(response.id);

      // Return the order ID for M-Pesa payment
      return response.id;
    } catch (error) {
      console.error('Error creating order:', error);
      toast.error('Failed to create order. Please try again.');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const handlePaymentComplete = async (paymentDetails) => {
    try {
      // For M-Pesa, the order is already created
      if (paymentMethod === 'mpesa') {
        clearCart();
        navigate(`/orders/${orderId}`);
      } else {
        await handleOrderCreation(paymentDetails);
      }
    } catch (error) {
      console.error('Error completing payment:', error);
      toast.error('Failed to complete payment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLocationSelect = (data) => {
    setLocationData(data);
    setDeliveryLocation(data.address);
  };

  const getBranchHours = () => {
    const today = new Date().getDay();
    return today === 0 || today === 6 ? BRANCH_HOURS.weekend : BRANCH_HOURS.weekday;
  };

  const isCurrentlyOpen = () => {
    const now = new Date();
    const hours = now.getHours();
    return hours >= 7 && hours < 23;
  };

  const renderBranchSelection = () => {
    if (deliveryMethod !== 'pickup') return null;

    const currentHours = getBranchHours();
    const isOpen = isCurrentlyOpen();

    return (
      <div className="branch-selection-container">
        <h3>Select Pickup Branch</h3>
        <p className="branch-selection-hint">
          Choose the most convenient branch for your pickup. Your order will be prepared at the selected branch.
        </p>
        <div className="branch-options">
          {branches.map((branch) => (
            <div
              key={branch.id}
              className={`branch-option ${selectedBranch?.id === branch.id ? 'selected' : ''}`}
              onClick={() => setSelectedBranch(branch)}
            >
              <div className="branch-option-content">
                <div className="branch-header">
                  <h4>{branch.name}</h4>
                  <span className={`branch-status ${isOpen ? 'open' : 'closed'}`}>
                    {isOpen ? 'Open' : 'Closed'}
                  </span>
                </div>
                
                <div className="branch-info">
                  <p className="branch-address">
                    <svg viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                    </svg>
                    {branch.address}
                  </p>
                  <p className="branch-hours">
                    <svg viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 002 0V6z" clipRule="evenodd" />
                    </svg>
                    Today: {currentHours}
                  </p>
                  <p className="branch-phone">
                    <svg viewBox="0 0 20 20" fill="currentColor">
                      <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
                    </svg>
                    {branch.phone}
                  </p>
                  <div className="branch-features">
                    {branch.features.map((feature, index) => (
                      <span key={index} className="feature-tag">
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="branch-actions">
                  <button
                    type="button"
                    className="map-link-button"
                    onClick={(e) => {
                      e.stopPropagation();
                      window.open(
                        `https://www.google.com/maps/search/?api=1&query=${branch.coordinates.lat},${branch.coordinates.lng}`,
                        '_blank'
                      );
                    }}
                  >
                    <svg className="map-icon" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                    </svg>
                    View on Map
                  </button>
                  <button
                    type="button"
                    className={`select-branch-button ${selectedBranch?.id === branch.id ? 'selected' : ''}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedBranch(branch);
                    }}
                  >
                    {selectedBranch?.id === branch.id ? 'Selected for Pickup' : 'Select for Pickup'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
        {!selectedBranch && (
          <p className="branch-selection-error">
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            Please select a branch to continue with your order
          </p>
        )}
      </div>
    );
  };

  const renderPaymentDetails = () => {
    switch (paymentMethod) {
      case 'mpesa':
        return (
          <MpesaPayment 
            amount={summary.total}
            orderId={orderId}
            onPaymentComplete={handlePaymentComplete}
            onInitiate={async (paymentDetails) => {
              // Create order first
              const createdOrderId = await handleOrderCreation({
                type: 'mpesa',
                ...paymentDetails
              });
              return createdOrderId;
            }}
          />
        );
      case 'card':
        return (
          <div className="payment-details">
            <h3>Card Details</h3>
            <div className="form-group">
              <label>Card Number</label>
              <input
                type="text"
                placeholder="1234 5678 9012 3456"
                value={cardDetails.number}
                onChange={(e) => setCardDetails({ ...cardDetails, number: e.target.value })}
                className="form-input"
                maxLength="19"
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Expiry Date</label>
                <input
                  type="text"
                  placeholder="MM/YY"
                  value={cardDetails.expiry}
                  onChange={(e) => setCardDetails({ ...cardDetails, expiry: e.target.value })}
                  className="form-input"
                  maxLength="5"
                />
              </div>
              <div className="form-group">
                <label>CVC</label>
                <input
                  type="text"
                  placeholder="123"
                  value={cardDetails.cvc}
                  onChange={(e) => setCardDetails({ ...cardDetails, cvc: e.target.value })}
                  className="form-input"
                  maxLength="3"
                />
              </div>
            </div>
            <div className="form-group">
              <label>Cardholder Name</label>
              <input
                type="text"
                placeholder="Name on card"
                value={cardDetails.name}
                onChange={(e) => setCardDetails({ ...cardDetails, name: e.target.value })}
                className="form-input"
              />
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  const handleSubmit = async () => {
    if (!paymentMethod) {
      toast.error('Please select a payment method');
      return;
    }

    if (deliveryMethod === 'delivery' && !locationData) {
      toast.error('Please select a delivery location');
      return;
    }

    try {
      setLoading(true);

      // Handle different payment methods
      switch (paymentMethod) {
        case 'mpesa':
          // M-Pesa payment is handled by the MpesaPayment component
          break;
        case 'card':
          // Validate card details
          if (!cardDetails.number || !cardDetails.expiry || !cardDetails.cvc || !cardDetails.name) {
            toast.error('Please fill in all card details');
            return;
          }
          await handleOrderCreation({
            type: 'card',
            details: cardDetails
          });
          break;
        case 'cash':
          await handleOrderCreation({
            type: 'cash',
            details: { payOnDelivery: true }
          });
          break;
        default:
          toast.error('Invalid payment method');
          return;
      }
    } catch (error) {
      console.error('Error processing order:', error);
      toast.error('Failed to process order. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="checkout-page">
      <div className="checkout-container">
        <h1>Checkout</h1>

        {/* Cart Items */}
        <div className="cart-items">
          {cart.items.map((item, index) => (
            <div key={index} className="cart-item">
              <div className="item-details">
                <h3>{item.name}</h3>
                <p>Quantity: {item.quantity}</p>
                <p>KSh {item.price.toFixed(2)}</p>
              </div>
              <div className="item-customizations">
                <label>
                  <input
                    type="checkbox"
                    checked={customizations[item.id]?.extraSauce || false}
                    onChange={(e) => {
                      setCustomizations(prev => ({
                        ...prev,
                        [item.id]: { ...prev[item.id], extraSauce: e.target.checked }
                      }));
                    }}
                  />
                  Extra Sauce (+KSh 50)
                </label>
                <label>
                  <input
                    type="checkbox"
                    checked={customizations[item.id]?.extraCheese || false}
                    onChange={(e) => {
                      setCustomizations(prev => ({
                        ...prev,
                        [item.id]: { ...prev[item.id], extraCheese: e.target.checked }
                      }));
                    }}
                  />
                  Extra Cheese (+KSh 100)
                </label>
              </div>
            </div>
          ))}
        </div>

        {/* Payment Method Selection */}
        <div className="payment-methods">
          <h2>Select Payment Method</h2>
          <div className="payment-options">
            <label className={`payment-option ${paymentMethod === 'mpesa' ? 'selected' : ''}`}>
              <input
                type="radio"
                name="payment"
                value="mpesa"
                checked={paymentMethod === 'mpesa'}
                onChange={(e) => setPaymentMethod(e.target.value)}
              />
              <span>M-Pesa</span>
            </label>
            <label className={`payment-option ${paymentMethod === 'card' ? 'selected' : ''}`}>
              <input
                type="radio"
                name="payment"
                value="card"
                checked={paymentMethod === 'card'}
                onChange={(e) => setPaymentMethod(e.target.value)}
              />
              <span>Card Payment</span>
            </label>
            <label className={`payment-option ${paymentMethod === 'cash' ? 'selected' : ''}`}>
              <input
                type="radio"
                name="payment"
                value="cash"
                checked={paymentMethod === 'cash'}
                onChange={(e) => setPaymentMethod(e.target.value)}
              />
              <span>Cash on Delivery</span>
            </label>
          </div>
          {renderPaymentDetails()}
        </div>

        {/* Delivery Method */}
        <div className="delivery-method-section">
          <h2>Delivery Method</h2>
          <div className="delivery-options">
            <button
              type="button"
              className={`delivery-option ${deliveryMethod === 'delivery' ? 'selected' : ''}`}
              onClick={() => {
                setDeliveryMethod('delivery');
                setSelectedBranch(null);
              }}
            >
              <span className="option-icon">🚚</span>
              <span className="option-text">Delivery</span>
            </button>
            <button
              type="button"
              className={`delivery-option ${deliveryMethod === 'pickup' ? 'selected' : ''}`}
              onClick={() => {
                setDeliveryMethod('pickup');
                setDeliveryLocation('');
                setLocationData(null);
              }}
            >
              <span className="option-icon">🏪</span>
              <span className="option-text">Pickup</span>
            </button>
          </div>

          {deliveryMethod === 'delivery' && (
            <DeliveryLocationPicker
              deliveryLocation={deliveryLocation}
              setDeliveryLocation={setDeliveryLocation}
              googleMapsApiKey={config.googleMaps.apiKey}
              onLocationSelect={handleLocationSelect}
              branches={branches}
            />
          )}

          {renderBranchSelection()}
        </div>

        {/* Order Summary */}
        <div className="order-summary">
          <h2>Order Summary</h2>
          <div className="summary-row">
            <span>Subtotal</span>
            <span>KSh {summary.subtotal.toFixed(2)}</span>
          </div>
          {summary.discount && (
            <div className="summary-row discount">
              <span>Discount</span>
              <span>-KSh {summary.discount.amount.toFixed(2)}</span>
            </div>
          )}
          <div className="summary-row total">
            <span>Total</span>
            <span>KSh {summary.total.toFixed(2)}</span>
          </div>
        </div>

        {/* Place Order Button */}
        <button
          onClick={handleSubmit}
          className="place-order-button"
          disabled={!paymentMethod || loading}
        >
          {loading ? 'Processing...' : 'Place Order'}
        </button>
      </div>
    </div>
  );
}

export default Checkout;
