import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet, useLocation } from 'react-router-dom';
import './App.css';
import { Container } from '@mui/material'; // For consistent padding
import Dashboard from './components/Dashboard';
import UseCaseForm from './components/UseCaseForm';
import Login from './components/Login';
import Header from './components/Header'; // Import Header
// Import UseCaseList if you plan to use it directly in a route,
// or it might be part of Dashboard. For now, not directly routed.
// import UseCaseList from './components/UseCaseList';

// Basic PrivateRoute component
// No changes needed to PrivateRoute itself for now
const PrivateRoute: React.FC = () => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
  // In a real app, you'd also want to check token validity, expiry, etc.
  // And likely have a global state (Context API or Redux) for auth status.
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

// Helper to conditionally render Header
const Layout: React.FC = () => {
  const location = useLocation();
  const noHeaderPaths = ['/login']; // Paths where header shouldn't be shown

  return (
    <>
      {!noHeaderPaths.includes(location.pathname) && <Header />}
      <Container sx={{ mt: 4, mb: 4 }}> {/* Add some margin top/bottom */}
        <Outlet /> {/* Child routes will render here */}
      </Container>
    </>
  );
};

function App() {
  return (
    <Router>
      {/* CssBaseline and ThemeProvider are in index.tsx */}
      {/* Header is now part of the Layout component */}
      <Routes>
        {/* Routes that should NOT have the main layout (e.g. Login) */}
        <Route path="/login" element={<Login />} />

        {/* Routes that SHOULD have the main layout (Header + Container) */}
        <Route element={<Layout />}>
          <Route element={<PrivateRoute />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/usecases/new" element={<UseCaseForm />} />
            <Route path="/usecases/edit/:id" element={<UseCaseForm />} />
          </Route>
        </Route>

        {/* Fallback for unmatched routes */}
        {/* If authenticated, redirect to dashboard, else to login */}
        <Route path="*" element={localStorage.getItem('isAuthenticated') === 'true' ? <Navigate to="/" replace /> : <Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
