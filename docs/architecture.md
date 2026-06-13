# Architecture

## Overview

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

## Components

- **Falco** — runtime threat detection, streams alerts via gRPC
- **Trivy Operator** — image/workload CVE scanning, VulnerabilityReport CRDs
- **AWS GuardDuty** — EKS Protection findings (optional, cloud-only)
- **RBAC Auditor** — kube-apiserver audit log analysis
- **Risk Engine** — weighted aggregation of all signal sources → 0-100 score
- **FastAPI Backend** — REST + WebSocket API
- **Next.js Frontend** — dashboard UI

## TODO
- [ ] ADR for event storage (Postgres vs TimescaleDB vs ClickHouse)
- [ ] Define WebSocket event schema
- [ ] RBAC for the dashboard itself
