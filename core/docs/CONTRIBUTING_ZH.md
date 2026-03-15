# 贡献指南 (Contributing to Proxy Agent Network - PAN)

[**English Version**](CONTRIBUTING.md)

欢迎来到 PAN 核心基础设施存储库。我们积极欢迎来自汽车工程师、DePIN 开发者和硬件安全专家的贡献，共同为自动驾驶汽车 (AV) 时代构建关键的物理恢复层 (Physical Recovery Layer)。

---

## 如何贡献 (The Vanguard Standard)

所有对 PAN M2H (机器对人) 网关的贡献必须符合企业级可靠性标准，因为该代码直接影响高价值车队资产的物理安全以及我们退伍军人 (Veteran) 节点网络的操作安全。

1.  **Fork 项目:** 创建您自己的独立环境。
2.  **创建分支 (Create a Branch):** `git checkout -b feature/UWB_Homing_Optimization`
3.  **提交更改 (Commit Changes):** `git commit -m 'Enhance Ultra-Wideband proximity logic for Sector 1'`
4.  **推送到分支 (Push to Branch):** `git push origin feature/UWB_Homing_Optimization`
5.  **发起 Pull Request:** 请确保您的 PR 描述明确说明了此更改如何影响梅萨市试点项目 (Mesa Pilot) 的 SLA 或 SB 1417 合规性。

---

## 工程标准 (Engineering Standards)

* **语言 (Language):** Python (遵循 PEP 8) 和 Rust (用于 Secure Enclave/TPM 2.0 绑定)。
* **API 规范:** 所有车队网关 (Fleet Gateway) 端点的修改必须记录在 `/docs/v2026.1/` 中。
* **零信任安全 (Zero-Trust Security):** **切勿**提交 API 密钥、L402 Macaroons (支付凭证) 或测试网闪电节点凭证。
* **测试覆盖率:** 所有影响 `/src/L402-Gateway/` 或 `/hardware-node/` 模块的 PR 都需要至少 90% 的测试覆盖率，以模拟自动驾驶汽车诊断故障的提取。

---

## 硬件与合规性贡献 (Hardware & Compliance Contributions)

我们积极欢迎旨在增强我们的物理安全性和法定报告能力的贡献：

### 1. SB 1417 审计增强 (SB 1417 Audit Enhancements)
* **要求 (Requirement):** 必须直接对应亚利桑那州修订法规第 28 篇，第 24 章 (自动驾驶汽车)。
* **重点 (Focus):** 改进“光学健康报告 (Optical Health Reports)”的加密哈希和不可篡改性。

### 2. 光学修复协议 (Optical Reclamation Protocol - ORP)
* **要求 (Requirement):** 提议更改物理清洁程序（例如：新的超细纤维标准或化学溶剂限制）必须引用当前 LiDAR/摄像头 OEM 制造商（例如：Waymo, Luminar, Hesai）的规格说明。
* **审查 (Review):** 物理协议的更改需要获得 PAN Command 的签字批准，以确保它们不会使 $500 万美元的 HNOA/E&O 责任险失效。

---

## 治理与协议升级 (Governance & Protocol Upgrades)

重大协议更改——例如更改动态 L402 激增定价逻辑、修改 15 分钟 SLA 执行参数或扩展运行设计域 (ODD)——需要正式共识。在编写代码之前，请提交一个带有 `[RFC]` (征求意见) 标签的 Issue，以启动与车队合作伙伴 (Fleet Partners) 和 PAN Command 的讨论。

感谢您为扩展 L4 级别自动驾驶构建关键的物理基础设施。