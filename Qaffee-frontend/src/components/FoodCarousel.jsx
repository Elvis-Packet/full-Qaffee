import React from 'react'
import PropTypes from 'prop-types'

const FoodCarousel = ({ category }) => {
  // This is a placeholder component that you can enhance with actual carousel functionality
  // and food images for each category
  return (
    <div className="food-carousel">
      {/* Add your carousel implementation here */}
      <div className="carousel-placeholder">
        <p>Food images for {category} will be displayed here</p>
      </div>
    </div>
  )
}

FoodCarousel.propTypes = {
  category: PropTypes.number.isRequired,
}

export default FoodCarousel 