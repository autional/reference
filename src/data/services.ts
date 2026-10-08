/**
 * 27 服务权威清单（结构单源；展示名归 i18n `services.*` 键，双语）：
 * - SERVICES 顺序/集合 = cn 基线 [service].astro getStaticPaths，与 public/specs 的 27 个 zh 规范一一对应；
 * - GATEWAY_SHORT = scripts/sync-specs-zh.py 同源映射（路由真源：
 *   shared/service-gateway/configs/service/gateway-service.yaml）；无公网 /bff 入口的六服务不在此表。
 * - SERVICE_GROUPS = cn 基线 index.astro 六分组（group 名归 i18n `index.groups.*` 键）。
 */

export const SERVICES: readonly string[] = [
  'identity-service', 'profile-service', 'tenant-service', 'session-service',
  'mfa-service', 'oauth-service', 'wallet-service', 'point-service',
  'audit-service', 'notification-service', 'communication-service',
  'storage-service', 'billing-service', 'compliance-service', 'status-service',
  'secret-service', 'saml-service', 'pay-service', 'thirdparty-service',
  'verification-service', 'rbac-service', 'gateway-service',
  'hash-service-standard', 'hash-service-sm', 'captcha3d-service',
  'config-service', 'stream-service',
];

/** 公开网关短名（与 scripts/sync-specs-zh.py GATEWAY_SHORT 同源）。 */
export const GATEWAY_SHORT: Readonly<Record<string, string>> = {
  'identity-service': 'identity',
  'profile-service': 'profile',
  'tenant-service': 'tenant',
  'session-service': 'session',
  'mfa-service': 'mfa',
  'oauth-service': 'oauth',
  'wallet-service': 'wallet',
  'point-service': 'point',
  'audit-service': 'audit',
  'notification-service': 'notification',
  'communication-service': 'communication',
  'storage-service': 'storage',
  'billing-service': 'billing',
  'compliance-service': 'compliance',
  'status-service': 'status',
  'secret-service': 'secret',
  'saml-service': 'saml',
  'pay-service': 'pay',
  'verification-service': 'verification',
  'rbac-service': 'rbac',
  'captcha3d-service': 'captcha3d',
};

export interface ServiceGroup {
  /** i18n 键尾（index.groups.<key>）。 */
  key: string;
  svcs: readonly string[];
}

export const SERVICE_GROUPS: readonly ServiceGroup[] = [
  { key: 'identity', svcs: ['identity-service', 'profile-service', 'tenant-service', 'session-service', 'mfa-service', 'oauth-service'] },
  { key: 'assets', svcs: ['wallet-service', 'point-service', 'pay-service', 'billing-service'] },
  { key: 'audit', svcs: ['audit-service', 'notification-service', 'communication-service'] },
  { key: 'storage', svcs: ['storage-service', 'compliance-service', 'status-service'] },
  { key: 'security', svcs: ['secret-service', 'saml-service', 'thirdparty-service', 'verification-service', 'rbac-service', 'captcha3d-service'] },
  { key: 'infrastructure', svcs: ['gateway-service', 'hash-service-standard', 'hash-service-sm', 'config-service', 'stream-service'] },
];
