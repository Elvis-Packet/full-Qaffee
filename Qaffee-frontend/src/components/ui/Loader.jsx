import './Loader.css'

function Loader({ size = 'medium', text = 'Loading...' }) {
  return (
    <div className="loader-container">
      <div className={`loader loader-${size}`}>
        <div className="coffee-cup">
          <div className="coffee-cup-body">
            <div className="coffee"></div>
          </div>
          <div className="coffee-cup-handle"></div>
        </div>
      </div>
      {text && <p className="loader-text">{text}</p>}
    </div>
  )
}

export default Loader