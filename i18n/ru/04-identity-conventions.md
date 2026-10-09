[English](../../04-identity-conventions.md) | **Русский** | [简体中文](../zh-CN/04-identity-conventions.md)

> **Перевод.** Перевод стандарта версии v2, исходный коммит `b6791c2`. Нормативным является английский текст: при любых расхождениях преимущество имеет английская версия.

# Соглашения об идентичностях — люди, агенты, сервисные учётные записи, группы, роли

> **Статус:** v2, развивается. Объединяет четырёхуровневую модель привилегированного доступа (T0–T3) с правилами потребителя и плоскости из [01](01-naming-conventions.md).
> **Независимость от продуктов.** Правила применяются к категориям систем: поставщик идентичностей (IdP), менеджер секретов, mesh VPN, идентичность рабочих нагрузок (SPIFFE), RBAC в Kubernetes, роли баз данных, клиенты LLM/MCP-шлюзов, робот-аккаунты реестров контейнеров, токены git-платформ и CI. Продукты в примерах (Keycloak, OpenBao/Vault, SPIRE, Harbor, Gitea, Jenkins, Grafana, …) — взаимозаменяемые иллюстрации.
> **Одна идентичность — один ID везде.** Одна и та же строка служит именем пользователя в IdP, политикой и машинной ролью в менеджере секретов, `x-user-id`, ролью БД (с `_`), OTel `service.name`.

## 1. Применяемые принципы

| # | Правило |
|---|---|
| I1 | **Вид виден в ID.** У людей, администраторов, учётных записей аварийного доступа, сервисных учётных записей, агентов и рабочих нагрузок разные префиксы, потому что у них разные жизненные циклы, учётные данные и требования к аудиту |
| I2 | **Агенты — не сервисные учётные записи.** Агент действует автономно и часто от имени человека; у него собственный вид, собственный узел секретов ([03](03-secrets-conventions.md) §3) и обязательный `operator` (человек, который за него отвечает) |
| I3 | **Группы дают права, имена описывают.** Метка DNS, имя хоста, путь никогда ничего не авторизуют (01 §3.1) |
| I4 | **Только три префикса групп**: `tier-` (уровень привилегий), `role-` (функция), `app-` (доступ к одной возможности). По специфичности: tier ⊂ role ⊂ app |
| I5 | **Отдельная администраторская учётная запись** для работ уровней T0/T1 (`<handle>-adm`), никогда не повседневная |
| I6 | **Аварийный доступ (break-glass) — это учётная запись, а не общий пароль**: `breakglass-<capability>-<NN>`, запечатана, с оповещением, ротация после каждого использования |
| I7 | **Сервисная учётная запись = приложение.** `svc-<plane>-<domain>-<product>`; одна на установку, одна на окружение, если окружения есть |
| I8 | **Идентичность рабочих нагрузок — это SPIFFE**, путь повторяет возможность, домен доверия — компания, а не зона DNS |
| I9 | **У каждой идентичности есть `owner` и `expires`** (или обоснованное `expires: none`). Пересмотры: t0 ежемесячно, t1 ежеквартально, остальные раз в полгода |
| I10 | **Имена в нижнем регистре через дефис (kebab)**; `_` только там, где хранилище запрещает `-` (Postgres, ClickHouse, переменные окружения) |

## 2. Виды идентичностей

| Вид | Форма ID | Пример | Учётные данные | Где хранится |
|---|---|---|---|---|
| Человек | `<first>.<last>` или короткий псевдоним (handle) | `jdoe` | пароль + WebAuthn | IdP |
| Администратор-человек | `<handle>-adm` | `jdoe-adm` | только WebAuthn; без почты/чата | IdP, группы уровней |
| Аварийный доступ | `breakglass-<capability>-<NN>` | `breakglass-sso-01` | запечатанный пароль в `<mount>/…/admin` | локально в системе |
| Сервисная учётная запись | `svc-<plane>-<domain>-<product>[-<env>]` | `svc-eng-sdlc-jenkins` | AppRole / OIDC-клиент / SPIFFE | IdP (машинный пользователь) + менеджер секретов |
| Агент | `agent-<name>` | `agent-code-review`, `agent-docs-writer` | AppRole → SPIFFE; ключ шлюза | менеджер секретов, `clients` шлюза |
| Инструмент человека | `user-<handle>-<tool>` | `user-jdoe-ide` | ключ шлюза, выданный инструменту человека | только `clients` шлюза |
| Рабочая нагрузка | `spiffe://mess.systems/<plane>/<domain>/<capability>` | `spiffe://mess.systems/corp/ai/gateway` | X.509-SVID | SPIRE |
| Узел | `spiffe://mess.systems/node/<host>` | `spiffe://mess.systems/node/dc1-corp-ai-litellm-prd-01` | join-токен / аттестатор | SPIRE |
| Внешний (B2B) | `ext-<org>-<handle>` | `ext-acme-jdoe` | федерация через `b2b.iam.shared` | источник в IdP |

Агенты фиксируют `operator: <human>` и `scope: <capability list>` в своей записи каталога; шлюз принудительно проверяет `x-user-id = <agent id>` и `x-session-id`.

## 3. Группы

### 3.1 Группы уровней (привилегии)

| Группа | Уровень | Кто | Доступ к |
|---|---|---|---|
| `tier-t0-superadmin` | T0 | 1–2 учётные записи `-adm` | всему, элементам `admin`, с оповещением |
| `tier-t1-platform-ops` | T1 | учётные записи `-adm` платформенных инженеров и инженеров безопасности | управляющим интерфейсам `shared/`, `platform/`, `eng/` |
| `tier-t2-developer` | T2 | повседневные учётные записи инженеров | `eng/`, продуктовым плоскостям, не-prod |
| `tier-t3-readonly` | T3 | наблюдатели, аудиторы, агенты по умолчанию | просмотру и чтению дашбордов, каталогов |

### 3.2 Ролевые группы (функция)

| Группа | Назначение |
|---|---|
| `role-platform-engineers` | эксплуатация общих и платформенных управляющих плоскостей |
| `role-security-engineers` | обнаружение угроз, управление уязвимостями, гигиена идентичностей |
| `role-developers` | разработка и поставка продуктов |
| `role-sre-observers` | чтение данных наблюдаемости, владение оповещениями |
| `role-data-engineers` | владение конвейерами данных, хранилищем, каталогами |
| `role-agent-operators` | люди, отвечающие за агентов |

Унаследованные группы привилегий из других схем (`sg-*`, `*-admins`, `operators`) отображаются на группу `tier-*` с той же семантикой; остаётся одна схема префиксов.

### 3.3 Группы приложений (доступ к одной возможности)

`app-<capability>-<access>`, access ∈ `user | editor | admin`.

| Пример | Что даёт |
|---|---|
| `app-dashboards-admin` | администрирование дашбордов (например, Grafana) |
| `app-git-admin` | администрирование git-платформы |
| `app-gateway-user` | право вызывать `gateway.ai.corp` |
| `app-warehouse-editor` | запись в хранилище данных |

Умолчания провижинеров вроде `app-<name>-operators` → `app-<capability>-admin`. Провайдеры с суффиксами зон (`grafana-public/-private/-admin`) упраздняются; уровень доступности — это группа mesh-сети (§4), администрирование — `app-dashboards-admin`.

## 4. Группы mesh VPN

| Форма группы | Содержит | Пример |
|---|---|---|
| `zone-<plane>` | ресурсы (пиры/маршруты) этой плоскости | `zone-shared`, `zone-corp`, `zone-eng`, `zone-platform`, `zone-ext` |
| `tier-*`, `role-*` | пиры-люди, синхронизированные из IdP | `role-developers` |
| `svc-<application>` | пиры-сервисы | `svc-eng-sdlc-jenkins` |
| `egress-<plane>` | шлюзы исходящего трафика | `egress-corp` |
| `site-<code>` | местоположение | `site-dc1`, `site-cld` |

Политики: `<subject-group> → <zone-group>`. Типичные унаследованные сопоставления: группа `admins` с полным доступом → `tier-t0-superadmin`; группа `devs` → `role-developers`; разрозненные группы-теги → соответствующая группа `tier-*` или `role-*`.

## 5. Владельцы

Метаданные `owner` (01 §2) — это всегда **группа**, а не человек: `role-platform-engineers`, `role-data-engineers`, `tier-t0-superadmin`. Исключение — `operator` агента (человек).

## 6. Объекты IdP

| Объект | Имя | Пример |
|---|---|---|
| Slug приложения | `<application>` (01 §5) | `shared-obs-grafana` |
| Отображаемое имя приложения | название продукта | `Grafana` |
| Провайдер | `<application>-<protocol>` | `shared-obs-grafana-oidc`, `eng-sdlc-gitea-oidc` |
| Сопоставление свойств / scope | `<application>-<claim>` | `shared-obs-grafana-groups` |
| Outpost | `outpost-<plane>-<capability>` | `outpost-shared-ingress` |
| Поток (flow) | `flow-<purpose>` | `flow-admin-webauthn` |
| Источник (федерация) | `src-<vendor>` | `src-github` |

Виды объектов соответствуют распространённым IdP (Keycloak, Entra ID, Okta, …); сопоставьте их с эквивалентами в вашем продукте.

Унаследованные slug, названные по продукту (`grafana`, `argocd`) → форма приложения (`shared-obs-grafana`, `eng-sdlc-argocd`). Redirect URI используют только канонические FQDN (01 §6).

## 7. Менеджер секретов (OpenBao / Vault)

Политика = ID идентичности; AppRole = ID идентичности; роль JWT = ID группы. Полные правила — в [03](03-secrets-conventions.md) §5–§6.

| Типичное унаследованное | Целевое |
|---|---|
| политика `admin` | `tier-t0-superadmin` |
| политика `ops` | `tier-t1-platform-ops` |
| политика `developers` | `tier-t2-developer` |
| политика `read-only` | `tier-t3-readonly` |
| AppRole `<app>` / политика `<app>-read` | `svc-<plane>-<domain>-<product>` (одно имя) |
| AppRole / политика, названная по боту | `agent-<name>` |
| политика `registry-read` (один чужой элемент) | `<identity-id>-<capability>-ro` (ограниченное чтение) |

## 8. SPIFFE / SPIRE

| Унаследованное (иллюстрация) | Целевое |
|---|---|
| домен доверия `spiffe://corp.lan` | `spiffe://mess.systems` (не prod: `spiffe://<env>.mess.systems`) |
| `spiffe://corp.lan/infra/llm-proxy` (папка репозитория) | `spiffe://mess.systems/corp/ai/gateway` |
| `spiffe://corp.lan/apps/doc-converter` | `spiffe://mess.systems/corp/data/convert` |
| `spiffe://corp.lan/node/vm042` | `spiffe://mess.systems/node/dc1-corp-ai-litellm-prd-01` |
| `spiffe://corp.lan/node/ws-jdoe-01` | `spiffe://mess.systems/node/ws-jdoe-01` (рабочая станция сохраняет своё имя — это не хост сервиса) |

Агенты: `spiffe://mess.systems/corp/ai/agent-<name>`. Пути следуют **кодам возможностей**, а не папкам репозитория.

## 9. Идентичности клиентов шлюза

Имена ключей в `corp/ai/gateway/prd/clients` и заголовок `x-user-id` — это ID идентичностей из §2.

| Унаследованное поле (иллюстрация) | Целевой ID | Вид |
|---|---|---|
| `codereview_bot` | `agent-code-review` | агент |
| `docs_bot` | `agent-docs-writer` | агент |
| `chat_ai` | `svc-corp-collab-mattermost` | сервисная учётная запись |
| `tracing` | `svc-corp-ai-langfuse` | сервисная учётная запись |
| `shopfront` | `svc-shopfront-api` | сервисная учётная запись продукта |
| `ide` | `user-jdoe-ide` | инструмент человека |

Имена переменных окружения: `GATEWAY_CLIENT_KEY_<ID_UPPER_SNAKE>` (`GATEWAY_CLIENT_KEY_AGENT_CODE_REVIEW`). Цели MCP: коды возможностей (`convert`, `cmdb`, `archrepo`, `data-catalog`), вендоры `<vendor>-<service>` (`acmesearch-web`).

## 10. RBAC в Kubernetes

| Объект | Форма | Унаследованное → целевое (иллюстрация) |
|---|---|---|
| ServiceAccount | `svc-<workload>` | `ci` → `svc-ci` |
| Role / ClusterRole для людей | `<group>-<scope>-<access>` | `view-all` → `role-developers-cluster-ro`; `sandbox-viewer` → `role-developers-sandbox-ro` |
| Role для SA | `<sa>-<scope>-<access>` | `ci-read` → `svc-ci-workload-ro`; `ci-gitops` → `svc-ci-gitops-rw` |
| RoleBinding | `<role>--<subject>` | `role-developers-sandbox-ro--role-developers` |
| Проект GitOps (например, Argo CD) | `<plane>` или `<product>` | `default` → `eng`, продуктовые приложения → `<product>` |
| Метки | `mess.systems/plane`, `mess.systems/owner`, … | |

Claim группы OIDC → субъекты RBAC — это группы `tier-*`/`role-*` без изменений.

## 11. Роли баз данных

Форма: `<plane>_<domain>_<capability>_<access>` для ролей, принадлежащих возможности (`ro | rw | owner`), `svc_<plane>_<domain>_<product>` для потребителей, `agent_<name>` для агентов, `breakglass_<capability>` для локальных администраторов.

| Хранилище | Унаследованное (иллюстрация) | Целевое |
|---|---|---|
| ClickHouse | `default` | отключён |
| ClickHouse | `writer` | `corp_data_warehouse_rw` |
| ClickHouse | `readonly` | `corp_data_warehouse_ro` |
| ClickHouse | `bi` (пользователь BI-инструмента) | `svc_corp_data_superset` |
| MongoDB | `admin` | `breakglass_docstore` |
| MongoDB | `bot` | `agent_docs_writer` |
| Postgres | пользователи по приложениям (`my_app`) | `svc_<plane>_<domain>_<product>`; база данных `<plane>_<domain>_<capability>_<env>` |

## 12. Токены, роботы, ID учётных данных

| Система | Форма | Пример |
|---|---|---|
| Робот реестра (например, Harbor) | `robot$<project>+<consumer-id>` | `robot$corp-ai+svc-eng-sdlc-jenkins` |
| Токен / deploy-ключ git-платформы | `<consumer-id>` (+ `--<purpose>`) | `svc-eng-sdlc-jenkins--clone` |
| ID учётных данных в CI | путь секрета с заменой `/`→`-` | `eng-sdlc-ci-prd-packages` |
| Токен реестра пакетов | `<consumer-id>` | `svc-eng-sdlc-jenkins` |
| Сервисная учётная запись дашбордов | `svc-<application>` | `svc-corp-ai-litellm` |
| Комментарий SSH-ключа | `<identity-id>@<host>` | `jdoe-adm@dc1-shared-infra-kvm-prd-01` |

## 13. Жизненный цикл

| Событие | Правило |
|---|---|
| Создание | сбор исходных данных (01 §9) → вид идентичности → группы → политика/роль в менеджере секретов → запись каталога с `owner`, `expires` |
| Ротация | согласно `custom_metadata.rotation`; агенты и инструменты — 90d; сервисные учётные записи — 365d; аварийный доступ — после каждого использования |
| Пересмотр | t0 ежемесячно, t1 ежеквартально, t2/t3 раз в полгода; агенты — вместе с их оператором |
| Уход / вывод из эксплуатации | отключить в IdP → отозвать secret-id AppRole → удалить роль БД → удалить поле клиента шлюза → закрыть запись каталога. ID никогда не используется повторно |

## 14. Отказы

- Группа без одного из трёх префиксов; четвёртый префикс.
- Уровень и роль в одном имени группы (`platform-admins`).
- Название продукта внутри группы (`grafana-admins` → `app-dashboards-admin`).
- Уровень доступности в имени группы или провайдера (`-public`, `-private`, провайдер `-admin`).
- Агент, зарегистрированный как `svc-*`, или инструмент человека, зарегистрированный как агент.
- Имя политики/AppRole/роли JWT, не являющееся ID идентичности или группы.
- Личный ID, используемый для автоматизации, или учётная запись `-adm` с почтой/чатом.
- Общая учётная запись с общим паролем (используйте учётные записи аварийного доступа).
- Подчёркивание в ID за пределами ролей БД / переменных окружения.
