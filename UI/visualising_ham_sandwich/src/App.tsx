import React, { useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import ReactChartJs from "./components/ReachChartJs/ReactChartJs";
import { createTheme, ThemeProvider, Button } from "@mui/material";
import "./App.css";

const App: React.FC = () => {
  const [darkMode, setDarkMode] = useState<boolean>(true);

  const theme = createTheme({
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
            style={{
              position: "absolute",
              top: 10,
              right: 10,
              background: darkMode ? "#444" : "#2196f3",
              color: darkMode ? "#fff" : "#fff",
            }}
          >
            {darkMode ? "☀️ Light Mode" : "🌙 Dark Mode"}
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
