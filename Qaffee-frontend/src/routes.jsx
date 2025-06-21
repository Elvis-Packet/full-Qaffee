import { useEffect, lazy, Suspense } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import Loader from './components/ui/Loader';
import RoleGuard from './components/auth/RoleGuard';
import { useAuth } from './contexts/AuthContext';

// Lazy loading pages for better performance
const Home = lazy(() => import('./pages/Home'));
const Menu = lazy(() => import('./pages/Menu'));
const ItemDetails = lazy(() => import('./pages/ItemDetails'));
const Cart = lazy(() => import('./pages/Cart'));
const Checkout = lazy(() => import('./pages/Checkout'));
const Login = lazy(() => import('./pages/auth/Login'));
const Signup = lazy(() => import('./pages/auth/Signup'));
const AdminLogin = lazy(() => import('./pages/auth/AdminLogin'));
const UserProfile = lazy(() => import('./pages/account/UserProfile'));
const OrderTracker = lazy(() => import('./pages/orders/OrderTracker'));
const OrderHistory = lazy(() => import('./pages/orders/OrderHistory'));
const OrderDetails = lazy(() => import('./pages/orders/OrderDetails'));
const AdminDashboard = lazy(() => import('./pages/admin/AdminDashboard'));
const MenuManager = lazy(() => import('./pages/admin/MenuManager'));
const OrderManager = lazy(() => import('./pages/admin/OrderManager'));
const UserManager = lazy(() => import('./pages/admin/UserManager'));
const AnalyticsDashboard = lazy(() => import('./pages/admin/AnalyticsDashboard'));
const PromoManager = lazy(() => import('./pages/admin/PromoManager'));
const StaffOrders = lazy(() => import('./pages/staff/StaffOrders'));
const Branches = lazy(() => import('./pages/Branches'));

// Add new informational pages
const AboutUs = lazy(() => import('./pages/info/AboutUs'));
const ContactUs = lazy(() => import('./pages/info/ContactUs'));
const TermsAndConditions = lazy(() => import('./pages/info/TermsAndConditions'));
const PrivacyPolicy = lazy(() => import('./pages/info/PrivacyPolicy'));

function AppRoutes() {
  const { checkAuthStatus } = useAuth();
  const location = useLocation();

  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location.pathname]);

  return (
    <div className="app-container">
      <Navbar />
      <main className="main-content">
        <Suspense fallback={<Loader />}>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Home />} />
            <Route path="/menu" element={<Menu />} />
            <Route path="/menu/item/:id" element={<ItemDetails />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/admin/login" element={<AdminLogin />} />
            <Route path="/branches" element={<Branches />} />
            
            {/* Information Pages */}
            <Route path="/about-us" element={<AboutUs />} />
            <Route path="/contact-us" element={<ContactUs />} />
            <Route path="/terms-and-conditions" element={<TermsAndConditions />} />
            <Route path="/privacy-policy" element={<PrivacyPolicy />} />
            
            {/* Customer Routes */}
            <Route path="/cart" element={
              <RoleGuard roles={['customer', 'admin']} fallback="/login">
                <Cart />
              </RoleGuard>
            } />
            <Route path="/checkout" element={
              <RoleGuard roles={['customer', 'admin']} fallback="/login">
                <Checkout />
              </RoleGuard>
            } />
            <Route path="/account" element={
              <RoleGuard roles={['customer', 'admin']} fallback="/login">
                <UserProfile />
              </RoleGuard>
            } />
            <Route path="/order-status" element={
              <RoleGuard roles={['customer', 'admin']} fallback="/login">
                <OrderTracker />
              </RoleGuard>
            } />
            <Route path="/orders/history" element={
              <RoleGuard roles={['customer', 'admin']} fallback="/login">
                <OrderHistory />
              </RoleGuard>
            } />
            <Route path="/orders/:id" element={
              <RoleGuard roles={['customer', 'admin', 'staff']} fallback="/login">
                <OrderDetails />
              </RoleGuard>
            } />
            
            {/* Admin Routes */}
            <Route path="/admin/dashboard" element={
              <RoleGuard roles={['admin']} fallback="/admin/login">
                <AdminDashboard />
              </RoleGuard>
            } />
            <Route path="/admin/menu" element={
              <RoleGuard roles={['admin']} fallback="/admin/login">
                <MenuManager />
              </RoleGuard>
            } />
            <Route path="/admin/orders" element={
              <RoleGuard roles={['admin']} fallback="/admin/login">
                <OrderManager />
              </RoleGuard>
            } />
            <Route path="/admin/users" element={
              <RoleGuard roles={['admin']} fallback="/admin/login">
                <UserManager />
              </RoleGuard>
            } />
            <Route path="/admin/stats" element={
              <RoleGuard roles={['admin']} fallback="/admin/login">
                <AnalyticsDashboard />
              </RoleGuard>
            } />
            <Route path="/admin/promotions" element={
              <RoleGuard roles={['admin']} fallback="/admin/login">
                <PromoManager />
              </RoleGuard>
            } />
            
            {/* Staff Routes */}
            <Route path="/staff/orders" element={
              <RoleGuard roles={['staff', 'admin']} fallback="/admin/login">
                <StaffOrders />
              </RoleGuard>
            } />
          </Routes>
        </Suspense>
      </main>
      <Footer />
    </div>
  );
}

export default AppRoutes;