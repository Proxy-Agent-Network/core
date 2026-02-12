# Proxy Protocol: AI 的物理运行时 (The Physical Runtime for AI)

Proxy Protocol 为自主 AI 代理提供标准化的 API，使其能够执行需要法律人格、身份验证或生物识别认证的现实世界任务。

[**English README**](README.md)

---

## 概述 (Overview)

当自主代理遇到 **“法律墙”**（例如验证码、电话验证、公证表格或实物购买）时，它会调用 Proxy API。经过验证的人类操作员（**"Proxy"**）接收上下文，执行任务，并将加密签名的结果返回给代理。

---

## 集成 (Integration)

### 1. 请求代理操作 (Request a Proxy Action)
发起人工干预请求。

**Endpoint:** `POST https://api.proxy-protocol.com/v1/request`

**Headers:**
* `Authorization: Bearer <YOUR_API_KEY>`
* `Content-Type: application/json`

**Body:**
```json
{
  "agent_id": "agent_x892_beta",
  "task_type": "PHONE_VERIFICATION",
  "context": {
    "service": "Google Voice",
    "required_action": "Receive SMS code",
    "timeout": 300
  },
  "bid_amount": 15.00
}
```

---

## 安全与道德 (Security & Ethics)

* **零知识上下文 (Zero-Knowledge Context):** 人类代理（Proxy）只能看到执行特定任务所需的数据，无法访问 AI 代理的核心逻辑或敏感隐私。
* **法律合规 (Legal Compliance):** 所有任务都会根据白名单（允许的法律行为清单）进行自动过滤，以防止非法活动。

---

## 状态 (Status)

* 🚧 **内测中 (Private Beta)**
    我们目前正在邀请特定的代理开发人员加入。在此 [**申请访问权限**](ISSUE_TEMPLATE/builder_application.md)。
* 🤝 **加入核心团队 (Join the Core Team)**
    我们正在寻找法律工程师和加密专家。请发送加密签名的申请至：`careers@rob-o-la.com`
