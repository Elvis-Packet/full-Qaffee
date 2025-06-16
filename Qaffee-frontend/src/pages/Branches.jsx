import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import './Branches.css';

const Branches = () => {
  const [branches, setBranches] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedBranch, setSelectedBranch] = useState(null);

  useEffect(() => {
    const fetchBranches = async () => {
      try {
        // TODO: Replace with actual API call
        const mockBranches = [
          {
            id: 1,
            name: 'Qaffee Point - Mombasa',
            address: 'Nyerere Avenue, Mombasa, Kenya',
            phone: '+254 758 222222',
            hours: {
              monday: '7:00 AM - 11:00 PM',
              tuesday: '7:00 AM - 11:00 PM',
              wednesday: '7:00 AM - 11:00 PM',
              thursday: '7:00 AM - 11:00 PM',
              friday: '7:00 AM - 11:00 PM',
              saturday: '7:00 AM - 11:00 PM',
              sunday: '7:00 AM - 11:00 PM'
            },
            coordinates: {
              lat: -4.0435,
              lng: 39.6682
            },
            features: ['Dine-in', 'Takeaway', 'Delivery', 'WiFi', 'VIP Lounge'],
            status: 'open'
          },
          {
            id: 2,
            name: 'Qaffee Point - Nairobi Westlands',
            address: 'THE OVAL BUILDING, RING ROAD, PRR4+G5H, Nairobi',
            phone: '+254 759 111111',
            hours: {
              monday: '7:30 AM - 10:30 PM',
              tuesday: '7:30 AM - 10:30 PM',
              wednesday: '7:30 AM - 10:30 PM',
              thursday: '7:30 AM - 10:30 PM',
              friday: '7:30 AM - 11:00 PM',
              saturday: '8:00 AM - 11:00 PM',
              sunday: '8:00 AM - 10:00 PM'
            },
            coordinates: {
              lat: -1.2648,  // Coordinates for The Oval Building
              lng: 36.8050
            },
            features: ['Dine-in', 'Takeaway', 'WiFi', 'Modern Ambiance', 'Outdoor Seating'],
            status: 'open'
          }
        ];

        setBranches(mockBranches);
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching branches:', error);
        toast.error('Failed to fetch branch information');
        setIsLoading(false);
      }
    };

    fetchBranches();
  }, []);

  const getDayOfWeek = () => {
    const days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
    return days[new Date().getDay()];
  };

  const openGoogleMaps = (lat, lng, address) => {
    // Updated to use both coordinates and address for better accuracy
    window.open(`https://www.google.com/maps/search/?api=1&query=${lat},${lng}&query_place_id=${encodeURIComponent(address)}`);
  };

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="branches-container">
      <div className="branches-header">
        <h1 className="branches-title">Our Locations</h1>
        <p className="branches-subtitle">Find a Qaffee Point near you</p>
      </div>

      <div className="branches-grid">
        {branches.map((branch) => (
          <div key={branch.id} className="branch-card">
            <div className="branch-content">
              <div className="branch-header">
                <div>
                  <h2 className="branch-name">{branch.name}</h2>
                  <p className="branch-address">{branch.address}</p>
                  <button 
                    onClick={() => openGoogleMaps(branch.coordinates.lat, branch.coordinates.lng, branch.address)}
                    className="map-button"
                    aria-label={`View ${branch.name} on Google Maps`}
                  >
                    <svg className="map-icon" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                    </svg>
                    View on Map
                  </button>
                </div>
                <span className={`status-badge ${branch.status === 'open' ? 'status-open' : 'status-closed'}`}>
                  {branch.status.toUpperCase()}
                </span>
              </div>

              <div className="branch-section">
                <h3 className="section-title">Today's Hours</h3>
                <p className="section-content">
                  {branch.hours[getDayOfWeek()]}
                </p>
              </div>

              <div className="branch-section">
                <h3 className="section-title">Contact</h3>
                <p className="section-content">{branch.phone}</p>
              </div>

              <div className="features-container">
                <h3 className="section-title">Features</h3>
                <div className="features-list">
                  {branch.features.map((feature, index) => (
                    <span key={index} className="feature-tag">
                      {feature}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <button
              onClick={() => setSelectedBranch(selectedBranch === branch.id ? null : branch.id)}
              className="action-button"
            >
              {selectedBranch === branch.id ? 'Hide Details' : 'View Details'}
            </button>

            {selectedBranch === branch.id && (
              <div className="expanded-details">
                <h3 className="section-title">Weekly Hours</h3>
                <div className="hours-grid">
                  {Object.entries(branch.hours).map(([day, hours]) => (
                    <div key={day} className="hours-row">
                      <span className="hours-day">{day.charAt(0).toUpperCase() + day.slice(1)}</span>
                      <span className="hours-time">{hours}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Branches;