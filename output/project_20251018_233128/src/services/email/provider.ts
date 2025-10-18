import type { EmailSubscriptionResult } from "@/types";
import { MailchimpEmailProvider } from "./mailchimp";

/**
 * Provider abstraction allows swapping out email vendors without changing business logic.
 */
export interface EmailProvider {
  subscribe(email: string): Promise<EmailSubscriptionResult>;
  readonly name: string;
}

/**
 * Null provider: logs subscriptions during development or if provider not configured.
 */
class LogEmailProvider implements EmailProvider {
  readonly name = "log";
  async subscribe(email: string): Promise<EmailSubscriptionResult> {
    console.log(`[email:log] Subscribing ${email}`);
    // Simulate as pending to reflect double opt-in like behavior
    return { status: "pending", idempotent: true, provider: this.name };
  }
}

/**
 * Factory for the email provider based on environment configuration
 */
export function createEmailProvider(): EmailProvider {
  const provider = (process.env.EMAIL_PROVIDER || "log").toLowerCase();

  if (provider === "mailchimp") {
    const apiKey = process.env.MAILCHIMP_API_KEY;
    const audienceId = process.env.MAILCHIMP_AUDIENCE_ID;
    if (!apiKey || !audienceId) {
      console.warn("MAILCHIMP_API_KEY or MAILCHIMP_AUDIENCE_ID missing. Falling back to log provider.");
      return new LogEmailProvider();
    }
    return new MailchimpEmailProvider({
      apiKey,
      audienceId,
      doubleOptIn: String(process.env.MAILCHIMP_DOUBLE_OPT_IN || "true").toLowerCase() === "true"
    });
  }

  return new LogEmailProvider();
}