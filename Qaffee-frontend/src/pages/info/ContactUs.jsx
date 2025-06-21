import React, { useState } from 'react';

const ContactUs = ({ user = {} }) => {
  const [message, setMessage] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [activeTab, setActiveTab] = useState('whatsapp'); // 'whatsapp', 'call', or 'email'

  // Business contact information
  const businessPhone = '254 758 222222'; // Replace with your business number
  const formattedPhone = '+254 758 222222'; // Formatted display version
  const businessEmail = 'info@qaffee.com';

  const handleWhatsAppSubmit = (e) => {
    e.preventDefault();
    if (!message.trim()) return;
    
    const encodedMsg = encodeURIComponent(
      `Name: ${user.name || 'Customer'}\nPhone: ${user.phone || 'Not provided'}\n\nMessage: ${message}`
    );
    const whatsappUrl = `https://wa.me/${businessPhone}?text=${encodedMsg}`;
    window.open(whatsappUrl, '_blank');
    setIsSubmitted(true);
    setMessage('');
  };

  const handleEmailClick = () => {
    const subject = encodeURIComponent("Inquiry from Qaffee Website");
    const body = encodeURIComponent(
      `Name: ${user.name || 'Not provided'}\nPhone: ${user.phone || 'Not provided'}\n\nMessage: ${message}`
    );
    window.location.href = `mailto:${businessEmail}?subject=${subject}&body=${body}`;
  };

  const handleCallClick = () => {
    window.location.href = `tel:${businessPhone}`;
  };

  const handleAddToContacts = () => {
    const vCard = `BEGIN:VCARD
VERSION:3.0
FN:Qaffee Cafe
TEL;TYPE=WORK,VOICE:${businessPhone}
EMAIL:${businessEmail}
ORG:Qaffee Cafe
URL:https://qaffee.com
NOTE:Your favorite coffee shop
END:VCARD`;
    
    const blob = new Blob([vCard], { type: 'text/vcard' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = 'qaffee-contact.vcf';
    link.click();
  };

  return (
    <div className="container mx-auto px-4 py-12">
      <h1 className="text-4xl font-bold mb-4 text-center">Contact Us</h1>
      <p className="text-gray-600 text-center mb-8">
        Reach out to us through your preferred method
      </p>

      <div className="flex justify-center space-x-4 mb-8">
        <button
          className={`px-6 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'whatsapp' 
              ? 'bg-primary-600 text-white' 
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
          onClick={() => setActiveTab('whatsapp')}
        >
          WhatsApp
        </button>
        <button
          className={`px-6 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'call' 
              ? 'bg-primary-600 text-white' 
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
          onClick={() => setActiveTab('call')}
        >
          Phone Call
        </button>
        <button
          className={`px-6 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'email' 
              ? 'bg-primary-600 text-white' 
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
          onClick={() => setActiveTab('email')}
        >
          Email
        </button>
      </div>

      <div className="max-w-2xl mx-auto">
        {activeTab === 'whatsapp' && (
          <form onSubmit={handleWhatsAppSubmit} className="space-y-6">
            {user.name && (
              <div>
                <label className="block text-gray-700 mb-2">Your Name</label>
                <input 
                  type="text" 
                  value={user.name} 
                  readOnly 
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
                />
              </div>
            )}

            {user.phone && (
              <div>
                <label className="block text-gray-700 mb-2">Your Phone</label>
                <input 
                  type="tel" 
                  value={user.phone} 
                  readOnly 
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
                />
              </div>
            )}

            <div>
              <label className="block text-gray-700 mb-2">Your Message*</label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                required
                placeholder="Type your message here..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg min-h-[120px]"
                rows="5"
              />
            </div>

            <button 
              type="submit" 
              className="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition-colors"
            >
              Send via WhatsApp
            </button>

            {isSubmitted && (
              <p className="text-green-600 text-center mt-4">
                WhatsApp is opening with your message...
              </p>
            )}
          </form>
        )}

        {activeTab === 'call' && (
          <div className="space-y-6">
            <div className="flex flex-col space-y-4">
              <button 
                onClick={handleCallClick}
                className="w-full bg-primary-600 text-white py-3 rounded-lg hover:bg-primary-700 transition-colors"
              >
                Call Us Now
              </button>
              
              <button 
                onClick={handleAddToContacts}
                className="w-full bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 transition-colors"
              >
                Save to Contacts
              </button>
            </div>
            
            <p className="text-gray-600 text-center">
              Tap "Call Us Now" to dial immediately or "Save to Contacts" to add us to your address book.
            </p>
          </div>
        )}

        {activeTab === 'email' && (
          <div className="space-y-6">
            <div>
              <label className="block text-gray-700 mb-2">Your Message</label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type your message here..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg min-h-[120px]"
                rows="5"
              />
            </div>
            
            <button 
              onClick={handleEmailClick}
              className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Open Email
            </button>
            
            <p className="text-gray-600 text-center">
              This will open your email app with our address pre-filled.
            </p>
          </div>
        )}

        <div className="mt-12 p-6 bg-gray-50 rounded-lg">
          <h3 className="text-xl font-semibold mb-4">Our Contact Information</h3>
          <div className="space-y-3">
            <p>
              <strong>Phone:</strong>{' '}
              <a href={`tel:${businessPhone}`} className="text-primary-600 hover:text-primary-700">
                {formattedPhone}
              </a>
            </p>
            <p>
              <strong>WhatsApp:</strong>{' '}
              <a 
                href={`https://wa.me/${businessPhone}`} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-primary-600 hover:text-primary-700"
              >
                {formattedPhone}
              </a>
            </p>
            <p>
              <strong>Email:</strong>{' '}
              <a 
                href={`mailto:${businessEmail}`}
                className="text-primary-600 hover:text-primary-700"
              >
                {businessEmail}
              </a>
            </p>
            <p>
              <strong>📍 Mombasa Branch:</strong>{' '}
              <span className="text-gray-600">Nyerere Avenue, Mombasa, Kenya</span>
            </p>
            <p>
              <strong>📍 Nairobi Branch:</strong>{' '}
              <span className="text-gray-600">The Oval, Parklands, Nairobi, Kenya</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContactUs;