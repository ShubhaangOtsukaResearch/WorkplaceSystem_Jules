import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns'; // Using date-fns

// A basic theme for consistent styling
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // A standard blue
    },
    secondary: {
      main: '#dc004e', // A standard pink/red
    },
    background: {
      default: '#f4f6f8', // Light grey background
      paper: '#ffffff',   // White for paper elements
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
    h1: {
      fontSize: '2.2rem',
      fontWeight: 500,
    },
    h2: {
      fontSize: '1.8rem',
      fontWeight: 500,
    }
    // You can define more typography variants here
  },
  spacing: 8, // Default spacing unit (8px)
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none', // Buttons without ALL CAPS
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          padding: '16px', // Default padding for Paper components
        }
      }
    }
  }
});

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <LocalizationProvider dateAdapter={AdapterDateFns}>
        <CssBaseline /> {/* Normalize CSS and apply background color */}
        <App />
      </LocalizationProvider>
    </ThemeProvider>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
