import type { EmailProvider } from "./provider";
import type { EmailSubscriptionResult } from "@/types";

/**
 * Mailchimp provider integrating with v3 API
 * Docs: https://mailchimp.com/developer/marketing/api/list-members/add-member-to-list/
 */
type MailchimpConfig = {
  apiKey: string;
  audienceId: string;
  doubleOptIn?: boolean;
};

type MailchimpErrorResponse = {
  type?: string;
  title?: string;
  status?: number;
  detail?: string;
  instance?: string;
};

export class MailchimpEmailProvider implements EmailProvider {
  readonly name = "mailchimp";
  private readonly apiKey: string;
  private readonly dc: string;
  private readonly audienceId: string;
  private readonly doubleOptIn: boolean;

  constructor(config: MailchimpConfig) {
    this.apiKey = config.apiKey;
    const parts = this.apiKey.split("-");
    if (parts.length < 2) {
      throw new Error("Invalid Mailchimp API key format. Expected suffix with data center, e.g. '-us21'");
    }
    this.dc = parts[parts.length - 1];
    this.audienceId = config.audienceId;
    this.doubleOptIn = Boolean(config.doubleOptIn ?? true);
  }

  private endpoint(path: string) {
    return `https://${this.dc}.api.mailchimp.com/3.0${path}`;
  }

  async subscribe(email: string): Promise<EmailSubscriptionResult> {
    // Mailchimp recommends status 'pending' for double opt-in, 'subscribed' for single
    const desiredStatus = this.doubleOptIn ? "pending" : "subscribed";

    try {
      const res = await fetch(this.endpoint(`/lists/${this.audienceId}/members`), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // Basic auth with any username and the API key as password
          "Authorization": `Basic ${Buffer.from(`anystring:${this.apiKey}`).toString("base64")}`
        },
        body: JSON.stringify({
          email_address: email,
          status: desiredStatus
        })
      });

      if (res.ok) {
        return { status: desiredStatus, idempotent: false, provider: this.name };
      }

      const err: MailchimpErrorResponse = await res.json().catch(() => ({}));
      // Handle idempotency: member already exists
      if (err?.title?.toLowerCase().includes("member exists")) {
        return { status: desiredStatus, idempotent: true, provider: this.name };
      }

      // If the email was previously unsubscribed, Mailchimp may require resubscribe via 'status_if_new'
      if (err?.title?.toLowerCase().includes("forgotten")) {
        // We could try a PUT to /lists/{list_id}/members/{subscriber_hash}
        // but for safety we return an instructive message
        throw new Error("This email was previously removed and cannot be resubscribed automatically.");
      }

      const status = err?.status ?? res.status;
      const message = err?.detail || err?.title || `Mailchimp error (status ${status})`;
      throw new Error(message);
    } catch (e: any) {
      // Map any error to a thrown error for the API layer to handle
      throw new Error(e?.message || "Unknown error from Mailchimp");
    }
  }
}