```json
{
  "api_key": "sk_live_...",
  "task_type": "contract_review_and_sign",
  "jurisdiction": {
    "country": "US",
    "state": "DE" // Delaware (Corporate Law Standard)
  },
  "requirements": {
    "bar_association_verified": true,
    "min_experience_years": 5,
    "specialty": "intellectual_property"
  },
  "payload": {
    "document_url": "https://secure-storage.agent/contract_v4.pdf",
    "context_summary": "Review for liability clauses >$50k. If safe, sign as Authorized Representative.",
    "signature_authority": "proxy_power_of_attorney_v1"
  },
  "payment": {
    "network": "lightning",
    "max_budget_sats": 500000, // ~0.005 BTC
    "escrow_release_condition": "signature_upload"
  }
}
```
