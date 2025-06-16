import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useCart } from '../contexts/CartContext.jsx';
import Loader from '../components/ui/Loader.jsx';
import api from '../services/api.js';
import './ItemDetails.css';

function ItemDetails() {
  const { id } = useParams();
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const { addToCart } = useCart();

  useEffect(() => {
    const fetchItemDetails = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await api.get(`/menu/items/${id}`);
        setItem(response.data);
      } catch (err) {
        console.error('Error fetching item details:', err);
        setError('Failed to load item details. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchItemDetails();
  }, [id]);

  const handleAddToCart = () => {
    if (item) {
      addToCart({
        id: item.id,
        name: item.name,
        price: item.price,
        image: item.image_url,
        description: item.description,
        quantity: quantity
      });
    }
  };

  const incrementQuantity = () => {
    setQuantity(prev => prev + 1);
  };

  const decrementQuantity = () => {
    if (quantity > 1) {
      setQuantity(prev => prev - 1);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Loader />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="alert alert-error">
          {error}
        </div>
        <Link to="/menu" className="btn btn-primary mt-4">Back to Menu</Link>
      </div>
    );
  }

  if (!item) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="alert alert-error">
          Item not found
        </div>
        <Link to="/menu" className="btn btn-primary mt-4">Back to Menu</Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Link to="/menu" className="text-primary hover:underline mb-4 inline-block">
        &larr; Back to Menu
      </Link>

      <div className="item-details-container">
        <div className="item-image-container">
          <img 
            src={item.image_url || '/placeholder-food.jpg'} 
            alt={item.name}
            className="item-image"
          />
          {item.is_available && <span className="availability-badge">Available</span>}
        </div>

        <div className="item-content">
          <h1 className="item-title">{item.name}</h1>
          <p className="item-price">KSh {item.price.toFixed(2)}</p>
          
          <div className="item-description">
            <h3 className="description-title">Description</h3>
            <p>{item.description}</p>
          </div>

          {item.ingredients && (
            <div className="item-ingredients">
              <h3 className="ingredients-title">Ingredients</h3>
              <p>{item.ingredients}</p>
            </div>
          )}

          {item.nutrition_info && (
            <div className="item-nutrition">
              <h3 className="nutrition-title">Nutrition Information</h3>
              <p>{item.nutrition_info}</p>
            </div>
          )}

          <div className="item-actions">
            <div className="quantity-selector">
              <button 
                onClick={decrementQuantity}
                className="quantity-btn"
                disabled={quantity <= 1}
              >
                -
              </button>
              <span className="quantity-value">{quantity}</span>
              <button 
                onClick={incrementQuantity}
                className="quantity-btn"
              >
                +
              </button>
            </div>

            <button
              onClick={handleAddToCart}
              className="add-to-cart-btn"
              disabled={!item.is_available}
            >
              {item.is_available ? 'Add to Cart' : 'Not Available'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ItemDetails;