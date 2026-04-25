// pan_client_config.js
//
// Frontend configuration template for the PAN Command Center.
// This file is loaded by index.html as a global window.ENV object.
//
// SETUP:
// 1. Copy this file to "pan_client_config.js" in the same directory.
// 2. Replace the placeholder values below with real credentials from
//    Google Cloud Console (Maps) and Firebase Console (project config).
// 3. NEVER commit pan_client_config.js to git. It is gitignored
//    in this directory and at the repo root.
//
// SECURITY NOTES:
// - GOOGLE_MAPS_API_KEY must be HTTP-referrer restricted in Google Cloud Console
//   to *.proxyagent.network/* and your localhost dev origins. An unrestricted
//   key in this file represents real billing risk if leaked.
// - FIREBASE_CONFIG values are designed by Google to be public, but are
//   only safe if Firebase Security Rules deny all access by default
//   (e.g., {".read": false, ".write": false} on Realtime Database).

window.ENV = {
    GOOGLE_MAPS_API_KEY: "REPLACE_WITH_DOMAIN_RESTRICTED_MAPS_KEY",

    FIREBASE_CONFIG: {
        apiKey: "REPLACE_WITH_FIREBASE_WEB_API_KEY",
        authDomain: "your-project.firebaseapp.com",
        databaseURL: "https://your-project-default-rtdb.firebaseio.com",
        projectId: "your-project",
        storageBucket: "your-project.firebasestorage.app",
        messagingSenderId: "REPLACE_WITH_SENDER_ID",
        appId: "REPLACE_WITH_APP_ID"
    }
};
