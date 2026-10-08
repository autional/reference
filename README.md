# Autional API Reference Portal

**Domain**: reference.autional.cn
**Stack**: Astro 5 + Tailwind 3.4 + Scalar UI
**Repository**: [github.com/autional-cn/reference](https://github.com/autional-cn/reference)

## Development

```bash
pnpm install
pnpm dev      # http://localhost:4434
pnpm build    # Static output to dist/
```

## Content Source

Chinese Swagger specs synced from the AuthMS backend monorepo:
`D:\go\auth_ms_new\docker\specs\<service>\swagger.json` → `public/specs/`

## Update Content

```bash
python D:\ws\autional-cn\sites\reference\scripts\sync-specs-zh.py   # sync + rebrand
pnpm build                                                          # rebuild
```
