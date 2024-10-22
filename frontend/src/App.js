import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './App.css';

function App() {
  const mapRef = useRef(null);
  const [spectatedFlightIcao, setSpectatedFlightIcao] = useState(null);
  const [flightDetails, setFlightDetails] = useState('');

  useEffect(() => {
    // Initialize the map when component mounts
    const map = L.map('map').setView([42.694771, 23.413245], 15);
    mapRef.current = map;

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    // map.on('zoomend', fetchAndDisplayFlights);
    // map.on('moveend', fetchAndDisplayFlights);

    map.on('click', () => {
      setFlightDetails('');
    });

    fetchAndDisplayFlights();

    const intervalId = setInterval(fetchAndDisplayFlights, 5000);

    return () => {
      clearInterval(intervalId);
      map.remove();
    };
  }, []);

  const fetchAndDisplayFlights = async () => {
    const map = mapRef.current;

    let data = await (await fetch('http://localhost:5000/flights', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    })).json()

    // Clear existing markers
    map.eachLayer((layer) => {
      if (layer instanceof L.Marker) {
        map.removeLayer(layer);
      }
    });

    const flights = data.flights;
    let foundedSpectatedFlight = false;

    for (const i in flights) {
      const flight = flights[i];

      if (flight.icao === spectatedFlightIcao) {
        displayFlightInfo(flight);
        foundedSpectatedFlight = true;
      }

      const isGroundVehicle = flight.callsign === 'GRND';
      const iconUrl = isGroundVehicle
        ? 'https://cdn2.iconfinder.com/data/icons/driverless-autonomous-electric-car/319/car-007-512.png'
        : 'https://cdn3.iconfinder.com/data/icons/remixicon-map/24/plane-line-256.png';
      const iconSize = isGroundVehicle ? [20, 20] : [30, 30];

      // Ensure latitude and longitude are not null or undefined
      if (flight.latitude == null || flight.longitude == null) {
        continue;
      }

      try {
        const flightMarker = L.marker([flight.latitude, flight.longitude], {
          icon: createRotatedIcon(flight.track, iconUrl, iconSize, `<p class="map-label-above-icon">${flight.callsign}</p>`),
          title: flight.aircraft_code,
        }).addTo(map);

        flightMarker.on('click', () => {
          displayFlightInfo(flight);
          setSpectatedFlightIcao(flight.icao);
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

  const createRotatedIcon = (angle, iconUrl, iconSize, htmlAfterIcon) => {
    return L.divIcon({
      html: `<img src="${iconUrl}" style="transform: rotate(${angle}deg);" width="${iconSize[0]}" height="${iconSize[1]}"/>${htmlAfterIcon}`,
      iconSize: iconSize,
      iconAnchor: [iconSize[0] / 2, iconSize[1] / 2],
      className: 'custom-icon',
    });
  };

  const displayFlightInfo = (flight) => {
    setFlightDetails(`
      <strong>${flight.icao}</strong><br />
      Callsign: ${flight.callsign}<br />
      Altitude: ${flight.altitude} feet
    `);
  };

  const hideFlightInfo = () => {
    setFlightDetails('');
    setSpectatedFlightIcao(null);
    bellNotifier('The spectated flight was lost!');
  };

  const bellNotifier = (message) => {
    const audio = document.getElementById('bell-audio');
    audio.play();
    setTimeout(() => {
      alert(message);
      audio.load();
    }, 0);
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div id="map" style={{ height: '60%' }}></div>
      <div id="flight-info" style={{ height: '40%', padding: '10px', borderTop: '1px solid #ccc', overflowY: 'auto' }}>
        <h2>Flight Information</h2>
        <div id="flight-details" dangerouslySetInnerHTML={{ __html: flightDetails }}></div>
      </div>
      <audio id="bell-audio">
        <source src="./assets/bell.mp3" type="audio/mpeg" />
      </audio>
    </div>
  );
}

export default App;
