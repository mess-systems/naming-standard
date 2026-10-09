[English](README.md) | [Русский](README.ru.md) | **简体中文**

> **译文说明。** 本文为标准 v2 版本的译文，源提交 `ca24160`（含链接编辑修订）。英文文本为规范性文本：如有任何不一致，以英文版本为准。

# mess.systems 命名标准

**mess.systems** 的命名标准：为 DNS 名称、主机、代码仓库、镜像、存储桶、数据库、Kubernetes 对象、可观测性、机密路径以及身份（人员、管理员、服务账号、AI 智能体、工作负载）提供统一的命名语法。

这是一个持续演进的模板：在应用中接受检验和质疑，并随着理解的加深不断修订。可以直接使用，也可以根据贵组织的情况进行调整。

**状态：** v2，持续演进中。名称和规则仍可能变化；变更记录在下方的变更日志中。

## 为什么

名称是成本最低的架构决策，却也是修改成本最高的决策。当每个团队各自命名时，就会出现 DNS 中夹带产品名、访问规则藏在主机名里、机密按供应商组织、服务账号与 AI 智能体无法区分等问题。本标准按固定顺序从同一组少量维度推导出所有名称：**平面 (plane)、域 (domain)、能力 (capability)、产品 (product)、环境 (env)**。因此名称可以根据登记信息预测，并可进行自动化审查。

## 文件

| 文件 | 规定内容 |
|---|---|
| [01-naming-conventions.md](i18n/zh-CN/01-naming-conventions.md) | 字符规则、十个元数据键、DNS 语法、代码、对象形式（主机、仓库、镜像、存储桶、k8s、可观测性）、TLS、流程、拒绝规则 |
| [02-worked-example.md](i18n/zh-CN/02-worked-example.md) | 一个虚构组织将遗留名称（`grafana.corp.lan`、`vm042`、`secret/users/...`）迁移到本标准 |
| [03-secrets-conventions.md](i18n/zh-CN/03-secrets-conventions.md) | 机密管理器（OpenBao / HashiCorp Vault）的挂载点、路径、条目与字段、策略、认证角色、元数据 |
| [04-identity-conventions.md](i18n/zh-CN/04-identity-conventions.md) | 人员、管理员、紧急访问账号、服务账号、智能体、组与层级、SPIFFE、网状网络组、k8s RBAC、数据库角色、网关客户端 |
| [CONTRIBUTING.md](i18n/zh-CN/CONTRIBUTING.md) | 如何提出变更以及讨论规则 |
| [i18n/](i18n/) | 俄语与简体中文译文（参考性） |
| [LICENSE](LICENSE) | CC BY 4.0 |

建议先阅读[命名流程](i18n/zh-CN/01-naming-conventions.md#9-命名流程)和[编码示例](i18n/zh-CN/01-naming-conventions.md#11-编码示例)，再阅读[完整示例](i18n/zh-CN/02-worked-example.md)。

## 核心思想一览

- **两种 DNS 语法，没有第三种。** 内部：`<capability>.<domain>.<plane>[.<env>].svc.<company-domain>`。公共：`<surface>.<product-domain>`。最左侧标签是能力，而不是产品。
- **一个实例，一个名称。** 别名是有时限的重定向。
- **名称不承载授权。** 标签用于路由和标识；访问权限来自组和策略（最小权限原则，[NIST SP 800-53 AC-6](https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/SP_800_53_5_2_0/home?element=AC-06)）。
- **处处使用同样的十个元数据键**（`plane, domain, capability, product, env, owner, tier, scope, data_class, exposure`）。DNS 编码其中四个；其余由目录、机密元数据、k8s 标签和虚拟化平台标签承载。
- **身份类型在 ID 中可见。** 智能体不是服务账号：它们自主行动，需要一名负责的人类操作员 (operator)，并拥有自己的前缀和机密节点。
- **机密跟随其使用方存放**：每个平面一个挂载点，路径为 `<domain>/<capability>/<env>/<item>`，每个使用方身份一条策略。
- **三种组前缀**：`tier-`、`role-`、`app-`。
- **信任域不等于 DNS 区域**（[SPIFFE](https://spiffe.io/docs/latest/spiffe-about/overview/)）。
- 所有对外标识符只使用**小写字母、数字、连字符**；仅在系统禁止连字符时使用 `snake_case`。
- **与产品无关。** 示例中提到的产品（IdP、机密管理器、网状 VPN、Git 托管平台、镜像仓库、仪表板……）只是可互换的示意，而非强制要求。

`mess.systems` 是本组织自己的域名，出现在示例中；调整使用时请替换为您自己的域名。

## 设计依据

本标准对照了 [RFC 1035](https://www.rfc-editor.org/rfc/rfc1035)、[RFC 1123](https://www.rfc-editor.org/rfc/rfc1123) 和 [RFC 9499](https://www.rfc-editor.org/rfc/rfc9499) 中的 DNS 约束，以及常见的企业实践：[Microsoft Cloud Adoption Framework 资源命名](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/resource-naming)、[OpenBao](https://openbao.org/docs/concepts/policies/) 和 [Vault](https://developer.hashicorp.com/vault/docs/concepts/policies) 的策略与路径指南、[SPIFFE ID 规范](https://github.com/spiffe/spiffe/blob/main/standards/SPIFFE-ID.md)、[Kubernetes 对象命名规则](https://kubernetes.io/docs/concepts/overview/working-with-objects/names/)，以及 [NIST SP 800-53](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) 中的控制项 [AC-2](https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/SP_800_53_5_2_0/home?element=AC-02)（账户管理）和 [AC-6](https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/SP_800_53_5_2_0/home?element=AC-06)（最小权限）。

经过质疑后保留的决策：

| 问题 | 决定 | 原因 |
|---|---|---|
| 生产环境中六级标签（`sso.iam.shared.svc.mess.systems`）是否太深？ | 保留 | RFC 1035 规定每个标签最多 63 个字符、整个名称最多 253 个字符。按名称签发 ACME 证书后，通配符深度只对无法使用 ACME 的端点有影响。深度换来的是可推导的名称 |
| `svc` 与 Kubernetes 的 `svc.cluster.local` 冲突？ | 保留 `svc` | 后缀不同，解析器也不同（见[语法 A](i18n/zh-CN/01-naming-conventions.md#31-语法-a内部)） |
| 私有伪顶级域（`.lan`、`.corp`、`.internal`）？ | 否，使用已注册域名的子域 | 公共 CA 不会为其签发证书。`.local` 保留给 mDNS（[RFC 6762](https://www.rfc-editor.org/rfc/rfc6762)），永远不要使用 |
| 生产 DNS 省略环境，而主机/schema 中保留？ | 保留 | DNS 按区域缩写；资产清单则不缩写 |
| 共享的 LLM 网关即使被产品使用也只保留一个名称（`gateway.ai.corp`）？ | 保留 | 一个实例，一个名称；`gateway.ai.platform` 仅作保留，不签发 |

## 变更日志

### v2（当前）

- 多词代码使用连字符连接（`data-catalog`、`hub-cache`、`service-desk`），绝不直接拼接。
- 能力代码在**所有**域中唯一（例如文档数据库是 `docstore` 而不是 `docs`；LLM 链路追踪是 `llm-traces` 而不是 `traces`；AI 护栏 (guardrail) 是 `guard` 而不是 `policy`）。
- 公共区域 `apps.<brand>` 被定义为语法 B 下的 `ext` 区域。
- 主机形式增加了前置的站点代码：`<site>-<plane>-<domain>-<product>-<env>-<NN>`。
- 新增[机密](i18n/zh-CN/03-secrets-conventions.md)和[身份](i18n/zh-CN/04-identity-conventions.md)规范；同一套元数据标签处处适用。
- SPIFFE 信任域为组织本身（`spiffe://mess.systems`），路径为 `/<plane>/<domain>/<capability>`。
- 明确规则：DNS 标签绝不作为授权依据。

### v1

- 能力优先的内部语法、浅层的公共语法、平面作为第一隔离维度、一个实例对应一个 URL、提供商作为目录 ID。

## 待解决问题

- 通用的切换操作手册（DNS、机密挂载点、SPIFFE 信任域的切换顺序）。完整示例中的[切换顺序](i18n/zh-CN/02-worked-example.md#8-切换顺序)给出了一个草案。
- `obs` 是继续作为独立的域，还是并入 `infra`。

## 讨论与贡献

- **问题、想法、“X 应该怎么命名？”**：请在 [GitHub Discussions](https://github.com/mess-systems/naming-standard/discussions) 中发起讨论。
- **具体的变更提案**（新代码、规则变更、示例错误）：使用 *Proposal* 模板提交 [Issue](https://github.com/mess-systems/naming-standard/issues)，然后提交 pull request。
- 请先阅读 [CONTRIBUTING.md](i18n/zh-CN/CONTRIBUTING.md)，特别是发布前检查清单：切勿在 issue、讨论或示例中发布真实的内部主机名、IP 地址、机密或个人数据。

## 翻译

- 英文文本为规范性文本；如有任何不一致，以英文版本为准。
- 译文存放在 `i18n/<lang>/` 下，文件名与英文相同：俄语在 `i18n/ru/`，简体中文在 `i18n/zh-CN/`。翻译后的 README 为仓库根目录下的 `README.ru.md` 和 `README.zh-CN.md`。
- 只翻译说明性文字。名称、令牌、代码、FQDN、路径和代码块在所有语言中保持一致。
- 每份译文在开头注明其所对应的英文源提交。如需更新译文，请按照 [CONTRIBUTING.md](i18n/zh-CN/CONTRIBUTING.md) 中的*翻译*一节操作。

## 许可证

文本采用 [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE) 许可（[官方中文说明](https://creativecommons.org/licenses/by/4.0/deed.zh-hans)）。您可以共享和改编本文本，包括用于商业目的，但须注明出处："mess.systems naming standard (https://github.com/mess-systems/naming-standard), CC BY 4.0"。
