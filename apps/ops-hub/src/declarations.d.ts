// Tells TypeScript that Node's 'process.env' exists
declare var process: {
    env: {
        REACT_APP_TELEMETRY_WS_URL?: string;
        [key: string]: string | undefined;
    }
};