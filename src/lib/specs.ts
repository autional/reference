/**
 * 规范文件解析单点（B2 单源双区；契约见 23 执行卡 §5）。
 *
 * public/specs 双源并存：
 * - zh 侧 = `<svc>.json`（27 个；scripts/sync-specs-zh.py 自 monorepo 同步，路由真源
 *   shared/service-gateway/configs/service/gateway-service.yaml）；
 * - en 侧 = `<svc>-en.json`（24 个；com 存量保留为 en 权威，en 侧唯三缺源 =
 *   captcha3d / config / stream，源与跟版口径见 README 与 B2 执行报告）。
 *
 * 页面按构建语言取规（SPEC_SUFFIX 由 DEFAULT_LANG 推导）：en 侧唯三缺源服务
 * 回退读 zh 原版 `X.json`，由页面 fallbackNote 可见标注（产品裁定见执行报告）。
 */
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { SPEC_SUFFIX } from './site-env';

export interface SpecRef {
  /** 实际读取的规范文件名（相对 public/specs）。 */
  file: string;
  /** 语言缺源回退：en 侧读 zh 原版时为 true。 */
  fallback: boolean;
}

export interface SpecShape {
  info?: { title?: string; description?: string };
  paths?: Record<string, unknown>;
}

const specsDir = (): string => join(process.cwd(), 'public', 'specs');

/** 按当前构建语言解析服务的规范文件；en 缺源回退 zh 原版。 */
export function specForService(service: string): SpecRef {
  const preferred = `${service}${SPEC_SUFFIX}.json`;
  if (existsSync(join(specsDir(), preferred))) return { file: preferred, fallback: false };
  return { file: `${service}.json`, fallback: SPEC_SUFFIX !== '' };
}

/** 端点计数：paths 下非 parameters 的方法数（与 cn 基线口径一致）。 */
export function countEndpoints(spec: SpecShape): number {
  let n = 0;
  for (const methods of Object.values(spec.paths ?? {})) {
    if (typeof methods === 'object' && methods !== null) {
      n += Object.keys(methods).filter((k) => k !== 'parameters').length;
    }
  }
  return n;
}

/** 读取并解析规范；文件缺失 / JSON 损坏返回 null（调用方回退默认元信息）。 */
export function readSpec(file: string): { spec: SpecShape; endpoints: number } | null {
  try {
    const spec = JSON.parse(readFileSync(join(specsDir(), file), 'utf-8')) as SpecShape;
    return { spec, endpoints: countEndpoints(spec) };
  } catch {
    return null;
  }
}
