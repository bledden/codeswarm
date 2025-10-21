export type ValidationStatus = 'default' | 'error' | 'success';

export interface ApiResponse<T = unknown> {
  ok: boolean;
  message: string;
  data?: T;
}

export interface SubscriptionRequest {
  email: string;
}

export type SubscriptionStatus = 'subscribed' | 'pending';

export interface EmailSubscriptionResult {
  status: SubscriptionStatus;
  idempotent?: boolean;
  provider?: string;
}