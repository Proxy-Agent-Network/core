# Proxy Agent Network (PAN)
**自动驾驶时代的人力基础设施 (The Human Infrastructure for the Autonomous Era)**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Status: Private Beta](https://img.shields.io/badge/Status-Private%20Beta-orange.svg)](https://www.proxyagent.network/)
[![Network: Mesa, AZ](https://img.shields.io/badge/Sector-Mesa%2C%20AZ-green.svg)]()

[**English Version**](README.md)

> 当自动驾驶汽车遇到无法自行解决的物理障碍时，PAN 会派出一名人类。

---

## 问题 (The Problem)

自动驾驶车队每天都会遇到数以千计软件无法解决的物理边缘情况——道路碎片导致的传感器遮挡、车门故障、生物危害泄漏、急救人员联络以及车辆回收操作。每一个未解决的事件都在耗费车队的时间、资金和乘客的信任。

今天，这些事件只能停滞不前，直到昂贵的车队运营团队派出响应人员——速度缓慢、依赖人工，且难以规模化。

---

## 解决方案 (The Solution)

PAN 是一个**去中心化的物理基础设施网络 (DePIN)**，它将自动驾驶车队与经过验证的先锋代理 (Vanguard Agents) 名册连接起来。这些经过培训和背景调查的现场操作员负责解决物理边缘情况，并获得通过闪电网络 (Lightning Network) 实时结算的赏金。

**车队发出信号。PAN 派出人类。问题在几分钟内解决。**

---

## 工作原理 (How It Works)

```
  自动驾驶车队合作伙伴             PAN 网络                     先锋代理 (Vanguard Agent)
  ─────────────────             ─────────                    ───────────────────────
  检测到故障          ──────────▶ 验证 Ed25519 签名            将任务警报调度给
  发送 V2X 求援信号    (Webhook)   地理空间调度           ────▶  最近的代理
                                将赏金锁定在 HODL 托管中
                                                             代理到达现场
  收到光学健康报告    ◀────────── 封装 SB 1417 审计报告          UWB 微距寻向
  (L402 支付)                    结算 L402 发票        ◀────   捕获证据
                                代理获得 90% 的分成            任务完成
```

---

## 核心特性 (Key Features)

### 🛡️ 零信任安全 (Zero-Trust Security)
每一次交互都经过密码学验证。车队信号需要 Ed25519 签名。代理的硬件通过 Google Play Integrity 证明绑定到 TPM。赏金结算需要三阶段预言机：硬件证明、SB 1417 合规性，以及由 Rust 智能合约验证的、带有自动驾驶汽车 (AV) 签名的 Ed25519 载荷。

### ⚡ 即时闪电网络结算 (Instant Lightning Settlements)
当求援信号到达时，赏金即被锁定在 L402 HODL 托管中。代理在任务完成后的几秒钟内，即可通过比特币闪电网络获得 90% 的已结算赏金。没有银行，没有 ACH 延迟，没有中间商。

### 📍 厘米级精准寻向 (Precision Micro-Homing)
代理使用两阶段接近系统导航至距离抛锚自动驾驶汽车几厘米的范围内：在 50 米处进行 BLE 带外 (OOB) 握手，在 15 米处过渡到 UWB 测距，以毫米级精度定位车辆。在现场无需猜测，没有延迟。

### 📋 内置 SB 1417 合规性 (SB 1417 Compliance Built-In)
每项任务都会自动生成一份密封的、不可篡改的光学健康报告 (Optical Health Report)——经过加密签名并存储，以满足加州/亚利桑那州的自动驾驶汽车事故文件强制要求。合规管道现在包括语音日志记录、生物特征安全事件、RATS 威胁检测日志、个人空气质量读数以及导电危害事件——所有数据均带有时间戳和 GPS 标签，且完全自动追加，无需代理进行任何操作。

### 📈 动态激增定价 (Dynamic Surge Pricing)
当代理利用率超过 75% 时，网络会自动提高赏金，确保关键事件始终有人员响应。赏金锚定于 OSM 颜色分类，最高可达基础费率的 3 倍。

### 🧠 AI 辅助调度 (Proxy-Alpha Companion Mode)
先锋代理可以使用 Proxy-Alpha，这是一个由 Gemini 2.5 Flash 驱动的战术 AI 引擎。Proxy-Alpha 在调度时（在代理开口之前）预加载任务上下文——车辆 VIN、活动故障代码、UDS 库、代理认证和实时遥测数据。代理通过通讯胸针 (Communicator Pin) 的唤醒词 ("Hey Dispatch") 免提激活 Proxy-Alpha，并通过胸针的集成扬声器接收现场指导。所有与合规性相关的交互都会被自动转录并追加到 SB 1417 报告中。安全系统受语义提示注入防火墙保护。

### 🦺 Project Copperfield — Vanguard 现场系统
参与 Vanguard 50 试点项目的 PAN 代理配备了完整的 Project Copperfield 可穿戴平台——四件集成的智能服装，共同使 Vanguard 代理成为任何事故现场中最安全、记录最完善、能力最强的现场操作员。请参阅下文的 [Vanguard 现场系统](#vanguard-现场系统-vanguard-field-system)。

---

## 运行状态矩阵 (OSM Color Taxonomy)

PAN 使用标准化的颜色分类法来进行任务分类、定价和仪表盘可视化。

| 颜色 (Color) | 类别 (Category) | 层级 (Tier) | 基础赏金 |
|---|---|---|---|
| 🔴 RED | 生物危害 / 异物 (Biological / Foreign Object) | 关键 (Critical) | $65.00 |
| 🟣 PURPLE | 车辆回收 (Defleeting) | 关键 (Critical) | $65.00 |
| 🟡 YELLOW | 技术 / 传感器故障 (Tech / Sensor Fault) | 升高 (Elevated) | $45.00 |
| 🟠 ORANGE | 传感器校准 (Calibrations) | 升高 (Elevated) | $45.00 |
| 🟢 GREEN | 断电与重置 (Power Down & Rest) | 标准 (Standard) | $14.00 |
| 🔵 BLUE | 验证 (Validation) | 标准 (Standard) | $14.00 |
| ⬜ WHITE | 演示车辆 (Demo Vehicle) | 标准 (Standard) | $14.00 |

---

## Vanguard 现场系统 (Vanguard Field System)

**Project Copperfield** 是 PAN 专有的智能可穿戴平台——四个组件被设计为一个统一的系统，每个组件均可独立运作，但在协同部署时可发挥最大效能。

```
  ┌─────────────────────────────────────────────────────────────────┐
  │                   VANGUARD 现场系统 (FIELD SYSTEM)               │
  │                                                                 │
  │  🧢 HapHat v2.3          🦺 PANOPLY Vest v1.2                  │
  │  身份认证 · 任务警报       态势感知 · RATS 后方威胁检测           │
  │  接近感知 · 触觉导航       LED 背板 · 脊柱触觉反馈                │
  │  加密 TPM                 SB 1417 自动化日志                     │
  │                                                                 │
  │  👕 Aegis Polo VFP-1 v1.2  🧤 Gauntlets VFG-1 v1.3            │
  │  生物特征监控              手势控制 · 社区文化                     │
  │  语音 AI (Proxy-Alpha)    工具 NFC 识别 · 多代理奖励              │
  │  热管理 · 紧急响应         彩蛋隐藏菜单 · 单手套欢迎奖励           │
  └─────────────────────────────────────────────────────────────────┘
```

### 🧢 HapHat v2.3
一款智能卡车帽，防汗带内装有五个触觉电机，带有全 RGB NeoPixel 帽檐灯带和无源 NFC 身份面板。该帽子通过触觉模式传达任务状态和方向导航，代理无需查看手机。NFC 帽檐轻触可为车队经理、急救人员和自动驾驶汽车面板提供即时的代理身份验证——无需安装应用程序。PCM 冷却衬里可确保在亚利桑那州梅萨市 115°F (约 46°C) 的夏季运行期间保持额头凉爽。

### 🦺 PANOPLY Vest v1.2
一款符合 ANSI/ISEA 107-2020 Class 3 标准的、具有主动智能的高能见度安全背心。后方感知与威胁检测系统 (RATS) 利用分层毫米波 (mmWave) 雷达、广角摄像头和超声波传感器，在代理回头之前，通过触觉脊柱带和 LED 背板警告他们有驶近的车辆。16×24 柔性 LED 背板可在 50 米以上的范围内，向车队经理和急救人员动态显示 OSM 任务状态。五电机触觉脊柱带无需代理转移注意力即可传达导航方向和接近程度。提供三个层级，通过任务里程碑解锁。

### 👕 Aegis Polo VFP-1 v1.2
最内层也是最贴身的组件——直接贴身穿着。Aegis Polo 监控代理的生物特征（心率、SpO₂、皮肤温度、皮肤电反应），读取其个人呼吸区的空气质量，并通过胸前安装的通讯胸针 (Communicator Pin) 倾听他们的声音。当背心的 RATS 系统检测到 Zone 2 威胁，而 Polo 衫的生物特征传感器同时检测到压力峰值时，系统会意识到代理已经知晓威胁——并直接升级至 Zone 1 最高响应级别，跳过冗余的警告。代理自身的生理机能成为了威胁升级算法的输入。D3O 肋骨冲击面板可防止车辆侧面擦撞。生物发光衣领条纹可确保即使所有电子设备发生故障，在夜间也能提供被动可见性。在 Tier 3 (完成 200 项任务) 解锁。

### 🧤 Gauntlets VFG-1 v1.3
防割 HPPE 现场工作手套，内置 IMU、NFC、触觉电机和手背 PCM 冷却模块。只需一个弹指手势 (Snap) 即可免提切换帽檐灯，让代理的双手始终专注于工作。多代理奖励 (Multi-agent bonuses) 鼓励在同一事件中经过验证的代理之间的物理互动。**率先戴着手套赶到现场？** 您在向未佩戴手套的代理致意时，仍可获得 $2 的单手套欢迎奖励 (Solo Glove Welcome)。当双方均佩戴手套时，基础问候（握手、碰拳）可各获 $5，而进阶华丽动作（秘密握手、BOOM 爆炸）可各获 $7。手势系统包含数量未公开的隐藏彩蛋，通过自然使用来发现。**以成本价发售——PAN 不赚取利润。** 始终提供单只手套购买选项。解锁条件：完成 10 项任务。

### 复合威胁响应 (Composite Threat Response)
Polo 衫和背心的结合实现了一种任何单一组件都无法提供的功能。当背心的 RATS 雷达在 Zone 2 范围内对驶近的车辆进行分类，而 Polo 衫的生物特征贴片同时检测到代理的压力反应飙升时——系统知道代理已经感知到了威胁。Zone 2 警告序列变得多余。系统直接跳至跨所有通道同步发出的 Zone 1 最高响应：帽子、脊柱带、LED 背板、手套和手机警报。代理自身的生理机能成为威胁升级算法的直接输入。

---

## 车队合作伙伴集成 (Fleet Partner Integration)

将您的自动驾驶车队与 PAN 集成只需几分钟。发送带有签名的求援信号，其余的交给我们。

### 1. 申请车队接入

请通过 [rob@proxyagent.network](mailto:rob@proxyagent.network) 联系我们注册您的车队，并获取您的 Ed25519 密钥对和车队凭证。

### 2. 发送求援信号 (Distress Signal)

```bash
POST https://api.proxyagent.network/api/v1/v2x/distress
X-Fleet-Id: WAYMO_MESA_01
X-Fleet-Signature: <ed25519_hex_signature>
Content-Type: application/json

{
  "vin": "WAYMO-404",
  "fault_code": "UDS_SENSOR_OCCLUSION_LIDAR_FL",
  "latitude": 33.420,
  "longitude": -111.840,
  "bounty_usd": 45.00,
  "osm_color": "YELLOW"
}
```

### 3. 接收确认

```json
{
  "status": "success",
  "task_id": "tsk_a3f8c291b04d"
}
```

PAN 会自动处理代理调度、SLA 监控、合规报告和闪电网络结算。您的车队运营团队可以通过 Ops Hub 仪表盘实时查看所有活动任务。

### 签名要求

所有车队 Webhook 请求都必须使用您注册的 Ed25519 私钥进行签名。签名是针对原始请求体计算的。超过 300 秒的请求将被拒绝，以防止重放攻击。

```python
import nacl.signing

signing_key = nacl.signing.SigningKey(your_private_key_bytes)
signature = signing_key.sign(request_body_bytes).signature.hex()
```

---

## 先锋代理计划 (Vanguard Agent Program)

PAN 正在积极招募其创始成员 Vanguard 50——梅萨市 (Mesa, AZ) 扇区的首批现场操作员。

### 我们在寻找谁
- 退伍军人、急救人员和熟练的技术工人
- 拥有有效的驾驶执照和可靠的车辆
- 智能手机 (Android 8.0+ 或 iOS 16+)
- 通过背景调查 (经 Checkr 验证)
- 居住在亚利桑那州梅萨市或附近 (欢迎 Gilbert、Chandler、Tempe 扇区的人员)

### 您能赚取什么
- **Tier 1 任务** (固定车门、验证): 基础费率 $14.00
- **Tier 2 任务** (传感器故障、校准): 基础费率 $45.00
- **Tier 3 任务** (生物危害清理、车辆回收): 基础费率 $65.00
- **激增乘数 (Surge multiplier)**: 在高需求时段最高可达 3 倍
- **即时闪电网络支付**: 任务完成后的几秒钟内资金即存入您的钱包
- **协作奖励 (Collaboration bonuses)**: 向未配备手套的代理致意可赚取 $2，在共享事件中进行经过验证的双边手势互动，每人最高可赚取 $7

### 层级晋升 (Tier Progression)
先锋代理在完成任务时解锁扩展功能和设备：

| 里程碑 | 解锁内容 |
|---|---|
| 10 项任务 | Gauntlets VFG-1 手套 (以成本价购买) |
| 50 项任务 | Tier 2 认证 · PANOPLY Vest Tier 2 功能 |
| 100 项任务 | 💯 里程碑奖励 |
| 200 项任务 | Tier 3 认证 · Aegis Polo VFP-1 · PANOPLY Vest Tier 3 功能 |

### 申请加入
[申请加入网络 →](https://www.proxyagent.network/)

---

## SDK 与开发者工具 (SDK & Developer Tools)

用于车队集成的官方客户端库：

| 语言 | 包名 | 安装命令 |
|---|---|---|
| **Python** | \`proxy-agent\` | \`pip install proxy-agent\` |
| **Node.js** | \`@proxy-protocol/node\` | \`npm install @proxy-protocol/node\` |

完整的 API 参考和集成指南可在 [\`/docs\`](docs/) 目录中找到。

---

## 合规与法律 (Compliance & Legal)

PAN 从底层架构开始即为满足监管合规而设计。

- **SB 1417 (加州/亚利桑那州):** 每次任务都会生成一份密封的光学健康报告，其中包含带时间戳的照片证据、硬件证明令牌，以及不可篡改的加密哈希存储。合规管道现在包括语音转录（通过通讯胸针）、RATS 威胁事件日志、生物特征安全事件、双重空气质量读数（环境 + 个人呼吸区）以及导电危害事件——所有数据均自动追加。
- **CPUC 自动驾驶事故报告:** 合规导出 API 汇总报告并为州监管机构签名。
- **零知识代理隐私:** 先锋代理的个人数据使用 AES-256 加密存储。车队合作伙伴只能看到任务结果，永远看不到代理的真实身份。Companion Mode 的完整语音转录永远不会与车队合作伙伴共享——仅共享标记为合规的摘录。
- **IDOR 保护:** 所有任务分配均有密码学绑定——代理只能完成分配给他们的任务。
- **设备端隐私过滤:** 所有照片和视频证据在离开代理手机之前，都会通过设备端 ML 脱敏管道 (`PrivacyFilter`) 进行处理。人脸和车牌在本地进行遮挡——原始 PII 永远不会接触网络。
- **NARCAN 认证代理:** 持有医疗响应认证的代理可以在 Aegis Polo 密封的紧急口袋中携带 Narcan（纳洛酮）急救用品。所有“好撒玛利亚人” (Good Samaritan) 施救行为均会通过 Companion Mode 自动记录语音转录、GPS 和时间戳。*(在 Vanguard 50 部署前等待亚利桑那州《好撒玛利亚人法》的最终法定审查)*。

详见 [COMPLIANCE.md](legal/COMPLIANCE.md)。

---

## 架构概览 (Architecture Overview)

面向技术合作伙伴和贡献者，核心技术栈如下：

| 组件 | 技术 |
|---|---|
| API 网关 | FastAPI + Redis |
| 调度引擎 | 地理空间 GEORADIUS + FIFO 队列 |
| 激增定价 | 基于 AUR 的指数重定价守护进程 |
| SLA 执行 | 两阶段 ACK 看门狗 (15秒超时) |
| 资金托管 | Rust 智能合约 (通过 PyO3 FFI) |
| 支付结算 | LND gRPC — 比特币主网闪电网络 |
| 移动端 | Kotlin Multiplatform (Android + iOS) |
| 硬件安全 | Android StrongBox TPM + Play Integrity |
| 接近传感 | BLE OOB (50米) → UWB 测距 (15米) |
| AI 引擎 | Gemini 2.5 Flash + Cognitive Vault |
| 背景调查 | Checkr API — driver_pro 检查包 |
| 可穿戴设备 | BLE 5.0 mesh · nRF52840 · ESP32-C3 |
| 威胁检测 | TI IWR6843AOP mmWave 雷达 + Edge ML (Coral TPU) |
| 触觉反馈 | 5电机 ERM 阵列 (帽子) · 5电机脊柱带 (背心) · 腕部电机 (手套 + Polo衫) |
| 生物特征 | MAX86150 PPG/ECG · BME688 空气质量 · VEML6075 紫外线 |
| NFC 通信 | PN532 无源帽檐标签 · PN532 有源/无源 (手套) · 背心背板标签 |
| PCM 热管理 | 共享的十水硫酸钠系统 · 45分钟冷冻循环 · 适用于所有四件服装 |

完整的架构文档可在 [\`/architecture\`](architecture/) 目录中获取。

---

## 参与贡献 (Contributing)

我们正在搭建数字智能与物理现实之间的桥梁。我们正在寻找有使命感的工程师，共同定义 2030 年的行业标准。

**开放职位 (远程 / 异步):**
- **Rust 协议工程师** — 将结算层迁移至高频闪电网络交互
- **法律工程负责人** — 为自主实体制作授权委托书模板
- **开发者关系** — 构建供 10,000 名 AI 开发者使用的 "Hello World" 教程
- **iOS 工程师** — 完成 KMP iOS 客户端及 UWB 测距实现
- **固件工程师** — `AndroidBleHapHatService` 真实实现 · ESP32 GATT 服务器 · OTA 升级管道
- **硬件工程师** — PANOPLY 背心 PCBA · Aegis Polo 传感器集成 · Gauntlets 柔性 PCB

申请方式：使用您的 GitHub 账号对一条消息进行密码学签名，并发送至 [rob@proxyagent.network](mailto:rob@proxyagent.network)。

开发指南请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 项目状态 (Status)

🚧 **内测阶段 (Private Beta)** — 亚利桑那州梅萨市扇区 1 (Mesa, AZ Sector 1) | Vanguard 50 试点 | 上线时间: 2026 年阵亡将士纪念日

| 系统 | 状态 |
|---|---|
| PAN API + 调度引擎 | ✅ 运行中 (Operational) |
| Android PAN Tactical 应用 | ✅ 试点就绪 (Pilot-ready) |
| 闪电网络结算 | ✅ 主网运行 (Mainnet) |
| SB 1417 合规管道 | ✅ 已完成 (Complete) |
| Checkr 背景调查验证 | 🔧 集成中 (Integration in progress) |
| HapHat v2.3 | 🔧 Mock → 真实 BLE 实现转换中 |
| PANOPLY Vest v1.2 | 📐 规格已完成 · 待生产原型 |
| Aegis Polo VFP-1 v1.2 | 📐 规格已完成 · 待生产原型 |
| Gauntlets VFG-1 v1.3 | 📐 规格已完成 · 待生产原型 |
| OSRM 战术路线 | 🔧 Phase 6 接线中 |
| iOS 客户端 | 📋 计划中 (Planned) |

[申请抢先体验 →](https://www.proxyagent.network/)

---

## 许可证 (License)

MIT — 详见 [LICENSE](LICENSE) 文件。

---

*自动驾驶时代的人力基础设施。与退伍军人共建，为未来而生。*