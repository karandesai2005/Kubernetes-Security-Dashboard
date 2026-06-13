"""
AWS GuardDuty findings fetcher.
Pulls EKS Protection findings and maps them to ThreatEvents.

TODO:
  - boto3 guardduty.list_findings + get_findings
  - Filter by resource type = EKSCluster / Container
  - Deduplicate by finding ID
"""

class GuardDutyFetcher:
    async def fetch_findings(self):
        raise NotImplementedError
