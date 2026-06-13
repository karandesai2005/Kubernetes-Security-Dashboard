// Hook: subscribe to live Falco events over WebSocket
// TODO: implement with socket.io-client, expose events[], loading, error
export function useFalcoEvents() { return { events: [], loading: true, error: null } }
