# Autional API Reference Portal

**Sites**: [reference.autional.com](https://reference.autional.com) (com) / [reference.autional.cn](https://reference.autional.cn) (cn)
**Stack**: Astro 5 + Tailwind 3.4 + Scalar UI（vendored `public/scalar/1.59.2/`）
**Repository**: [github.com/autional/reference](https://github.com/autional/reference)

Interactive Swagger 2.0 (OpenAPI 2.0) reference for all 27 Autional microservices, rendered by Scalar UI.

Single source, dual-region build: one repo serves both regions. Regional differences (site URL, default/fallback language, CDN host, brother-site links, API gateway host) are injected at build time via env — `REGION` / `SITE_URL` / `DEFAULT_LANG` / `FALLBACK_LANG` / `CDN_HOST`（读取单点 `scripts/env.mjs`；落点见 `astro.config.mjs` 的 `vite.define` 与 `src/lib/site-env.ts`）。默认语言 zh 兜底为本区（cn）。文案双语化（`src/i18n/{en-US,zh-CN}.json` 单键空间，`scripts/check-i18n.mjs` 门禁）；语言切换为客户端行为（localStorage 键 `autional-lang`），静态页始终是区域默认语言。

## Development

```bash
pnpm install
pnpm dev      # http://localhost:4434（无 env 时兜底 cn 值）
pnpm build    # 产物 dist/；prebuild 生成 public/robots.txt（按 SITE_URL 区域化，gitignored）+ 跑 check-i18n
```

双区本地构建：

```bash
REGION=cn SITE_URL=https://reference.autional.cn DEFAULT_LANG=zh FALLBACK_LANG=zh CDN_HOST=https://cdn.autional.cn pnpm build
REGION=com SITE_URL=https://reference.autional.com DEFAULT_LANG=en FALLBACK_LANG=en CDN_HOST=https://cdn.autional.com pnpm build
```

## Specs（双源并存）

`public/specs/` 同时承载双语规范；页面按构建语言取规（`src/lib/specs.ts`）：zh 读 `<svc>.json`，en 读 `<svc>-en.json`。

- **zh（27 个，`<svc>.json`）** — 由 `python scripts/sync-specs-zh.py` 从 Autional monorepo `D:\go\auth_ms_new\docker\specs\<service>\swagger.json` 同步 + 改牌（host/接入路径按网关路由真源 `shared/service-gateway/configs/service/gateway-service.yaml` 注入）。脚本只负责 zh 侧，**不再清理 `*-en.json`**。
- **en（`<svc>-en.json`）** — monorepo 生成器的既有英文导出（`autional/scripts/translate_swagger.py` 翻译导出 + `autional/scripts/sync_specs.py` 同步到本仓 `public/specs/`；后者脚本内的门户路径须跟版前先核对/更新）。版本跟版：monorepo 规范变更后重跑导出/同步并提交本仓；本仓存量为幂等基线。
- **en 缺源服务** — `captcha3d-service` / `config-service` / `saml-service` / `stream-service` 无 en 导出；en 区构建期回退读 zh 原版并在页内显示 "English spec pending — showing the Chinese original." 标注（裁定见 B2 执行报告）。
- **en 端点覆盖落后（待管线重跑·已登记）** — 存量 en 规范合计比 zh 少约 80 个端点（billing −13 / communication −13 / notification −16 / compliance −10 / storage −8 / oauth −7 / tenant −6 / pay −4 / point −3 / rbac −3 / profile −1 / status −1；identity/mfa 反向多 2/3）。**根因**：`translate-swagger.py` 读取的是 monorepo 顶层旧 `<svc>.json`（过期），而非最新的 `<svc>/swagger.json`（与 zh 侧一致）。**修法**：把导出器输入改为 `<svc>/swagger.json` 后重跑导出/同步并提交本仓（受人工校对的既有英文须保留，勿用词典全量覆盖）；随后同步刷新 `wiki-src/en`。在重跑前，en 页展示属**已知覆盖缺口**，非错误调用路径（basePath 已与 zh 对齐）。构建期已在 en 服务页给出 `service.partialNote` 页内标注（"lags … by N of M endpoints"），缺口不再静默。

## Deploy

Push 到 main — Vercel 自动部署。Projects: `reference` (com) / `cn-reference` (cn)；env 按项目分别注入。
