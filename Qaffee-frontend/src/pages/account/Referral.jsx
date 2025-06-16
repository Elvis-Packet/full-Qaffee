import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext.jsx';
import { toast } from 'react-hot-toast';

const Referral = () => {
  const { user } = useAuth();
  const [referralData, setReferralData] = useState({
    code: '',
    totalReferrals: 0,
    pendingReferrals: 0,
    completedReferrals: 0,
    pointsEarned: 0,
    history: []
  });
  const [loading, setLoading] = useState(true);
  const [copying, setCopying] = useState(false);

  useEffect(() => {
    const fetchReferralData = async () => {
      try {
        // TODO: Implement actual API call to fetch referral data
        // This is a mock implementation
        setReferralData({
          code: 'FRIEND123',
          totalReferrals: 5,
          pendingReferrals: 2,
          completedReferrals: 3,
          pointsEarned: 300,
          history: [
            {
              id: 1,
              name: 'John D.',
              date: '2024-03-15',
              status: 'completed',
              points: 100
            },
            {
              id: 2,
              name: 'Sarah M.',
              date: '2024-03-14',
              status: 'pending',
              points: 0
            },
            {
              id: 3,
              name: 'Mike R.',
              date: '2024-03-10',
              status: 'completed',
              points: 100
            }
          ]
        });
        setLoading(false);
      } catch (error) {
        console.error('Error fetching referral data:', error);
        toast.error('Failed to fetch referral information');
        setLoading(false);
      }
    };

    fetchReferralData();
  }, []);

  const copyReferralCode = async () => {
    try {
      await navigator.clipboard.writeText(referralData.code);
      setCopying(true);
      toast.success('Referral code copied to clipboard!');
      setTimeout(() => setCopying(false), 2000);
    } catch (error) {
      toast.error('Failed to copy referral code');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-4 sm:p-6 lg:p-8">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-3xl font-bold mb-6">Refer a Friend</h1>

        {/* Referral Code Section */}
        <div className="bg-gray-50 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Your Referral Code</h2>
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <div className="flex items-center space-x-4 p-4 bg-white rounded-lg border border-gray-200">
                <span className="text-lg font-mono">{referralData.code}</span>
                <button
                  onClick={copyReferralCode}
                  className="ml-auto px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
                >
                  {copying ? 'Copied!' : 'Copy Code'}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-500">Total Referrals</h3>
            <p className="mt-1 text-2xl font-semibold">{referralData.totalReferrals}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-500">Points Earned</h3>
            <p className="mt-1 text-2xl font-semibold">{referralData.pointsEarned}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-500">Pending Referrals</h3>
            <p className="mt-1 text-2xl font-semibold">{referralData.pendingReferrals}</p>
          </div>
        </div>

        {/* How It Works */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-4 border border-gray-200 rounded-lg">
              <div className="text-2xl font-bold text-primary-600 mb-2">1</div>
              <h3 className="font-medium mb-2">Share Your Code</h3>
              <p className="text-sm text-gray-600">Share your unique referral code with friends and family</p>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg">
              <div className="text-2xl font-bold text-primary-600 mb-2">2</div>
              <h3 className="font-medium mb-2">Friends Order</h3>
              <p className="text-sm text-gray-600">They get 10% off their first order using your code</p>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg">
              <div className="text-2xl font-bold text-primary-600 mb-2">3</div>
              <h3 className="font-medium mb-2">Earn Rewards</h3>
              <p className="text-sm text-gray-600">You earn 100 points for each successful referral</p>
            </div>
          </div>
        </div>

        {/* Referral History */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Referral History</h2>
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Points
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {referralData.history.map((referral) => (
                  <tr key={referral.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {referral.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(referral.date).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span
                        className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold
                          ${
                            referral.status === 'completed'
                              ? 'bg-green-100 text-green-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}
                      >
                        {referral.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                      {referral.points}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Referral; 