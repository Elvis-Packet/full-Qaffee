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

        fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`)
          .then(res => res.json())
          .then(data => {
            const loc = {
              address: data.display_name,
              coordinates: { lat, lng },
            };
            setSelectedLocation(loc);
            setSearch(data.display_name);
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
      address: suggestion.display_name,
      coordinates: { lat, lng },
    });
    setSuggestions([]);
    setSearch(suggestion.display_name);

    if (mapRef.current) {
      mapRef.current.setView([lat, lng], 16);
    }
  };

  const handleRecenter = () => {
    setMapCenter(DEFAULT_CENTER);
    if (mapRef.current) {
      mapRef.current.setView(DEFAULT_CENTER, 13);
    }
  };

  return (
    <div style={{ height: '350px', marginBottom: '1rem', position: 'relative' }}>
      {/* Recenter button */}
      <button
        onClick={handleRecenter}
        style={{
          position: 'absolute',
          top: 10,
          right: 10,
          zIndex: 1100,
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
        zoom={13}
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
      {/* Location display */}
      <p style={{ marginTop: '0.5rem' }}>
        {selectedLocation ? `Selected: ${selectedLocation.address}` : 'Click on map or search for your delivery location'}
      </p>
    </div>
  );
}

export default DeliveryLocationPicker;
