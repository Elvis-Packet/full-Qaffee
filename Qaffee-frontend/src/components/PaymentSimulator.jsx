import React, { useState } from 'react';
import { toast } from 'react-hot-toast';
import './PaymentSimulator.css';

const PaymentSimulator = ({ paymentMethod, amount, onSuccess, onCancel }) => {
  const [mpesaPhone, setMpesaPhone] = useState('');
  const [cardNumber, setCardNumber] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [cvv, setCvv] = useState('');
  const [loading, setLoading] = useState(false);

  const handleMpesaPayment = async (e) => {
    e.preventDefault();
    if (!mpesaPhone || mpesaPhone.length !== 12 || !mpesaPhone.startsWith('254')) {
      toast.error('Please enter a valid phone number (format: 254XXXXXXXXX)');
      return;
    }

    setLoading(true);
    try {
      // Simulate M-Pesa STK push
      toast.loading('Sending M-Pesa STK push...');
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Show confirmation dialog
      const confirmed = window.confirm(
        `An M-Pesa prompt has been sent to ${mpesaPhone}. ` +
        'For this simulation, click OK to simulate successful payment, or Cancel to simulate failure.'
      );

      if (confirmed) {
        toast.success('Payment successful!');
        onSuccess();
      } else {
        toast.error('Payment cancelled');
        onCancel();
      }
    } catch (error) {
      toast.error('Payment failed');
      onCancel();
    } finally {
      setLoading(false);
    }
  };

  const handleStripePayment = async (e) => {
    e.preventDefault();
    if (!cardNumber || !expiryDate || !cvv) {
      toast.error('Please fill in all card details');
      return;
    }

    setLoading(true);
    try {
      // Simulate card processing
      toast.loading('Processing payment...');
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Simulate successful payment (in real implementation, this would be handled by Stripe)
      toast.success('Payment successful!');
      onSuccess();
    } catch (error) {
      toast.error('Payment failed');
      onCancel();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="payment-simulator">
      <h2>Payment Simulation</h2>
      <div className="amount">
        <span>Amount to pay:</span>
        <span className="price">KSh {amount.toFixed(2)}</span>
      </div>

      {paymentMethod === 'mpesa' && (
        <form onSubmit={handleMpesaPayment} className="payment-form">
          <div className="form-group">
            <label>Phone Number (format: 254XXXXXXXXX)</label>
            <input
              type="text"
              value={mpesaPhone}
              onChange={(e) => setMpesaPhone(e.target.value)}
              placeholder="254712345678"
              maxLength="12"
              required
            />
          </div>
          <button type="submit" disabled={loading}>
            {loading ? 'Processing...' : 'Simulate M-Pesa Payment'}
          </button>
        </form>
      )}

      {paymentMethod === 'stripe' && (
        <form onSubmit={handleStripePayment} className="payment-form">
          <div className="form-group">
            <label>Card Number</label>
            <input
              type="text"
              value={cardNumber}
              onChange={(e) => setCardNumber(e.target.value)}
              placeholder="4242 4242 4242 4242"
              maxLength="19"
              required
            />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Expiry Date</label>
              <input
                type="text"
                value={expiryDate}
                onChange={(e) => setExpiryDate(e.target.value)}
                placeholder="MM/YY"
                maxLength="5"
                required
              />
            </div>
            <div className="form-group">
              <label>CVV</label>
              <input
                type="text"
                value={cvv}
                onChange={(e) => setCvv(e.target.value)}
                placeholder="123"
                maxLength="3"
                required
              />
            </div>
          </div>
          <button type="submit" disabled={loading}>
            {loading ? 'Processing...' : 'Simulate Card Payment'}
          </button>
        </form>
      )}
    </div>
  );
};

export default PaymentSimulator; 