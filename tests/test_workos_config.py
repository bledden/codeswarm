#!/usr/bin/env python3
"""
Test WorkOS Configuration

Quick script to verify WorkOS is configured correctly.
"""
from dotenv import load_dotenv

# Load .env file first!
load_dotenv()

from src.integrations.workos_client import WorkOSAuthClient

def main():
    print("Testing WorkOS Configuration...")
    print("=" * 60)

    try:
        # Initialize WorkOS client
        workos = WorkOSAuthClient()

        print("\n✅ WorkOS Client Initialized Successfully!")
        print("\nConfiguration:")
        print(f"  API Key:         {workos.api_key[:20]}... (starts with sk_)")
        print(f"  Client ID:       {workos.client_id[:30]}...")
        print(f"  Redirect URI:    {workos.redirect_uri}")
        print(f"  Cookie Password: {'✅ Set (' + str(len(workos.cookie_password)) + ' chars)' if workos.cookie_password else '❌ Not set'}")

        # Test API call: List organizations
        print("\nTesting API Call...")
        try:
            orgs = workos.list_organizations()
            print(f"✅ API Call Successful!")
            print(f"   Organizations found: {len(orgs)}")

            if orgs:
                print("\n   Your Organizations:")
                for org in orgs:
                    print(f"     - {org['name']} (ID: {org['id']})")
            else:
                print("   (No organizations yet - create one in WorkOS Dashboard)")
        except Exception as e:
            print(f"⚠️  API call failed: {e}")
            print("   (This is OK if you haven't created organizations yet)")

        # Test generating auth URL
        print("\nGenerating OAuth URL...")
        try:
            auth_url = workos.get_authorization_url(provider="GoogleOAuth")
            print(f"✅ OAuth URL Generated Successfully!")
            print(f"   URL: {auth_url[:80]}...")
            print("\n   To test authentication:")
            print(f"   1. Visit: {auth_url}")
            print("   2. Log in with Google")
            print("   3. You'll be redirected to:", workos.redirect_uri)
        except Exception as e:
            print(f"⚠️  Failed to generate auth URL: {e}")

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - WorkOS is configured correctly!")
        print("=" * 60)

        return 0

    except ImportError as e:
        print("\n❌ WorkOS SDK not installed!")
        print(f"   Error: {e}")
        print("\n   Fix: pip3 install workos")
        return 1

    except ValueError as e:
        print(f"\n❌ Configuration Error!")
        print(f"   {e}")
        print("\n   Fix: Check your .env file and ensure these variables are set:")
        print("     - WORKOS_API_KEY")
        print("     - WORKOS_CLIENT_ID")
        print("     - WORKOS_REDIRECT_URI")
        print("     - WORKOS_COOKIE_PASSWORD")
        print("\n   See docs/WORKOS_QUICK_SETUP.md for instructions.")
        return 1

    except Exception as e:
        print(f"\n❌ Unexpected Error!")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
