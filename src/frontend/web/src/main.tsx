import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./app/styles/app.css";
import { AppProviders } from "./app/providers/AppProviders";
import { AppRouter } from "./app/router";

const root = document.getElementById("root");
if (!root) throw new Error("Root element not found");

createRoot(root).render(
  <StrictMode>
    <AppProviders>
      <AppRouter />
    </AppProviders>
  </StrictMode>,
);
