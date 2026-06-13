// Hook: fetch Trivy vulnerability findings
// TODO: react-query useQuery wrapping GET /api/v1/vulns
export function useTrivyScan() { return { findings: [], loading: true, error: null } }
