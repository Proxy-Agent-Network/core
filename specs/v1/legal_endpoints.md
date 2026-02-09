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

### Success Response (200 OK)
Returns the Job ID and Escrow status.
```json
{
  "id": "job_lg_9948214",
  "status": "matching",
  "estimated_wait": "14 minutes",
  "compliance_check": "passed",
  "message": "Request broadcast to 12 verified attorneys in Delaware. Funds locked in escrow."
}
```

### Webhook Event (Async Completion)
Sent to Agent when the human finishes the task.
```json
{
  "type": "job.completed",
  "job_id": "job_lg_9948214",
  "result": {
    "status": "signed",
    "human_notes": "Clause 4.2 was ambiguous; I added a standard rider as requested. Document signed.",
    "signed_document_url": "[https://proxy-secure.com/doc/signed_883.pdf](https://proxy-secure.com/doc/signed_883.pdf)",
    "transaction_hash": "tx_btc_88392..."
  }
}
'''
