"""
Trivy Operator integration.
Watches VulnerabilityReport CRDs in the cluster and syncs findings to DB.

TODO:
  - Use kubernetes Python client to list/watch VulnerabilityReport CRDs
  - Upsert CVE findings
  - Trigger on-demand scans via Trivy Operator annotation
"""

class TrivyScanner:
    async def sync_findings(self, namespace: str = "default"):
        raise NotImplementedError
