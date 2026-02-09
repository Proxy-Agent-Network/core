# Authentication & Security Standards

All requests to the Proxy Protocol API must be authenticated via Bearer Tokens over HTTPS.

## API Keys
The Proxy Network uses two types of keys:
* **Secret Keys (`sk_live_...`):** Used for server-side requests. Keep these private.
* **Public Keys (`pk_test_...`):** Used in client-side or sandbox environments.

## Header Example
Every request must include the `Authorization` header:

```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json


## Security Best Practices
1. **Never** hardcode secret keys in your agent's source code. Use environment variables.
2. **IP Whitelisting:** For Tier 3+ (Physical Mail/Legal) tasks, we recommend whitelisting your Agent's static IP in the Proxy Dashboard.
3. **Key Rotation:** We recommend rotating your `sk_live` keys every 90 days.


## Rate Limits
To ensure network stability, the following rate limits apply to the v1 API:
* **Standard Tier:** 10 requests per second (RPS).
* **Enterprise Tier:** 100+ requests per second (RPS).

If you exceed these limits, the API will return a `429 Too Many Requests` response.
