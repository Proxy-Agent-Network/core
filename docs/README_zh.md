# Proxy Agent Network (PAN) | 核心基础设施 (Core Infrastructure)

![Sector Status](https://img.shields.io/badge/Sector-Mesa_AZ_01-blue)
![Compliance](https://img.shields.io/badge/Compliance-SB_1417-success)
![Protocol](https://img.shields.io/badge/Protocol-L402-orange)

## 自动驾驶时代的人力基础设施 (The Human Infrastructure for the Autonomous Era)
PAN 是一个去中心化的物理基础设施网络 (DePIN)，为自动驾驶汽车 (AV) 车队提供关键的“最后一英里”物理层支持。我们利用经过硬件认证的退伍军人 (Veteran) 节点网络，解决导致自动驾驶资产停运的物理边缘情况（如传感器遮挡、车辆回收和物理维护）。

[**English README**](README.md)

### 🛠 技术栈 (Tech Stack)
* **结算引擎 (Settlement Engine):** 采用 L402 (闪电网络) 实现机器对人 (M2H) 的即时微支付。
* **身份与信任 (Identity & Trust):** 通过 TPM 2.0 (Android StrongBox) 和 Apple Secure Enclave 实现基于硬件支持的零信任身份认证。
* **合规性 (Compliance):** 自动化生成符合 **亚利桑那州 SB 1417** (第 28-9701 节) 传感器诊断审计要求的加密日志。

### 🛰 运行设计域 (ODD)
* **主要扇区:** 亚利桑那州梅萨市 (Mesa, AZ) - 扇区 1
* **锚点:** Waymo/Magna 集成工厂 (85212)
* **响应 SLA (服务等级协议):** < 12 分钟

## 🏗 仓库结构 (Repository Structure)
* `/docs/SB-1417/`: 法定合规框架和审计日志模式 (Audit log schemas)。
* `/src/L402-Gateway/`: 用于处理自动驾驶车辆触发赏金的结算逻辑。
* `/protocols/ORP/`: 光学修复协议 (HP Potion) 标准操作程序。

## 🎖 50人先锋队 (The Vanguard 50)
我们目前正在为梅萨市 (Mesa) 试点项目招募 50 名退伍军人代理。
* **上线时间:** 2026 年阵亡将士纪念日周末 (Memorial Day Weekend 2026)。
* **注册:** [proxyagent.network/enlist](https://www.proxyagent.network/enlist)

---

## 协议集成 (Protocol Integration)

### 1. 车辆请求物理干预 (AV Requests Physical Intervention)
当车辆的车载 AI（如 Waymo 或 Zoox 的诊断系统）检测到无法自行清除的物理故障（如激光雷达被泥土遮挡）时，它会通过 API 呼叫附近的 PAN 代理。

\```json
POST [https://api.proxyagent.network/v1/fleet/dispatch](https://api.proxyagent.network/v1/fleet/dispatch)
Content-Type: application/json

{
  "vehicle_id": "WAYMO_MESA_78",
  "fault_code": "LIDAR_OCCLUSION_FRONT",
  "location": {"lat": 33.3214, "lng": -111.6608},
  "l402_bounty": 15000,
  "priority": "HIGH"
}
\```

---
**机密 // 专有基础设施 (CONFIDENTIAL // PROPRIETARY INFRASTRUCTURE)**
*© 2026 ProxyAgent.Network 保留所有权利。*