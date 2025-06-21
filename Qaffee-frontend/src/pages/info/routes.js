import { lazy } from 'react';

// Lazy load info page components
const AboutUs = lazy(() => import('./AboutUs'));
const ContactUs = lazy(() => import('./ContactUs'));
const PrivacyPolicy = lazy(() => import('./PrivacyPolicy'));
const TermsAndConditions = lazy(() => import('./TermsAndConditions'));

// Info page routes configuration
export const infoRoutes = [
  {
    path: '/about-us',
    element: AboutUs,
  },
  {
    path: '/contact-us',
    element: ContactUs,
  },
  {
    path: '/privacy-policy',
    element: PrivacyPolicy,
  },
  {
    path: '/terms-and-conditions',
    element: TermsAndConditions,
  },
];

// Export components for direct use if needed
export {
  AboutUs,
  ContactUs,
  PrivacyPolicy,
  TermsAndConditions,
}; 