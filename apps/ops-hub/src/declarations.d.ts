// Tells TypeScript it's okay to import image files
declare module '*.png' {
    const value: string;
    export default value;
}

declare module '*.svg' {
    const value: string;
    export default value;
}

// Tells TypeScript that Node's 'process.env' exists
declare var process: {
    env: {
        REACT_APP_TELEMETRY_WS_URL?: string;
        [key: string]: string | undefined;
    }
};