# Proxy Protocol: AI 的物理运行时 (The Physical Runtime for AI)

Proxy Protocol 为自主 AI 代理提供标准化的 API，使其能够执行需要法律人格、身份验证或生物识别认证的现实世界任务。我们通过全球硬件认证的人类节点网络，架起硅基意图与生物代理之间的桥梁。

[**English README**](README.md)

---

## 概述 (Overview)
当自主代理遇到 **“法律墙”**（例如验证码、电话验证、公证表格或实物购买）时，它会调用 Proxy API。经过验证的人类操作员（**"Proxy"**）接收上下文，执行任务，并将加密签名的结果返回给代理。

---

## 核心特性 (Key Features)
* 🛡️ **硬件信任根:** 所有 Tier 2+ 人类节点必须使用封装在 **Infineon OPTIGA™ TPM 2.0** 中的不可导出私钥对证明进行签名。
* ⚡ **无信任结算:** 支付使用 Lightning HODL 发票。仅在硬件遥测数据经过加密验证后（PIP-017）才释放资金。
* ⚖️ **去中心化正义:** 争议由 VRF 随机选出的陪审团解决。陪审团通过比特币区块熵选择，并由谢林点（Schelling Point）博弈论激励。
* 🏥 **节点保险:** 0.1% 的协议税用于资助国库，以补偿操作员因验证的系统错误或关键漏洞造成的损失。

---

## 基础设施可视化工具 (Infrastructure Visualizers)
核心协议包括用于监控网络健康的实时仪表板：
* **托管电路 (Escrow Circuit):** 监控 HODL 发票结算和 HTLC 逻辑。
* **法定人数审计 (Quorum Audit):** 观察 7 签名多签仪式的最终确定。
* **取证增量 (Forensic Delta):** 审计节点之间的加密清单不匹配。
* **法律纽带 (Legal Nexus):** 探索硬件认证的司法管辖区先例。

---

## 集成 (Integration)

### 1. 请求代理操作 (Request a Proxy Action)
```json
POST [https://api.proxyagent.network/v1/request](https://api.proxyagent.network/v1/request)
Authorization: Bearer <YOUR_API_KEY>
Content-Type: application/json

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
* **零知识上下文:** Proxy 仅查看特定的任务数据，而不查看代理的核心逻辑。
* **法律合规:** 所有任务均根据受限的许可操作列表进行过滤。详见 [COMPLIANCE.md](./COMPLIANCE.md)。

---

## 状态 (Status)
🚧 **内测中 (Private Beta).** 目前正在邀请部分代理开发者。 [点击此处申请访问权限](https://www.proxyagent.network/)。
