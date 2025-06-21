import React from 'react';
import { Link } from 'react-router-dom';
import { FaFacebook, FaInstagram, FaTiktok, FaMapMarkerAlt, FaPhone, FaClock } from 'react-icons/fa';
import { MdDeliveryDining } from 'react-icons/md';

const AboutUs = () => {
  const branches = [
    {
      name: "Mombasa Main Branch",
      location: "Nyerere Avenue, Mombasa, Kenya",
      hours: "7:00 AM - 11:00 PM",
      mapUrl: "/branches/mombasa"
    },
    {
      name: "Nairobi Branch",
      location: "The Oval, Parklands, Nairobi, Kenya",
      hours: "7:00 AM - 11:00 PM",
      mapUrl: "/branches/nairobi"
    }
  ];

  const socialLinks = [
    {
      name: "Facebook",
      url: "https://www.facebook.com/Qaffeepoint/",
      icon: <FaFacebook className="w-6 h-6" />
    },
    {
      name: "Instagram",
      url: "https://www.instagram.com/qaffeepoint/",
      icon: <FaInstagram className="w-6 h-6" />
    },
    {
      name: "TikTok",
      url: "https://www.tiktok.com/@qaffeepoint",
      icon: <FaTiktok className="w-6 h-6" />
    }
  ];

  const menuCategories = [
    {
      name: "Middle Eastern Cuisine",
      items: ["Kebabs", "Shawarma", "Falafel", "Hummus"],
      icon: "🍢"
    },
    {
      name: "Burgers & Sandwiches",
      items: ["Beef Burgers", "Chicken Burgers", "Veggie Options", "Qaffee Point Special"],
      icon: "🍔"
    },
    {
      name: "Pasta & Grills",
      items: ["Lasagna", "Seafood Pasta", "Mixed Grill Platters", "T-bone Steak"],
      icon: "🍝"
    },
    {
      name: "Seafood & Biryani",
      items: ["Seafood Platters", "Lobster Specials", "Chicken Biryani", "Vegetable Biryani"],
      icon: "🍤"
    },
    {
      name: "Desserts & Beverages",
      items: ["Waffles", "Brownies", "Smoothies", "Specialty Coffee"],
      icon: "☕"
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <header className="bg-primary-600 text-white py-20 px-4">
        <div className="container mx-auto text-center">
          <h1 className="text-4xl font-bold mb-4">About Qaffee Point</h1>
          <p className="text-xl">Where bold flavors meet cozy ambiance</p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8">Our Story</h2>
          <div className="max-w-3xl mx-auto">
            <p className="text-gray-600 mb-8">
              Founded in 2015 in Mombasa, Qaffee Point has grown from a local coffee shop to a premier dining 
              destination known for its <strong>bold coffee blends</strong> and <strong>diverse international menu</strong>. 
              Our expansion to Nairobi's The Oval in Parklands brings our signature experience to more food 
              enthusiasts across Kenya.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center p-6 bg-gray-50 rounded-lg">
                <span className="block text-3xl font-bold text-primary-600 mb-2">8+</span>
                <span className="text-gray-600">Years in Business</span>
              </div>
              <div className="text-center p-6 bg-gray-50 rounded-lg">
                <span className="block text-3xl font-bold text-primary-600 mb-2">50+</span>
                <span className="text-gray-600">Menu Items</span>
              </div>
              <div className="text-center p-6 bg-gray-50 rounded-lg">
                <span className="block text-3xl font-bold text-primary-600 mb-2">2</span>
                <span className="text-gray-600">Locations</span>
              </div>
            </div>
          </div>
        </section>

        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8">Our Locations</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {branches.map((branch, index) => (
              <div key={index} className="bg-white shadow-lg rounded-lg p-6">
                <h3 className="text-xl font-semibold mb-4">{branch.name}</h3>
                <div className="flex items-center mb-3">
                  <FaMapMarkerAlt className="text-primary-600 w-5 h-5 mr-2" />
                  <p className="text-gray-600">{branch.location}</p>
                </div>
                <div className="flex items-center mb-4">
                  <FaClock className="text-primary-600 w-5 h-5 mr-2" />
                  <p className="text-gray-600"><strong>Hours:</strong> {branch.hours}</p>
                </div>
                <Link 
                  to={branch.mapUrl}
                  className="inline-flex items-center text-primary-600 hover:text-primary-700"
                >
                  View on map <FaMapMarkerAlt className="ml-2" />
                </Link>
              </div>
            ))}
          </div>
        </section>

        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8">Our Menu Highlights</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {menuCategories.map((category, index) => (
              <div key={index} className="bg-white shadow-lg rounded-lg p-6">
                <div className="text-4xl mb-4">{category.icon}</div>
                <h3 className="text-xl font-semibold mb-4">{category.name}</h3>
                <ul className="space-y-2">
                  {category.items.map((item, itemIndex) => (
                    <li key={itemIndex} className="text-gray-600">{item}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <div className="mt-8 flex items-center justify-center bg-gray-50 p-6 rounded-lg">
            <MdDeliveryDining className="text-primary-600 w-8 h-8 mr-3" />
            <p className="text-gray-600">
              Enjoy our food at home! Available on{' '}
              <a 
                href="https://glovoapp.com/ke/en/mombasa/qaffee-point-mbs/" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-primary-600 hover:text-primary-700"
              >
                Glovo
              </a>
            </p>
          </div>
        </section>

        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8">Connect With Us</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-xl font-semibold mb-6">Follow Us</h3>
              <div className="flex flex-col space-y-4">
                {socialLinks.map((social, index) => (
                  <a 
                    key={index}
                    href={social.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="flex items-center text-gray-600 hover:text-primary-600"
                    aria-label={`Visit our ${social.name} page`}
                  >
                    {social.icon}
                    <span className="ml-3">{social.name}</span>
                  </a>
                ))}
              </div>
            </div>
            <div>
              <h3 className="text-xl font-semibold mb-6">Contact Information</h3>
              <div className="flex items-center mb-6">
                <FaPhone className="text-primary-600 w-5 h-5 mr-3" />
                <p className="text-gray-600">+254 758 222222</p>
              </div>
              <Link 
                to="/contact-us"
                className="inline-flex items-center bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700"
              >
                Send us a message
              </Link>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default AboutUs;