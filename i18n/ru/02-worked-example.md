[English](../../02-worked-example.md) | **Русский** | [简体中文](../zh-CN/02-worked-example.md)

> **Перевод.** Перевод стандарта версии v2, исходный коммит `ca24160` с редакторской правкой ссылок. Нормативным является английский текст: при любых расхождениях преимущество имеет английская версия.

# Разобранный пример: миграция вымышленной организации

> **Статус:** иллюстративный. Всё здесь вымышлено: организация, хосты, сервисы и пути существуют лишь для того, чтобы показать, как соглашения об [именовании](01-naming-conventions.md), [секретах](03-secrets-conventions.md) и [идентичностях](04-identity-conventions.md) применяются совместно.
> **Подстановка домена:** стандарт использует домен организации `mess.systems`. В этом примере используется **`northwind.example`** (зарезервирован [RFC 2606](https://www.rfc-editor.org/rfc/rfc2606) и [RFC 6761](https://www.rfc-editor.org/rfc/rfc6761)), чтобы показать, что домен компании — это параметр: `svc.mess.systems` превращается в `svc.northwind.example`, `spiffe://mess.systems` — в `spiffe://northwind.example` и так далее.

## 1. Исходная ситуация

Northwind Traders эксплуатирует около дюжины сервисов на двухузловом гипервизоре в своём офисе (площадка `hq`) и одну ВМ в публичном облаке (площадка `cld`). За пять лет накопились такие имена:

- `grafana.corp.lan`, `grafana-admin.corp.lan` — названия продуктов и уровень доступности в имени;
- `git.corp.lan` и `gitea.corp.lan` — два имени для одной установки;
- `vm042`, `srv-old-2`, `docker1` — хосты без смысловых имён;
- `*.int.corp.lan` и `*.corp.lan` — «внутренняя» подзона, которая на деле является правилом доступа;
- одна точка монтирования менеджера секретов `secret/` с путями по вендорам, по продуктам и по людям.

`.lan` не является зарезервированным TLD, и на него нельзя получить сертификаты публичного УЦ, поэтому целевая внутренняя зона — `svc.northwind.example` (split-horizon, публично не делегируется).

## 2. Зоны

| Зона | Целевое состояние | Грамматика |
|---|---|---|
| Внутренние сервисы | `svc.northwind.example` | A |
| Хосты управления | `mgmt.northwind.example` | имена хостов, а не возможности |
| Публичная ext | `apps.northwind.example` | B, бренд в роли продукта |
| Бренд | `www.northwind.example` | B |
| Продукт | `app.shopfront.example` | B |

## 3. Сервисы: сбор исходных данных и кодирование

Сбор исходных данных (intake) выполняется по [процедуре именования](01-naming-conventions.md#9-процедура-именования): плоскость, домен, возможность, продукт, окружение. Все сервисы здесь продуктивные, поэтому грамматика A опускает окружение, а в хостах, схемах и секретах пишется `prd`.

| Унаследованное имя | Исходные данные (plane / domain / capability / product) | Целевое FQDN | Приложение | Владелец |
|---|---|---|---|---|
| `grafana.corp.lan`, `grafana-admin.corp.lan` | shared / obs / dashboards / Grafana | `dashboards.obs.shared.svc.northwind.example` | `shared-obs-grafana` | `role-sre-observers` |
| `prometheus.corp.lan` | shared / obs / metrics / Prometheus | `metrics.obs.shared.svc.northwind.example` | `shared-obs-prometheus` | `role-sre-observers` |
| `keycloak.int.corp.lan` | shared / iam / sso / Keycloak | `sso.iam.shared.svc.northwind.example` | `shared-iam-keycloak` | `tier-t1-platform-ops` |
| `vault.int.corp.lan` | shared / iam / secrets / OpenBao | `secrets.iam.shared.svc.northwind.example` | `shared-iam-openbao` | `tier-t0-superadmin` |
| `git.corp.lan`, `gitea.corp.lan` | eng / sdlc / git / Gitea | `git.sdlc.eng.svc.northwind.example` | `eng-sdlc-gitea` | `role-platform-engineers` |
| `jenkins.corp.lan` | eng / sdlc / ci / Jenkins | `ci.sdlc.eng.svc.northwind.example` | `eng-sdlc-jenkins` | `role-platform-engineers` |
| `registry.corp.lan` | eng / sdlc / oci / Harbor | `oci.sdlc.eng.svc.northwind.example` | `eng-sdlc-harbor` | `role-platform-engineers` |
| `pg01.corp.lan` | shared / data / sql / PostgreSQL | `sql.data.shared.svc.northwind.example` | `shared-data-postgres` | `role-platform-engineers` |
| `chat.corp.lan` | corp / collab / chat / Mattermost | `chat.collab.corp.svc.northwind.example` | `corp-collab-mattermost` | `role-platform-engineers` |
| `wiki.corp.lan` | corp / collab / wiki / Wiki.js | `wiki.collab.corp.svc.northwind.example` | `corp-collab-wikijs` | `role-developers` |
| `llm.corp.lan`, `llm-ui.corp.lan` | corp / ai / gateway / LiteLLM | `gateway.ai.corp.svc.northwind.example` (UI = путь `/ui`) | `corp-ai-litellm` | `role-agent-operators` |
| `demo.corp.lan` (публичное) | ext / gov / demo / demo portal | `demo.apps.northwind.example` | `ext-gov-demo-portal` | `role-developers` |

Решения, принятые по ходу:

- `grafana-admin` — это не второе имя. Администраторский доступ становится группой `app-dashboards-admin` (см. [группы приложений](04-identity-conventions.md#33-группы-приложений-доступ-к-одной-возможности)), а у сервиса остаётся одно FQDN (см. [грамматику A](01-naming-conventions.md#31-грамматика-a-внутренняя) и [единый базовый URL](01-naming-conventions.md#6-единый-базовый-url)).
- `gitea.corp.lan` становится 90-дневным редиректом на каноническое FQDN, затем удаляется (см. [единый базовый URL](01-naming-conventions.md#6-единый-базовый-url)).
- `*.int.corp.lan` кодировал уровень доступности. Все имена переходят на грамматику A; кто может к ним обращаться, определяет группа mesh-сети или IdP (см. [группы mesh VPN](04-identity-conventions.md#4-группы-mesh-vpn)).
- UI для LLM — это путь на шлюзе, а не второе FQDN (одна установка, одно имя).

## 4. Хосты

Форма: `<site>-<plane>-<domain>-<product>-<env>-<NN>` (см. [формы объектов](01-naming-conventions.md#5-формы-объектов)). Интерфейсы управления размещаются в `mgmt.northwind.example`.

| Унаследованный хост | Что работает | Целевой хост |
|---|---|---|
| `hv1`, `hv2` | узлы гипервизора | `hq-shared-infra-pve-prd-01`, `hq-shared-infra-pve-prd-02` |
| `vm042` | Grafana + Prometheus | `hq-shared-obs-grafana-prd-01` (Prometheus — второе приложение на том же хосте) |
| `srv-old-2` | Gitea | `hq-eng-sdlc-gitea-prd-01` |
| `docker1` | Jenkins | `hq-eng-sdlc-jenkins-prd-01` |
| `pg01` | PostgreSQL | `hq-shared-data-postgres-prd-01` |
| `cloud-vm-1` | демо-портал | `cld-ext-gov-portal-prd-01` |
| `ws-jdoe-01` | рабочая станция | без изменений — рабочие станции не являются хостами сервисов |

## 5. Секреты и идентичности

Вместо `secret/` — одна точка монтирования на плоскость (см. [точки монтирования](03-secrets-conventions.md#2-точки-монтирования)):

| Унаследованное (`secret/`) | Целевое | Правило |
|---|---|---|
| `grafana/oidc` | `shared/obs/dashboards/prd/oidc` | возможность, а не продукт (см. [отказы для секретов](03-secrets-conventions.md#9-отказы)) |
| `postgres/root` | `shared/data/sql/prd/admin` | элемент аварийного доступа, только t0 (правило [S6](03-secrets-conventions.md#1-применяемые-принципы)) |
| `jenkins/registry` | `eng/sdlc/ci/prd/oci` | копия потребителя, названная по возможности, к которой она даёт доступ |
| `llm/acmeai` | `corp/ai/gateway/prd/provider-acmeai` | вендор — это элемент, а не узел (правило [S4](03-secrets-conventions.md#1-применяемые-принципы)) |
| `users/jdoe/*` | **отклонено** | личные секреты хранятся в менеджере паролей (правило [S5](03-secrets-conventions.md#1-применяемые-принципы)) |

Идентичности и группы (см. [соглашения об идентичностях](04-identity-conventions.md)):

| Унаследованное | Целевое | Вид |
|---|---|---|
| `jdoe` (повседневная + администраторская) | `jdoe` и `jdoe-adm` | человек, администратор-человек (правило [I5](04-identity-conventions.md#1-применяемые-принципы)) |
| общий `root` в Postgres | `breakglass-sql-01` | учётная запись аварийного доступа |
| сервисный пользователь `jenkins` | `svc-eng-sdlc-jenkins` | сервисная учётная запись |
| `release-bot` | `agent-release-notes`, оператор `jdoe` | агент |
| группа `admins` | `tier-t0-superadmin` | группа уровня |
| группа `devs` | `role-developers` | ролевая группа |
| группа `grafana-admins` | `app-dashboards-admin` | группа приложения |

## 6. Сертификаты

По умолчанию — ACME на каждое имя. Заранее выпущенный wildcard получают только конечные точки, которые не умеют ACME, — по одному на каждую используемую пару `<domain>.<plane>` (см. [TLS](01-naming-conventions.md#7-tls)):

```
*.obs.shared.svc.northwind.example
*.sdlc.eng.svc.northwind.example
```

Публичные: `*.apps.northwind.example` и `*.shopfront.example` через DNS-01.

## 7. Имена, отклонённые в ходе миграции

- `grafana-public.apps.northwind.example` — уровень доступности в имени; внутренние инструменты не публикуются в зоне ext.
- `gitea.sdlc.eng.svc.northwind.example` — продукт в самой левой метке.
- `ci.sdlc.eng.prd.svc.northwind.example` — окружение в prod-имени DNS.
- `shared/obs/grafana/oidc` — нет окружения, продукт в роли узла.
- группа `platform-admins` — уровень и роль в одном имени.

## 8. Порядок переключения

1. Зарегистрировать каждый целевой объект в каталоге (owner, tier, data_class, exposure).
2. Поднять внутреннюю зону и УЦ; выпустить сертификаты на новые имена.
3. Добавить новые FQDN рядом с унаследованными; унаследованные имена становятся редиректами (90 дней).
4. Создать группы и идентичности; перенести секреты по одной точке монтирования, затем отключить `secret/`.
5. Переименовать хосты в обычные окна обслуживания.
6. Удалить редиректы и унаследованные группы; закрыть таблицу миграции.
