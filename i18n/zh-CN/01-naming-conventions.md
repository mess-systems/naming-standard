[English](../../01-naming-conventions.md) | [Русский](../ru/01-naming-conventions.md) | **简体中文**

> **译文说明。** 本文为标准 v2 版本的译文，源提交 `b6791c2`。英文文本为规范性文本：如有任何不一致，以英文版本为准。

# 命名规范 v2 — mess.systems

> **状态：** v2，持续演进中。自成体系：应用本标准所需的全部规则都在本仓库中。
> **范围：** 人或机器读取的所有标识符：DNS、主机、代码仓库、镜像、存储桶、数据库、Kubernetes、可观测性、目录 ID。机密 → [03](03-secrets-conventions.md)。身份 → [04](04-identity-conventions.md)。迁移示例 → [02](02-worked-example.md)。
> **组织域名：** `mess.systems` 是本组织自己的域名，全文均使用该域名。调整使用本标准时，请替换为您自己已注册的域名。

## 1. 字符规则（适用于所有类别）

| 规则 | 取值 | 原因 |
|---|---|---|
| 字母表 | `a-z 0-9 -` | RFC 1123 主机名、Kubernetes 名称、S3、容器镜像仓库、大多数 IdP |
| 大小写 | 仅小写 | DNS 不区分大小写；其他系统则区分 |
| 维度之间的分隔符 | 名称中用 `-`，DNS 和点分 ID 中用 `.`，路径中用 `/` | 每种分隔符只有一种含义 |
| 多词令牌 (token) | 用连字符连接（`data-catalog`），绝不直接拼接或使用 camelCase | 可读性；DNS 允许 |
| `_` | 仅用于不允许 `-` 的场合：SQL 标识符、环境变量、机密字段名 | 由系统限制决定 |
| 标签长度 | ≤ 63 个字符；FQDN ≤ 253 | RFC 1035 |
| 开头/结尾的 `-` | 绝不允许 | RFC 1123 |
| 数字 | 允许；令牌绝不以数字开头 | k8s 标签值、shell |
| 序号 | 两位数，左侧补零（`01`） | 排序正确 |
| 保留字 | `api`、`www`、`app`、`admin`、`internal`、`public`、`prod`、`test`、`svc`、`local`、`cluster`——绝不能用作平面、域、能力或产品代码 | 与语法令牌或 RFC 6762/6761 冲突 |

## 2. 十个元数据键

每一类对象都携带相同的键。DNS 编码前四个（非生产环境时再加上环境）。其余的键记录在该类对象的目录中。

| 键 | 取值 | 编码位置 |
|---|---|---|
| `plane` | `shared corp eng platform ext <product>` | DNS、主机、仓库、k8s 标签、机密挂载点 |
| `domain` | §4.2 中的代码 | DNS、主机、仓库、schema |
| `capability` | §4.3 中的代码 | DNS 最左侧标签、SPIFFE 路径、MCP 目标 |
| `product` | 实例代码（`keycloak`、`gitea`） | 主机、仓库、镜像、k8s 命名空间 |
| `env` | `prd dev tst stg` | DNS（仅非生产）、主机、schema、机密路径（始终） |
| `owner` | [04](04-identity-conventions.md) §5 中的组 ID | 目录、机密元数据、k8s 标签 |
| `tier` | `t0 t1 t2 t3`（特权访问层级，[04](04-identity-conventions.md) §3.1） | 目录、身份组 |
| `scope` | `dev tst stg prd`——对象获准使用的最高环境 | 仅目录 |
| `data_class` | `public internal confidential restricted` | 目录、机密元数据、存储桶标签 |
| `exposure` | `mesh lan public` | 目录、网状网络组——**绝不出现在名称中** |

Kubernetes 标签键：`mess.systems/<key>`。虚拟化平台和云标签：`<key>-<value>`（`plane-corp`），或在支持的情况下使用原生键/值标签。容器镜像仓库标签：与虚拟化平台标签相同。机密管理器：`custom_metadata.<key>`。

## 3. DNS——两种语法，别无其他

### 3.1 语法 A——内部

```
<capability>.<domain>.<plane>.svc.mess.systems                 # prod
<capability>.<domain>.<plane>.<env>.svc.mess.systems           # dev|tst|stg
<surface>.<product>.svc.mess.systems                           # internal product (plane = product)
```

- `svc.mess.systems` 是内部区域（水平分割 DNS (split-horizon)、内部 CA + ACME），不对外公开委派。这里的 `svc` 表示“服务区域”，与 Kubernetes 的 `*.svc.cluster.local` 无关——后缀不同，解析器也不同。
- 最左侧标签是**能力 (capability)**，而不是产品（用 `git`，不用 `gitea`）。产品属于资产清单信息，不属于名称的一部分。
- 生产环境省略环境。其他所有地方（主机、schema、机密）都写出 `prd`。
- 一个实例 → 恰好一个规范 FQDN。别名是重定向，不是名称。
- **标签绝不作为授权依据。** 可达性和权限来自网状网络组、IdP 组和机密管理器策略（[04](04-identity-conventions.md)）。同一实例的两个使用方使用相同的名称和不同的组。

### 3.2 语法 B——公共

```
<surface>.<product-domain>            # www | app | api | docs | status | auth
<capability>.apps.mess.systems        # ext plane on the brand domain
www.mess.systems                      # brand
```

- 公共名称绝不包含平面、域、环境或供应商。
- `apps.mess.systems` 是品牌域名下**唯一**的公共子区域，承载 `ext` 能力（合作伙伴/演示门户）。它是以品牌作为产品的语法 B。
- 对于必须在网状网络建立之前就可访问的控制平面（例如网状网络协调器），允许使用单个公共专用名称，但必须作为有记录、有文档的例外——而不是一种模式。

### 3.3 不存在语法 C

| 常见反模式 | 为什么它不是名称 | 目标 |
|---|---|---|
| `*.admin.corp.lan`、`*.private.corp.lan` | 名称中包含暴露范围 (exposure) | 同一 FQDN，不同的网状网络/IdP 组 |
| `*.mesh`、`*.apps.mesh` | 网状网络内部的伪顶级域；在网状网络 DNS 之外无法解析 | 语法 A |
| `vcenter.corp.lan`（产品而非能力） | 违反“最左侧是能力”规则 | `compute.infra.shared.svc.mess.systems` |
| 仓库目录名（`infra/llm-proxy`） | 仓库目录不是命名维度 | `gateway.ai.corp` |

## 4. 代码

### 4.1 平面

| 代码 | 使用者 | 信任级别 |
|---|---|---|
| `shared` | 所有人都依赖的控制平面（IAM、PKI、机密、DNS、网状网络、可观测性、虚拟化平台） | 最高 |
| `corp` | 员工 | 内部 |
| `eng` | 构建产品的工程师 | 内部 |
| `platform` | 各产品共享的运行时 | 产品级 |
| `<product>` | 单个产品自己的运行时 | 产品级 |
| `ext` | 合作伙伴、演示、面向公众的门户 | 外部 |

### 4.2 域

| 代码 | 域 | 默认平面 |
|---|---|---|
| `iam` | 身份、访问、PKI、机密、密码 | shared |
| `gov` | 架构、策略、CMDB、ADR | corp |
| `sec` | 威胁检测、漏洞管理、SIEM | shared |
| `obs` | 指标、日志、链路追踪、告警（参见 README 中的待解决问题） | shared |
| `net` | DNS、网状网络、边缘、防火墙 | shared |
| `infra` | 计算、存储、备份、虚拟化平台 | shared |
| `sdlc` | 代码、CI、制品、GitOps | eng |
| `adlc` | AI/智能体生命周期、评测 (evals)、策略 sidecar | eng |
| `ai` | 推理、网关、语音、视觉、智能体 | corp |
| `data` | 数据仓库、数据管道、目录、BI、文档存储 | platform |
| `collab` | 聊天、wiki、文档、视频 | corp |
| `comm` | 邮件、通知 | corp |
| `biz` | ERP/CRM/财务 | corp |
| `itsm` | 服务台、变更管理 | corp |
| `api` | 面向产品的 API 管理 | platform |
| `edge` | 面向产品的入口 (ingress) | platform |

### 4.3 能力代码（在所有域中唯一）

一个代码在整个公司内只有**一种含义**。同一代码可以出现在多个平面中（`egress.net.corp`、`egress.net.platform`），因为平面是另一个维度；但它不能出现在两个域中。

| 域 | 代码 |
|---|---|
| `iam` | `sso directory pki spiffe secrets passwords b2b` |
| `gov` | `cmdb archrepo adr policy catalog demo audit` |
| `sec` | `siem vuln ids scan` |
| `obs` | `dashboards metrics logs traces alerts` |
| `net` | `dns mesh ingress egress firewall` |
| `infra` | `compute storage backup k8s` |
| `sdlc` | `git ci oci packages gitops flags hub-cache` |
| `adlc` | `registry sandbox evals` |
| `ai` | `gateway inference stt tts ocr llm-traces kb docs guard` |
| `data` | `warehouse orchestrate transform ingest data-catalog bi docstore convert sql cache objects` |
| `collab` | `chat wiki intranet video` |
| `comm` | `mail notify` |
| `biz` | `crm billing` |
| `itsm` | `service-desk change` |
| `api` | `gateway-api portal-api` |
| `edge` | `lb` |

此表是一个示例参考集，而不是资产清单；请按照下面的规则，根据各组织情况进行扩充或删减。

新增代码：在整张表中检查唯一性，多词代码用连字符连接，先在能力目录中登记该能力，再添加到此处。

### 4.4 环境与站点

| 环境 | 代码 | 站点 | 代码 |
|---|---|---|---|
| 生产 | `prd` | 本地 (on-premises) 数据中心 | `dc1` |
| 预发布 (staging) | `stg` | 公有云租户 | `cld` |
| 测试 | `tst` | | |
| 开发 | `dev` | | |

站点代码简短、因组织而异，并在目录中列出；上面两个仅为示例。

## 5. 对象形式

| 类别 | 形式 | 示例 |
|---|---|---|
| 内部 FQDN | §3.1 | `git.sdlc.eng.svc.mess.systems` |
| 公共 FQDN | §3.2 | `app.shopfront.example` |
| 应用（目录、`service.name`、OIDC slug、AppRole） | `<plane>-<domain>-<product>` | `eng-sdlc-gitea` |
| 主机 / 容器 / 虚拟机 | `<site>-<plane>-<domain>-<product>-<env>-<NN>` | `dc1-eng-sdlc-gitea-prd-01` |
| 虚拟化平台节点 | `<site>-shared-infra-<hypervisor>-<env>-<NN>` | `dc1-shared-infra-kvm-prd-01` |
| Git 组织 / 仓库 | 组织 `<plane>` · 仓库 `<domain>-<product>` | `eng/sdlc-gitea` |
| 容器镜像 | `oci.sdlc.eng.svc.mess.systems/<plane>-<domain>/<product>[-<component>]:<tag>` | `oci.sdlc.eng.svc.mess.systems/corp-ai/litellm:1.4.0` |
| 镜像仓库项目（例如 Harbor） | `<plane>-<domain>` | `corp-ai` |
| 软件包源 | `<ecosystem>-<plane>` 或 `<ecosystem>-proxy` | `npm-proxy`、`pypi-eng` |
| S3 / 对象存储桶 | `<plane>-<domain>-<capability>-<env>` | `platform-data-warehouse-prd` |
| Postgres 数据库 | `<plane>_<domain>_<capability>_<env>` | `eng_sdlc_git_prd` |
| Postgres / ClickHouse schema | 与数据库相同 | `platform_data_warehouse_prd` |
| 数据集 / dbt 数据集市 | `<plane>.<domain>.<table>` | `platform.data.catalog_coverage` |
| Kubernetes 命名空间 | `<product>[-<env>]`；平台服务使用能力代码 | `shopfront-stg`、`gitops` |
| Kubernetes 工作负载 | `<product>-<context>-<role>` | `shopfront-api-web` |
| Kubernetes 标签 | `mess.systems/<key>=<value>` | `mess.systems/plane=platform` |
| 提供商目录 ID | `<vendor>.<service>` | `acmecloud.foundation-models` |
| LLM 路由前缀（网关） | `<provider-short>/<model>`；`local/` = 企业自有推理 | `acmecloud/large-chat` |
| MCP 目标（网关） | 能力代码；提供商为 `<vendor>-<service>` | `convert`、`acmesearch-web` |
| OTel `service.name`、Prometheus `job`、Loki `service_name` | 应用形式 | `corp-ai-litellm` |
| 仪表板文件夹（例如 Grafana）/ 仪表板 uid | 文件夹 `<plane>-<domain>` · uid `<application>-<view>` | `corp-ai` / `corp-ai-litellm-overview` |
| 告警规则 | `<Domain><Capability><Symptom>` | `AiGatewayHighErrorRate` |
| Ansible 清单组 | `<plane>_<domain>` 和 `<application>` | `corp_ai`、`corp_ai_litellm` |
| OpenTofu 资源名称 | `<application>_<env>` | `corp_ai_litellm_prd` |
| 证书（内部） | 每个域-平面组合一个 `*.<domain>.<plane>.svc.mess.systems` | `*.ai.corp.svc.mess.systems` |
| 系统邮件发件人 | `<capability>@mess.systems` | `alerts@mess.systems` |

## 6. 单一基础 URL

一个实例只有一个基础 URL：`https://<fqdn>`。基于路径的多租户（`/admin`、`/ui`）由产品自行处理，不体现在 FQDN 中。旧名称的重定向允许保留 90 天并列入迁移表，之后删除。

## 7. TLS

- 内部：通过 `pki.iam.shared` 使用 ACME。默认按名称签发（例如支持按需 TLS 的入口代理）。只有无法使用 ACME 的端点才使用预先签发的通配符证书：每个 `<domain>.<plane>` 组合一张，并列入部署的证书清单（示例见 [02](02-worked-example.md) §6）。
- 公共：在产品域名上通过 DNS-01 向公共 CA 申请。每个产品域名一张通配符证书。
- SAN 中的名称始终是规范 FQDN 加上已登记的重定向名称，绝不包含遗留名称。

## 8. 提供商与出站流量

- 外部供应商是目录 ID（`<vendor>.<service>`），绝不是内部 FQDN。
- 访问供应商的出站流量经由所属能力（LLM 提供商经由 `gateway.ai.corp`，网络经由 `mesh.net.shared` 出站组）。
- 提供商机密存放在**使用方**能力的路径下（[03](03-secrets-conventions.md) §4）。

## 9. 流程

**步骤 A——登记 (intake)，按顺序确定维度：** 平面 → 域 → 能力 → 产品 → 环境 → 所有者/层级/scope/data_class/exposure。
**步骤 B——编码：** FQDN（§3）、应用（§5）、主机（§5），然后是各类别的特定形式。先在目录中登记，再配置 DNS。
**步骤 C——身份与机密：** 创建组/机器角色（[04](04-identity-conventions.md)），创建路径（[03](03-secrets-conventions.md)）。
**步骤 D——可观测性：** `service.name` = 应用；仪表板文件夹 = `<plane>-<domain>`。

## 10. 拒绝规则（出现以下情况时拒绝该名称）

| 问题特征 | 违反的规则 |
|---|---|
| 产品作为最左侧标签 | §3.1 |
| 名称中包含暴露范围或层级（`admin.`、`public.`、`t0-`） | §3.1、§2 |
| 生产 DNS 名称中包含环境 | §3.1 |
| 主机、schema、存储桶或机密路径中缺少环境 | §5、[03](03-secrets-conventions.md) |
| 供应商作为内部 FQDN | §8 |
| 通过路径在一个 FQDN 上承载两个能力 | §6 |
| 仓库目录作为名称 | §3.3 |
| DNS 或 k8s 中出现 `_` | §1 |
| 能力代码被赋予第二种含义重复使用 | §4.3 |
| 为“特殊”情况创建新语法 | §3.3 |

## 11. 编码示例

| 登记信息 (intake) | FQDN | 应用 | 主机 |
|---|---|---|---|
| shared / iam / sso / Keycloak / prd | `sso.iam.shared.svc.mess.systems` | `shared-iam-keycloak` | `dc1-shared-iam-keycloak-prd-01` |
| eng / sdlc / git / Gitea / prd | `git.sdlc.eng.svc.mess.systems` | `eng-sdlc-gitea` | `dc1-eng-sdlc-gitea-prd-01` |
| corp / ai / gateway / LiteLLM / prd | `gateway.ai.corp.svc.mess.systems` | `corp-ai-litellm` | `dc1-corp-ai-litellm-prd-01` |
| corp / ai / gateway / LiteLLM / stg | `gateway.ai.corp.stg.svc.mess.systems` | `corp-ai-litellm` | `dc1-corp-ai-litellm-stg-01` |
| platform / data / docstore / MongoDB / prd | `docstore.data.platform.svc.mess.systems` | `platform-data-mongodb` | `dc1-platform-data-mongodb-prd-01..03` |
| shared / net / mesh / Headscale / prd (cloud site) | `mesh.net.shared.svc.mess.systems` | `shared-net-headscale` | `cld-shared-net-headscale-prd-01` |
| ext / demo portal | `demo.apps.mess.systems` | `ext-gov-demo-portal` | `cld-ext-gov-portal-prd-01` |
| shopfront (product) / app | `app.shopfront.example` | `shopfront-api` | `cld-shopfront-api-prd-01` |
