import React from 'react';
import ReactDOM from 'react-dom/client';
import 'leaflet/dist/leaflet.css';
import { LiveSectorMap } from './components/LiveSectorMap';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <LiveSectorMap />
  </React.StrictMode>
);