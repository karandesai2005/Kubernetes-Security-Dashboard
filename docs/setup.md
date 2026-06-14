# Setup

## Local (recommended for development)

1. `cp .env.example .env`
2. `cp frontend/.env.example frontend/.env.local`
3. `make dev` (or `docker compose up --build`)
4. `make seed` (or visit dashboard and click seed button)
5. Open http://localhost:3000

## Production notes

Use the k8s/ manifests with Kustomize (`kubectl apply -k k8s/overlays/prod`).

Real collectors (Falco, Trivy Operator, etc) should be installed in the target cluster first. See collectors/ dir.
