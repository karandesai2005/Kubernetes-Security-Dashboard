# K8s Security Posture Dashboard

> **Status: 🚧 Early Development** — structure and interfaces are being defined. Contributions and feedback welcome.

A unified security observability dashboard for Kubernetes clusters, aggregating signals from **Falco**, **Trivy**, **AWS GuardDuty**, and **RBAC audit logs** into a single risk-scored interface.

---

## Why

Running security tools in isolation means alert fatigue and blind spots. This project aims to:

- Correlate runtime threats (Falco), image vulnerabilities (Trivy), cloud-level detections (GuardDuty), and RBAC misconfigurations in one view
- Produce a single **Cluster Risk Score** from weighted signal aggregation
- Make Kubernetes security posture legible without requiring 4 separate dashboards

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  K8s Cluster                         │
│                                                       │
│  Falco ──────┐                                        │
│  Trivy Op ───┼──► Collector Layer ──► FastAPI Backend │
│  RBAC Audit ─┘         │                │            │
│                         │              DB (Postgres)  │
│                         │              Cache (Redis)  │
└─────────────────────────┼──────────────┼─────────────┘
                          │              │
                    GuardDuty (AWS)    Next.js Frontend
```

| Component | Role |
|---|---|
| **Falco** | Runtime threat detection — streams alerts via gRPC |
| **Trivy Operator** | Image/workload CVE scanning via VulnerabilityReport CRDs |
| **AWS GuardDuty** | EKS Protection findings (optional, requires AWS) |
| **RBAC Auditor** | kube-apiserver audit log analysis for privilege issues |
| **Risk Engine** | Weighted aggregation → 0–100 cluster risk score |
| **FastAPI** | REST + WebSocket API, Postgres + Redis |
| **Next.js** | Dashboard UI with real-time threat feed |

---

## Project Structure

```
k8s-security-dashboard/
├── backend/                    # FastAPI service
│   ├── app/
│   │   ├── api/routes.py       # REST endpoints
│   │   ├── core/               # Config, auth, logging
│   │   ├── models/             # SQLAlchemy ORM models
│   │   └── services/           # Falco, Trivy, GuardDuty, RBAC, RiskEngine
│   └── tests/
├── frontend/                   # Next.js + Tailwind dashboard
│   └── src/
│       ├── components/         # Dashboard, ThreatFeed, VulnTable, RBACViewer
│       ├── hooks/              # useFalcoEvents, useTrivyScan, useRBACGraph
│       └── pages/              # threats, vulnerabilities, rbac, settings
├── collectors/                 # Per-tool Helm values and config
│   ├── falco/
│   ├── trivy/
│   ├── guardduty/
│   └── rbac/
├── k8s/                        # Kubernetes manifests (Kustomize)
│   ├── base/
│   └── overlays/
│       ├── dev/
│       └── prod/
├── scripts/                    # setup, local-dev, deploy, seed
├── docs/                       # architecture, setup, API reference
└── .github/workflows/          # CI, lint, scan
```

---

## Getting Started

### Prerequisites

- Docker + Docker Compose
- Node.js 20+
- Python 3.12+
- `kubectl` + a running cluster (or `kind`/`minikube` locally)

### Local Development

```bash
# Clone
git clone https://github.com/karandesai2005/k8s-security-dashboard
cd k8s-security-dashboard

# Copy env files
cp .env.example .env
cp frontend/.env.example frontend/.env.local

# Start everything (Postgres, Redis, backend, frontend)
make dev
# or: docker compose up --build

# Seed mock data (no live cluster needed)
make seed
```

Frontend: http://localhost:3000  
Backend API: http://localhost:8000  
API docs: http://localhost:8000/docs

### Running Tests

```bash
make test
```

---

## Planned Features

- [ ] Real-time Falco event stream via WebSocket
- [ ] Trivy Operator CRD watcher and CVE table
- [ ] RBAC graph visualisation (highlight overpermissioned subjects)
- [ ] GuardDuty EKS Protection findings ingestion
- [ ] Cluster Risk Score with configurable weights
- [ ] Alert deduplication and suppression rules
- [ ] Namespace-scoped views
- [ ] Prometheus metrics export
- [ ] Slack / PagerDuty alert routing

---

## Tech Stack

**Backend:** Python · FastAPI · SQLAlchemy · Pydantic · structlog  
**Frontend:** Next.js 14 · TypeScript · Tailwind CSS · Recharts · React Query  
**Infra:** Kubernetes · Kustomize · Docker Compose  
**Security tools:** Falco · Trivy Operator · AWS GuardDuty · kube-apiserver audit logs

---

## Contributing

This project is in early development. See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## Author

**Karan Desai** — [github.com/karandesai2005](https://github.com/karandesai2005) · [karan-desai.vercel.app](https://karan-desai.vercel.app)

---

## License

MIT — see [LICENSE](./LICENSE)
