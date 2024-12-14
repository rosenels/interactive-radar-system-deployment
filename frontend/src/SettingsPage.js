import React, { useContext, useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Context } from "./Context";

function SettingsPage() {
  document.title = "Settings | Interactive radar system";

  const context = useContext(Context);

  const [flightsUpdateInterval, setFlightsUpdateInterval] = useState();
  const [maxTimeInterval, setMaxTimeInterval] = useState();

  useEffect(() => {
    loadConfiguration();

    const intervalId = setInterval(() => {
      context.kc.updateToken(60); // update the token if it expires in the next 60 seconds
    }, 30000); // check once at every 30 seconds

    return () => {
      clearInterval(intervalId);
    };
    // eslint-disable-next-line
  }, []);

  async function loadConfiguration() {
    let data;
    try {
      data = await (await fetch(`${context.backendAddress}/configuration?token=${context.kc.token}`)).json();
    }
    catch(error) {
      // console.error(error);
      return;
    }
    setFlightsUpdateInterval(data.configuration.RADAR_FLIGHTS_UPDATE_TIME_IN_SECONDS);
    setMaxTimeInterval(data.configuration.MAX_FLIGHT_UPDATE_INTERVAL_IN_SECONDS);
  }

  async function saveConfiguration() {
    try {
      await fetch(`${context.backendAddress}/configuration`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          "token": context.kc.token,
          "RADAR_FLIGHTS_UPDATE_TIME_IN_SECONDS": flightsUpdateInterval,
          "MAX_FLIGHT_UPDATE_INTERVAL_IN_SECONDS": maxTimeInterval
        })
      });
    }
    catch(error) {
      // console.error(error);
      return;
    }
  }

  return (
    <div className="App">
      <div style={{ display: "flex", justifyContent: "right", margin: "10px" }}>
        <Link to="/">Back to Radar Page</Link>
        {context.kc.hasResourceRole(context.adminUserRole, context.adminUserResource) ? (
          <div>
            <a href={`${context.kcOptions.url}admin/${context.kcOptions.realm}/console/#/${context.kcOptions.realm}/users`} target="_blank" rel="noreferrer" style={{ marginLeft: "10px" }}>Manage system users</a>
          </div>
        ) : null}
        <a href={`${context.kcOptions.url}realms/${context.kcOptions.realm}/account`} target="_blank" rel="noreferrer" style={{ marginLeft: "10px" }}>Manage your account</a>
        <button onClick={() => context.kc.logout()} style={{ marginLeft: "10px" }}>Logout</button>
      </div>
      <h1>System settings</h1>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", marginTop: "50px" }}>
        <p style={{ margin: "0 10px", textAlign: "right" }}>Set flights update time in seconds:</p>
        <input type="number" value={flightsUpdateInterval} onChange={(e) => setFlightsUpdateInterval(e.target.value)} style={{ margin: "0 10px", width: "300px" }}/>
        <p style={{ margin: "0 10px", textAlign: "right" }}>Set maximal time interval between two messages before flight considered to lost:</p>
        <input type="number" value={maxTimeInterval} onChange={(e) => setMaxTimeInterval(e.target.value)} style={{ margin: "0 10px", width: "300px" }}/>
      </div>
      <button onClick={saveConfiguration} style={{ margin: "40px" }}>Save</button>
    </div>
  );
}

export default SettingsPage;
