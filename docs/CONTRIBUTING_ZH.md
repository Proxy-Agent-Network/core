# 贡献指南 (Contributing to Proxy Agent Network - PAN)

[**English Version**](CONTRIBUTING.md)

欢迎来到 PAN 核心基础设施存储库。我们积极欢迎来自汽车工程师、DePIN 开发者、移动端工程师、固件工程师和硬件安全专家的贡献，共同为自动驾驶汽车 (AV) 时代构建关键的物理恢复层 (Physical Recovery Layer)。

本项目代码直接影响在公路旁自动驾驶汽车旁边工作的 Vanguard Agent 的人身安全，我们对所有贡献均执行企业级可靠性标准。

---

## 开始之前 (Getting Started)

在编写任何代码之前，请完整阅读 **[DEVELOPER.md](DEVELOPER.md)**。该文档包含完整的环境配置、所有必需的密钥、Firebase RTDB 规则要求、Key Ceremony 流程以及硬件集成架构。其中有若干非显而易见的配置要求，若忽略将耗费大量调试时间。

---

## 如何贡献 (The Vanguard Standard)

1. **Fork 项目:** 创建您自己的独立环境。
2. **创建分支 (Create a Branch):** `git checkout -b feature/uwb-homing-optimization`
3. **提交更改 (Commit Changes):** `git commit -m 'Enhance Ultra-Wideband proximity logic for Sector 1'`
4. **推送到分支 (Push to Branch):** `git push origin feature/uwb-homing-optimization`
5. **发起 Pull Request:** 您的 PR 描述必须明确说明：
   - 涉及哪个组件或模块
   - 此更改如何影响梅萨市试点项目 (Mesa Pilot) 的 SLA、SB 1417 合规性或 Agent 人身安全
   - 是否需要同步进行硬件侧的更改
   - 已添加或修改的测试覆盖范围

---

## 工程标准 (Engineering Standards)

### 语言与框架 (Languages & Frameworks)

| 层级 | 语言 / 框架 | 说明 |
| :--- | :--- | :--- |
| 后端 API | Python 3.10+（遵循 PEP 8）| FastAPI + Redis。详见 `apps/backend/`。|
| 移动端 | Kotlin Multiplatform (KMP) | Android 为主要目标平台。iOS KMP 开发中。|
| 智能合约 / 托管 | Rust（通过 PyO3 FFI）| 使用 Maturin 构建。运行 `maturin develop` 前须激活虚拟环境。|
| 固件 | C / nRF Connect SDK | nRF52840（四个 Copperfield 组件均使用）。BLE GATT 服务器。Nordic DFU OTA 升级。|
| 嵌入式控制器 | Arduino / ESP-IDF | ESP32-C3（HapHat 主控制器——电机 PWM、LED 灯带）。|

### API 文档

所有车队网关 (Fleet Gateway) 端点的修改必须记录在 `/docs/v2026.2/` 中。`/docs/v2026.1/` 目录已归档，请勿在其中添加新文档。

### 安全标准 (Security Standards)

- **禁止提交**以下内容：`local.properties`、`google-services.json`、`GoogleService-Info.plist`，或任何包含 API 密钥、L402 Macaroon 或闪电节点凭证的文件。
- **禁止提交** `COGNITIVE_ENCRYPTION_KEY`——此密钥在每次部署中必须保持静态，更换后将导致所有已存储的 Agent 记忆失效。
- **GCP 凭证：** `gcloud auth application-default login`（应用默认凭证 ADC）**仅用于本地开发**。生产环境必须使用具有最低权限的专用 JSON 服务账号密钥，不得在生产容器中使用 ADC。
- **Firebase RTDB 规则必须保持 `deny-all`。** 任何应用程序代码均不得直接写入 RTDB。所有 Agent 状态必须通过 Python 后端写入 Redis。直接向 RTDB 写入 Agent 状态的 PR 将被拒绝。
- **固件包**在分发前必须使用 PAN 私钥签名。设备固件会在应用更新前验证签名，未签名的固件包将被拒绝。

### 测试覆盖率 (Test Coverage)

影响以下模块的 PR 需要至少 90% 的测试覆盖率：

- `/src/L402-Gateway/` — 闪电托管与支付结算
- `/src/escrow_oracle.py` — 三阶段零信任结算（硬件 + SB1417 + Ed25519）
- `PrivacyFilter.kt` — SB 1417 照片脱敏管道（人脸 + 车牌）。故障安全路径必须始终返回全黑位图，绝不返回未脱敏的原始图像。
- `BleHapHatService` 的任何实现——替代当前 mock 的真实 BLE 实现
- `validate_multi_agent_bonus()` — 手势奖励反作弊机制（Redis 原子 NX、事件锁、轮班冷却）
- 任何向 SB 1417 光学健康报告追加数据的模块

影响硬件固件的 PR 无最低覆盖率要求，但必须附上测试计划，说明在实体硬件上验证了哪些物理场景。

---

## 开放职位——高优先级 (Open Roles — High Priority)

以下是 2026 年阵亡将士纪念日试点前最迫切需要贡献的方向。如您有意承担其中某项，请在开始前提交 Issue 进行认领。

| 职位 | 所需工作 | 相关文件 / 位置 |
| :--- | :--- | :--- |
| **Android BLE 工程师** | `AndroidBleHapHatService`——替代当前 mock 的真实 BLE 实现。接口定义于 `BleHapHatService.kt`。**此为试点阻断项 (Pilot Blocker)**。| `apps/mobile/src/ble/BleHapHatService.kt` |
| **固件工程师 (nRF52840)** | 为 Gauntlets VFG-1 开发 TFLite Micro 手指弹指手势分类器。三因素检测架构（加速度峰值 + 持续时间 + 掌心摩擦特征）定义于 Gauntlets VFG-1 规格文档 5.4 节。分类器必须使用真实负样本训练（工具坠落、车门撞击、驾驶振动），不得使用合成数据。| Gauntlets 固件仓库 |
| **固件工程师 (Gazell P2P)** | 使用 nRF52840 Gazell 协议实现手套间直接无线链路，用于多 Agent 手势编舞同步。通过 PAN Command 的 BLE 扇出无法保证手势奖励系统所需的亚 100ms 同步精度。更正后的架构详见 Gauntlets VFG-1 规格文档 15.2 节。| Gauntlets 固件仓库 |
| **后端工程师** | 在 `onboarding_api.py` 中集成 Checkr 背景调查验证。API 设计已完成，`CHECKR_API_KEY` 和 `CHECKR_WEBHOOK_SECRET` 环境变量已定义。**此为试点阻断项**。| `apps/backend/src/onboarding_api.py` |
| **移动端工程师** | 在 `AgentDashboardScreen` 中完成 Phase 6 OSRM 战术路线接线。`PanApiClient` 中已存在 `getTacticalRoute()`，含 TODO 注释，需将路线数据接入仪表盘导航 UI。| `apps/mobile/src/screens/AgentDashboardScreen.kt` |
| **iOS 工程师** | 完成 KMP iOS 客户端及 UWB 测距实现。| `apps/mobile/iosApp/` |
| **硬件工程师** | PANOPLY Vest v1.2 电子仓热设计。电子仓必须使用铝质或导热复合材料外壳——密封聚合物材料在亚利桑那州野外环境中不可接受。完整要求见 Vest 规格文档 4.3 节，原型签审需提供 40°C 环境温度下的热仿真结果。| 硬件设计文件 |
| **法律工程负责人** | 为自主实体制作授权委托书模板；Narcan 急救口袋的法律审查（AZ Good Samaritan 法令、HNOA 保险对医疗响应行为的覆盖范围）。| |
| **Rust 协议工程师** | 将结算层迁移至高频闪电网络交互。| `apps/backend/src/core/economics/` |
| **开发者关系** | 构建车队集成的"Hello World"教程。大多数车队合作伙伴的第一次接触将是求援信号 webhook——目标是 15 分钟内完成集成。| `/docs/` |

申请方式：使用您的 GitHub 账号对一条消息进行密码学签名，并发送至 [rob@proxyagent.network](mailto:rob@proxyagent.network)。

---

## 已知技术债务——适合新手的 Issue (Known Tech Debt — Good First Issues)

以下是范围明确、无需深入系统知识的待办事项：

| 事项 | 文件 | 描述 |
| :--- | :--- | :--- |
| `@file:Suppress` 清理 | `PanWalletClient.kt`、`PanApiClient.kt` | `visibility(PUBLIC)` 修复后 Gradle 同步遗留的 `INVISIBLE_REFERENCE` / `INVISIBLE_MEMBER` 警告，待处理。|
| Callsign 后端持久化 | `WalletAndProfileScreen.kt` | `firstName` 和 `callsign` 当前仅为 `rememberSaveable`，未持久化到后端。需在变更时写入 Agent 档案端点。|
| `net_payout` 字段验证 | `PanApiClient.kt`、`v2x_bounty_api.py` | 确认后端从 Redis 计算 `net_payout`，而非由客户端提交计算值给结算预言机。|
| imgbb → S3 迁移 | 所有证据上传调用 | imgbb 仅批准用于 Vanguard 50 试点。在车队合作伙伴签约前必须迁移至 AWS S3 或 GCP Cloud Storage。|
| `ANDROID_PACKAGE_NAME` 环境变量检查 | `onboarding_api.py` | 在 Play Integrity 检查运行前，添加生产环境启动断言，确保 `ANDROID_PACKAGE_NAME` 已设置。|
| `HARDWARE_REGISTRY_URL` 环境变量检查 | `logistics_webhook_api.py` | 在注册表接线前添加启动断言。|
| RFC 8037 测试向量移除 | `escrow_oracle.py` | 模拟块包含 RFC 8037 测试向量，绝不能进入生产环境。需添加等同于 `BuildConfig.DEBUG` 的守卫，或直接移除。|

---

## 治理与协议升级 (Governance & Protocol Upgrades)

重大协议变更在实施前需要正式共识。在编写代码前，请提交一个带有 `[RFC]`（征求意见）标签的 Issue，以下任一情形均须如此：

- 更改动态 L402 激增定价逻辑或 AUR 阈值
- 修改 15 分钟 SLA 执行参数
- 将运行设计域 (ODD) 扩展至 Sector 1（亚利桑那州梅萨市）以外
- 更改任何 Copperfield 组件的 BLE GATT 命令协议或服务 UUID
- 更改多 Agent 手势奖励系统（金额、反作弊规则、轮班冷却）
- 更改 SB 1417 光学健康报告的数据结构
- 更改复合威胁响应算法（RATS + 生物特征升级逻辑）
- 影响手势同步路径的硬件架构更改（Gazell 对等链路）

影响车队合作伙伴集成的 RFC 在合并前需经历 14 天的意见征集期，且必须在实施前与车队合作伙伴及 PAN Command 协商。

---

## 硬件与合规性贡献 (Hardware & Compliance Contributions)

### 1. SB 1417 审计增强 (SB 1417 Audit Enhancements)

- **要求：** 必须直接对应亚利桑那州修订法规第 28 篇，第 24 章（自动驾驶汽车）。最终规则于 2026 年 12 月 31 日生效——请持续关注法规更新。
- **重点方向：** 光学健康报告的加密哈希与不可篡改性；自动化数据管道扩展；设备端脱敏（`PrivacyFilter`）准确性提升。
- **隐私规则：** 任何导致原始 PII（未脱敏的人脸或车牌）离开 Agent 设备的更改，无论其他方面优劣，均将被无条件拒绝。
- **数据结构变更：** 对 SB 1417 报告数据结构的任何修改，均需提交 `[RFC]` Issue 并经法律审查后方可实施。

### 2. 光学修复协议 (Optical Reclamation Protocol - ORP)

- **要求：** 提议更改物理清洁程序（如新的超细纤维标准或化学溶剂限制）必须引用当前 LiDAR/摄像头 OEM 制造商（如 Waymo、Luminar、Hesai）的规格说明。
- **审查：** 物理协议的更改需要获得 PAN Command 的签字批准，以确保不会使 500 万美元的 HNOA/E&O 责任险失效。

### 3. Project Copperfield — Vanguard Field System

对 Project Copperfield 可穿戴平台（HapHat v2.3、PANOPLY Vest v1.2、Aegis Polo VFP-1、Gauntlets VFG-1）的贡献须遵守以下附加要求：

- **规格文档具有权威性。** 硬件行为必须与已发布的规格文档一致。如有偏差，必须先（或同步）通过 PR 更新规格文档，再进行固件更改。
- **必须保留触觉划分协议。** 帽子、背心脊柱、手套和 Polo 衫手腕电机各自拥有特定的触觉通道。导致两个组件在 Zone 1 紧急情况之外同时传递相同信息的 PR，违反划分协议，将被拒绝。
- **手势彩蛋——Tier C 仅存于固件。** Tier C 秘密是刻意不记录在案的。禁止在任何文档、代码注释或日志条目中透露 Tier C 内容。三 Agent 秘密及其他 Tier C 彩蛋应仅存在于固件和后端中，不得有任何 Agent 可访问的人类可读描述。
- **OTA 固件包在分发前必须使用 PAN 私钥签名。** nRF52840 和 ESP32-C3 固件均会在应用更新前验证包签名。
- **电子仓热设计：** 任何修改 PANOPLY Vest 电子仓外壳的硬件 PR，必须附上热仿真结果，证明在 40°C 环境温度、持续 5W 平均负载下，外壳温度不超过 60°C。密封聚合物外壳不予受理。
- **集成端口触点：** 任何修改 Polo 衫或背心集成端口的硬件 PR，必须指定镀金触点（最低 30µin，覆盖在镍阻挡层上）。普通弹簧针触点在领口汗液暴露环境中会迅速腐蚀。

### 4. Agent 安全——不可妥协 (Agent Safety — Non-Negotiable)

任何影响安全关键代码路径的贡献——包括 RATS 威胁检测、Zone 1 紧急响应、求救按钮、撞击检测、导电危害告警、复合威胁升级或 `PrivacyFilter` 故障安全路径——均需至少两名 PAN 核心团队成员审查方可合并，无论测试覆盖率如何。Agent 安全不是个人判断的场合。

---

感谢您为扩展 L4 级别自动驾驶构建关键的物理基础设施。在梅萨市公路旁工作的 Vanguard Agent 依赖这份代码的正确性。
