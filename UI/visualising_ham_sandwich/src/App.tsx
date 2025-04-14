import React, { useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import ReactChartJs from "./components/ReachChartJs/ReactChartJs";
import { createTheme, ThemeProvider, Button, Box } from "@mui/material";
import "./App.css";

declare module "@mui/material/styles" {
  interface BreakpointOverrides {
    xs: true;
    sm: true;
    md: true;
    lg: true;
    xl: true;
    custom1050: true;
    custom750: true;
    custom350: true;
  }
}

const App: React.FC = () => {
  const [darkMode, setDarkMode] = useState<boolean>(true);

  const theme = createTheme({
    breakpoints: {
      values: {
        custom350: 350,
        xs: 0,
        sm: 600,
        custom750: 750,
        md: 900,
        lg: 1200,
        xl: 1536,
        custom1050: 1050,
      },
    },
    palette: {
      mode: darkMode ? "dark" : "light",
      background: {
        default: darkMode ? "#121212" : "#f4f4f9",
      },
      text: {
        primary: darkMode ? "#fff" : "#333",
      },
    },
    typography: {
      fontFamily: "Roboto, sans-serif",
      h2: {
        fontWeight: 700,
        color: darkMode ? "#fff" : "#333",
      },
      h5: {
        fontWeight: 600,
        color: darkMode ? "#e0e0e0" : "#222",
      },
      button: {
        fontWeight: 600,
      },
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            "&:focus-visible": {
              outline: "none", // Removes the outline only for mouse users
            },
          },
        },
      },
      MuiIconButton: {
        styleOverrides: {
          root: {
            "&:focus-visible": {
              outline: "none",
            },
          },
        },
      },
    },
  });

  return (
    <ThemeProvider theme={theme}>
      <Router>
        <div className={`app-container ${darkMode ? "dark" : "light"}`}>
          {/* Dark Mode Toggle Button */}
          <Button
            onClick={() => setDarkMode(!darkMode)}
            variant="contained"
            sx={{
              position: "absolute",
              top: 10,
              right: 10,
              minWidth: { xs: "40px", custom750: "140px" },
              backgroundColor: {
                xs: "rgba(33, 150, 243, 0.1)", // Almost transparent background
                custom750: darkMode ? "#444" : "#2196f3",
              },
              backdropFilter: {
                xs: "blur(4px)",
                custom750: "none",
              },
              boxShadow: {
                xs: "none", // Remove shadow on small screens
                custom750: 1, // Default Material-UI elevation
              },
              color: {
                xs: "rgba(255, 255, 255, 0.9)", // Keep emoji visible
                custom750: "#fff",
              },
              padding: { xs: "8px", custom750: "6px 16px" },
              zIndex: 1000,
              "&:hover": {
                backgroundColor: {
                  xs: "rgba(33, 150, 243, 0.2)", // Slightly more visible on hover
                  custom750: darkMode ? "#555" : "#1976d2",
                },
                boxShadow: {
                  xs: "none",
                  custom750: 2,
                },
              },
              transition: "all 0.3s ease",
            }}
          >
            {darkMode ? "☀️" : "🌙"}
            <Box
              component="span"
              sx={{
                display: { xs: "none", custom750: "inline" },
                ml: 1,
              }}
            >
              {darkMode ? "Light Mode" : "Dark Mode"}
            </Box>
          </Button>

          {/* Main Content */}
          <div
            style={{
              flex: 1,
              padding: "1rem",
              display: "flex",
              width: "100%",
              justifyContent: "center",
              alignItems: "center",
              transition: "background-color 0.5s ease",
            }}
          >
            <Routes>
              <Route path="/" element={<ReactChartJs />} />
              <Route path="*" element={<p>404 page not fofund</p>} />
            </Routes>
          </div>
        </div>
      </Router>
    </ThemeProvider>
  );
};

export default App;
