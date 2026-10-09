[English](../../04-identity-conventions.md) | [Русский](../ru/04-identity-conventions.md) | **简体中文**

> **译文说明。** 本文为标准 v2 版本的译文，源提交 `b6791c2`。英文文本为规范性文本：如有任何不一致，以英文版本为准。

# 身份规范——人员、智能体、服务账号、组、角色

> **状态：** v2，持续演进中。将四级特权访问模型（T0–T3）与 [01](01-naming-conventions.md) 中的使用方和平面规则相结合。
> **与产品无关。** 规则适用于各类系统：身份提供方 (IdP)、机密管理器、网状 VPN (mesh VPN)、工作负载身份 (SPIFFE)、Kubernetes RBAC、数据库角色、LLM/MCP 网关客户端、容器镜像仓库机器人账号、Git 托管平台和 CI 令牌。示例中提到的产品（Keycloak、OpenBao/Vault、SPIRE、Harbor、Gitea、Jenkins、Grafana……）只是可互换的示意。
> **一个身份，一个 ID，处处通用。** 同一个字符串同时是 IdP 用户名、机密管理器的策略和机器角色、`x-user-id`、数据库角色（使用 `_`）以及 OTel `service.name`。

## 1. 所采用的原则

| # | 规则 |
|---|---|
| I1 | **类型在 ID 中可见。** 人员、管理员、紧急访问账号、服务账号、智能体、工作负载使用不同的前缀，因为它们的生命周期、凭据和审计需求各不相同 |
| I2 | **智能体 (agent) 不是服务账号。** 智能体自主行动，且常常代表某个人行动；它拥有自己的类型、自己的机密节点（[03](03-secrets-conventions.md) §3）以及必填的 `operator`（为其负责的人） |
| I3 | **组授予权限，名称只作描述。** DNS 标签、主机名、路径绝不授予任何权限（01 §3.1） |
| I4 | **只有三种组前缀**：`tier-`（特权层级）、`role-`（职能）、`app-`（对单个能力的访问）。按具体程度：tier ⊂ role ⊂ app |
| I5 | T0/T1 工作使用**独立的管理员账号**（`<handle>-adm`），绝不使用日常账号 |
| I6 | **紧急访问 (break-glass) 是账号，而不是共享密码**：`breakglass-<capability>-<NN>`，密封保存、触发告警、每次使用后轮换 |
| I7 | **服务账号 = 应用。** `svc-<plane>-<domain>-<product>`；每个实例一个，如有多个环境则每个环境一个 |
| I8 | **工作负载身份采用 SPIFFE**，路径对应能力，信任域是公司而不是 DNS 区域 |
| I9 | **每个身份都有 `owner` 和 `expires`**（或经论证的 `expires: none`）。审查周期：t0 每月，t1 每季度，其余每半年 |
| I10 | **名称使用小写 kebab 风格**；仅在存储系统禁止 `-` 时使用 `_`（Postgres、ClickHouse、环境变量） |

## 2. 身份类型

| 类型 | ID 形式 | 示例 | 凭据 | 所在位置 |
|---|---|---|---|---|
| 人员 | `<first>.<last>` 或简短用户名 (handle) | `jdoe` | 密码 + WebAuthn | IdP |
| 人员管理员账号 | `<handle>-adm` | `jdoe-adm` | 仅 WebAuthn；无邮件/聊天 | IdP、层级组 |
| 紧急访问账号 | `breakglass-<capability>-<NN>` | `breakglass-sso-01` | 密封保存在 `<mount>/…/admin` 中的密码 | 系统本地 |
| 服务账号 | `svc-<plane>-<domain>-<product>[-<env>]` | `svc-eng-sdlc-jenkins` | AppRole / OIDC 客户端 / SPIFFE | IdP（机器用户）+ 机密管理器 |
| 智能体 | `agent-<name>` | `agent-code-review`、`agent-docs-writer` | AppRole → SPIFFE；网关密钥 | 机密管理器、网关 `clients` |
| 人员工具 | `user-<handle>-<tool>` | `user-jdoe-ide` | 颁发给人员工具的网关密钥 | 仅网关 `clients` |
| 工作负载 | `spiffe://mess.systems/<plane>/<domain>/<capability>` | `spiffe://mess.systems/corp/ai/gateway` | X.509-SVID | SPIRE |
| 节点 | `spiffe://mess.systems/node/<host>` | `spiffe://mess.systems/node/dc1-corp-ai-litellm-prd-01` | join 令牌 / 证明器 (attestor) | SPIRE |
| 外部 (B2B) | `ext-<org>-<handle>` | `ext-acme-jdoe` | 通过 `b2b.iam.shared` 联合认证 | IdP 身份源 |

智能体在其目录条目中记录 `operator: <human>` 和 `scope: <capability list>`；网关强制要求 `x-user-id = <agent id>` 和 `x-session-id`。

## 3. 组

### 3.1 层级组（特权）

| 组 | 层级 | 成员 | 可访问范围 |
|---|---|---|---|
| `tier-t0-superadmin` | T0 | 1–2 个 `-adm` 账号 | 一切资源、`admin` 条目，并触发告警 |
| `tier-t1-platform-ops` | T1 | 平台工程师和安全工程师的 `-adm` 账号 | `shared/`、`platform/`、`eng/` 的控制界面 |
| `tier-t2-developer` | T2 | 工程师的日常账号 | `eng/`、产品平面、非生产环境 |
| `tier-t3-readonly` | T3 | 观察者、审计员、默认情况下的智能体 | 列出/读取仪表板、目录 |

### 3.2 角色组（职能）

| 组 | 用途 |
|---|---|
| `role-platform-engineers` | 运行共享控制平面和平台控制平面 |
| `role-security-engineers` | 威胁检测、漏洞管理、身份卫生 |
| `role-developers` | 构建和交付产品 |
| `role-sre-observers` | 读取可观测性数据，负责告警 |
| `role-data-engineers` | 负责数据管道、数据仓库、目录 |
| `role-agent-operators` | 为智能体负责的人员 |

其他体系中的遗留特权组（`sg-*`、`*-admins`、`operators`）映射到语义相同的 `tier-*` 组；最终只保留一套前缀体系。

### 3.3 应用组（对单个能力的访问）

`app-<capability>-<access>`，access ∈ `user | editor | admin`。

| 示例 | 授予权限 |
|---|---|
| `app-dashboards-admin` | 仪表板管理员（例如 Grafana） |
| `app-git-admin` | Git 托管平台站点管理员 |
| `app-gateway-user` | 可以调用 `gateway.ai.corp` |
| `app-warehouse-editor` | 数据仓库写入 |

预配工具的默认组如 `app-<name>-operators` → `app-<capability>-admin`。带区域后缀的提供方（`grafana-public/-private/-admin`）予以取消；暴露范围由网状网络组（§4）表达，管理员权限为 `app-dashboards-admin`。

## 4. 网状 VPN 组

| 组形式 | 包含 | 示例 |
|---|---|---|
| `zone-<plane>` | 该平面的资源（对等节点/路由） | `zone-shared`、`zone-corp`、`zone-eng`、`zone-platform`、`zone-ext` |
| `tier-*`、`role-*` | 从 IdP 同步的人员对等节点 | `role-developers` |
| `svc-<application>` | 服务对等节点 | `svc-eng-sdlc-jenkins` |
| `egress-<plane>` | 出站网关 | `egress-corp` |
| `site-<code>` | 位置 | `site-dc1`、`site-cld` |

策略：`<subject-group> → <zone-group>`。典型的遗留映射：拥有全部访问权限的 `admins` 组 → `tier-t0-superadmin`；`devs` 组 → `role-developers`；临时性的标签式组 → 对应的 `tier-*` 或 `role-*` 组。

## 5. 所有者

`owner` 元数据（01 §2）始终是一个**组**，绝不是个人：`role-platform-engineers`、`role-data-engineers`、`tier-t0-superadmin`。智能体的 `operator` 是例外（是一个人）。

## 6. IdP 对象

| 对象 | 名称 | 示例 |
|---|---|---|
| 应用 slug | `<application>`（01 §5） | `shared-obs-grafana` |
| 应用显示名称 | 产品名称 | `Grafana` |
| 提供方 (provider) | `<application>-<protocol>` | `shared-obs-grafana-oidc`、`eng-sdlc-gitea-oidc` |
| 属性映射 / scope | `<application>-<claim>` | `shared-obs-grafana-groups` |
| Outpost | `outpost-<plane>-<capability>` | `outpost-shared-ingress` |
| 流程 (flow) | `flow-<purpose>` | `flow-admin-webauthn` |
| 身份源（联合） | `src-<vendor>` | `src-github` |

对象类型参照常见 IdP（Keycloak、Entra ID、Okta……）；请将其映射到您所用产品中的对应概念。

以产品命名的遗留 slug（`grafana`、`argocd`）→ 应用形式（`shared-obs-grafana`、`eng-sdlc-argocd`）。重定向 URI 只使用规范 FQDN（01 §6）。

## 7. 机密管理器（OpenBao / Vault）

策略 = 身份 ID；AppRole = 身份 ID；JWT 角色 = 组 ID。完整规则见 [03](03-secrets-conventions.md) §5–§6。

| 典型遗留 | 目标 |
|---|---|
| 策略 `admin` | `tier-t0-superadmin` |
| 策略 `ops` | `tier-t1-platform-ops` |
| 策略 `developers` | `tier-t2-developer` |
| 策略 `read-only` | `tier-t3-readonly` |
| AppRole `<app>` / 策略 `<app>-read` | `svc-<plane>-<domain>-<product>`（一个名称） |
| 以机器人命名的 AppRole / 策略 | `agent-<name>` |
| 策略 `registry-read`（一个他方条目） | `<identity-id>-<capability>-ro`（限定读取） |

## 8. SPIFFE / SPIRE

| 遗留（示意） | 目标 |
|---|---|
| 信任域 `spiffe://corp.lan` | `spiffe://mess.systems`（非生产：`spiffe://<env>.mess.systems`） |
| `spiffe://corp.lan/infra/llm-proxy`（仓库目录） | `spiffe://mess.systems/corp/ai/gateway` |
| `spiffe://corp.lan/apps/doc-converter` | `spiffe://mess.systems/corp/data/convert` |
| `spiffe://corp.lan/node/vm042` | `spiffe://mess.systems/node/dc1-corp-ai-litellm-prd-01` |
| `spiffe://corp.lan/node/ws-jdoe-01` | `spiffe://mess.systems/node/ws-jdoe-01`（工作站保留其名称——它不是服务主机） |

智能体：`spiffe://mess.systems/corp/ai/agent-<name>`。路径遵循**能力代码**，绝不遵循仓库目录。

## 9. 网关客户端身份

`corp/ai/gateway/prd/clients` 中的键名和 `x-user-id` 请求头均为 §2 中的身份 ID。

| 遗留字段（示意） | 目标 ID | 类型 |
|---|---|---|
| `codereview_bot` | `agent-code-review` | 智能体 |
| `docs_bot` | `agent-docs-writer` | 智能体 |
| `chat_ai` | `svc-corp-collab-mattermost` | 服务账号 |
| `tracing` | `svc-corp-ai-langfuse` | 服务账号 |
| `shopfront` | `svc-shopfront-api` | 产品服务账号 |
| `ide` | `user-jdoe-ide` | 人员工具 |

环境变量名：`GATEWAY_CLIENT_KEY_<ID_UPPER_SNAKE>`（`GATEWAY_CLIENT_KEY_AGENT_CODE_REVIEW`）。MCP 目标：能力代码（`convert`、`cmdb`、`archrepo`、`data-catalog`），供应商为 `<vendor>-<service>`（`acmesearch-web`）。

## 10. Kubernetes RBAC

| 对象 | 形式 | 遗留 → 目标（示意） |
|---|---|---|
| ServiceAccount | `svc-<workload>` | `ci` → `svc-ci` |
| 面向人员的 Role / ClusterRole | `<group>-<scope>-<access>` | `view-all` → `role-developers-cluster-ro`；`sandbox-viewer` → `role-developers-sandbox-ro` |
| 面向 SA 的 Role | `<sa>-<scope>-<access>` | `ci-read` → `svc-ci-workload-ro`；`ci-gitops` → `svc-ci-gitops-rw` |
| RoleBinding | `<role>--<subject>` | `role-developers-sandbox-ro--role-developers` |
| GitOps 项目（例如 Argo CD） | `<plane>` 或 `<product>` | `default` → `eng`，产品应用 → `<product>` |
| 标签 | `mess.systems/plane`、`mess.systems/owner`…… | |

OIDC 组声明 → RBAC 主体直接使用 `tier-*`/`role-*` 组，不做改动。

## 11. 数据库角色

形式：能力所属角色使用 `<plane>_<domain>_<capability>_<access>`（`ro | rw | owner`），使用方使用 `svc_<plane>_<domain>_<product>`，智能体使用 `agent_<name>`，本地管理员使用 `breakglass_<capability>`。

| 存储 | 遗留（示意） | 目标 |
|---|---|---|
| ClickHouse | `default` | 停用 |
| ClickHouse | `writer` | `corp_data_warehouse_rw` |
| ClickHouse | `readonly` | `corp_data_warehouse_ro` |
| ClickHouse | `bi`（BI 工具用户） | `svc_corp_data_superset` |
| MongoDB | `admin` | `breakglass_docstore` |
| MongoDB | `bot` | `agent_docs_writer` |
| Postgres | 按应用划分的用户（`my_app`） | `svc_<plane>_<domain>_<product>`；数据库 `<plane>_<domain>_<capability>_<env>` |

## 12. 令牌、机器人账号、凭据 ID

| 系统 | 形式 | 示例 |
|---|---|---|
| 镜像仓库机器人账号（例如 Harbor） | `robot$<project>+<consumer-id>` | `robot$corp-ai+svc-eng-sdlc-jenkins` |
| Git 托管平台令牌 / 部署密钥 | `<consumer-id>`（+ `--<purpose>`） | `svc-eng-sdlc-jenkins--clone` |
| CI 凭据 ID | 机密路径，`/`→`-` | `eng-sdlc-ci-prd-packages` |
| 软件包仓库令牌 | `<consumer-id>` | `svc-eng-sdlc-jenkins` |
| 仪表板服务账号 | `svc-<application>` | `svc-corp-ai-litellm` |
| SSH 密钥注释 | `<identity-id>@<host>` | `jdoe-adm@dc1-shared-infra-kvm-prd-01` |

## 13. 生命周期

| 事件 | 规则 |
|---|---|
| 创建 | 登记（01 §9）→ 身份类型 → 组 → 机密管理器策略/角色 → 带有 `owner`、`expires` 的目录条目 |
| 轮换 | 按 `custom_metadata.rotation` 执行；智能体和工具 90d；服务账号 365d；紧急访问账号每次使用后轮换 |
| 审查 | t0 每月，t1 每季度，t2/t3 每半年；智能体与其操作员一起审查 |
| 离职 / 退役 | 在 IdP 中停用 → 吊销 AppRole secret-id → 删除数据库角色 → 删除网关客户端字段 → 关闭目录条目。ID 绝不复用 |

## 14. 拒绝规则

- 组没有使用三种前缀之一；出现第四种前缀。
- 层级和角色混在一个组名中（`platform-admins`）。
- 组名中包含产品名（`grafana-admins` → `app-dashboards-admin`）。
- 组名或提供方名称中包含暴露范围（`-public`、`-private`、`-admin` 提供方）。
- 智能体注册为 `svc-*`，或人员工具注册为智能体。
- 策略/AppRole/JWT 角色名称不是身份 ID 或组 ID。
- 个人 ID 用于自动化，或 `-adm` 账号开通了邮件/聊天。
- 共享账号使用共享密码（应使用紧急访问账号）。
- 在数据库角色/环境变量之外的 ID 中使用下划线。
