import React from 'react';
import './PaymentForm.css';

const PaymentForm = ({ paymentMethod, mpesaNumber, setMpesaNumber, cardDetails, setCardDetails }) => {
  if (!paymentMethod) return null;

  return (
    <div className="payment-form">
      {paymentMethod === 'mpesa' && (
        <div className="form-group">
          <label>M-Pesa Phone Number</label>
          <input
            type="tel"
            placeholder="Enter M-Pesa number (e.g., 254712345678)"
            value={mpesaNumber}
            onChange={(e) => setMpesaNumber(e.target.value)}
            className="form-input"
            pattern="254[0-9]{9}"
            required
          />
          <small>Enter your M-Pesa number starting with 254</small>
        </div>
      )}

      {paymentMethod === 'stripe' && (
        <>
          <div className="form-group">
            <label>Card Number</label>
            <input
              type="text"
              placeholder="1234 5678 9012 3456"
              value={cardDetails.number}
              onChange={(e) => setCardDetails({ ...cardDetails, number: e.target.value })}
              className="form-input"
              maxLength="19"
              required
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
                required
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
                required
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
              required
            />
          </div>
        </>
      )}

      {paymentMethod === 'cash' && (
        <div className="cash-notice">
          <p>You will pay in cash upon delivery.</p>
        </div>
      )}
    </div>
  );
};

export default PaymentForm; 