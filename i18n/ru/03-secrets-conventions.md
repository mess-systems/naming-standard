[English](../../03-secrets-conventions.md) | **Русский** | [简体中文](../zh-CN/03-secrets-conventions.md)

> **Перевод.** Перевод стандарта версии v2, исходный коммит `ca24160` с редакторской правкой ссылок. Нормативным является английский текст: при любых расхождениях преимущество имеет английская версия.

# Соглашения о секретах для OpenBao и HashiCorp Vault

> **Статус:** v2, развивается. Правила выводятся из [соглашений об именовании](01-naming-conventions.md): секрет принадлежит своему потребителю, плоскость — первая граница изоляции, вендоры — это ID каталога, окружения изолированы.
> **Типичная отправная точка:** одна точка монтирования KV v2 `secret/` с несколькими конкурирующими формами путей (см. [миграцию](#7-миграция-с-унаследованных-путей-иллюстрация)). **Целевое состояние:** `https://secrets.iam.shared.svc.mess.systems`, одна точка монтирования (mount) на плоскость, одна грамматика путей.
> В этом файле нет значений секретов. Только имена. Написано для движка KV v2 в [OpenBao](https://openbao.org/docs/secrets/kv/kv-v2/) и [HashiCorp Vault](https://developer.hashicorp.com/vault/docs/secrets/kv/kv-v2); правила путей и именования переносятся на другие менеджеры секретов.

## 1. Применяемые принципы

| # | Правило | Источник |
|---|---|---|
| S1 | Секрет хранится по пути своего **потребителя**, потому что политики выдают префиксы путей, а политика выдаётся потребителю | рекомендации по политикам [OpenBao](https://openbao.org/docs/concepts/policies/) и [Vault](https://developer.hashicorp.com/vault/docs/concepts/policies) |
| S2 | Точка монтирования = плоскость. Радиус поражения и аудит следуют первой оси изоляции | [Плоскости](01-naming-conventions.md#41-плоскости) |
| S3 | `env` **всегда** присутствует в пути, включая prod. Хранилища не сокращаются по зоне | [Грамматика A: внутренняя](01-naming-conventions.md#31-грамматика-a-внутренняя) |
| S4 | Учётные данные вендоров лежат под возможностью, которая взаимодействует с вендором, элемент `provider-<vendor>` | [Провайдеры и исходящий трафик](01-naming-conventions.md#8-провайдеры-и-исходящий-трафик) |
| S5 | У людей нет личных секретов в OpenBao. Личные секреты хранятся в `passwords.iam.corp` (менеджер паролей). Привилегированный доступ людей — вход через OIDC и политика, никогда не хранимый токен | [NIST SP 800-53 AC-2](https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/SP_800_53_5_2_0/home?element=AC-02) |
| S6 | Учётные данные аварийного доступа (break-glass) — отдельные элементы с именем `admin`, закрытые политикой для `tier-t0-superadmin`; каждое чтение порождает оповещение | уровни привилегированного доступа ([Группы уровней](04-identity-conventions.md#31-группы-уровней-привилегии)) |
| S7 | Один секрет на элемент, несколько полей в секрете. Поля используют стандартные имена в `snake_case`, чтобы потребители были переносимы | переносимость |
| S8 | Каждый секрет несёт `custom_metadata` с [десятью ключами метаданных](01-naming-conventions.md#2-десять-ключей-метаданных), а также `rotation` и `issuer` | обнаруживаемость, аудит |
| S9 | Prod-секреты никогда не появляются в не-prod пути. Не-prod элементы создаются заново, а не копируются | изоляция окружений |
| S10 | Имена политик и AppRole **являются** именами идентичностей ([Виды идентичностей](04-identity-conventions.md#2-виды-идентичностей)). Никаких суффиксов `-policy`, `-role` | одно имя на идентичность |

## 2. Точки монтирования

| Точка монтирования | Тип | Содержит |
|---|---|---|
| `shared/` | kv-v2 | секреты управляющих плоскостей (IAM, PKI, DNS, mesh, наблюдаемость, инфраструктура) |
| `corp/` | kv-v2 | сервисы для сотрудников, агенты сотрудников |
| `eng/` | kv-v2 | инструменты SDLC/ADLC |
| `platform/` | kv-v2 | общая среда выполнения продуктов |
| `ext/` | kv-v2 | партнёрские и демо-порталы |
| `<product>/` | kv-v2 | одна точка монтирования на продукт (например, `shopfront/`, `ledger/`) |
| `pki-int/` | pki | внутренний выпускающий УЦ |
| `transit/` | transit | ключи шифрования-как-сервиса, именуются `<application>` |
| `auth/approle` | auth | рабочие нагрузки без SPIFFE |
| `auth/jwt-<idp>` (например, `jwt-keycloak`) | auth | люди и CI через OIDC |
| `auth/jwt-spire` | auth | рабочие нагрузки SPIFFE (целевое состояние) |
| `auth/kubernetes-<cluster>` | auth | сервисные учётные записи Kubernetes |

Унаследованная точка монтирования `secret/` сохраняется, пока все пути из раздела [«Миграция»](#7-миграция-с-унаследованных-путей-иллюстрация) не будут перенесены, затем отключается.

## 3. Грамматика путей

```
<mount>/<domain>/<capability>/<env>/<item>
<mount>/<domain>/<agent-id>/<env>/<item>          # agents: agent-id replaces capability
<product>/<component>/<env>/<item>                # product mounts
```

| Токен | Значения |
|---|---|
| `<domain>` | [Домены](01-naming-conventions.md#42-домены) |
| `<capability>` | возможность потребителя, из [Коды возможностей](01-naming-conventions.md#43-коды-возможностей-уникальны-во-всех-доменах) |
| `<agent-id>` | `agent-<name>` из [Виды идентичностей](04-identity-conventions.md#2-виды-идентичностей) (агенты потребляют несколько возможностей, поэтому являются отдельным узлом) |
| `<env>` | `prd dev tst stg` — обязательно |
| `<item>` | [Элементы и поля](#4-элементы-и-поля) |

Глубина фиксирована: четыре уровня под точкой монтирования. Более глубокие пути отклоняются; больше структуры означает ещё один элемент, а не ещё один уровень.

## 4. Элементы и поля

Стандартные элементы (item) — используйте их, прежде чем придумывать новый:

| Элемент | Значение | Стандартные поля |
|---|---|---|
| `config` | секреты уровня приложения (ключи подписи, секрет сессии) | `secret_key`, `encryption_key`, `jwt_secret` |
| `db` | учётные данные БД потребителя | `host`, `port`, `database`, `username`, `password`, `dsn` |
| `oidc` | OIDC-клиент этого приложения в `sso.iam.shared` | `issuer`, `client_id`, `client_secret`, `redirect_uri` |
| `api` | собственный административный/API-токен приложения для операторов и автоматизации | `url`, `token` |
| `admin` | локальная учётная запись аварийного доступа (S6) | `username`, `password` |
| `clients` | ключи, которые это приложение **выдаёт** вызывающим (копия эмитента) | одно поле на идентичность вызывающего, имя = ID идентичности |
| `provider-<vendor>` | учётные данные внешнего вендора (S4) | `api_key`, `base_url`, `account_id` |
| `<capability>` | учётные данные, которые потребитель держит **для** другой возможности (копия потребителя) | поля в том виде, в каком выданы (`api_key`, `token`, `url`) |
| `tls` | материал сертификатов, когда ACME не используется | `cert`, `key`, `ca` |
| `join-tokens`, `regcred`, `webhook` | узкоспециализированные эксплуатационные элементы | по необходимости |

Правила для полей: `snake_case`, строчные буквы; `url` всегда включает схему; поля не называются по переменным окружения (`api_key`, а не `MESH_API_KEY`).

`custom_metadata` (S8): `plane, domain, capability, product, env, owner, tier, data_class, rotation` (`90d` | `365d` | `manual`), `issuer` (идентичность, создавшая секрет), `consumer` (идентичность, которая его читает).

## 5. Политики

| Вид | Имя | Что выдаёт |
|---|---|---|
| Политика потребителя | `<identity-id>` (например, `corp-ai-litellm`, `agent-code-review`) | `read` на свой `<mount>/<domain>/<capability>/<env>/*`; `read` на нужные ему копии потребителя |
| Политика уровня (люди) | `tier-t0-superadmin`, `tier-t1-platform-ops`, `tier-t2-developer`, `tier-t3-readonly` | t0: все точки монтирования, включая элементы `admin`, с оповещением; t1: `shared/`, `platform/`, `eng/`, кроме `admin`; t2: `eng/` и `<product>/`, кроме `admin`; t3: только `list` + метаданные |
| Ролевая политика | `role-<function>` | чтение/запись в пределах домена для этой функции (например, `role-security-engineers` получает `*/sec/*`) |
| Ограниченная политика чтения | `<identity-id>-<capability>-ro` | когда потребителю нужен ровно один чужой элемент, например `eng-sdlc-jenkins-packages-ro` |

Форма пути в HCL: `path "<mount>/data/<domain>/<capability>/<env>/*"` плюс `metadata/` для листинга. Запрет на `*/admin` для всех, кроме `tier-t0-superadmin`.

## 6. Роли аутентификации и токены

| Метод аутентификации | Имя роли | Привязка | Политики | TTL |
|---|---|---|---|---|
| `approle` | `<identity-id>` | secret-id на хост, привязка к CIDR | `<identity-id>` | токен 1 ч, продление до 24 ч |
| `jwt-<idp>` | `<group-id>` (`tier-t1-platform-ops`, `role-developers`) | claim группы IdP | соответствующие политики уровня/роли | 8 ч |
| `jwt-spire` | `<identity-id>` | SPIFFE ID `spiffe://mess.systems/<plane>/<domain>/<capability>` | `<identity-id>` | 1 ч |
| `kubernetes-<cluster>` | `<namespace>-<serviceaccount>` | SA + пространство имён | `<identity-id>` | 1 ч |

`display_name` токена = ID идентичности. Долгоживущие root- и периодические токены вне аварийного доступа отклоняются.

## 7. Миграция с унаследованных путей (иллюстрация)

Унаследованные пути ниже вымышлены, но показывают пять типичных форм, встречающихся в единственной точке монтирования `secret/`: по вендору, по продукту, по команде, по человеку и по уровню.

| Унаследованное (`secret/`) | Целевое | Примечания |
|---|---|---|
| `bots/code-review` (+ `/tracing`) | `corp/ai/agent-code-review/prd/gateway`, `.../llm-traces` | копии потребителя; элементы названы по возможностям, к которым дают доступ |
| `llm-gateway/clients` | `corp/ai/gateway/prd/clients` | копия эмитента; имена полей становятся ID идентичностей ([Идентичности клиентов шлюза](04-identity-conventions.md#9-идентичности-клиентов-шлюза)) |
| `llm-gateway/keys` | `corp/ai/gateway/prd/provider-acmeai`, `provider-acmecloud` | один элемент на вендора |
| `acmecloud/vm-api` | `shared/infra/compute/prd/provider-acmecloud` | вендор как узел → вендор как элемент |
| `grafana/oidc` | `shared/obs/dashboards/prd/oidc` | узел продукта → узел возможности |
| `postgres/admin` | `shared/data/sql/prd/admin` | аварийный доступ |
| `ci/registry-pull` | `eng/sdlc/ci/prd/oci` | потребитель = CI |
| `shopfront/db` | `shopfront/api/prd/db` | уже в форме продукта; добавить компонент и окружение |
| `services/<other>` | под потребляющей возможностью | разбирать по одному |
| `dev/<username>/*` | **отклонено** | правило [S5](#1-применяемые-принципы): менеджер паролей или токены, выданные IdP |
| `platform/*`, `admin/*` (в форме уровней) | политики уровней ([Политики](#5-политики)) | пути — это не уровни |

UI: ссылки меняются с `https://<legacy-host>/ui/vault/secrets/secret/list` на `https://secrets.iam.shared.svc.mess.systems/ui/vault/secrets/<mount>/kv/list/<domain>/<capability>/<env>/`.

## 8. Разобранный пример: LLM-шлюз

```
corp/ai/gateway/prd/config                  secret_key
corp/ai/gateway/prd/clients                 agent-code-review, agent-docs-writer, user-jdoe-ide, svc-corp-collab-mattermost, ...
corp/ai/gateway/prd/provider-acmeai         api_key, base_url
corp/ai/gateway/prd/provider-acmecloud      api_key, base_url, account_id
corp/ai/gateway/prd/provider-acmesearch     api_key, base_url
corp/ai/gateway/prd/llm-traces              public_key, secret_key, url
corp/ai/gateway/prd/oidc                    issuer, client_id, client_secret
corp/ai/agent-code-review/prd/gateway       api_key, url          # consumer copy of one field of clients
```

Политика `corp-ai-litellm`: чтение `corp/data/ai/gateway/prd/*`. Политика `agent-code-review`: чтение `corp/data/ai/agent-code-review/prd/*`. Ни одна не может читать данные другой. AppRole `agent-code-review` привязана к CIDR своего раннера; целевая замена — `jwt-spire` с `spiffe://mess.systems/corp/ai/agent-code-review`.

## 9. Отказы

- Путь глубже, чем `<mount>/<a>/<b>/<env>/<item>`.
- Имя вендора как узел пути (`acmecloud/`, `github/`) — вендоры являются элементами (`provider-*`).
- Имя продукта как узел под точкой монтирования плоскости (`mongodb/`, `grafana/`) — вместо него возможность.
- Путь без `env`.
- Поле, названное как переменная окружения, или в ВЕРХНЕМ регистре / kebab-case.
- Элемент `admin`, доступный на чтение любой политике, кроме t0.
- Имя политики или роли, отличающееся от имени идентичности.
- Копирование prod-секрета в `dev|tst|stg`.
