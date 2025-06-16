import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { toast } from 'react-hot-toast';
import api from '../../services/api';
import './MpesaPayment.css';

const MpesaPayment = ({ amount, orderId, onPaymentComplete, onInitiate }) => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [checkoutRequestId, setCheckoutRequestId] = useState(null);
  const [pollInterval, setPollInterval] = useState(null);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [pollInterval]);

  const startPolling = (checkoutRequestId) => {
    // Poll every 5 seconds
    const interval = setInterval(async () => {
      try {
        const response = await api.get(`/api/payments/mpesa/status/${checkoutRequestId}`);
        if (response.data.status === 'COMPLETED') {
          clearInterval(interval);
          setPollInterval(null);
          onPaymentComplete();
          toast.success('Payment completed successfully!');
        } else if (response.data.status === 'FAILED') {
          clearInterval(interval);
          setPollInterval(null);
          toast.error('Payment failed. Please try again.');
        }
      } catch (error) {
        console.error('Error checking payment status:', error);
      }
    }, 5000);
    setPollInterval(interval);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // First create the order
      const createdOrderId = await onInitiate({
        phoneNumber,
        amount
      });

      // Then initiate the payment
      const response = await api.post('/api/payments/mpesa', {
        phoneNumber,
        amount,
        orderId: createdOrderId
      });

      if (response.data.checkoutRequestId) {
        setCheckoutRequestId(response.data.checkoutRequestId);
        startPolling(response.data.checkoutRequestId);
        toast.success('Payment request sent! Please check your phone.');
      }
    } catch (error) {
      console.error('Payment error:', error);
      toast.error(error.response?.data?.message || 'Failed to initiate payment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mpesa-payment">
      <h3>M-Pesa Payment</h3>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Phone Number</label>
          <input
            type="tel"
            placeholder="254XXXXXXXXX"
            value={phoneNumber}
            onChange={(e) => setPhoneNumber(e.target.value)}
            className="form-input"
            required
            pattern="^254[0-9]{9}$"
            title="Please enter a valid Kenyan phone number starting with 254"
          />
          <small>Format: 254XXXXXXXXX (e.g., 254712345678)</small>
        </div>
        <button 
          type="submit" 
          className="submit-button" 
          disabled={loading}
        >
          {loading ? 'Processing...' : 'Pay with M-Pesa'}
        </button>
      </form>
    </div>
  );
};

MpesaPayment.propTypes = {
  amount: PropTypes.number.isRequired,
  orderId: PropTypes.string,
  onPaymentComplete: PropTypes.func.isRequired,
  onInitiate: PropTypes.func.isRequired
};

export default MpesaPayment;