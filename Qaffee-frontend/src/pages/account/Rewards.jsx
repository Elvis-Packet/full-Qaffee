import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext'; // Updated import path
import axios from 'axios';
import './Rewards.css'; // CSS import

const Rewards = () => {
  const { user, token } = useAuth();
  const [balance, setBalance] = useState(null);
  const [rewards, setRewards] = useState([]);
  const [claims, setClaims] = useState([]);
  const [referralInfo, setReferralInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [referralCode, setReferralCode] = useState('');

  // Fetch all rewards data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const headers = { Authorization: `Bearer ${token}` };
        
        // Fetch points balance
        const balanceRes = await axios.get('/api/rewards/balance', { headers });
        setBalance(balanceRes.data);
        
        // Fetch available rewards
        const rewardsRes = await axios.get('/api/rewards/rewards', { headers });
        setRewards(rewardsRes.data);
        
        // Fetch user's claims
        const claimsRes = await axios.get('/api/rewards/claims', { headers });
        setClaims(claimsRes.data);
        
        // Fetch referral info
        const referralRes = await axios.get('/api/rewards/referral/share', { headers });
        setReferralInfo(referralRes.data);
        
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load rewards data');
      } finally {
        setLoading(false);
      }
    };

    if (user && token) {
      fetchData();
    } else {
      setLoading(false);
    }
  }, [user, token]);

  const handleClaimReward = async (rewardId) => {
    try {
      const headers = { Authorization: `Bearer ${token}` };
      const response = await axios.post(`/api/rewards/rewards/${rewardId}/claim`, {}, { headers });
      
      // Update local state
      setClaims([response.data, ...claims]);
      setRewards(rewards.map(reward => 
        reward.id === rewardId ? 
        {...reward, quantity_available: reward.quantity_available - 1} : 
        reward
      ));
      
      // Refresh balance
      const balanceRes = await axios.get('/api/rewards/balance', { headers });
      setBalance(balanceRes.data);
      
      alert('Reward claimed successfully!');
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to claim reward');
    }
  };

  const handleUseReward = async (claimId) => {
    try {
      const headers = { Authorization: `Bearer ${token}` };
      const response = await axios.post(`/api/rewards/claims/${claimId}/use`, {}, { headers });
      
      // Update local state
      setClaims(claims.map(c => c.id === claimId ? response.data : c));
      alert('Reward used successfully!');
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to use reward');
    }
  };

  const handleReferralSubmit = async (e) => {
    e.preventDefault();
    try {
      const headers = { Authorization: `Bearer ${token}` };
      await axios.post('/api/rewards/referral/claim', { referral_code: referralCode }, { headers });
      
      // Refresh data
      const balanceRes = await axios.get('/api/rewards/balance', { headers });
      setBalance(balanceRes.data);
      
      const referralRes = await axios.get('/api/rewards/referral/share', { headers });
      setReferralInfo(referralRes.data);
      
      setReferralCode('');
      alert('Referral claimed successfully!');
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to claim referral');
    }
  };

  if (loading) return <div className="loading">Loading rewards...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!user) return <div className="error">Please login to view rewards</div>;

  return (
    <div className="rewards-container">
      <section className="points-balance">
        <h2>Your Points</h2>
        <div className="points-display">
          <span className="points-value">{balance?.current_points || 0}</span>
          <span className="points-label">points</span>
        </div>
        <p>Earn {balance?.points_per_dollar || 10} points per $1 spent</p>
        
        <h3>Points History</h3>
        <ul className="points-history">
          {balance?.points_history?.map((item, index) => (
            <li key={index}>
              <span>Order #{item.order_id}</span>
              <span>+{item.points_earned} points</span>
              <span>{new Date(item.date).toLocaleDateString()}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="available-rewards">
        <h2>Available Rewards</h2>
        <div className="rewards-grid">
          {rewards.filter(r => r.is_active && 
            (r.quantity_available === null || r.quantity_available > 0)).map(reward => (
            <div key={reward.id} className="reward-card">
              <h3>{reward.name}</h3>
              <p>{reward.description}</p>
              <div className="reward-cost">{reward.points_required} points</div>
              {balance?.current_points >= reward.points_required ? (
                <button 
                  onClick={() => handleClaimReward(reward.id)}
                  className="claim-button"
                  disabled={reward.quantity_available !== null && reward.quantity_available <= 0}
                >
                  {reward.quantity_available !== null && reward.quantity_available <= 0 ? 
                    'Out of stock' : 'Claim Reward'}
                </button>
              ) : (
                <button disabled className="claim-button disabled">
                  Need {reward.points_required - (balance?.current_points || 0)} more points
                </button>
              )}
            </div>
          ))}
        </div>
      </section>

      <section className="referral-program">
        <h2>Referral Program</h2>
        {referralInfo && (
          <>
            <p>Share your code and earn {referralInfo.points_per_referral} points per referral!</p>
            <div className="referral-code">
              <strong>Your Code:</strong> {referralInfo.referral_code}
              <button 
                onClick={() => {
                  navigator.clipboard.writeText(referralInfo.referral_code);
                  alert('Copied to clipboard!');
                }}
                className="copy-button"
              >
                Copy
              </button>
            </div>
            <p className="share-message">{referralInfo.share_message}</p>
          </>
        )}
        
        {!user?.referral_claimed && (
          <div className="claim-referral">
            <h3>Have a referral code?</h3>
            <form onSubmit={handleReferralSubmit}>
              <input
                type="text"
                value={referralCode}
                onChange={(e) => setReferralCode(e.target.value)}
                placeholder="Enter referral code"
                required
              />
              <button type="submit">Claim Referral</button>
            </form>
          </div>
        )}
      </section>

      <section className="your-claims">
        <h2>Your Claimed Rewards</h2>
        {claims.length === 0 ? (
          <p>You haven't claimed any rewards yet.</p>
        ) : (
          <ul className="claims-list">
            {claims.map(claim => (
              <li key={claim.id} className={claim.status}>
                <div>
                  <strong>{claim.reward?.name || 'Reward'}</strong>
                  <span>Claimed on {new Date(claim.claimed_at).toLocaleDateString()}</span>
                  {claim.expiry_date && (
                    <span>Expires on {new Date(claim.expiry_date).toLocaleDateString()}</span>
                  )}
                </div>
                {claim.status === 'active' ? (
                  <button 
                    onClick={() => handleUseReward(claim.id)}
                    className="use-button"
                  >
                    Use Now
                  </button>
                ) : (
                  <span className="used-badge">Used</span>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
};

export default Rewards;