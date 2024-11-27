import React, { useContext } from "react";
import { Link } from "react-router-dom";
import { Context } from "./Context";

function SettingsPage() {
  const context = useContext(Context);

  return (
    <div className="App">
      <div style={{display: "flex", justifyContent: "right", margin: "10px"}}>
        <Link to="/">Back to Radar Page</Link>
        {context.kc.hasResourceRole(context.adminUserRole, context.adminUserResource) ? (
          <div>
            <a href={`${context.kcOptions.url}admin/${context.kcOptions.realm}/console/#/${context.kcOptions.realm}/users`} target="_blank" rel="noreferrer" style={{marginLeft: "10px"}}>Manage system users</a>
          </div>
        ) : null}
        <a href={`${context.kcOptions.url}realms/${context.kcOptions.realm}/account`} target="_blank" rel="noreferrer" style={{marginLeft: "10px"}}>Manage your account</a>
        <button onClick={() => context.kc.logout()} style={{marginLeft: "10px"}}>Logout</button>
      </div>
      <h1>System settings</h1>
      <div style={{display: "grid", gridTemplateColumns: "repeat(2, 1fr)", marginTop: "50px"}}>
        <p style={{margin: "0 10px", textAlign: "right"}}>Set flights update time in seconds:</p>
        <input style={{margin: "0 10px", width: "300px"}}/>
        <p style={{margin: "0 10px", textAlign: "right"}}>Set maximal time interval between two messages before flight considered to lost:</p>
        <input style={{margin: "0 10px", width: "300px"}}/>
      </div>
      <button style={{margin: "40px"}}>Save</button>
    </div>
  );
}

export default SettingsPage;
