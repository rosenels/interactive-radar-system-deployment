import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Keycloak from "keycloak-js";
import RadarPage from "./RadarPage";
import { Context } from "./Context";

let kcOptions = {
  url: 'http://localhost:8080/',
  realm: 'interactive-radar-system',
  clientId: 'frontend',
}

let kc = new Keycloak(kcOptions);

await kc.init({
  onLoad: 'login-required', // Supported values: 'check-sso' (default), 'login-required'
});
// console.log(kc.token);

let contextValue = {
  "backendAddress": "http://localhost:5000",
  "kcOptions": kcOptions,
  "kc": kc,
  "adminUserRole": "realm-admin",
  "adminUserResource": "realm-management"
}

function App() {
  return (
    <Context.Provider value={contextValue}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<RadarPage/>}/>
        </Routes>
      </BrowserRouter>
    </Context.Provider>
  );
}

export default App;
