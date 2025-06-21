import { Link } from 'react-router-dom';
import { FaFacebook, FaInstagram, FaTwitter, FaCcVisa, FaCcMastercard, FaMoneyBillWave } from 'react-icons/fa';
import './Footer.css';

function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-main">
          <div className="footer-brand">
            <Link to="/" className="footer-logo">
              <img src="/images/qaffee-logo.svg" alt="Qaffee Point" className="footer-logo-img" />
              <span className="footer-logo-text">Qaffee Point</span>
            </Link>
            <p className="footer-tagline">Premium coffee, exceptional service</p>
            <div className="footer-social">
              <a 
                href="https://www.facebook.com/Qaffeepoint/" 
                className="social-link" 
                aria-label="Facebook"
                target="_blank"
                rel="noopener noreferrer"
              >
                <FaFacebook className="social-icon" />
              </a>
              <a 
                href="https://www.instagram.com/qaffeepoint/" 
                className="social-link" 
                aria-label="Instagram"
                target="_blank"
                rel="noopener noreferrer"
              >
                <FaInstagram className="social-icon" />
              </a>
              <a 
                href="https://twitter.com/qaffeepoint" 
                className="social-link" 
                aria-label="Twitter"
                target="_blank"
                rel="noopener noreferrer"
              >
                <FaTwitter className="social-icon" />
              </a>
            </div>
          </div>
          
          <div className="footer-links-container">
            <div className="footer-links-column">
              <h3 className="footer-column-title">Quick Links</h3>
              <ul className="footer-links">
                <li><Link to="/">Home</Link></li>
                <li><Link to="/menu">Menu</Link></li>
                <li><Link to="/branches">Locations</Link></li>
              </ul>
            </div>
            
            <div className="footer-links-column">
              <h3 className="footer-column-title">Account</h3>
              <ul className="footer-links">
                <li><Link to="/login">Login</Link></li>
                <li><Link to="/signup">Sign Up</Link></li>
                <li><Link to="/account">My Profile</Link></li>
                <li><Link to="/orders/history">Order History</Link></li>
              </ul>
            </div>
            
            <div className="footer-links-column">
              <h3 className="footer-column-title">Information</h3>
              <ul className="footer-links">
                <li><Link to="/about-us">About Us</Link></li>
                <li><Link to="/contact-us">Contact Us</Link></li>
                <li><Link to="/terms-and-conditions">Terms & Conditions</Link></li>
                <li><Link to="/privacy-policy">Privacy Policy</Link></li>
              </ul>
            </div>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p className="copyright">© {currentYear} Qaffee Point. All rights reserved.</p>
          <div className="footer-payments">
            <FaCcVisa className="payment-icon" />
            <FaCcMastercard className="payment-icon" />
            <FaMoneyBillWave className="payment-icon" />
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;