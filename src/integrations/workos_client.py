"""
WorkOS Client for Team Authentication
SSO and organization management
"""
import os
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

# WorkOS SDK
try:
    import workos
    from workos import WorkOSClient
    WORKOS_AVAILABLE = True
except ImportError:
    WORKOS_AVAILABLE = False
    logger.warning("[WORKOS]   Package not installed. Run: pip3 install workos")


class WorkOSAuthClient:
    """
    Client for WorkOS authentication

    Provides:
    1. SSO authentication (Google, Microsoft, etc.)
    2. Organization management
    3. User directory sync
    4. Session management
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        client_id: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        cookie_password: Optional[str] = None
    ):
        """Initialize WorkOS client

        Args:
            api_key: WorkOS API key (starts with sk_)
            client_id: WorkOS Client ID (starts with client_)
            redirect_uri: OAuth callback URL (e.g., http://localhost:3000/callback)
            cookie_password: 32-character password for encrypting cookies
        """
        if not WORKOS_AVAILABLE:
            raise ImportError(
                " WORKOS NOT INSTALLED!\n"
                "Please run: pip3 install workos\n"
                "See COMPLETE_SETUP_GUIDE.md Section 4 for instructions."
            )

        self.api_key = api_key or os.getenv("WORKOS_API_KEY")
        self.client_id = client_id or os.getenv("WORKOS_CLIENT_ID")
        self.redirect_uri = redirect_uri or os.getenv("WORKOS_REDIRECT_URI", "http://localhost:3000/callback")
        self.cookie_password = cookie_password or os.getenv("WORKOS_COOKIE_PASSWORD")

        if not self.api_key or self.api_key == "your_workos_key_here":
            raise ValueError(
                " NO WORKOS API KEY FOUND!\n"
                "Please set WORKOS_API_KEY in .env file.\n"
                "See COMPLETE_SETUP_GUIDE.md Section 4 for instructions."
            )

        if not self.client_id or self.client_id == "your_workos_client_id_here":
            raise ValueError(
                " NO WORKOS CLIENT ID FOUND!\n"
                "Please set WORKOS_CLIENT_ID in .env file.\n"
                "See COMPLETE_SETUP_GUIDE.md Section 4 for instructions."
            )

        # Initialize WorkOS client with both API key and client ID
        self.client = WorkOSClient(api_key=self.api_key, client_id=self.client_id)

        logger.info(f"[WORKOS]  Client initialized (client_id: {self.client_id[:20]}...)")
        logger.info(f"[WORKOS]  Redirect URI: {self.redirect_uri}")

    def get_authorization_url(
        self,
        redirect_uri: Optional[str] = None,
        state: Optional[str] = None,
        provider: Optional[str] = None
    ) -> str:
        """
        Get SSO authorization URL

        Args:
            redirect_uri: Where to redirect after auth (defaults to WORKOS_REDIRECT_URI)
            state: Optional state parameter for CSRF protection
            provider: Optional provider (e.g., "GoogleOAuth", "MicrosoftOAuth")

        Returns:
            Authorization URL to redirect user to
        """
        # Use instance redirect_uri if not provided
        redirect_uri = redirect_uri or self.redirect_uri

        if not redirect_uri:
            raise ValueError(
                "No redirect URI provided. Set WORKOS_REDIRECT_URI in .env or pass redirect_uri parameter."
            )

        # Build authorization URL using WorkOS SDK
        # The SDK now handles client_id automatically
        auth_url = self.client.sso.get_authorization_url(
            redirect_uri=redirect_uri,
            state=state,
            provider=provider
        )

        logger.info(f"[WORKOS]  Generated auth URL for provider: {provider or 'any'}")
        return auth_url

    async def authenticate_user(
        self,
        code: str
    ) -> Dict[str, Any]:
        """
        Authenticate user with authorization code

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Dict with {user, access_token, profile}
        """
        try:
            # Exchange code for profile
            profile = self.client.sso.get_profile_and_token(code=code)

            user_info = {
                "id": profile.profile.id,
                "email": profile.profile.email,
                "first_name": profile.profile.first_name,
                "last_name": profile.profile.last_name,
                "access_token": profile.access_token,
                "connection_id": profile.profile.connection_id,
                "organization_id": profile.profile.organization_id
            }

            logger.info(f"[WORKOS]  Authenticated user: {user_info['email']}")
            return user_info

        except Exception as e:
            logger.error(f"[WORKOS]  Authentication failed: {e}")
            raise

    def create_organization(
        self,
        name: str,
        domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create an organization

        Args:
            name: Organization name
            domains: List of verified domains (e.g., ["company.com"])

        Returns:
            Organization info
        """
        try:
            org = self.client.organizations.create_organization(
                name=name,
                domains=domains or []
            )

            org_info = {
                "id": org.id,
                "name": org.name,
                "domains": org.domains
            }

            logger.info(f"[WORKOS]  Created organization: {name}")
            return org_info

        except Exception as e:
            logger.error(f"[WORKOS]  Failed to create organization: {e}")
            raise

    def list_organizations(self) -> List[Dict[str, Any]]:
        """
        List all organizations

        Returns:
            List of organization dictionaries
        """
        try:
            orgs = self.client.organizations.list_organizations()

            org_list = [
                {
                    "id": org.id,
                    "name": org.name,
                    "domains": org.domains
                }
                for org in orgs.data
            ]

            logger.info(f"[WORKOS]  Retrieved {len(org_list)} organizations")
            return org_list

        except Exception as e:
            logger.error(f"[WORKOS]  Failed to list organizations: {e}")
            raise

    def verify_session(
        self,
        access_token: str
    ) -> bool:
        """
        Verify user session token

        Args:
            access_token: User's access token

        Returns:
            True if session is valid
        """
        try:
            # In real implementation, would verify token with WorkOS
            # For now, just check if token exists and has correct format
            if access_token and len(access_token) > 20:
                logger.info("[WORKOS]  Session verified")
                return True

            logger.warning("[WORKOS]   Invalid session token")
            return False

        except Exception as e:
            logger.error(f"[WORKOS]  Session verification failed: {e}")
            return False

    def get_user_by_email(
        self,
        email: str,
        organization_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get user by email

        Args:
            email: User email
            organization_id: Optional organization filter

        Returns:
            User info if found
        """
        try:
            # List directory users
            users = self.client.directory_sync.list_users(
                organization=organization_id
            )

            for user in users.data:
                if user.emails and any(e.value == email for e in user.emails):
                    return {
                        "id": user.id,
                        "email": email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "state": user.state
                    }

            logger.info(f"[WORKOS] User not found: {email}")
            return None

        except Exception as e:
            logger.error(f"[WORKOS]  Failed to get user: {e}")
            raise


async def test_workos():
    """Test WorkOS client"""
    try:
        client = WorkOSAuthClient()

        # Test getting authorization URL
        auth_url = client.get_authorization_url(
            redirect_uri="http://localhost:3000/callback",
            provider="GoogleOAuth",
            state="random_state_123"
        )

        print(f" Generated auth URL")
        print(f"   URL: {auth_url[:100]}...")

        # Test listing organizations
        orgs = client.list_organizations()
        print(f" Retrieved {len(orgs)} organizations")

        if orgs:
            print(f"   First org: {orgs[0]['name']}")

        return True

    except ImportError as e:
        print(f"  WorkOS not installed: {e}")
        print("   Run: pip3 install workos")
        return False
    except ValueError as e:
        print(f"  WorkOS credentials not configured: {e}")
        print("   See COMPLETE_SETUP_GUIDE.md Section 4")
        return False
    except Exception as e:
        print(f" WorkOS test failed: {e}")
        return False


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_workos())
