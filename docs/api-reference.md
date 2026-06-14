# API Reference

Base: /api/v1

- GET /health
- GET /threats?limit=50&severity=high&source=falco
- GET /vulns
- GET /rbac
- GET /risk-score
- POST /seed
- POST /scan/trivy?namespace=foo
- WS /ws/threats   (pushes new threat objects when mock mode enabled)

Full interactive docs: http://localhost:8000/docs
