# Autional API Reference Portal

**Domain**: reference.autional.com
**Stack**: Astro 5 + Tailwind 3.4 + Scalar UI
**Repository**: [github.com/autional/reference](https://github.com/autional/reference)

## Development

```bash
pnpm install
pnpm dev      # http://localhost:4434
pnpm build    # Static output to dist/
```

## Content Source

English Swagger specs synced from the AuthMS backend monorepo:
`D:\go\auth_ms_new\docker\specs\*-en.json` → `public/specs/`

## Update Content

```bash
cd D:\go\auth_ms_new
python autional/scripts/translate_swagger.py   # re-translate if needed
python autional/scripts/sync_specs.py           # sync to portal
cd D:\autional\reference && pnpm build         # rebuild
```
