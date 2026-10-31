# 07. 部署与租户

> 译文仅供参考；规范文本为[英文版](../../07-deployment-and-tenants.md)。本文为标准 v2.7 版本的译文，源提交 `a60b331`。

**产品轮廓**的规则：mess.systems 开发、运营和销售的云原生产品，它们如何在提供商、区域和单元（cell）之间部署，以及如何标识租户。所有示例均使用虚构公司 mess.systems 及其虚构的**产品 X**（`x`）：一个简单的记录应用，包含登录、订阅、管理控制台、带 webhook 的 API 和支付。

产品 X（`x`）是虚构的。其域名 `x.mess.systems` 是[语法 B](01-naming-conventions.md#32-语法-b公共) 中产品域名的占位符，而不是 mess.systems 真正的产品子区域 `x.mess.systems`。示例中的 `api.x.mess.systems` 和 `api.stg.x.mess.systems` 是虚构产品 `x` 的界面 `api`（`<surface>.<product-domain>`），而不是产品子区域中代码为 `api` 的产品。在真正的子区域中，产品 `arch` 的同一界面是 `api.arch.x.mess.systems`。代码 `x` 只存在于示例、示例目录和黄金测试中；组织自己的目录不包含它。

本部分源于对本标准的一次外部评审；感谢评审者。

## 1. 两个轮廓

mess.systems 有两个轮廓。它们共享字符规则、“名称从不授权”规则、先登记目录的流程、机密与身份约定以及 [05](05-labels-and-tags.md) 的标签语法。区别在于名称由什么组成。

| | 企业轮廓 | 产品轮廓 |
|---|---|---|
| 覆盖范围 | 内部服务，`corp`、`eng`、`shared`、`ext` 平面，员工设备 | 面向客户的产品及其环境、单元和租户 |
| 规则 | [01](01-naming-conventions.md) 至 [06](06-endpoint-conventions.md)，不变 | 本部分，建立在共享规则之上 |
| 逻辑身份 | `<capability>.<domain>.<plane>` | `<service>.<domain>.<product>` |
| 最左代码的唯一性 | 能力代码在全公司唯一 | 服务在其产品内唯一 |
| 内部 DNS，生产 | 省略环境：`git.sdlc.eng.svc.mess.systems` | 始终写出环境：`store.records.x.prd.svc.mess.systems` |
| 公共 DNS | `www.mess.systems`、`<capability>.apps.mess.systems` | `api.<product-domain>`、`api.stg.<product-domain>` |
| 成本维度 | `capability` | `product`、`domain`、`service` |
| SPIFFE 信任域 | `mess.systems`，非生产 `<env>.mess.systems` | `product.mess.systems`、`nonprod.product.mess.systems`、`sandbox.product.mess.systems` |

**如何共存。**

- 每个对象只属于一个轮廓。目录记录为 `contour: corp` 或 `contour: product`。
- 在企业轮廓中产品本来就是一个平面（[01 第 4.1 节](01-naming-conventions.md)：`<product>`）。产品轮廓沿用这一点：产品内部名称的第三个标签是产品代码，产品代码绝不等于 `shared`、`corp`、`eng` 或 `ext`。
- 所有产品共用的服务（构建、镜像仓库、产品侧可观测性）属于产品 **`platform`**，与平面 `platform` 代码和含义相同。
- 产品以企业名称使用企业服务（员工 SSO、代码托管、机密管理器）。企业服务从不使用产品轮廓的名称。
- 环境的不对称是有意的：企业轮廓保留简短的生产名称；产品轮廓写出 `prd`，使每个名称在任何环境中都以同样方式解析。

在本标准中，“轮廓”仅指 `corp` 或 `product`（键 `contour`）。拥有自己产品实例的某个客户组织的数据边界称为**组织边界**，绝不进入名称：在 mess.systems 内部它是专用单元 `d<tenant-key>`（[租户](#5-租户)），客户一侧的实例则按客户自己的标准命名。

## 2. 产品、域、服务、实现

| 概念 | 含义 | 产品 X 示例 |
|---|---|---|
| `product` | 客户购买的东西 | `x` |
| `domain` | 产品内的限界区域 | `records`、`access`、`billing`、`integration`、`admin` |
| `service` | 稳定的逻辑服务，比其实现存在得更久 | `store`、`export`、`login`、`session`、`subscription`、`payment`、`webhook`、`console` |
| `component` | 条件：同一服务的多个可部署部分 | `api`、`worker`、`migrate` |
| `implementation` | 可替换的技术；属于台账，绝不进入名称 | `postgresql`、`keycloak` |

- 服务代码在**其产品内**唯一，而非全公司唯一。`x` 和另一个产品都可以有 `login`。
- 域代码只有在含义相同时才能复用企业域代码（`iam` 在两个轮廓中都表示身份）。否则它是产品本地的。
- 实现是元数据（`implementation` 键），不是 DNS 标签、SPIFFE 路径段或 OTel 服务名。替换 PostgreSQL 不会重命名 `store`。

产品 X 的完整服务列表：

| 域 | 服务 |
|---|---|
| `records` | `store`、`export` |
| `access` | `login`、`session` |
| `billing` | `subscription`、`payment` |
| `integration` | `webhook` |
| `admin` | `console` |

## 3. 环境与 DNS

| 环境 | 代码 | 轮廓 |
|---|---|---|
| 生产 | `prd` | 两者 |
| 预发布 | `stg` | 两者 |
| 测试 | `tst` | 两者 |
| 开发 | `dev` | 两者 |
| 沙箱 | `sbx` | 仅产品轮廓：短期、无客户数据、独立信任域 |

产品轮廓的内部名称：

```
<service>.<domain>.<product>.<env>.svc.mess.systems            # product-wide
<service>.<domain>.<cell>.<product>.<env>.svc.mess.systems     # cell-bound
```

- `store.records.x.prd.svc.mess.systems`、`store.records.c01.x.prd.svc.mess.systems`、`login.access.x.stg.svc.mess.systems`。
- 始终写出 `prd`。企业规则“生产环境省略环境”（[01 第 3.1 节](01-naming-conventions.md)）不变，且不适用于此处。
- 需要单独名称的组件加在服务标签上：`store-worker.records.x.prd.svc.mess.systems`。

公共名称保持简洁：

```
api.<product-domain>                 # production
api.stg.<product-domain>             # non-production surface
app.<product-domain>, docs.<product-domain>, status.<product-domain>
```

mess.systems 在子区域 `x.mess.systems` 中发布其产品（[语法 B](01-naming-conventions.md#32-语法-b公共)）：产品域名为 `<product>.x.mess.systems`。拥有自己注册域名的产品使用该域名代替子区域，绝不同时使用两者。

产品 X 使用占位域名 `x.mess.systems`：`api.x.mess.systems`、`app.x.mess.systems`、`api.stg.x.mess.systems`。公共名称中不含域、服务、单元、区域、提供商或租户。把请求路由到单元是路由层的工作，而不是公共名称的工作。

## 4. 部署键

| 键 | 含义 | 取值 | 是否进入名称 |
|---|---|---|---|
| `provider` | 运行在哪里 | 目录代码；自有基础设施和私有云为 `own`；公有提供商使用中性代码（`pub-a`、`pub-b`） | 从不 |
| `jurisdiction` | 适用其规则的法律区域 | 不透明的目录代码（`jur-a`、`jur-b`） | 从不 |
| `region` | 公司区域代码，在目录中映射到提供商的原生区域 | `reg-a1`、`reg-b1` | 从不 |
| `site` | 物理位置或提供商位置（[01 第 4.4 节](01-naming-conventions.md)） | `dc1`、`cld` | 从不进入产品轮廓名称 |
| `cell` | 可独立部署的产品副本，服务一组租户 | 共享 `c01` 至 `c99`；专用 `d<tenant-key>` | 是，名称中唯一的部署键 |
| `tenant-scope` | 租户如何共享单元 | `pooled`、`dedicated` | 从不 |

**提供商独立性。**

- 任何名称都不包含提供商。单元从 `own` 迁到 `pub-a` 无需重命名任何服务。
- 提供商特有资源（账户、项目、资源组、存储桶）按该提供商的形式和限制从元数据生成；逻辑身份在所有提供商上保持一致。
- 每个产品都保持至少能在两个提供商上运行，其中之一可以是 `own`。只能在一个提供商上运行的设计记录为例外，并附复审日期。
- 提供商代码是中性的：提供商的商业名称只在目录中，不进入代码、名称或标签。

## 5. 租户

租户由三个不透明键由外向内标识：

| 键 | 是谁 | 形式 | 示例 |
|---|---|---|---|
| `tenant-operator` | 为客户运营服务的一方：mess.systems 本身或合作伙伴 | `op-` 加 6 个字符 | `op-a7k2mz` |
| `tenant-entity` | 签订合同的法律实体 | `le-` 加 6 个字符 | `le-q4w9np` |
| `tenant-customer` | 使用产品的最终客户组织 | `ec-` 加 6 个字符 | `ec-h3t8rd` |

- 6 个字符使用 [06](06-endpoint-conventions.md) 的 asset-id 字母表：`a-z 2-9`，去掉 `o l i`，首字符为字母。键由目录分配，不透明且不可变。绝不包含客户名称、品牌、国家或合同号。
- 完整租户路径为 `op-a7k2mz/le-q4w9np/ec-h3t8rd`。没有合作伙伴的租户以 mess.systems 为运营方。
- 示例和文档只使用通用名称（“运营方 A”、“实体 B”、“客户 C”）。
- **共享单元中的租户绝不进入名称。** 它们是数据行和标签。
- **专用租户**获得自己的单元 `d<key>`，取法律实体键（`tenant-entity`）的 6 个字符：`dq4w9np`。该实体的所有最终客户共用其专用单元。示例：`store.records.dq4w9np.x.prd.svc.mess.systems`。

## 6. 什么进入名称

| 进入名称 | 只在元数据中 |
|---|---|
| `service`、`domain`、`product`、`env`、`cell`（包含专用租户键） | `provider`、`jurisdiction`、`region`、`site`、`tenant-scope`、`residency`、共享租户键、`implementation`、`owner`、`cost-center`、`criticality`、`data-class` |

## 7. 治理标签

标签遵循 [05](05-labels-and-tags.md) 的语法。每个键有一个类别：

- **必填**：由作者设置；缺少则检查失败。
- **条件**：条件成立时必填。
- **派生**：由工具从目录或流水线填写；从不手工输入。

| 键 | 类别 | 取值 | 说明 |
|---|---|---|---|
| `contour` | 必填 | `corp`、`product` | |
| `product`、`domain`、`service` | 必填（产品轮廓） | 目录代码 | 产品轮廓的成本维度 |
| `component` | 条件：服务有多个可部署部分 | `api`、`worker`、`migrate` | |
| `env` | 必填 | `prd`、`stg`、`tst`、`dev`、`sbx` | |
| `owner` | 必填 | 组 ID | 同 05 |
| `cost-center` | 必填 | `cc-<name>` | 同 05 |
| `criticality` | 必填（产品轮廓） | `critical`、`high`、`medium`、`low` | |
| `data-class` | 必填 | `public`、`internal`、`confidential`、`restricted` | 同 05 |
| `residency` | 必填（产品轮廓） | 司法辖区代码或 `any` | 即使为 `any` 也必填 |
| `tenant-scope` | 必填（产品轮廓运行时） | `pooled`、`dedicated` | |
| `cell` | 条件：资源绑定到单元 | `c01`、`d<key>` | |
| `tenant-operator`、`tenant-entity`、`tenant-customer` | 条件：专用资源 | `op-…`、`le-…`、`ec-…` | |
| `lifecycle` | 条件：不是普通的长期资源 | `ephemeral`、`retiring` | 缺省表示 active |
| `provider`、`region`、`jurisdiction`、`site` | 派生 | 来自目录中的单元 | |
| `managed-by` | 派生 | `opentofu`、`argo-cd`、`ansible` | 由 IaC 模块或 GitOps 工具设置 |
| `source-repo` | 派生 | `<org>/<repo>` | 由 CI 设置 |
| `implementation` | 派生 | 安装代码 | 来自目录 |

**与 05 的协调。** [05 第 2 节](05-labels-and-tags.md)的成本标签对企业轮廓保持不变。在产品轮廓中，必填成本标签为 `cost-center`、`owner`、`env`、`product`、`domain`、`service`；不设 `capability`。`initiative` 和 `plane` 在两个轮廓中都仍为可选。

## 8. OpenTelemetry

| 属性 | 产品轮廓 | 产品 X 示例 |
|---|---|---|
| `service.namespace` | `<product>.<domain>` | `x.records` |
| `service.name` | `<service>` 或 `<service>-<component>` | `store`、`store-worker` |
| `deployment.environment.name` | 环境代码 | `prd` |
| `service.instance.id` | 按实例生成 | |
| `service.version` | 发布版本 | |

单元、租户模式和提供商是带 `mess.systems.` 前缀的资源属性（`mess.systems.cell`），不是服务名的一部分。企业轮廓保留 [01 第 5 节](01-naming-conventions.md)的应用形式。

## 9. SPIFFE

产品轮廓有三个信任域，与企业的 `mess.systems` 分开：

| 信任域 | 环境 |
|---|---|
| `spiffe://product.mess.systems` | `prd` |
| `spiffe://nonprod.product.mess.systems` | `stg`、`tst`、`dev` |
| `spiffe://sandbox.product.mess.systems` | `sbx` |

路径：`/<product>/<domain>/<service>[/<cell>]`，在非生产和沙箱域中环境为第一段：`spiffe://product.mess.systems/x/records/store/c01`、`spiffe://nonprod.product.mess.systems/stg/x/access/login`。跨信任域需要显式联邦；非生产负载绝不持有生产身份。

## 10. 可执行标准

本部分的词汇和规则也以数据形式存放在仓库中：

| 路径 | 内容 |
|---|---|
| `schema/resource-metadata.schema.json` | 产品轮廓资源元数据的 JSON Schema |
| `catalog/*.yaml` | 词汇：轮廓、环境、提供商、司法辖区、区域、单元、环境类别和 DNS 别名、产品 X 的域和服务、标签类别、站点、公共 DNS 例外 |
| `tests/golden/*.yaml` | 黄金示例：元数据及其必须生成的名称，包括“一个对象，一个环境代码”检查 |
| `tests/check_golden.py` | 按 schema 和目录校验黄金示例的测试 |
| `tests/names/*.yaml` | 企业轮廓形式和运维对象的名称示例，包括有效和无效示例 |
| `tests/check_names.py` | 校验名称示例以及站点和 DNS 例外登记册的测试 |

CI 在每个 pull request 上运行该测试。数据文件是虚构产品 X 的示例；组织应以自己的目录替换。

## 11. 拒绝情形

| 迹象 | 违反的规则 |
|---|---|
| 产品轮廓名称中含提供商、区域、司法辖区或站点 | 第 4 节 |
| 任何名称中含共享租户键、客户名称或品牌 | 第 5 节 |
| 以实现（`postgresql`、`keycloak`）作为服务代码 | 第 2 节 |
| 产品轮廓内部名称缺少环境 | 第 3 节 |
| 面向客户的公共名称中含环境、单元或域（`stg` 入口除外） | 第 3 节 |
| 产品代码等于 `shared`、`corp`、`eng` 或 `ext` | 第 1 节 |
| 生产与非生产负载在同一信任域 | 第 9 节 |
| 产品轮廓资源缺少 `residency` | 第 7 节 |
| 以真实提供商名称作为提供商代码 | 第 4 节 |
| 只服务一个环境的资源使用类别代码 | 第 12.1 节 |
| 环境 DNS 别名出现在公开 DNS 之外，或公开名称中混用别名和代码 | 第 12.2 节 |
| 名为 `-prd` 的集群运行非生产节点池 | 第 12.3 节 |
| 一个对象的名称中出现两个不同的环境代码 | 第 12.10 节 |
| 外部令牌缺少 `owner`、`consumer` 或 `expires` | 第 12.9 节 |

## 12. 产品的基础设施对象（v2.5）

产品在其服务之外所需对象的规则：环境类别、集群、镜像、主机、存储桶、基础设施即代码和访问令牌。仅适用于产品轮廓；企业轮廓（[01](01-naming-conventions.md) 至 [06](06-endpoint-conventions.md)）保持不变，以后可自行决定是否采用。

### 12.1 环境类别

有些资源同时服务多个环境：云项目、节点池、同时承载 `stg` 和 `tst` 数据库的数据库集群。它们使用环境类别代替环境代码。

| 类别 | 环境 | 信任域 |
|---|---|---|
| `prd` | `prd` | `product.mess.systems` |
| `nonprod` | `stg`、`tst`、`dev` | `nonprod.product.mess.systems` |
| `sandbox` | `sbx` | `sandbox.product.mess.systems` |

- 类别记录在 `catalog/environments.yaml`（键 `class`）。
- 只有资源确实服务多个环境时，类别代码才进入名称：`x-nonprod`（云项目）、`x-records-store-nonprod`（数据库集群）。其内部对象仍写自己的环境：数据库 `x_records_store_stg`。
- 只服务一个环境的资源从不使用类别代码。

### 12.2 环境的 DNS 别名

公开名称可使用环境代码的可读别名，每个组织在 `catalog/environments.yaml`（键 `dns_alias`）中登记一次。

| 环境 | 各处使用的代码 | 可选 DNS 别名 |
|---|---|---|
| staging | `stg` | `stage` |
| test | `tst` | `test` |

- 别名只允许出现在公开 DNS 名称中：`api.stage.x.mess.systems`。其他所有名称（namespace、GitOps 应用、身份、组、机密路径、存储桶、state 键）都使用代码。
- 一个组织只做一种选择：所有公开名称要么用代码，要么用别名，不得混用。

### 12.3 集群与节点池

| 对象 | 形式 | 示例 |
|---|---|---|
| 单一环境或类别的集群 | `<product>-k8s-<env-or-class>` | `x-k8s-prd`、`x-k8s-nonprod` |
| 运行多个类别的集群 | `<product>-k8s-multi` | `x-k8s-multi` |
| 节点池 | `<cluster>-<env-or-class>` | `x-k8s-multi-prd`、`x-k8s-multi-nonprod` |
| 产品环境的 namespace | `<product>-<env>` | `x-prd`、`x-stg` |

集群名称不得声称它并非独占运行的环境：带有 `nonprod` 节点池的集群不叫 `-prd`。

### 12.4 产品平台与企业服务

如果产品在自己的部署中离不开某个服务，该服务属于产品 `platform`：面向客户和产品运维人员的 IdP、产品网格、产品机密存储、产品的 CI 运行器和镜像仓库、产品侧可观测性。企业轮廓保留服务全公司员工和工程工作的部分。如果一套安装同时服务两者，它保留企业名称，产品引用它。

| 服务 | 轮廓 | 名称 |
|---|---|---|
| 产品 X 运维人员的 IdP | product | `login.access.platform.prd.svc.mess.systems` |
| 产品单元的网格协调器 | product | `mesh.net.platform.prd.svc.mess.systems` |
| 员工 SSO | corp | `sso.iam.shared.svc.mess.systems`（不变） |

### 12.5 容器镜像与镜像仓库

| 对象 | 形式 | 示例 |
|---|---|---|
| 镜像 | `<registry>/<product>/<service>[-<component>]:<tag>` | `<registry>/x/store-worker:v1.4.0` |
| 发布标签 | `vX.Y.Z`，不可变 | `v1.4.0` |
| 构建标签 | `main-<sha7>`，可选 `pr-<n>` | `main-3f9c2d1` |

镜像仓库主机属于供应商或平台，不属于名称；清单中只在一个变量（`image.registry`）里保存它。提交哈希和构建号是注解，不是标签。

### 12.6 承担多个角色的主机

主机形式仍为 `<site>-<plane-or-product>-<domain>-<service>-<env>-<NN>`。一台主机承担多个角色时，按主要角色命名，其余角色列在元数据 `roles` 中。角色迁出主机时无需改名。

### 12.7 基础设施即代码与运行器

- 产品 `platform` 的 `build` 域新增服务 `iac`：state 存储和 plan/apply 流水线。
- CI 运行器是 `ci` 的组件，不是独立服务：`ci-runner.build.platform.prd.svc.mess.systems`。

| 对象 | 形式 | 示例 |
|---|---|---|
| 栈目录 | `stacks/<product-or-platform>/<env-or-class>` | `stacks/x/prd`、`stacks/platform/prd` |
| Bootstrap 栈 | `bootstrap`（手动应用一次） | `bootstrap` |
| 模块 | `modules/<capability>` | `modules/k8s`、`modules/pg` |
| State 键 | `<product-or-platform>/<stack>/<env>.tfstate` | `x/app/prd.tfstate`、`bootstrap/platform/prd.tfstate` |
| 资源地址 | `<service>_<env>`（snake_case） | `x_k8s_prd` |

存放这些代码的仓库按命名约定的[对象形式](01-naming-conventions.md#5-对象形式)命名：`<product>-<domain>-iac`，例如 `platform-build-iac`。Git 分支、CI 工作流和作业遵循[运维对象](08-operations-objects.md)。

### 12.8 存储桶

| 对象 | 形式 | 示例 |
|---|---|---|
| 存储桶 | `<product>-<domain>-<service>-<env-or-class>` | `platform-build-iac-prd`、`x-records-backup-prd` |
| 提供商要求全局唯一名称时 | `<org>-` 加上述形式 | `<org>-platform-build-iac-prd` |

是否使用 `<org>-` 按提供商决定一次，并记录在目录中（`catalog/deployment.yaml`，键 `global_bucket_names`）。

### 12.9 外部系统签发的访问令牌

个人访问令牌、SaaS 服务的 API 密钥和代码托管平台令牌命名为：

```
<issuer>-<consumer>-<scope>-<access>
```

| 部分 | 含义 | 示例 |
|---|---|---|
| `issuer` | 签发令牌的组织或系统 | `forge-x`、`mirror` |
| `consumer` | 使用者：代理、服务、运行器 | `agent`、`gitops`、`ci-runner` |
| `scope` | 作用对象：仓库、项目、服务 | `infra`、`registry` |
| `access` | 级别 | `ro`、`rw`、`adm` |

示例：`forge-x-agent-infra-rw`。必需元数据：`owner`、`consumer`、`expires`（ISO 8601）。令牌有描述字段时写在那里，否则写在存放它的机密的自定义元数据中。没有 `expires` 的令牌不予签发；永不过期的令牌需要目录登记。令牌值只存放在机密存储中（[03](03-secrets-conventions.md)）。

### 12.10 一个对象，一个环境代码

一个对象的所有名称使用同一个环境代码：`stg` 部署的 namespace、GitOps 应用、身份、机密路径和存储桶都写 `stg`。DNS 别名只允许出现在公开 DNS 中。golden 测试 `invalid-mixed-env-codes.yaml` 和 `invalid-alias-outside-dns.yaml` 检查这一点；资源在元数据 `names` 中列出其具体名称。
