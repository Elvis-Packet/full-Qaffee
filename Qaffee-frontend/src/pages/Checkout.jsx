import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { useCart } from '../contexts/CartContext';
import PaymentSimulator from '../components/PaymentSimulator';
import PaymentForm from '../components/PaymentForm';
import MpesaPayment from '../components/payment/MpesaPayment';
import DeliveryLocationPicker from '../components/DeliveryLocationPicker';
import orderService from '../services/orderService';
import api from '../services/api';
import './Checkout.css';

const BRANCH_HOURS = {
  weekday: '7:00 AM - 11:00 PM',
  weekend: '8:00 AM - 11:00 PM',
};

function Checkout() {
  const { user } = useAuth();
  const { cart, getCartSummary, clearCart } = useCart();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [deliveryMethod, setDeliveryMethod] = useState('delivery');
  const [selectedBranch, setSelectedBranch] = useState(null);
  const [promoCode, setPromoCode] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('');
  const [deliveryLocation, setDeliveryLocation] = useState('');
  const [locationData, setLocationData] = useState(null);
  const [mpesaNumber, setMpesaNumber] = useState('');
  const [cardDetails, setCardDetails] = useState({
    number: '',
    expiry: '',
    cvc: '',
    name: '',
  });
  const [orderId, setOrderId] = useState(null);

  const [branches] = useState([
    {
      id: 1,
      name: 'Qaffee Point - Mombasa',
      address: 'Nyerere Avenue, Mombasa, Kenya',
      phone: '+254 758 222222',
      coordinates: { lat: -4.0435, lng: 39.6682 },
      features: ['Dine-in', 'Takeaway', 'WiFi'],
    },
    {
      id: 2,
      name: 'Qaffee Point - Nairobi Westlands',
      address: 'THE OVAL BUILDING, RING ROAD, PRR4+G5H, Nairobi',
      phone: '+254 759 111111',
      coordinates: { lat: -1.2648, lng: 36.8050 },
      features: ['Dine-in', 'Takeaway', 'WiFi', 'Outdoor Seating'],
    },
  ]);

  const summary = getCartSummary();

  const syncCartToBackend = async () => {
    for (const item of cart.items) {
      const cartData = {
        menu_item_id: item.id,
        quantity: item.quantity,
        customization: item.options || {},
      };
      await api.post('/cart', cartData);
    }
  };

  const handleOrderCreation = async (paymentDetails) => {
    if (!cart.items.length) throw new Error('Cart is empty');

    await syncCartToBackend();

    // Validate delivery address for delivery orders
    if (deliveryMethod === 'delivery') {
      if (!locationData || !locationData.address || typeof locationData.address !== 'string' || !locationData.address.trim()) {
        throw new Error('A valid delivery address is required.');
      }
    }

    const orderData = {
      is_delivery: deliveryMethod === 'delivery',
      ...(deliveryMethod === 'delivery' && locationData && {
        delivery_address: locationData.address,
        delivery_coordinates: locationData.coordinates,
      }),
      // For pickup, do not include delivery_address
    };

    const response = await orderService.createOrder(orderData);

    if (!response.order_id) throw new Error('Invalid server response');
    setOrderId(response.order_id);
    return response.order_id;
  };

  const handlePaymentComplete = async (paymentDetails) => {
    if (paymentMethod === 'mpesa') {
      clearCart();
      navigate(`/orders/${orderId}`);
    } else {
      await handleOrderCreation(paymentDetails);
    }
  };

  const handleLocationSelect = (data) => {
    setLocationData(data);
    setDeliveryLocation(data.address);
  };

  const handleSubmit = async () => {
    if (!paymentMethod) return toast.error('Please select a payment method');
    if (deliveryMethod === 'delivery' && !locationData) {
      return toast.error('Please select a delivery location');
    }

    try {
      setLoading(true);

      let createdOrderId;

      switch (paymentMethod) {
        case 'mpesa':
          break;
        case 'card':
          if (!cardDetails.number || !cardDetails.expiry || !cardDetails.cvc || !cardDetails.name) {
            return toast.error('Fill all card details');
          }
          createdOrderId = await handleOrderCreation({
            type: 'card',
            details: cardDetails,
          });
          clearCart();
          navigate(`/orders/${createdOrderId}`);
          break;
        case 'cash':
          createdOrderId = await handleOrderCreation({
            type: 'cash',
            details: { payOnDelivery: true },
          });
          clearCart();
          navigate(`/orders/${createdOrderId}`);
          break;
        default:
          return toast.error('Invalid payment method');
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('Failed to process order');
    } finally {
      setLoading(false);
    }
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
              const createdOrderId = await handleOrderCreation({ type: 'mpesa', ...paymentDetails });
              return createdOrderId;
            }}
          />
        );
      case 'card':
        return (
          <div className="payment-details">
            <h3>Card Details</h3>
            <input
              type="text"
              placeholder="Card Number"
              value={cardDetails.number}
              onChange={(e) => setCardDetails({ ...cardDetails, number: e.target.value })}
            />
            <input
              type="text"
              placeholder="Expiry (MM/YY)"
              value={cardDetails.expiry}
              onChange={(e) => setCardDetails({ ...cardDetails, expiry: e.target.value })}
            />
            <input
              type="text"
              placeholder="CVC"
              value={cardDetails.cvc}
              onChange={(e) => setCardDetails({ ...cardDetails, cvc: e.target.value })}
            />
            <input
              type="text"
              placeholder="Name on Card"
              value={cardDetails.name}
              onChange={(e) => setCardDetails({ ...cardDetails, name: e.target.value })}
            />
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="checkout-page">
      <h1>Checkout</h1>

      {/* Cart */}
      <div className="cart-items">
        {cart.items.map((item) => (
          <div key={item.id}>
            <p>{item.name} × {item.quantity}</p>
            <p>KSh {item.price.toFixed(2)}</p>
          </div>
        ))}
      </div>

      {/* Delivery Method */}
      <div className="delivery-method">
        <button
          className={deliveryMethod === 'delivery' ? 'selected' : ''}
          onClick={() => {
            setDeliveryMethod('delivery');
            setSelectedBranch(null);
          }}
        >
          Delivery
        </button>
        <button
          className={deliveryMethod === 'pickup' ? 'selected' : ''}
          onClick={() => {
            setDeliveryMethod('pickup');
            setDeliveryLocation('');
            setLocationData(null);
          }}
        >
          Pickup
        </button>
      </div>

      {/* Location Picker or Branch Selector */}
      {deliveryMethod === 'delivery' && <DeliveryLocationPicker onLocationSelect={handleLocationSelect} />}
      {deliveryMethod === 'pickup' && (
        <div className="pickup-branches" style={{ margin: '1rem 0' }}>
          <h3>Select Pickup Branch</h3>
          {branches.map((branch) => (
            <button
              key={branch.id}
              style={{
                display: 'block',
                width: '100%',
                margin: '0.5rem 0',
                padding: '1rem',
                border: selectedBranch && selectedBranch.id === branch.id ? '2px solid #4CAF50' : '1px solid #ccc',
                borderRadius: '8px',
                background: selectedBranch && selectedBranch.id === branch.id ? '#f0fdf4' : '#fff',
                fontWeight: selectedBranch && selectedBranch.id === branch.id ? 'bold' : 'normal',
                cursor: 'pointer',
              }}
              onClick={() => setSelectedBranch(branch)}
            >
              <div>{branch.name}</div>
              <div style={{ fontSize: '0.95em', color: '#666' }}>{branch.address}</div>
            </button>
          ))}
          {selectedBranch && (
            <div style={{ marginTop: '0.5rem', color: '#166534' }}>
              Selected: {selectedBranch.name}
            </div>
          )}
        </div>
      )}

      {/* Payment Method */}
      <div className="payment-methods">
        <label>
          <input
            type="radio"
            value="mpesa"
            checked={paymentMethod === 'mpesa'}
            onChange={() => setPaymentMethod('mpesa')}
          />
          M-Pesa
        </label>
        <label>
          <input
            type="radio"
            value="card"
            checked={paymentMethod === 'card'}
            onChange={() => setPaymentMethod('card')}
          />
          Card
        </label>
        <label>
          <input
            type="radio"
            value="cash"
            checked={paymentMethod === 'cash'}
            onChange={() => setPaymentMethod('cash')}
          />
          Cash
        </label>
        {renderPaymentDetails()}
      </div>

      {/* Summary */}
      <div className="order-summary">
        <p>Subtotal: KSh {summary.subtotal.toFixed(2)}</p>
        <p>Total: KSh {summary.total.toFixed(2)}</p>
      </div>

      {/* Submit */}
      <button onClick={handleSubmit} disabled={loading || !paymentMethod}>
        {loading ? 'Processing...' : 'Place Order'}
      </button>
    </div>
  );
}

export default Checkout;
