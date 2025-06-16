import React from 'react';

const TermsAndConditions = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Terms and Conditions</h1>
      
      <div className="prose max-w-none">
        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">1. Acceptance of Terms</h2>
          <p>
            By accessing and using Qaffee Point's website and services, you accept and agree to be bound
            by the terms and conditions outlined here. If you do not agree to these terms, please do not
            use our services.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">2. Use of Services</h2>
          <p>Our services are available for personal, non-commercial use. You agree to:</p>
          <ul className="list-disc ml-6 mt-2">
            <li>Provide accurate and complete information when creating an account</li>
            <li>Maintain the security of your account credentials</li>
            <li>Accept responsibility for all activities under your account</li>
            <li>Use the services in compliance with applicable laws</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">3. Ordering and Payment</h2>
          <p>
            When placing orders through our platform:
          </p>
          <ul className="list-disc ml-6 mt-2">
            <li>All prices are in local currency and include applicable taxes</li>
            <li>Payment is required at the time of ordering</li>
            <li>We accept various payment methods as displayed during checkout</li>
            <li>Orders cannot be modified once confirmed</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">4. Delivery and Pickup</h2>
          <p>
            We offer both delivery and pickup options. Delivery times are estimates and may vary based
            on location, traffic, and other factors. We are not responsible for delays beyond our
            control.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">5. Refunds and Cancellations</h2>
          <p>
            Orders can be cancelled before preparation begins. Once preparation has started, cancellations
            and refunds are at our discretion. Quality issues must be reported within 30 minutes of
            delivery/pickup.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">6. Loyalty Program</h2>
          <p>
            Our loyalty program benefits are subject to change. Points have no cash value and cannot be
            transferred. We reserve the right to modify or terminate the program at any time.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">7. Intellectual Property</h2>
          <p>
            All content on our website and app is our property and protected by copyright laws. You may
            not use, reproduce, or distribute our content without permission.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">8. Limitation of Liability</h2>
          <p>
            We strive to provide the best service possible but make no warranties about the reliability
            or accuracy of our services. We are not liable for any indirect, incidental, or consequential
            damages.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">9. Changes to Terms</h2>
          <p>
            We reserve the right to modify these terms at any time. Continued use of our services after
            changes constitutes acceptance of the new terms.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">10. Contact Information</h2>
          <p>
            For questions about these terms, please contact us at{' '}
            <a href="mailto:legal@qaffee.com" className="text-primary-600 hover:text-primary-700">
              legal@qaffee.com
            </a>
          </p>
        </section>

        <section>
          <p className="text-sm text-gray-600">
            Last updated: {new Date().toLocaleDateString()}
          </p>
        </section>
      </div>
    </div>
  );
};

export default TermsAndConditions;