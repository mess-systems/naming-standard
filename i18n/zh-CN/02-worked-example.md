[English](../../02-worked-example.md) | [Русский](../ru/02-worked-example.md) | **简体中文**

> **译文说明。** 本文为标准 v2 版本的译文，源提交 `b6791c2`。英文文本为规范性文本：如有任何不一致，以英文版本为准。

# 完整示例——迁移一个虚构组织

> **状态：** 示意性。此处一切均为虚构：组织、主机、服务和路径仅用于展示 [01](01-naming-conventions.md)、[03](03-secrets-conventions.md) 和 [04](04-identity-conventions.md) 如何协同应用。
> **域名替换：** 本标准使用组织域名 `mess.systems`。本示例使用 **`northwind.example`**（RFC 2606/6761 保留域名），以说明公司域名只是一个参数：`svc.mess.systems` 变为 `svc.northwind.example`，`spiffe://mess.systems` 变为 `spiffe://northwind.example`，依此类推。

## 1. 背景

Northwind Traders 在其办公室的双节点虚拟化平台上运行约十几个服务（站点 `hq`），另在公有云中有一台虚拟机（站点 `cld`）。五年来积累了这样一些名称：

- `grafana.corp.lan`、`grafana-admin.corp.lan`——名称中包含产品名和暴露范围；
- `git.corp.lan` 和 `gitea.corp.lan`——同一个实例有两个名称；
- `vm042`、`srv-old-2`、`docker1`——毫无含义的主机名；
- `*.int.corp.lan` 与 `*.corp.lan`——一个“内部”子区域，实际上是一条访问规则；
- 机密管理器只有一个挂载点 `secret/`，路径有的按供应商、有的按产品、有的按人员划分。

`.lan` 不是保留的顶级域，无法获得公共 CA 证书，因此目标内部区域是 `svc.northwind.example`（水平分割 DNS，不对外公开委派）。

## 2. 区域

| 区域 | 目标 | 语法 |
|---|---|---|
| 内部服务 | `svc.northwind.example` | A |
| 管理主机 | `mgmt.northwind.example` | 主机名，而非能力 |
| 公共 ext | `apps.northwind.example` | B，品牌作为产品 |
| 品牌 | `www.northwind.example` | B |
| 产品 | `app.shopfront.example` | B |

## 3. 服务——登记与编码

登记 (intake) 遵循 01 §9：平面 → 域 → 能力 → 产品 → 环境。此处所有服务都是生产环境，因此语法 A 省略环境，而主机、schema 和机密中写出 `prd`。

| 遗留名称 | 登记信息 (plane / domain / capability / product) | 目标 FQDN | 应用 | 所有者 |
|---|---|---|---|---|
| `grafana.corp.lan`、`grafana-admin.corp.lan` | shared / obs / dashboards / Grafana | `dashboards.obs.shared.svc.northwind.example` | `shared-obs-grafana` | `role-sre-observers` |
| `prometheus.corp.lan` | shared / obs / metrics / Prometheus | `metrics.obs.shared.svc.northwind.example` | `shared-obs-prometheus` | `role-sre-observers` |
| `keycloak.int.corp.lan` | shared / iam / sso / Keycloak | `sso.iam.shared.svc.northwind.example` | `shared-iam-keycloak` | `tier-t1-platform-ops` |
| `vault.int.corp.lan` | shared / iam / secrets / OpenBao | `secrets.iam.shared.svc.northwind.example` | `shared-iam-openbao` | `tier-t0-superadmin` |
| `git.corp.lan`、`gitea.corp.lan` | eng / sdlc / git / Gitea | `git.sdlc.eng.svc.northwind.example` | `eng-sdlc-gitea` | `role-platform-engineers` |
| `jenkins.corp.lan` | eng / sdlc / ci / Jenkins | `ci.sdlc.eng.svc.northwind.example` | `eng-sdlc-jenkins` | `role-platform-engineers` |
| `registry.corp.lan` | eng / sdlc / oci / Harbor | `oci.sdlc.eng.svc.northwind.example` | `eng-sdlc-harbor` | `role-platform-engineers` |
| `pg01.corp.lan` | shared / data / sql / PostgreSQL | `sql.data.shared.svc.northwind.example` | `shared-data-postgres` | `role-platform-engineers` |
| `chat.corp.lan` | corp / collab / chat / Mattermost | `chat.collab.corp.svc.northwind.example` | `corp-collab-mattermost` | `role-platform-engineers` |
| `wiki.corp.lan` | corp / collab / wiki / Wiki.js | `wiki.collab.corp.svc.northwind.example` | `corp-collab-wikijs` | `role-developers` |
| `llm.corp.lan`、`llm-ui.corp.lan` | corp / ai / gateway / LiteLLM | `gateway.ai.corp.svc.northwind.example`（UI = 路径 `/ui`） | `corp-ai-litellm` | `role-agent-operators` |
| `demo.corp.lan`（公共） | ext / gov / demo / demo portal | `demo.apps.northwind.example` | `ext-gov-demo-portal` | `role-developers` |

过程中做出的决定：

- `grafana-admin` 不是第二个名称。管理员访问权限改为组 `app-dashboards-admin`（04 §3.3）；FQDN 保持唯一（01 §3.1、§6）。
- `gitea.corp.lan` 改为指向规范 FQDN 的 90 天重定向，之后删除（01 §6）。
- `*.int.corp.lan` 编码的是暴露范围。所有名称都迁移到语法 A；谁可以访问由网状网络/IdP 组决定（04 §4）。
- LLM 的 UI 是网关上的一个路径，而不是第二个 FQDN（一个实例 → 一个名称）。

## 4. 主机

形式：`<site>-<plane>-<domain>-<product>-<env>-<NN>`（01 §5）。管理接口位于 `mgmt.northwind.example` 下。

| 遗留主机 | 运行内容 | 目标主机 |
|---|---|---|
| `hv1`、`hv2` | 虚拟化平台节点 | `hq-shared-infra-pve-prd-01`、`hq-shared-infra-pve-prd-02` |
| `vm042` | Grafana + Prometheus | `hq-shared-obs-grafana-prd-01`（Prometheus 是同一主机上的第二个应用） |
| `srv-old-2` | Gitea | `hq-eng-sdlc-gitea-prd-01` |
| `docker1` | Jenkins | `hq-eng-sdlc-jenkins-prd-01` |
| `pg01` | PostgreSQL | `hq-shared-data-postgres-prd-01` |
| `cloud-vm-1` | 演示门户 | `cld-ext-gov-portal-prd-01` |
| `ws-jdoe-01` | 一台工作站 | 不变——工作站不是服务主机 |

## 5. 机密与身份

每个平面一个挂载点，取代 `secret/`（03 §2）：

| 遗留（`secret/`） | 目标 | 规则 |
|---|---|---|
| `grafana/oidc` | `shared/obs/dashboards/prd/oidc` | 用能力而不是产品（03 §9） |
| `postgres/root` | `shared/data/sql/prd/admin` | 紧急访问条目，仅限 t0（03 S6） |
| `jenkins/registry` | `eng/sdlc/ci/prd/oci` | 使用方副本，以其所解锁的能力命名 |
| `llm/acmeai` | `corp/ai/gateway/prd/provider-acmeai` | 供应商是条目，不是节点（03 S4） |
| `users/jdoe/*` | **拒绝** | 个人机密存放在密码管理器中（03 S5） |

身份与组（04）：

| 遗留 | 目标 | 类型 |
|---|---|---|
| `jdoe`（日常 + 管理） | `jdoe` 和 `jdoe-adm` | 人员、人员管理员账号（04 I5） |
| Postgres 上共用的 `root` | `breakglass-sql-01` | 紧急访问账号 |
| 服务用户 `jenkins` | `svc-eng-sdlc-jenkins` | 服务账号 |
| `release-bot` | `agent-release-notes`，操作员 `jdoe` | 智能体 |
| 组 `admins` | `tier-t0-superadmin` | 层级组 |
| 组 `devs` | `role-developers` | 角色组 |
| 组 `grafana-admins` | `app-dashboards-admin` | 应用组 |

## 6. 证书

默认按名称使用 ACME 签发。只有无法使用 ACME 的端点才获得预先签发的通配符证书，每个实际使用的 `<domain>.<plane>` 组合一张（01 §7）：

```
*.obs.shared.svc.northwind.example
*.sdlc.eng.svc.northwind.example
```

公共：`*.apps.northwind.example` 和 `*.shopfront.example`，通过 DNS-01 签发。

## 7. 迁移过程中被拒绝的名称

- `grafana-public.apps.northwind.example`——名称中包含暴露范围；内部工具不在 ext 区域发布。
- `gitea.sdlc.eng.svc.northwind.example`——产品作为最左侧标签。
- `ci.sdlc.eng.prd.svc.northwind.example`——生产 DNS 名称中包含环境。
- `shared/obs/grafana/oidc`——缺少环境，且产品作为节点。
- 组 `platform-admins`——层级和角色混在一个名称中。

## 8. 切换顺序

1. 在目录中登记每个目标（owner、tier、data_class、exposure）。
2. 建立内部区域和 CA；为新名称签发证书。
3. 在遗留 FQDN 旁添加新 FQDN；遗留名称改为重定向（90 天）。
4. 创建组和身份；逐个挂载点迁移机密，然后停用 `secret/`。
5. 在常规维护窗口内重命名主机。
6. 删除重定向和遗留组；关闭迁移表。
