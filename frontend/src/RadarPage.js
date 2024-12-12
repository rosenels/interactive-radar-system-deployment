import React, { useContext, useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import Bell from "./assets/bell.mp3";
import { Context } from "./Context";

let spectatedFlightIcao = null;
let foundedSpectatedFlight = false;

function useSound(audioSource) {
  const soundRef = useRef();

  useEffect(() => {
    soundRef.current = new Audio(audioSource);
    // eslint-disable-next-line
  }, []);

  const playSound = () => {
    soundRef.current.play();
  };

  const pauseSound = () => {
    soundRef.current.pause();
  };

  return {
    playSound,
    pauseSound,
  };
};

function RadarPage() {
  document.title = "Interactive radar system";

  const context = useContext(Context);

  const mapRef = useRef(null);
  const [flightDetails, setFlightDetails] = useState("");
  const [flightsUpdateIntervalInSeconds, setFlightsUpdateIntervalInSeconds] = useState(5);

  const playBellSound = useSound(Bell).playSound;

  useEffect(() => {
    loadConfiguration();

    // Initialize the map when component mounts
    const map = L.map("map").setView([42.694771, 23.413245], 15);
    mapRef.current = map;

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors",
    }).addTo(map);

    map.on("click", () => {
      setFlightDetails("");
      spectatedFlightIcao = null;
    });

    fetchAndDisplayFlights();

    const intervalId = setInterval(() => {
      fetchAndDisplayFlights();
      context.kc.updateToken();
    }, flightsUpdateIntervalInSeconds * 1000);

    return () => {
      clearInterval(intervalId);
      map.remove();
    };
    // eslint-disable-next-line
  }, [flightsUpdateIntervalInSeconds]);

  async function loadConfiguration() {
    let data;
    try {
      data = await (await fetch(`${context.backendAddress}/configuration?token=${context.kc.token}`)).json();
    }
    catch(error) {
      // console.error(error);
      return;
    }
    setFlightsUpdateIntervalInSeconds(data.configuration.RADAR_FLIGHTS_UPDATE_TIME_IN_SECONDS);
  }

  async function fetchAndDisplayFlights() {
    const map = mapRef.current;
    let data;

    try {
      data = await (await fetch(`${context.backendAddress}/flights`)).json();
    }
    catch(error) {
      // console.error(error);
      return;
    }

    // Clear existing markers
    map.eachLayer((layer) => {
      if (layer instanceof L.Marker) {
        map.removeLayer(layer);
      }
    });

    const flights = data.flights;
    foundedSpectatedFlight = false;

    for (const i in flights) {
      const flight = flights[i];

      if (flight.icao === spectatedFlightIcao) {
        displayFlightInfo(flight);
        foundedSpectatedFlight = true;
      }

      const isGroundVehicle = flight.callsign === "GRND";
      const iconUrl = isGroundVehicle
        ? "https://cdn2.iconfinder.com/data/icons/driverless-autonomous-electric-car/319/car-007-512.png"
        : "https://cdn3.iconfinder.com/data/icons/remixicon-map/24/plane-line-256.png";
      const iconSize = isGroundVehicle ? [20, 20] : [30, 30];

      // Ensure latitude and longitude are not null
      if (flight.latitude == null || flight.longitude == null) {
        continue;
      }

      try {
        const flightMarker = L.marker([flight.latitude, flight.longitude], {
          icon: createRotatedIcon(flight.track, iconUrl, iconSize, `<p class="map-label-above-icon">${(flight.callsign !== null) ? flight.callsign : ""}</p>`),
          title: flight.callsign,
        }).addTo(map);

        // flightMarker.bindPopup(`
        //   <strong>${flight.aircraft_code} ${flight.number}</strong><br>
        //   Callsign: ${flight.callsign}<br>
        //   Altitude: ${flight.altitude} feet
        // `);

        // eslint-disable-next-line
        flightMarker.on("click", () => {
          displayFlightInfo(flight);
          spectatedFlightIcao = flight.icao;
          foundedSpectatedFlight = true;
        });
      }
      catch(error) {
        // console.error(error);
      }
    }

    if (!foundedSpectatedFlight && spectatedFlightIcao) {
      hideFlightInfo();
    }
  };

  function createRotatedIcon(angle, iconUrl, iconSize, htmlAfterIcon) {
    return L.divIcon({
      html: `<img src="${iconUrl}" style="transform: rotate(${angle}deg);" width="${iconSize[0]}" height="${iconSize[1]}"/>${htmlAfterIcon}`,
      iconSize: iconSize,
      iconAnchor: [iconSize[0] / 2, iconSize[1] / 2],
      className: "custom-icon",
    });
  };

  async function displayFlightInfo(flight) {
    let imageSrc = "";
    let imagePhotographer = "";
    let imageLink = "";
    let imageWidth = 0;
    let imageHeight = 0;
    try {
      imageSrc = await (await fetch(`https://api.planespotters.net/pub/photos/hex/${flight.icao}`)).json();
      imageSrc = imageSrc.photos[0];
      imagePhotographer = "© " + imageSrc.photographer;
      imageLink = imageSrc.link;
      if (imageSrc.thumbnail_large !== undefined) {
        imageWidth = imageSrc.thumbnail_large.size.width;
        imageHeight = imageSrc.thumbnail_large.size.height;
        imageSrc = imageSrc.thumbnail_large.src;
      }
      else {
        imageWidth = imageSrc.thumbnail.size.width;
        imageHeight = imageSrc.thumbnail.size.height;
        imageSrc = imageSrc.thumbnail.src;
      }
    } catch (error) {
      imageSrc = "";
      imagePhotographer = "";
      imageLink = "";
      imageWidth = 0;
      imageHeight = 0;
      // console.error(error);
    }
    let imageShowHeight = 180;
    setFlightDetails(`
      <div style="height: 100%; margin-right: 10px">
        <img style="height: ${imageShowHeight}px" src="${imageSrc}"></img>
        <br>
        <a style="margin: 0" target="_blank" href="${imageLink}">
          <p style="margin: 0; max-width: ${(imageWidth * imageShowHeight) / imageHeight}px; word-wrap: break-word">${imagePhotographer}</p>
        </a>
      </div>
      <div style="height: 100%">
        ICAO: <strong>${flight.icao}</strong><br>
        Callsign: ${(flight.callsign !== null) ? flight.callsign : "---"}<br>
        Altitude: ${(flight.altitude !== null) ? flight.altitude : "---"} feet<br>
        Speed: ${(flight.ground_speed !== null) ? flight.ground_speed : "---"} knots<br>
        Track: ${(flight.track !== null) ? flight.track : "---"}°
      </div>
    `);
  };

  function hideFlightInfo() {
    setFlightDetails("");
    spectatedFlightIcao = null;
    bellNotifier("The spectated flight was lost!");
  };

  function bellNotifier(message) {
    playBellSound();
    setTimeout(() => {
      alert(message);
    }, 10);
  };

  async function startControllingFlight() {
    try {
      await fetch(`${context.backendAddress}/instructions/${spectatedFlightIcao}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          "token": context.kc.token
        })
      });
    } catch (error) {
      // console.error(error);
    }
  }

  return (
    <div style={{height: "100vh", display: "flex", flexDirection: "column"}}>
      <div style={{display: "flex", justifyContent: "right", margin: "10px"}}>
        {context.kc.hasResourceRole(context.adminUserRole, context.adminUserResource) ? (
          <div>
            <Link to="/settings">Manage system settings</Link>
            <a href={`${context.kcOptions.url}admin/${context.kcOptions.realm}/console/#/${context.kcOptions.realm}/users`} target="_blank" rel="noreferrer" style={{marginLeft: "10px"}}>Manage system users</a>
          </div>
        ) : null}
        <a href={`${context.kcOptions.url}realms/${context.kcOptions.realm}/account`} target="_blank" rel="noreferrer" style={{marginLeft: "10px"}}>Manage your account</a>
        <button onClick={() => context.kc.logout()} style={{marginLeft: "10px"}}>Logout</button>
      </div>
      <div id="map" style={{height: "55%"}}></div>
      <h2 style={{margin: "10px", paddingTop: "5px", borderTop: "1px solid #ccc"}}>Flight Information</h2>
      <div id="flight-info" style={{display: "flex", height: "45%", padding: "10px", border: "0", overflowY: "auto"}}>
        <div id="flight-details" style={{display: "flex"}} dangerouslySetInnerHTML={{ __html: flightDetails }}></div>
        <div id="flight-controls" style={{display: "flex", marginLeft: "10px"}}>
          <button onClick={startControllingFlight} style={{height: "20px"}}>Control this flight</button>
        </div>
      </div>
    </div>
  );
}

export default RadarPage;
