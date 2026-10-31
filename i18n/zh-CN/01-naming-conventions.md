[English](../../01-naming-conventions.md) | [Русский](../ru/01-naming-conventions.md) | **简体中文**

> **译文说明。** 本文为标准 v2.7 版本的译文，源提交 `a60b331`（含链接编辑修订）。英文文本为规范性文本：如有任何不一致，以英文版本为准。

# mess.systems 命名规范（v2）

> **状态：** v2，持续演进中。自成体系：应用本标准所需的全部规则都在本仓库中。
> **范围：** 人或机器读取的所有标识符：DNS、主机、代码仓库、镜像、存储桶、数据库、Kubernetes、可观测性、目录 ID。机密见[机密规范](03-secrets-conventions.md)，身份见[身份规范](04-identity-conventions.md)，完整的迁移过程见[完整示例](02-worked-example.md)。
> **组织域名：** `mess.systems` 是本组织自己的域名，全文均使用该域名。调整使用本标准时，请替换为您自己已注册的域名。

## 1. 字符规则（适用于所有类别）

| 规则 | 取值 | 原因 |
|---|---|---|
| 字母表 | `a-z 0-9 -` | [RFC 1123](https://www.rfc-editor.org/rfc/rfc1123) 主机名、[Kubernetes 名称](https://kubernetes.io/docs/concepts/overview/working-with-objects/names/)、S3、容器镜像仓库、大多数 IdP |
| 大小写 | 仅小写 | DNS 不区分大小写；其他系统则区分 |
| 维度之间的分隔符 | 名称中用 `-`，DNS 和点分 ID 中用 `.`，路径中用 `/` | 每种分隔符只有一种含义 |
| 多词令牌 (token) | 用连字符连接（`data-catalog`），绝不直接拼接或使用 camelCase | 可读性；DNS 允许 |
| `_` | 仅用于不允许 `-` 的场合：SQL 标识符、环境变量、机密字段名 | 由系统限制决定 |
| 标签长度 | ≤ 63 个字符；FQDN ≤ 253 | [RFC 1035](https://www.rfc-editor.org/rfc/rfc1035) |
| 开头/结尾的 `-` | 绝不允许 | RFC 1123 |
| 数字 | 允许；令牌绝不以数字开头 | k8s 标签值、shell |
| 序号 | 两位数，左侧补零（`01`） | 排序正确 |
| 保留字 | `api`、`www`、`app`、`admin`、`internal`、`public`、`prod`、`test`、`svc`、`local`、`cluster`——绝不能用作平面、域、能力或产品代码 | 与语法令牌或 [RFC 6762](https://www.rfc-editor.org/rfc/rfc6762)、[RFC 6761](https://www.rfc-editor.org/rfc/rfc6761) 保留的名称冲突 |

### 1.1 连字符解析规则

连字符既分隔名称的各个轴，又连接同一令牌中的单词（`data-catalog`）。名称按位置解析，因此 `dc1-eng-sdlc-data-catalog-prd-01` 只有一种读法。

| 规则 | 含义 |
|---|---|
| 平面和域代码 | 一个不含连字符的令牌（`shared`、`eng`、`sdlc`、`obs`） |
| 解析 | 按[对象形式](#5-对象形式)中的位置从左到右：先是站点（仅主机名），然后是平面，然后是域，然后是产品或能力，然后是环境和序号（如果形式中包含） |
| 环境 | 始终是[环境与站点](#44-环境与站点)中的代码，因此可按取值识别 |
| 序号 | 始终是最后位置上的两位数字 |
| 其余部分 | 域与环境（或名称末尾）之间的全部内容是一个产品或能力令牌，即使其中含有连字符 |
| 检查 | 只有每个位置都与 `catalog/` 中对应列表匹配时名称才有效；不匹配即拒绝，而不是猜测 |

示例：`dc1-eng-sdlc-data-catalog-prd-01`——站点 `dc1`、平面 `eng`、域 `sdlc`、产品 `data-catalog`、环境 `prd`、序号 `01`。

所有者、范围和环境的限定绝不进入名称。它们只存在于标签中（`owner`、`scope`、`env`，见[标签与标记](05-labels-and-tags.md)），而这些标签无论如何都是必需的。双连字符不用作限定分隔符：它与 DNS 标签的保留形式 `xn--`（[RFC 5891](https://www.rfc-editor.org/rfc/rfc5891)）冲突。RoleBinding 形式 `<role>--<subject>`（[Kubernetes RBAC](04-identity-conventions.md#10-kubernetes-rbac)）保持不变：它连接两个完整名称，不是限定。

## 2. 十个元数据键

每一类对象都携带相同的键。DNS 编码前四个（非生产环境时再加上环境）。其余的键记录在该类对象的目录中。

| 键 | 取值 | 编码位置 |
|---|---|---|
| `plane` | `shared corp eng platform ext <product>` | DNS、主机、仓库、k8s 标签、机密挂载点 |
| `domain` | [域代码](#42-域) | DNS、主机、仓库、schema |
| `capability` | [能力代码](#43-能力代码在所有域中唯一) | DNS 最左侧标签、SPIFFE 路径、MCP 目标 |
| `product` | 实例代码（`keycloak`、`gitea`） | 主机、仓库、镜像、k8s 命名空间 |
| `env` | `prd dev tst stg` | DNS（仅非生产）、主机、schema、机密路径（始终） |
| `owner` | 组 ID（见[所有者](04-identity-conventions.md#5-所有者)） | 目录、机密元数据、k8s 标签 |
| `tier` | `t0 t1 t2 t3`（特权访问层级，见[层级组](04-identity-conventions.md#31-层级组特权)） | 目录、身份组 |
| `scope` | `dev tst stg prd`——对象获准使用的最高环境 | 仅目录 |
| `data_class` | `public internal confidential restricted` | 目录、机密元数据、存储桶标签 |
| `exposure` | `mesh lan public` | 目录、网状网络组——**绝不出现在名称中** |

[Kubernetes 标签](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)键：`mess.systems/<key>`。云和虚拟化平台标签：使用原生键/值标签；仅在平台不支持键/值标签时使用 `<key>-<value>`（`plane-corp`）。所有标签均遵循[标签与标记](05-labels-and-tags.md)。容器镜像仓库标签：与虚拟化平台标签相同。机密管理器：`custom_metadata.<key>`。

这十个键描述**企业轮廓**。**产品轮廓**（面向客户销售的产品及其单元和租户）使用 `product`、`domain`、`service` 和 `implementation`，以及部署和租户键；见 [07 部署与租户](07-deployment-and-tenants.md)。

## 3. DNS：两种语法，别无其他

### 3.1 语法 A：内部

```
<capability>.<domain>.<plane>.svc.mess.systems                 # prod
<capability>.<domain>.<plane>.<env>.svc.mess.systems           # dev|tst|stg
<surface>.<product>.svc.mess.systems                           # superseded by 07 (product contour)
```

- `svc.mess.systems` 是内部区域（水平分割 DNS (split-horizon)、内部 CA + ACME），不对外公开委派。这里的 `svc` 表示“服务区域”，与 Kubernetes 的 `*.svc.cluster.local` 无关——后缀不同，解析器也不同。
- 最左侧标签是**能力 (capability)**，而不是产品（用 `git`，不用 `gitea`）。产品属于资产清单信息，不属于名称的一部分。
- 生产环境省略环境。其他所有地方（主机、schema、机密）都写出 `prd`。
- 产品轮廓在内部 DNS 中同样写出 `prd`；见 [07 环境与 DNS](07-deployment-and-tenants.md)。这种不对称是有意的：企业名称保持简短，产品名称在任何环境中都以同样方式解析。
- 一个实例恰好对应一个规范 FQDN。别名是重定向，不是名称。
- **标签绝不作为授权依据。** 可达性和权限来自网状网络组、IdP 组和机密管理器策略（见[身份规范](04-identity-conventions.md)）。同一实例的两个使用方使用相同的名称和不同的组。

### 3.2 语法 B：公共

```
<surface>.<product-domain>            # www | app | api | docs | status | auth
<capability>.apps.mess.systems        # ext plane on the brand domain
<surface>.<product>.x.mess.systems    # products in the showcase sub-zone
www.mess.systems                      # brand
```

- 公共名称绝不包含平面、域、环境或供应商。唯一的例外是产品的非生产界面（`api.stg.<product-domain>`，见[环境与 DNS](07-deployment-and-tenants.md#3-环境与-dns)）。
- 品牌恰好有两个公共子区域，没有第三个：
  - `apps.mess.systems` 承载 `ext` 能力（合作伙伴/演示门户）：`<capability>.apps.mess.systems`。它是以品牌作为产品的语法 B。
  - `x.mess.systems` 承载产品轮廓中的产品（[部署与租户](07-deployment-and-tenants.md)）：产品域名 `<product>.x.mess.systems`，界面 `<surface>.<product>.x.mess.systems`，非生产界面 `<surface>.<env>.<product>.x.mess.systems`。拥有自己注册域名的产品使用该域名代替子区域，绝不同时使用两者。
- `x` 是子区域标签，不是产品代码，也不是平台名称。发布在 `x.mess.systems` 中的产品集合称为**展示区**。子区域标签绝不是组织目录中的产品代码。[部署与租户](07-deployment-and-tenants.md#2-产品域服务实现)示例中的虚构产品 `x` 不在该目录中；在那里 `x.mess.systems` 是占位的产品域名。
- 产品域名的顶点（`arch.x.mess.systems`）是产品的主界面，就像品牌的 `www`。
- `mess.systems` 下语法 A 和 B 之外的公共名称，只允许作为 `catalog/dns-exceptions.yaml` 中登记的例外：名称、其语法 A 规范名称、原因、所有者组和复审日期。典型情况是必须在网状网络建立之前就可访问的控制平面的专用名称，例如网状网络协调器。两种语法之外且未登记的名称将被拒绝。例外绝不作为新名称的模式。

```yaml
- name: netbird.mess.systems
  canonical: mesh.net.shared.svc.mess.systems
  reason: the mesh coordinator must be reachable before the mesh is up
  owner: role-platform-engineers
  review: 2027-10-31
```

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
| `obs` | 指标、日志、链路追踪、告警（参见 README 中的[待解决问题](../../README.zh-CN.md#待解决问题)） | shared |
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
| `device` | 员工设备、设备侧代理、虚拟桌面 | corp |

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
| `ai` | `gateway inference stt tts ocr llm-traces kb docs guard assistant` |
| `data` | `warehouse orchestrate transform ingest data-catalog bi docstore convert sql cache objects` |
| `collab` | `chat wiki intranet video` |
| `comm` | `mail notify` |
| `biz` | `crm billing` |
| `itsm` | `service-desk change` |
| `api` | `gateway-api portal-api` |
| `edge` | `lb` |
| `device` | `endpoint vdi` |

`endpoint` 属于设备侧：指员工设备上运行的一切，从不出现在 DNS 名称中；`vdi` 是服务器侧的虚拟工作场所，按普通服务命名（`vdi.device.corp.svc.mess.systems`）。见 [06](06-endpoint-conventions.md)。

此表是一个示例参考集，而不是资产清单；请按照下面的规则，根据各组织情况进行扩充或删减。

新增代码：在整张表中检查唯一性，多词代码用连字符连接，先在能力目录中登记该能力，再添加到此处。

### 4.4 环境与站点

| 环境 | 代码 | 站点 | 代码 |
|---|---|---|---|
| 生产 | `prd` | 本地 (on-premises) 数据中心 | `dc1` |
| 预发布 (staging) | `stg` | 公有云租户 | `cld` |
| 测试 | `tst` | | |
| 开发 | `dev` | | |
| 沙箱（仅产品轮廓，见 [07](07-deployment-and-tenants.md)） | `sbx` | | |

站点代码简短、因组织而异；上面两个仅为示例。站点代码在该站点出现第一台主机之前登记在 `catalog/sites.yaml` 中：代码（2 到 4 个 `a-z0-9` 字符，以字母开头）、类型（`own` 或 `cld`）和所有者组。站点代码绝不包含城市、地址或提供商名称；提供商是部署键 `provider`（[部署键](07-deployment-and-tenants.md#4-部署键)）。

## 5. 对象形式

| 类别 | 形式 | 示例 |
|---|---|---|
| 内部 FQDN | [语法 A](#31-语法-a内部) | `git.sdlc.eng.svc.mess.systems` |
| 公共 FQDN | [语法 B](#32-语法-b公共) | `app.shopfront.x.mess.systems` |
| 应用（目录、`service.name`、OIDC slug、AppRole） | `<plane>-<domain>-<product>` | `eng-sdlc-gitea` |
| 主机 / 容器 / 虚拟机 | `<site>-<plane>-<domain>-<product>-<env>-<NN>` | `dc1-eng-sdlc-gitea-prd-01` |
| 虚拟化平台节点 | `<site>-shared-infra-<hypervisor>-<env>-<NN>` | `dc1-shared-infra-kvm-prd-01` |
| 企业终端（笔记本、台式机） | `<profile>-<form>-<asset-id>`，见 [06 终端约定](06-endpoint-conventions.md) | `std-lt-a1b2c3` |
| Git 组织 / 仓库 | 组织 `<plane>` · 仓库 `<domain>-<product>` | `eng/sdlc-gitea` |
| 基础设施即代码仓库，扁平组织 | `<plane>-<domain>-iac` | `shared-sec-iac`、`shared-obs-iac` |
| 产品的基础设施即代码仓库 | `<product>-<domain>-iac` | `platform-build-iac`、`shopfront-edge-iac` |
| 基础设施即代码仓库，每个平面一个组织 | 组织 `<plane>` · 仓库 `<domain>-iac` | `shared/infra-iac` |
| 共享的角色或模块库 | 所属仓库 + `-roles` 或 `-modules` | `shared-infra-iac-roles` |
| 容器镜像 | `oci.sdlc.eng.svc.mess.systems/<plane>-<domain>/<product>[-<component>]:<tag>` | `oci.sdlc.eng.svc.mess.systems/corp-ai/agentgateway:1.6.0` |
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
| OTel `service.name`、Prometheus `job`、Loki `service_name` | 应用形式 | `corp-ai-agentgateway` |
| 仪表板文件夹（例如 Grafana）/ 仪表板 uid | 文件夹 `<plane>-<domain>` · uid `<application>-<view>` | `corp-ai` / `corp-ai-agentgateway-overview` |
| 告警规则 | `<Domain><Capability><Symptom>` | `AiGatewayHighErrorRate` |
| Ansible 清单组 | `<plane>_<domain>` 和 `<application>` | `corp_ai`、`corp_ai_agentgateway` |
| OpenTofu 资源名称 | `<application>_<env>` | `corp_ai_agentgateway_prd` |
| 证书（内部） | 每个域-平面组合一个 `*.<domain>.<plane>.svc.mess.systems` | `*.ai.corp.svc.mess.systems` |
| 系统邮件发件人 | `<capability>@mess.systems` | `alerts@mess.systems` |

基础设施即代码仓库：工具（`ansible`、`opentofu`、`terraform`）和站点（`dc1`、`cld`、云名称）绝不进入仓库名称。它们成为仓库内的文件夹（`stacks/<site>/…`、`roles/`、`modules/`）；工具已记录在 `managed-by` 标签中（[部署与租户](07-deployment-and-tenants.md#7-治理标签)）。一个仓库服务于一对平面和域：同一台机器上两个不同域的系统使用两个仓库，共享的机器在清单中描述。后缀 `-iac` 保留给基础设施代码。

其他对象形式位于其他部分：

| 对象 | 位置 |
|---|---|
| kv 以外机密引擎（database、ssh、pki）的挂载点、角色和签发者 | [kv 以外的引擎](03-secrets-conventions.md#21-kv-以外的引擎) |
| 网状网络的组、策略、规则、状态检查、网络、资源、设置密钥、名称服务器组 | [网状 VPN 组](04-identity-conventions.md#4-网状-vpn-组)及其后的小节 |
| 产品访问组 | [产品访问组](04-identity-conventions.md#34-产品访问组) |
| 临时数据库用户 | [临时数据库用户](04-identity-conventions.md#111-临时数据库用户) |
| Git 分支和标签 | [Git 分支与标签](08-operations-objects.md#1-git-分支与标签) |
| CI 工作流和作业、计划任务 | [CI 与计划任务](08-operations-objects.md#2-ci-与计划任务) |
| 备份作业、快照 | [备份与快照](08-operations-objects.md#3-备份与快照) |
| 虚拟机管理程序客户机、资源池、模板 | [虚拟机管理程序客户机](08-operations-objects.md#4-虚拟机管理程序客户机) |
| API 网关的路由、上游和使用方 | [API 网关](08-operations-objects.md#5-api-网关) |
| DNS 记录 | [DNS 记录](08-operations-objects.md#6-dns-记录) |
| PostgreSQL 集群、复制槽、发布 | [PostgreSQL 对象](08-operations-objects.md#7-postgresql-对象) |

## 6. 单一基础 URL

一个实例只有一个基础 URL：`https://<fqdn>`。基于路径的多租户（`/admin`、`/ui`）由产品自行处理，不体现在 FQDN 中。旧名称的重定向允许保留 90 天并列入迁移表，之后删除。

## 7. TLS

- 内部：通过 `pki.iam.shared` 使用 [ACME](https://www.rfc-editor.org/rfc/rfc8555)。默认按名称签发（例如支持按需 TLS 的入口代理）。只有无法使用 ACME 的端点才使用预先签发的通配符证书：每个 `<domain>.<plane>` 组合一张，并列入部署的证书清单（示例见完整示例中的[证书](02-worked-example.md#6-证书)一节）。
- 公共：在产品域名上通过 DNS-01 向公共 CA 申请。每个产品域名一张通配符证书。
- SAN 中的名称始终是规范 FQDN 加上已登记的重定向名称，绝不包含遗留名称。

## 8. 提供商与出站流量

- 外部供应商是目录 ID（`<vendor>.<service>`），绝不是内部 FQDN。
- 访问供应商的出站流量经由所属能力（LLM 提供商经由 `gateway.ai.corp`，网络经由 `mesh.net.shared` 出站组）。
- 提供商机密存放在**使用方**能力的路径下（见[条目与字段](03-secrets-conventions.md#4-条目与字段)）。

## 9. 命名流程

- **步骤 A：登记 (intake)。** 按以下顺序确定维度：平面、域、能力、产品、环境，然后是所有者、层级、scope、data_class 和 exposure。
- **步骤 B：编码。** 先推导 FQDN（[DNS 语法](#3-dns两种语法别无其他)），再推导应用名和主机名（[对象形式](#5-对象形式)），然后是各类别的特定形式。先在目录中登记，再创建 DNS 记录。
- **步骤 C：身份与机密。** 创建组和机器角色（[身份规范](04-identity-conventions.md)），以及机密路径（[机密规范](03-secrets-conventions.md)）。
- **步骤 D：可观测性。** 将 `service.name` 设为应用名，将仪表板文件夹设为 `<plane>-<domain>`。

## 10. 拒绝规则（出现以下情况时拒绝该名称）

| 问题特征 | 违反的规则 |
|---|---|
| 产品作为最左侧标签 | [语法 A：内部](#31-语法-a内部) |
| 名称中包含暴露范围或层级（`admin.`、`public.`、`t0-`） | [语法 A：内部](#31-语法-a内部)、[十个元数据键](#2-十个元数据键) |
| 生产 DNS 名称中包含环境 | [语法 A：内部](#31-语法-a内部) |
| 主机、schema、存储桶或机密路径中缺少环境 | [对象形式](#5-对象形式)、[路径语法](03-secrets-conventions.md#3-路径语法) |
| 供应商作为内部 FQDN | [提供商与出站流量](#8-提供商与出站流量) |
| 通过路径在一个 FQDN 上承载两个能力 | [单一基础 URL](#6-单一基础-url) |
| 仓库目录作为名称 | [不存在语法 C](#33-不存在语法-c) |
| DNS 或 k8s 中出现 `_` | [字符规则](#1-字符规则适用于所有类别) |
| 能力代码被赋予第二种含义重复使用 | [能力代码](#43-能力代码在所有域中唯一) |
| 为“特殊”情况创建新语法 | [不存在语法 C](#33-不存在语法-c) |
| 标签值中包含用户、主机名、IP、机密或客户 | [标签与标记](05-labels-and-tags.md) |
| 资源缺少 `cost-center`、`owner`、`env`、`capability` 标签 | [标签与标记](05-labels-and-tags.md) |
| 以产品而非 capability 作为成本维度 | [标签与标记](05-labels-and-tags.md) |
| 代码托管实例没有所有组织可见的 `default` 运行器 | [标签与标记](05-labels-and-tags.md) |
| 在实例级别注册 `sock` 或 `host` CI 运行器 | [标签与标记](05-labels-and-tags.md) |
| 以提交哈希或构建号作为 Kubernetes 标签 | [标签与标记](05-labels-and-tags.md) |
| 将标签用作授权依据 | [标签与标记](05-labels-and-tags.md) |
| 平面或域代码中含有连字符 | [连字符解析规则](#11-连字符解析规则) |
| 名称中含有所有者、范围或环境的限定，或用 `--` 作为限定分隔符 | [连字符解析规则](#11-连字符解析规则) |
| 基础设施即代码仓库名称中含有工具或站点（`ansible-roles`、`infra-onprem`） | [对象形式](#5-对象形式) |
| 一个基础设施即代码仓库中有两个域 | [对象形式](#5-对象形式) |
| `mess.systems` 下语法 A 和 B 之外的公共名称，且未在 `catalog/dns-exceptions.yaml` 中登记 | [语法 B：公共](#32-语法-b公共) |
| 品牌的第三个公共子区域 | [语法 B：公共](#32-语法-b公共) |
| 不在 `catalog/sites.yaml` 中的站点代码，或含有城市、地址或提供商的站点代码 | [环境与站点](#44-环境与站点) |

## 11. 编码示例

| 登记信息 (intake) | FQDN | 应用 | 主机 |
|---|---|---|---|
| shared / iam / sso / Keycloak / prd | `sso.iam.shared.svc.mess.systems` | `shared-iam-keycloak` | `dc1-shared-iam-keycloak-prd-01` |
| eng / sdlc / git / Gitea / prd | `git.sdlc.eng.svc.mess.systems` | `eng-sdlc-gitea` | `dc1-eng-sdlc-gitea-prd-01` |
| corp / ai / gateway / agentgateway / prd | `gateway.ai.corp.svc.mess.systems` | `corp-ai-agentgateway` | `dc1-corp-ai-agentgateway-prd-01` |
| corp / ai / gateway / agentgateway / stg | `gateway.ai.corp.stg.svc.mess.systems` | `corp-ai-agentgateway` | `dc1-corp-ai-agentgateway-stg-01` |
| platform / data / docstore / MongoDB / prd | `docstore.data.platform.svc.mess.systems` | `platform-data-mongodb` | `dc1-platform-data-mongodb-prd-01..03` |
| shared / net / mesh / NetBird / prd | `mesh.net.shared.svc.mess.systems` | `shared-net-netbird` | `dc1-shared-net-netbird-prd-01` |
| ext / demo portal | `demo.apps.mess.systems` | `ext-gov-demo-portal` | `cld-ext-gov-portal-prd-01` |
| shopfront (product) / app | `app.shopfront.x.mess.systems` | `shopfront-api` | `cld-shopfront-api-prd-01` |

网状网络协调器还有一个公共专用名称 `netbird.mess.systems`，登记在 `catalog/dns-exceptions.yaml` 中（[语法 B：公共](#32-语法-b公共)）。
