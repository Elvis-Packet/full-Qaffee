import React, { useEffect, useRef, useState } from 'react';
import { config } from '../config';
import { loadGoogleMapsApi } from '../utils/googleMaps';
import { toast } from 'react-hot-toast';

const DeliveryLocationPicker = ({ onLocationSelect }) => {
  const inputRef = useRef(null);
  const autocompleteRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initializeAutocomplete = async () => {
      try {
        await loadGoogleMapsApi();
        if (inputRef.current) {
          autocompleteRef.current = new window.google.maps.places.Autocomplete(
            inputRef.current,
            config.googleMaps.options
          );

          autocompleteRef.current.addListener('place_changed', () => {
            const place = autocompleteRef.current.getPlace();
            if (place.formatted_address) {
              onLocationSelect({
                address: place.formatted_address,
                lat: place.geometry?.location?.lat(),
                lng: place.geometry?.location?.lng(),
                placeId: place.place_id
              });
            }
          });
        }
        setIsLoading(false);
      } catch (error) {
        console.error('Failed to initialize location picker:', error);
        toast.error('Failed to load location services');
        setIsLoading(false);
      }
    };

    initializeAutocomplete();

    return () => {
      if (autocompleteRef.current) {
        window.google.maps.event.clearInstanceListeners(autocompleteRef.current);
      }
    };
  }, [onLocationSelect]);

  return (
    <div className="delivery-location-picker">
      <input
        ref={inputRef}
        type="text"
        id="delivery-location-input"
        placeholder={isLoading ? "Loading..." : "Enter delivery location"}
        className="form-input"
        disabled={isLoading}
      />
    </div>
  );
};

export default DeliveryLocationPicker; 