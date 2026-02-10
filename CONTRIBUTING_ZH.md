# 贡献指南 (Contributing to Proxy Protocol)

[**English Version**](CONTRIBUTING.md)

我们欢迎来自社区的贡献，无论您是 AI 研究员、法律工程师还是密码学家。感谢您构建连接 AI 与物理世界的桥梁。

---

## 如何贡献 (How to Contribute)

1.  **Fork 项目:** 创建您自己的存储库副本。
2.  **创建分支 (Create a Branch):** `git checkout -b feature/AmazingFeature`
3.  **提交更改 (Commit Changes):** `git commit -m 'Add some AmazingFeature'`
4.  **推送到分支 (Push to Branch):** `git push origin feature/AmazingFeature`
5.  **发起 Pull Request**

---

## 法律工程贡献 (Legal Engineering)

我们积极欢迎新的司法管辖区模板（例如：欧盟/GDPR、阿联酋/迪拜 DIFC、日本）的贡献。

### 新模板要求
* **引用 (Citation):** 必须引用具体的管辖法案（例如：日本民法典第 99 条）。
* **语言 (Language):** 必须提供英文（或英文/本地双语）。
* **格式 (Format):** 必须遵循现有模板的 Markdown 结构（前言 -> 授权 -> 赔偿）。
* **审查 (Review):** 法律模板在合并前需要具有法律工程经验的核心维护者批准。

---

## 代码标准 (Coding Standards)

* **Python:** 遵循 PEP 8 风格指南。
* **API 规范:** 所有端点更改必须反映在 `specs/v1/` 中。
* **安全性:** **切勿**提交 API 密钥或私钥。

---

## 治理 (Governance)

重大协议更改（例如：更改费用结构或托管逻辑）需要在实施前开启 **征求意见 (RFC)**。请提交一个带有 `RFC` 标签的 Issue 以开始社区讨论。
