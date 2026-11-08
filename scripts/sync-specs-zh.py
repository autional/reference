#!/usr/bin/env python3
"""Sync Chinese OpenAPI specs from the AuthMS monorepo into this portal.

Source: D:\\go\\auth_ms_new\\docker\\specs\\<service>\\swagger.json (Chinese, native)
Target: public/specs/<service>.json

B2 单源双区（并入 com 仓后）：本脚本只管 zh 侧 `<service>.json`（27 个）。
en 侧 `<service>-en.json`（23 个）在同一目录并存、为 en 权威资产，由本仓独立维护
（源 = monorepo autional/scripts/translate_swagger.py 的既有 -en 导出；跟版口径见
README「Specs 双源」与 B2 reference 执行报告）。en 侧缺源 4 个 = captcha3d / config /
saml / stream，构建期回退读 zh 原版并在页内标注。故脚本不再清理 `*-en.json`——cn 单仓时代
的清理逻辑已移除，避免误删 en 权威文件。

发布规则：`responses` 为空的 operation 会被丢弃并打印（上游 swag 注解缺失时产物非法，
Scalar 只能渲染空响应）；补齐注解后自动回来。

Usage:
    python scripts/sync-specs-zh.py            # 写入 public/specs/*.json
    python scripts/sync-specs-zh.py --check    # 只比对，漂移则 exit 1（CI 门禁）
"""

import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

SPECS_SRC = r"D:\go\auth_ms_new\docker\specs"
PORTAL_SPECS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public", "specs")

# Public gateway entry. The specs ship without host/schemes/basePath, so Scalar
# resolves sample requests against the docs origin (reference.autional.cn),
# which 404s on every /api/v1 path. The only public entry that routes these
# services is the gateway: https://api.autional.cn/bff/<short>/api/v1/...
# Route source of truth: shared/service-gateway/configs/service/gateway-service.yaml
GATEWAY_HOST = "api.autional.cn"

# service name -> gateway short name (27-slot demoServiceHosts map in
# shared/service-gateway/demo/embed.go, mirrored by the ingress template).
# Only services with a public /bff route are listed; the remaining six
# (config, thirdparty, hash-standard, hash-sm, stream, gateway) have no public
# REST surface and keep their specs unmodified.
GATEWAY_SHORT = {
    "identity-service": "identity",
    "profile-service": "profile",
    "tenant-service": "tenant",
    "session-service": "session",
    "mfa-service": "mfa",
    "oauth-service": "oauth",
    "wallet-service": "wallet",
    "point-service": "point",
    "audit-service": "audit",
    "notification-service": "notification",
    "communication-service": "communication",
    "storage-service": "storage",
    "billing-service": "billing",
    "compliance-service": "compliance",
    "status-service": "status",
    "secret-service": "secret",
    "saml-service": "saml",
    "pay-service": "pay",
    "verification-service": "verification",
    "rbac-service": "rbac",
    "captcha3d-service": "captcha3d",
}

# Upstream descriptions for these services are English-only; the portal is zh-CN.
DESC_ZH = {
    "pay-service": "Autional 支付服务——处理支付、退款、支付渠道、Webhook 与对账。",
    "thirdparty-service": "第三方集成服务——提供 CAPTCHA 与外部供应商集成能力。",
    "hash-service-standard": "Argon2id 密码哈希服务（标准配置）。gRPC-only，不经 API 网关暴露。",
    "hash-service-sm": "国密密码哈希服务（PBKDF2-SM3 变体）。gRPC-only，不经 API 网关暴露。",
}

SERVICES = [
    "identity-service", "profile-service", "tenant-service", "session-service",
    "mfa-service", "oauth-service", "wallet-service", "point-service",
    "audit-service", "notification-service", "communication-service",
    "storage-service", "billing-service", "compliance-service", "status-service",
    "secret-service", "saml-service", "pay-service", "thirdparty-service",
    "verification-service", "rbac-service", "gateway-service",
    "hash-service-standard", "hash-service-sm", "captcha3d-service", "config-service",
    "stream-service",
]

# Display names used across the .cn portals (nav, page titles, spec titles).
TITLES = {
    "identity-service": "身份服务",
    "profile-service": "用户资料服务",
    "tenant-service": "租户服务",
    "session-service": "会话服务",
    "mfa-service": "多因素认证服务",
    "oauth-service": "OAuth 服务",
    "wallet-service": "钱包服务",
    "point-service": "积分服务",
    "audit-service": "审计服务",
    "notification-service": "通知服务",
    "communication-service": "通信服务",
    "storage-service": "存储服务",
    "billing-service": "计费服务",
    "compliance-service": "合规服务",
    "status-service": "状态服务",
    "secret-service": "密钥服务",
    "saml-service": "SAML 服务",
    "pay-service": "支付服务",
    "thirdparty-service": "第三方服务",
    "verification-service": "身份验证服务",
    "rbac-service": "RBAC 服务",
    "gateway-service": "网关服务",
    "hash-service-standard": "密码哈希服务",
    "hash-service-sm": "国密哈希服务",
    "captcha3d-service": "3D 验证码服务",
    "config-service": "配置中心服务",
    "stream-service": "实时事件流服务",
}


def rebrand(node):
    """Upstream descriptions/examples say `AuthMS`; the portals are Autional.
    All three casings appear upstream (e.g. `https://authms.example.com`), so
    replace each variant — the patterns are mutually exclusive."""
    if isinstance(node, str):
        return (
            node.replace("AuthMS", "Autional")
            .replace("AUTHMS", "AUTIONAL")
            .replace("authms", "autional")
        )
    if isinstance(node, list):
        return [rebrand(v) for v in node]
    if isinstance(node, dict):
        return {k: rebrand(v) for k, v in node.items()}
    return node


METHODS = ("get", "put", "post", "delete", "options", "head", "patch")


def strip_invalid_operations(spec: dict) -> list[str]:
    """丢弃 responses 为空的操作（上游 swag 注解缺失）。

    发布契约必须是合法 Swagger 2.0：`responses` 为空的 operation 会被
    校验器判错、Scalar 只能渲染空响应。上游补齐注解后会自动回来，
    因此这里丢弃并打印，不静默。
    """
    dropped = []
    for path, item in list((spec.get("paths") or {}).items()):
        if not isinstance(item, dict):
            continue
        for method in METHODS:
            op = item.get(method)
            if isinstance(op, dict) and not op.get("responses"):
                dropped.append(f"{method.upper()} {path}")
                del item[method]
        if not any(m in item for m in METHODS):
            del spec["paths"][path]
    return dropped


def main() -> int:
    check = "--check" in sys.argv
    if not os.path.isdir(SPECS_SRC):
        print(f"ERROR: source not found: {SPECS_SRC}")
        return 1

    os.makedirs(PORTAL_SPECS, exist_ok=True)

    written = 0
    changed = 0
    for svc in SERVICES:
        src = os.path.join(SPECS_SRC, svc, "swagger.json")
        if not os.path.isfile(src):
            print(f"  [WARN] missing source spec: {svc}")
            continue

        with open(src, encoding="utf-8") as fh:
            spec = rebrand(json.load(fh))

        info = spec.setdefault("info", {})
        info["title"] = f"{TITLES[svc]} API"
        if svc in DESC_ZH:
            info["description"] = DESC_ZH[svc]

        short = GATEWAY_SHORT.get(svc)
        if short:
            base = spec.get("basePath") or ""
            if base == "/":
                base = ""
            spec["host"] = GATEWAY_HOST
            spec["schemes"] = ["https"]
            spec["basePath"] = f"/bff/{short}{base}"

        dropped = strip_invalid_operations(spec)
        if dropped:
            print(f"  [WARN] {svc}: dropped {len(dropped)} operation(s) without responses "
                  f"(upstream swag 注解缺失): {', '.join(dropped[:3])}"
                  f"{' …' if len(dropped) > 3 else ''}")

        dst = os.path.join(PORTAL_SPECS, f"{svc}.json")
        payload = json.dumps(spec, ensure_ascii=False, indent=2)
        old = None
        if os.path.isfile(dst):
            with open(dst, encoding="utf-8") as fh:
                old = fh.read()
        if check:
            if old != payload:
                changed += 1
                print(f"  [DRIFT] {svc}: 门户规范与上游快照不一致")
            written += 1
            continue
        with open(dst, "w", encoding="utf-8", newline="") as fh:
            fh.write(payload)
        written += 1

    # （B2 并入后）不再清理 `*-en.json`——它们是 en 权威规范（本仓 23 个资产，
    # 缺源 4 个：captcha3d / config / saml / stream），由 en 侧独立维护；
    # 本脚本只负责 zh 侧 `X.json`。
    if check:
        print(f"checked {written} Chinese specs, {changed} drifted")
        return 1 if changed else 0

    print(f"wrote {written} Chinese specs -> {PORTAL_SPECS}")
    return 0



if __name__ == "__main__":
    raise SystemExit(main())
