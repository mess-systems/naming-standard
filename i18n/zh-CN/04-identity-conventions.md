[English](../../04-identity-conventions.md) | [Русский](../ru/04-identity-conventions.md) | **简体中文**

> **译文说明。** 本文为标准 v2.7 版本的译文，源提交 `a60b331`（含链接编辑修订）。英文文本为规范性文本：如有任何不一致，以英文版本为准。

# 身份规范：人员、智能体、服务账号、组、角色

> **状态：** v2，持续演进中。将四级特权访问模型（T0 至 T3）与[命名规范](01-naming-conventions.md)中的使用方和平面规则相结合。
> **与产品无关。** 规则适用于各类系统：身份提供方 (IdP)、机密管理器、网状 VPN (mesh VPN)、工作负载身份 ([SPIFFE](https://spiffe.io/docs/latest/spiffe-about/overview/))、Kubernetes RBAC、数据库角色、LLM/MCP 网关客户端、容器镜像仓库机器人账号、Git 托管平台和 CI 令牌。示例中提到的产品（Keycloak、OpenBao/Vault、SPIRE、Harbor、Gitea、Jenkins、Grafana 等）只是可互换的示意。
> **一个身份，一个 ID，处处通用。** 同一个字符串同时是 IdP 用户名、机密管理器的策略和机器角色、`x-user-id`、数据库角色（使用 `_`）以及 OTel `service.name`。

## 1. 所采用的原则

| # | 规则 |
|---|---|
| I1 | **类型在 ID 中可见。** 人员、管理员、紧急访问账号、服务账号、智能体、工作负载使用不同的前缀，因为它们的生命周期、凭据和审计需求各不相同 |
| I2 | **智能体 (agent) 不是服务账号。** 智能体自主行动，且常常代表某个人行动；它拥有自己的类型、自己的机密节点（[路径语法](03-secrets-conventions.md#3-路径语法)）以及必填的 `operator`（为其负责的人） |
| I3 | **组授予权限，名称只作描述。** DNS 标签、主机名、路径绝不授予任何权限（[语法 A：内部](01-naming-conventions.md#31-语法-a内部)） |
| I4 | **只有三种组前缀**：`tier-`（特权层级）、`role-`（职能）、`app-`（对单个能力的访问）。具体程度从 tier 到 role 再到 app 递增 |
| I5 | T0/T1 工作使用**独立的管理员账号**（`<handle>-adm`），绝不使用日常账号 |
| I6 | **紧急访问 (break-glass) 是账号，而不是共享密码**：`breakglass-<capability>-<NN>`，密封保存、触发告警、每次使用后轮换 |
| I7 | **服务账号 = 应用。** `svc-<plane>-<domain>-<product>`；每个实例一个，如有多个环境则每个环境一个 |
| I8 | **工作负载身份采用 [SPIFFE](https://github.com/spiffe/spiffe/blob/main/standards/SPIFFE-ID.md)**，路径对应能力，信任域是公司而不是 DNS 区域 |
| I9 | **每个身份都有 `owner` 和 `expires`**（或经论证的 `expires: none`）。审查周期：t0 每月，t1 每季度，其余每半年 |
| I10 | **名称使用小写 kebab 风格**；仅在存储系统禁止 `-` 时使用 `_`（Postgres、ClickHouse、环境变量） |

## 2. 身份类型

| 类型 | ID 形式 | 示例 | 凭据 | 所在位置 |
|---|---|---|---|---|
| 人员 | `<first>.<last>` 或简短用户名 (handle) | `jdoe` | 密码 + WebAuthn | IdP |
| 人员管理员账号 | `<handle>-adm` | `jdoe-adm` | 仅 WebAuthn；无邮件/聊天 | IdP、层级组 |
| 紧急访问账号 | `breakglass-<capability>-<NN>` | `breakglass-sso-01` | 密封保存在 `<mount>/…/admin` 中的密码 | 系统本地 |
| 服务账号 | `svc-<plane>-<domain>-<product>[-<env>]` | `svc-eng-sdlc-jenkins` | AppRole / OIDC 客户端 / SPIFFE | IdP（机器用户）+ 机密管理器 |
| 智能体 | `agent-<name>` | `agent-code-review`、`agent-docs-writer` | AppRole，之后改用 SPIFFE；网关密钥 | 机密管理器、网关 `clients` |
| 人员工具 | `user-<handle>-<tool>` | `user-jdoe-ide` | 颁发给人员工具的网关密钥 | 仅网关 `clients` |
| 工作负载 | `spiffe://mess.systems/<plane>/<domain>/<capability>` | `spiffe://mess.systems/corp/ai/gateway` | [X.509-SVID](https://github.com/spiffe/spiffe/blob/main/standards/X509-SVID.md) | SPIRE |
| 节点 | `spiffe://mess.systems/node/<host>` | `spiffe://mess.systems/node/dc1-corp-ai-agentgateway-prd-01` | join 令牌 / 证明器 (attestor) | SPIRE |
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

`app-<capability>-<access>`，其中 access 为 `user`、`editor` 或 `admin`。

| 示例 | 授予权限 |
|---|---|
| `app-dashboards-admin` | 仪表板管理员（例如 Grafana） |
| `app-git-admin` | Git 托管平台站点管理员 |
| `app-gateway-user` | 可以调用 `gateway.ai.corp` |
| `app-warehouse-editor` | 数据仓库写入 |

预配工具的默认组如 `app-<name>-operators` 改为 `app-<capability>-admin`。带区域后缀的提供方（`grafana-public/-private/-admin`）予以取消：暴露范围由网状网络组表达（见[网状 VPN 组](#4-网状-vpn-组)），管理员权限由 `app-dashboards-admin` 表达。

### 3.4 产品访问组

应用组描述对企业轮廓中某个能力的访问。产品轮廓中的产品（[部署与租户](07-deployment-and-tenants.md)）没有能力，因此对它的访问用其产品代码描述。

| 形式 | 何时使用 | 示例 |
|---|---|---|
| `app-<product>-<access>` | 访问整个产品 | `app-arch-user` |
| `app-<product>-<service>-<access>` | 访问产品的某一个服务 | `app-arch-store-editor` |

- `<access>` 取自同一列表：`user`、`editor`、`admin`。
- 产品代码绝不等于[能力代码](01-naming-conventions.md#43-能力代码在所有域中唯一)，以使 `app-<code>-user` 只有一种解读；检查依据 `catalog/products.yaml` 进行。
- 产品代码是产品轮廓的代码，而不是供应商产品的名称，因此组名中拒绝供应商产品名称的规则依然有效。
- 产品客户（租户）的组绝不在员工 IdP 中创建；它们存在于产品的 IdP 中，并遵循[租户键](07-deployment-and-tenants.md#5-租户)。

## 4. 网状 VPN 组

| 组形式 | 包含 | 示例 |
|---|---|---|
| `zone-<plane>` | 该平面的资源（对等节点/路由） | `zone-shared`、`zone-corp`、`zone-eng`、`zone-platform`、`zone-ext` |
| `tier-*`、`role-*` | 从 IdP 同步的人员对等节点 | `role-developers` |
| `svc-<application>` | 服务对等节点 | `svc-eng-sdlc-jenkins` |
| `egress-<plane>` | 出站网关 | `egress-corp` |
| `site-<code>` | 位置 | `site-dc1`、`site-cld` |
| `router-<site>` | 进入站点网络的路由对等节点，用于没有网状网络代理的设备 | `router-dc1` |

路由器不是出站网关：出站网关让流量出到互联网，路由器让网状网络对等节点进入站点的本地网络。

策略：`<subject-group> -> <target-group>`，其中目标为 `zone-<plane>` 或更窄的 `svc-<application>`。典型的遗留映射：拥有全部访问权限的 `admins` 组改为 `tier-t0-superadmin`，`devs` 组改为 `role-developers`，临时性的标签式组改为对应的 `tier-*` 或 `role-*` 组。

### 4.1 网状网络策略、规则与状态检查

| 对象 | 形式 | 示例 |
|---|---|---|
| 策略 | `<subject-group> -> <target-group>`（ASCII 箭头，两侧各一个空格） | `role-platform-engineers -> svc-shared-data-postgres` |
| 按协议拆分的策略 | 上述形式 + ` (<protocol>)` | `role-developers -> svc-shared-net-dns (udp)` |
| 策略内的规则 | 端口的 [IANA 服务名称](https://www.iana.org/assignments/service-names-port-numbers/)；多个名称用 `-` 连接 | `postgresql`、`https`、`ssh`、`ssh-https` |
| 无 IANA 名称的端口，或不提供其 IANA 服务的端口的规则 | `<protocol>-<port>` | `tcp-9100`、`tcp-8200` |
| 状态检查（posture check） | `posture-<what>-<condition>` | `posture-client-current`、`posture-os-supported` |

- 每对组一个策略。只有当网状网络产品每条规则只允许一种协议而该组对需要两种时，才使用协议后缀。
- 方向是规则的属性（默认单向），不是名称的一部分。
- 内置策略 `Default` 保留其产品名称并被停用。任何策略都不以内置的 `All` 组作为主体或目标。

### 4.2 网状网络的网络、资源与密钥

| 对象 | 形式 | 示例 |
|---|---|---|
| 站点网络 | `site-<site>`（与站点组相同） | `site-dc1` |
| 网络资源：单台主机 | 主机名（[对象形式](01-naming-conventions.md#5-对象形式)） | `dc1-shared-net-dns-prd-01` |
| 网络资源：多台主机上的服务 | `<site>-<application>` | `dc1-shared-net-dns` |
| 网络资源：子网 | `<site>-<plane>-<purpose>` | `dc1-shared-mgmt` |
| 设置密钥（setup key） | 为其签发的主机名；一次性 | `dc1-shared-data-postgres-prd-01` |
| 一组机器的设置密钥（仅限临时对等节点） | `<application>-<env>-ephemeral` | `platform-build-ci-runner-prd-ephemeral` |
| 用于基础设施即代码的网状网络服务用户 | `svc-<iac-repo>`（[对象形式](01-naming-conventions.md#5-对象形式)） | `svc-shared-net-iac` |

地址、子网和 VLAN 编号绝不进入网状网络对象的名称；它们存放在资源描述和清单中。

### 4.3 网状网络 DNS

| 对象 | 形式 | 示例 |
|---|---|---|
| 名称服务器组（nameserver group） | 区域中的点替换为连字符，再加站点 | `svc-mess-systems-dc1` |
| 搜索域 | 仅 `svc.mess.systems`；不设按站点的搜索域 | `svc.mess.systems` |

## 5. 所有者

`owner` 元数据（见[元数据键](01-naming-conventions.md#2-十个元数据键)）始终是一个**组**，绝不是个人：`role-platform-engineers`、`role-data-engineers`、`tier-t0-superadmin`。智能体的 `operator` 是例外（是一个人）。

## 6. IdP 对象

| 对象 | 名称 | 示例 |
|---|---|---|
| 应用 slug | `<application>`（[对象形式](01-naming-conventions.md#5-对象形式)） | `shared-obs-grafana` |
| 应用显示名称 | 产品名称 | `Grafana` |
| 提供方 (provider) | `<application>-<protocol>` | `shared-obs-grafana-oidc`、`eng-sdlc-gitea-oidc` |
| 属性映射 / scope | `<application>-<claim>` | `shared-obs-grafana-groups` |
| Outpost | `outpost-<plane>-<capability>` | `outpost-shared-ingress` |
| 流程 (flow) | `flow-<purpose>` | `flow-admin-webauthn` |
| 身份源（联合） | `src-<vendor>` | `src-github` |
| 员工 IdP 的 realm（或租户） | `<org>`，每个组织一个 | `mess-systems` |
| 产品 IdP 的 realm | `<product>-<env>` | `arch-prd`、`arch-stg` |
| 智能体的 OIDC 客户端 | 智能体 ID | `agent-code-review` |
| 人员工具（CLI 智能体、IDE）的 OIDC 客户端 | 该工具的账号 ID | `user-jdoe-cursor` |
| 目标服务的令牌受众（audience） | 目标服务的应用 | `shared-data-postgres`、`corp-infra-kubernetes-mcp-server` |

对象类型参照常见 IdP（Keycloak、Entra ID、Okta……）；请将其映射到您所用产品中的对应概念。

- 人员工具（`user-<handle>-<tool>`）代表某个人行事，使用此人的组并加以收窄。智能体（`agent-<name>`）自行行事，并有一名操作员。选择取决于由谁发起操作，而不是工具产品。
- 在令牌交换（[RFC 8693](https://www.rfc-editor.org/rfc/rfc8693)）中，主体是人员，行为者（`act`）是工具或智能体的客户端，按上表命名。

以产品命名的遗留 slug（`grafana`、`argocd`）改为应用形式（`shared-obs-grafana`、`eng-sdlc-argocd`）。重定向 URI 只使用规范 FQDN（见[单一基础 URL](01-naming-conventions.md#6-单一基础-url)）。

## 7. 机密管理器（OpenBao / Vault）

策略 = 身份 ID；AppRole = 身份 ID；JWT 角色 = 组 ID。完整规则见机密规范中的[策略](03-secrets-conventions.md#5-策略)和[认证角色与令牌](03-secrets-conventions.md#6-认证角色与令牌)两节。

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
| `spiffe://corp.lan/node/vm042` | `spiffe://mess.systems/node/dc1-corp-ai-agentgateway-prd-01` |
| `spiffe://corp.lan/node/ws-jdoe-01` | `spiffe://mess.systems/node/std-lt-a1b2c3`（[终端名称](06-endpoint-conventions.md)，绝不使用用户名；仅限经过证明的完全托管设备；BYOD 没有节点身份） |

智能体：`spiffe://mess.systems/corp/ai/agent-<name>`。路径遵循**能力代码**，绝不遵循仓库目录。

产品轮廓为 prod、non-prod 和沙箱分别设有信任域；见 [07 SPIFFE](07-deployment-and-tenants.md)。

## 9. 网关客户端身份

`corp/ai/gateway/prd/clients` 中的键名和 `x-user-id` 请求头均为[身份类型](#2-身份类型)中的身份 ID。

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

| 对象 | 形式 | 遗留与目标（示意） |
|---|---|---|
| ServiceAccount | `svc-<workload>` | `ci` 改为 `svc-ci` |
| 面向人员的 Role / ClusterRole | `<group>-<scope>-<access>` | `view-all` 改为 `role-developers-cluster-ro`；`sandbox-viewer` 改为 `role-developers-sandbox-ro` |
| 面向 SA 的 Role | `<sa>-<scope>-<access>` | `ci-read` 改为 `svc-ci-workload-ro`；`ci-gitops` 改为 `svc-ci-gitops-rw` |
| RoleBinding | `<role>--<subject>` | `role-developers-sandbox-ro--role-developers` |
| GitOps 项目（例如 Argo CD） | `<plane>` 或 `<product>` | `default` 改为 `eng`，产品应用 改为 `<product>` |
| 标签 | `mess.systems/plane`、`mess.systems/owner`…… | |

RBAC 主体取自 OIDC 组声明，直接使用 `tier-*` 和 `role-*` 组，不做改动。

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

### 11.1 临时数据库用户

临时数据库用户由机密管理器的 database 引擎签发（[kv 以外的引擎](03-secrets-conventions.md#21-kv-以外的引擎)）。名称说明了访问是如何、由谁、以哪个角色、在何时获得的，因此无需机密管理器的审计日志即可读懂数据库日志中的一行，而审计日志可以加以确认。

```
v_<auth>_<identity>_<role>_<ts>_<rand6>
```

| 部分 | 含义 | 示例 |
|---|---|---|
| `v_` | 标记临时用户 | `v_` |
| `<auth>` | 请求者登录机密管理器的方式，取自下表的代码 | `oidc` |
| `<identity>` | 人员、工具或智能体的 ID（[身份类型](#2-身份类型)），其中 `-` 替换为 `_` | `jdoe`、`user_jdoe_cursor`、`agent_code_review` |
| `<role>` | 该用户所属的 `NOLOGIN` 数据库角色 | `eng_sdlc_git_ro` |
| `<ts>` | UTC 签发时间，`YYYYMMDDtHHMMSSz`，与[快照](08-operations-objects.md#3-备份与快照)相同 | `20261031t020000z` |
| `<rand6>` | 6 个 `[a-z0-9]` 字符 | `k7m2qa` |

| 认证挂载点（[挂载点](03-secrets-conventions.md#2-挂载点)） | `<auth>` |
|---|---|
| `auth/jwt-<idp>`（通过 OIDC 认证的人员和 CI） | `oidc` |
| `auth/jwt-spire` | `spire` |
| `auth/kubernetes-<cluster>` | `k8s` |
| `auth/approle` | `approle` |

- 仅使用 `[a-z0-9_]`，因此名称在 SQL 中无需加引号，与其他数据库角色名称相同。
- 最多 63 个字符（PostgreSQL 的限制）。当 `<auth>` = `oidc` 时，固定部分占 32 个字符，`<identity>` 和 `<role>` 合计剩余 31 个（`approle` 为 28 个）。
- 名称放不下时缩短 `<identity>`；角色、时间和随机部分绝不缩短。拒绝对完成后的整个名称截断（`truncate 63`），因为这会截掉时间和随机部分。
- 临时用户绝不拥有对象，也绝不获得 DDL 权限；DDL 通过流水线以 `<…>_owner` 角色执行。
- 示例：`v_oidc_jdoe_eng_sdlc_git_ro_20261031t020000z_k7m2qa`（51 个字符）、`v_oidc_user_jdoe_cursor_eng_sdlc_git_ro_20261031t020000z_k7m2qa`（63 个）。

OpenBao 模板（连接的 `username_template`），适用于 `user_claim = preferred_username` 的 `auth/jwt-keycloak`：

```
{{ printf "v_%s_%s_%s_%s" (.DisplayName | replace "jwt-keycloak-" "oidc-" | replace "-" "_" | truncate 21) (.RoleName) (timestamp "20060102t150405z") (random 6 | lowercase) }}
```

`truncate 21`（`oidc_` 加 16 个 `<identity>` 字符）适用于最长 15 个字符的角色；更长的角色需要更小的数字。请在测试连接上检查模板：数据库日志中的时间必须与审计日志中的 UTC 签发时间一致。

与 OpenBao 默认模板（`v-%s-%s-%s-%s`，带 `random 20`、`unix_time`，并对整个名称使用 `truncate 63`）的比较：

| 属性 | 默认模板 | 本标准 |
|---|---|---|
| 认证方式 | 由挂载点前缀推出 | 取自表中的代码 |
| 时间 | Unix 时间，10 位数字，位于末尾 | UTC `YYYYMMDDtHHMMSSz`，位于随机部分之前：可读且可排序 |
| 分隔符 | `-`，在 SQL 中需要引号 | `_`，与其他数据库角色名称相同 |
| 随机部分 | 20 个字符，大小写混合 | 6 个 `[a-z0-9]` 字符；时间加随机部分使名称唯一 |
| 超过 63 | 名称末尾连同时间和随机部分被截掉 | 缩短 `<identity>` |

## 12. 令牌、机器人账号、凭据 ID

| 系统 | 形式 | 示例 |
|---|---|---|
| 镜像仓库机器人账号（例如 Harbor） | `robot$<project>+<consumer-id>` | `robot$corp-ai+svc-eng-sdlc-jenkins` |
| Git 托管平台令牌 / 部署密钥 | `<consumer-id>`（+ `--<purpose>`） | `svc-eng-sdlc-jenkins--clone` |
| CI 凭据 ID | 机密路径，其中 `/` 替换为 `-` | `eng-sdlc-ci-prd-packages` |
| 软件包仓库令牌 | `<consumer-id>` | `svc-eng-sdlc-jenkins` |
| 仪表板服务账号 | `svc-<application>` | `svc-corp-ai-agentgateway` |
| SSH 密钥注释 | `<identity-id>@<host>` | `jdoe-adm@dc1-shared-infra-kvm-prd-01` |

## 13. 生命周期

| 事件 | 规则 |
|---|---|
| 创建 | 登记（[命名流程](01-naming-conventions.md#9-命名流程)），然后依次确定身份类型、组、机密管理器策略和角色，并创建带有 `owner` 和 `expires` 的目录条目 |
| 轮换 | 按 `custom_metadata.rotation` 执行；智能体和工具 90d；服务账号 365d；紧急访问账号每次使用后轮换 |
| 审查 | t0 每月，t1 每季度，t2/t3 每半年；智能体与其操作员一起审查 |
| 离职 / 退役 | 按以下顺序：在 IdP 中停用，吊销 AppRole secret-id，删除数据库角色，删除网关客户端字段，关闭目录条目。ID 绝不复用 |

## 14. 拒绝规则

- 组没有使用三种前缀之一；出现第四种前缀。
- 层级和角色混在一个组名中（`platform-admins`）。
- 组名中包含产品名（`grafana-admins`；应使用 `app-dashboards-admin`）。
- 组名或提供方名称中包含暴露范围（`-public`、`-private`、`-admin` 提供方）。
- 智能体注册为 `svc-*`，或人员工具注册为智能体。
- 策略/AppRole/JWT 角色名称不是身份 ID 或组 ID。
- 个人 ID 用于自动化，或 `-adm` 账号开通了邮件/聊天。
- 共享账号使用共享密码（应使用紧急访问账号）。
- 在数据库角色/环境变量之外的 ID 中使用下划线。
- 网状网络组不符合[网状 VPN 组](#4-网状-vpn-组)的形式（`admins`、`servers`、`vpn-users`）。
- 网状网络策略以内置的 `All` 组作为主体或目标（[网状网络策略](#41-网状网络策略规则与状态检查)）。
- 网状网络对象名称中含有地址、子网或 VLAN 编号（[网状网络的网络、资源与密钥](#42-网状网络的网络资源与密钥)）。
- 产品代码等于能力代码（[产品访问组](#34-产品访问组)）。
- 临时数据库用户不符合[临时数据库用户](#111-临时数据库用户)的形式（没有认证代码或时间、使用 `-`、整体截断到 63），或拥有 DDL 权限。
