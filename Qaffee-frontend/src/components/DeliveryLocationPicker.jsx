import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Set up default Leaflet marker icon
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const DEFAULT_CENTER = [-1.2921, 36.8219]; // Nairobi center

function DeliveryLocationPicker({ onLocationSelect }) {
  const [search, setSearch] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [markerPosition, setMarkerPosition] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [mapCenter, setMapCenter] = useState(DEFAULT_CENTER);
  const mapRef = useRef();
  const [locationError, setLocationError] = useState('');

  // Fetch search suggestions from Nominatim
  useEffect(() => {
    if (search.length < 3) return setSuggestions([]);

    const controller = new AbortController();

    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(search)}&addressdetails=1&limit=5`, { signal: controller.signal })
      .then(res => res.json())
      .then(data => setSuggestions(data))
      .catch(() => {});

    return () => controller.abort();
  }, [search]);

  // Trigger location select externally
  useEffect(() => {
    if (selectedLocation) {
      onLocationSelect(selectedLocation);
    }
  }, [selectedLocation, onLocationSelect]);

  // Handle map click and perform reverse geocoding
  function MapClickHandler() {
    useMapEvents({
      click: (e) => {
        const { lat, lng } = e.latlng;
        setMarkerPosition([lat, lng]);
        setLocationError('');
        fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`)
          .then(res => res.json())
          .then(data => {
            const address = data?.display_name || `Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}`;
            const loc = {
              address,
              coordinates: { lat, lng },
            };
            setSelectedLocation(loc);
            setSearch(address);
            // Zoom in for precision
            if (mapRef.current) mapRef.current.setView([lat, lng], 17);
          })
          .catch((err) => {
            setLocationError('Could not fetch address. Using coordinates only.');
            const fallbackLoc = {
              address: `Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}`,
              coordinates: { lat, lng },
            };
            setSelectedLocation(fallbackLoc);
            setSearch(fallbackLoc.address);
            if (mapRef.current) mapRef.current.setView([lat, lng], 17);
          });
      },
    });
    return null;
  }

  // Handle suggestion click
  const handleSuggestionClick = (suggestion) => {
    const lat = parseFloat(suggestion.lat);
    const lng = parseFloat(suggestion.lon);

    setMapCenter([lat, lng]);
    setMarkerPosition([lat, lng]);
    setSelectedLocation({
      address: suggestion.display_name || `Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}`,
      coordinates: { lat, lng },
    });
    setSuggestions([]);
    setSearch(suggestion.display_name || `Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}`);

    if (mapRef.current) {
      mapRef.current.setView([lat, lng], 17);
    }
  };

  // Use browser geolocation
  const handleUseMyLocation = () => {
    setLocationError('');
    if (!navigator.geolocation) {
      setLocationError('Geolocation is not supported by your browser.');
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        setMapCenter([lat, lng]);
        setMarkerPosition([lat, lng]);
        if (mapRef.current) mapRef.current.setView([lat, lng], 17);
        fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`)
          .then(res => res.json())
          .then(data => {
            const address = data.display_name || `Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}`;
            setSelectedLocation({
              address,
              coordinates: { lat, lng },
            });
            setSearch(address);
          })
          .catch(() => {
            setLocationError('Could not fetch address. Using coordinates only.');
            setSelectedLocation({
              address: `Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}`,
              coordinates: { lat, lng },
            });
            setSearch(`Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}`);
          });
      },
      (err) => {
        setLocationError('Could not get your location.');
      }
    );
  };

  const handleRecenter = () => {
    setMapCenter(DEFAULT_CENTER);
    if (mapRef.current) {
      mapRef.current.setView(DEFAULT_CENTER, 16);
    }
  };

  return (
    <div style={{ height: '370px', marginBottom: '1rem', position: 'relative' }}>
      {/* Recenter and Geolocate buttons */}
      <div style={{ position: 'absolute', top: 10, right: 10, zIndex: 1100, display: 'flex', gap: 8 }}>
        <button
          onClick={handleRecenter}
          style={{
            background: '#fff',
            border: '1px solid #ccc',
            borderRadius: '4px',
            padding: '6px 12px',
            cursor: 'pointer',
            boxShadow: '0 2px 6px rgba(0,0,0,0.08)'
          }}
        >
          Recenter
        </button>
        <button
          onClick={handleUseMyLocation}
          style={{
            background: '#fff',
            border: '1px solid #4CAF50',
            borderRadius: '4px',
            padding: '6px 12px',
            cursor: 'pointer',
            color: '#166534',
            fontWeight: 500,
            boxShadow: '0 2px 6px rgba(0,0,0,0.08)'
          }}
        >
          Use my location
        </button>
      </div>
      {/* Search input */}
      <div style={{ position: 'relative', marginBottom: '0.5rem' }}>
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search for address..."
          style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
        />
        {suggestions.length > 0 && (
          <ul style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            background: 'white',
            zIndex: 1000,
            listStyle: 'none',
            margin: 0,
            padding: 0,
            border: '1px solid #ccc',
            maxHeight: '180px',
            overflowY: 'auto',
          }}>
            {suggestions.map((s, idx) => (
              <li
                key={s.place_id}
                onClick={() => handleSuggestionClick(s)}
                style={{
                  padding: '8px',
                  cursor: 'pointer',
                  borderBottom: idx !== suggestions.length - 1 ? '1px solid #eee' : 'none',
                }}
              >
                {s.display_name}
              </li>
            ))}
          </ul>
        )}
      </div>
      {/* Map display */}
      <MapContainer
        center={mapCenter}
        zoom={16}
        style={{ height: '260px', width: '100%' }}
        whenCreated={(mapInstance) => { mapRef.current = mapInstance; }}
      >
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapClickHandler />
        {markerPosition && <Marker position={markerPosition} />}
      </MapContainer>
      {/* Location display and error */}
      <p style={{ marginTop: '0.5rem' }}>
        {selectedLocation ? (
          <span>
            <strong>Delivery Address:</strong> {selectedLocation.address}<br />
            <strong>Coordinates:</strong> {selectedLocation.coordinates.lat}, {selectedLocation.coordinates.lng}
          </span>
        ) : 'Click on map or search for your delivery location'}
      </p>
      {locationError && <div style={{ color: 'red', fontSize: '0.95em' }}>{locationError}</div>}
    </div>
  );
}

export default DeliveryLocationPicker;
