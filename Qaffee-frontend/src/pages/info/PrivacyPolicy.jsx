import React from 'react';

const PrivacyPolicy = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Privacy Policy</h1>

      <div className="prose max-w-none">
        <p className="text-gray-600 mb-8">
          At <strong>Qaffee Point</strong>, we value your privacy and are committed to protecting the personal information you share with us. This Privacy Policy outlines how we collect, use, store, and protect your data when you interact with us online or in-store.
        </p>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">1. Information We Collect</h2>
          <p className="mb-4">We may collect the following types of information:</p>
          <ul className="list-disc pl-6 space-y-2 text-gray-600">
            <li><strong>Personal Information:</strong> Name, phone number, email address, and contact details provided when placing an order, creating an account, or contacting us via WhatsApp or other channels.</li>
            <li><strong>Order Information:</strong> Items ordered, delivery details, payment methods, and transaction history.</li>
            <li><strong>Technical Information:</strong> Device type, browser information, IP address, and usage data for website analytics and improvement.</li>
            <li><strong>Location Data:</strong> When using our website or app with location services enabled, we may collect approximate location to provide relevant services.</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">2. How We Use Your Information</h2>
          <p className="mb-4">Your information is used to:</p>
          <ul className="list-disc pl-6 space-y-2 text-gray-600">
            <li>Process and fulfill your orders and reservations</li>
            <li>Provide customer support and respond to inquiries</li>
            <li>Improve our services, menu offerings, and customer experience</li>
            <li>Send updates, promotions, and important notices (with your consent)</li>
            <li>Ensure the security of our services and prevent fraud</li>
            <li>Comply with legal obligations and regulations</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">3. Data Sharing and Disclosure</h2>
          <p className="mb-4">
            We do not sell or rent your personal data to third parties. However, we may share information with:
          </p>
          <ul className="list-disc pl-6 space-y-2 text-gray-600">
            <li><strong>Service Providers:</strong> Trusted delivery partners (e.g., Glovo) and payment processors strictly for order fulfillment</li>
            <li><strong>Legal Compliance:</strong> When required by law or to protect our rights and safety</li>
            <li><strong>Business Transfers:</strong> In case of merger, acquisition, or sale of assets</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">4. Data Security</h2>
          <p className="mb-4">
            We implement robust security measures including:
          </p>
          <ul className="list-disc pl-6 space-y-2 text-gray-600">
            <li>Encryption of sensitive data during transmission</li>
            <li>Secure access controls and authentication protocols</li>
            <li>Regular security audits and vulnerability assessments</li>
            <li>Employee training on data protection best practices</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">5. Cookies and Tracking Technologies</h2>
          <p className="mb-4">
            Our website uses cookies and similar technologies to:
          </p>
          <ul className="list-disc pl-6 space-y-2 text-gray-600">
            <li>Enhance user experience and remember preferences</li>
            <li>Analyze website traffic and usage patterns</li>
            <li>Deliver targeted advertisements (with your consent)</li>
          </ul>
          <p className="mt-4 text-gray-600">
            You can manage cookie preferences through your browser settings or our cookie consent tool.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">6. Your Rights and Choices</h2>
          <p className="mb-4">You have the right to:</p>
          <ul className="list-disc pl-6 space-y-2 text-gray-600">
            <li>Access and receive a copy of your personal data</li>
            <li>Request correction of inaccurate or incomplete information</li>
            <li>Request deletion of your personal data when no longer needed</li>
            <li>Object to or restrict certain processing activities</li>
            <li>Withdraw consent for marketing communications at any time</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">7. Data Retention</h2>
          <p className="mb-4">
            We retain your personal data only as long as necessary to fulfill the purposes outlined in this policy, unless a longer retention period is required by law. Typical retention periods include:
          </p>
          <ul className="list-disc pl-6 space-y-2 text-gray-600">
            <li>Order history: 3 years for accounting and customer service purposes</li>
            <li>Marketing preferences: Until you unsubscribe or request deletion</li>
            <li>Website analytics: Up to 2 years</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">8. Contact Us</h2>
          <p className="mb-4">
            For privacy-related inquiries or to exercise your rights, please contact our Data Protection Officer via:
          </p>
          <ul className="list-none space-y-2">
            <li>
              <a 
                href="https://wa.me/254758222222" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="text-primary-600 hover:text-primary-700"
              >
                WhatsApp: +254 758 222222
              </a>
            </li>
            <li>
              <a 
                href="mailto:privacy@qaffeepoint.com" 
                className="text-primary-600 hover:text-primary-700"
              >
                Email: privacy@qaffeepoint.com
              </a>
            </li>
            <li>In-person: At any Qaffee Point location during business hours</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">9. Policy Updates</h2>
          <p className="text-gray-600">
            We may update this Privacy Policy periodically. Significant changes will be communicated through our website or direct notifications. The "Last Updated" date at the bottom of this page indicates the latest revision.
          </p>
        </section>

        <p className="text-sm text-gray-500 italic">
          Last Updated: {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
        </p>
      </div>
    </div>
  );
};

export default PrivacyPolicy;