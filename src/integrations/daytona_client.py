"""
Daytona Client for Development Workspace Integration
Automated development environment and code deployment
"""
import os
from typing import Dict, Any, List, Optional
import aiohttp
from aiohttp import ClientTimeout
import logging

logger = logging.getLogger(__name__)


class DaytonaClient:
    """
    Client for Daytona workspace integration

    Provides:
    1. Create development workspaces
    2. Deploy generated code
    3. Run tests in isolated environments
    4. Manage workspace lifecycle
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        workspace_id: Optional[str] = None
    ):
        """Initialize Daytona client

        Args:
            api_key: Daytona API key (starts with dtna_)
            api_url: Daytona API URL (e.g., https://api.daytona.io)
            workspace_id: Optional default workspace ID
        """
        self.api_key = api_key or os.getenv("DAYTONA_API_KEY")
        self.api_url = api_url or os.getenv("DAYTONA_API_URL", "https://api.daytona.io")
        self.workspace_id = workspace_id or os.getenv("DAYTONA_WORKSPACE_ID", "")

        if not self.api_key or self.api_key == "your_daytona_key_here":
            raise ValueError(
                " NO DAYTONA API KEY FOUND!\n"
                "Please set DAYTONA_API_KEY in .env file.\n"
                "See COMPLETE_SETUP_GUIDE.md Section 5 for instructions."
            )

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        self.session: Optional[aiohttp.ClientSession] = None

        logger.info(f"[DAYTONA]  Client initialized (API: {self.api_url})")

    async def __aenter__(self):
        """Context manager entry"""
        timeout = ClientTimeout(total=300, connect=10, sock_read=300)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()

    async def create_session_if_needed(self):
        """Create session if not exists"""
        if not self.session:
            timeout = ClientTimeout(total=300, connect=10, sock_read=300)
            self.session = aiohttp.ClientSession(timeout=timeout)

    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def create_workspace(
        self,
        name: str,
        repository_url: Optional[str] = None,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Create a new development workspace

        Args:
            name: Workspace name
            repository_url: Optional git repository to clone
            branch: Git branch to checkout

        Returns:
            Workspace info with {id, name, status, url}
        """
        await self.create_session_if_needed()

        payload = {
            "name": name,
            "repository_url": repository_url,
            "branch": branch
        }

        try:
            async with self.session.post(
                f"{self.api_url}/workspaces",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    workspace = {
                        "id": data.get("id"),
                        "name": data.get("name"),
                        "status": data.get("status"),
                        "url": data.get("url")
                    }

                    logger.info(f"[DAYTONA]  Created workspace: {name}")
                    return workspace
                else:
                    error = await response.text()
                    logger.error(f"[DAYTONA]  Failed to create workspace: {error}")
                    raise Exception(f"Failed to create workspace: {error}")

        except Exception as e:
            logger.error(f"[DAYTONA]  Error creating workspace: {e}")
            raise

    async def deploy_code(
        self,
        workspace_id: Optional[str] = None,
        files: Dict[str, str] = None,
        run_command: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Deploy generated code to workspace

        Args:
            workspace_id: Workspace ID (uses default if not provided)
            files: Dict mapping file_path -> file_content
            run_command: Optional command to run after deployment

        Returns:
            Deployment info with {status, output, url}
        """
        await self.create_session_if_needed()

        workspace_id = workspace_id or self.workspace_id
        if not workspace_id:
            raise ValueError("No workspace ID provided")

        payload = {
            "files": files or {},
            "run_command": run_command
        }

        try:
            async with self.session.post(
                f"{self.api_url}/workspaces/{workspace_id}/deploy",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    deployment = {
                        "status": data.get("status"),
                        "output": data.get("output"),
                        "url": data.get("url")
                    }

                    logger.info(f"[DAYTONA]  Deployed code to workspace {workspace_id}")
                    return deployment
                else:
                    error = await response.text()
                    logger.error(f"[DAYTONA]  Deployment failed: {error}")
                    raise Exception(f"Deployment failed: {error}")

        except Exception as e:
            logger.error(f"[DAYTONA]  Error deploying code: {e}")
            raise

    async def run_tests(
        self,
        workspace_id: Optional[str] = None,
        test_command: str = "npm test"
    ) -> Dict[str, Any]:
        """
        Run tests in workspace

        Args:
            workspace_id: Workspace ID (uses default if not provided)
            test_command: Test command to run

        Returns:
            Test results with {success, output, coverage}
        """
        await self.create_session_if_needed()

        workspace_id = workspace_id or self.workspace_id
        if not workspace_id:
            raise ValueError("No workspace ID provided")

        payload = {
            "command": test_command
        }

        try:
            async with self.session.post(
                f"{self.api_url}/workspaces/{workspace_id}/run",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    results = {
                        "success": data.get("exit_code") == 0,
                        "output": data.get("output"),
                        "exit_code": data.get("exit_code")
                    }

                    logger.info(
                        f"[DAYTONA]  Tests {'passed' if results['success'] else 'failed'}"
                    )
                    return results
                else:
                    error = await response.text()
                    logger.error(f"[DAYTONA]  Test execution failed: {error}")
                    raise Exception(f"Test execution failed: {error}")

        except Exception as e:
            logger.error(f"[DAYTONA]  Error running tests: {e}")
            raise

    async def get_workspace_status(
        self,
        workspace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get workspace status

        Args:
            workspace_id: Workspace ID (uses default if not provided)

        Returns:
            Status info with {id, name, status, created_at}
        """
        await self.create_session_if_needed()

        workspace_id = workspace_id or self.workspace_id
        if not workspace_id:
            raise ValueError("No workspace ID provided")

        try:
            async with self.session.get(
                f"{self.api_url}/workspaces/{workspace_id}",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    status = {
                        "id": data.get("id"),
                        "name": data.get("name"),
                        "status": data.get("status"),
                        "created_at": data.get("created_at"),
                        "url": data.get("url")
                    }

                    logger.info(f"[DAYTONA]  Workspace status: {status['status']}")
                    return status
                else:
                    error = await response.text()
                    logger.error(f"[DAYTONA]  Failed to get status: {error}")
                    raise Exception(f"Failed to get workspace status: {error}")

        except Exception as e:
            logger.error(f"[DAYTONA]  Error getting workspace status: {e}")
            raise

    async def list_workspaces(self) -> List[Dict[str, Any]]:
        """
        List all workspaces

        Returns:
            List of workspace dictionaries
        """
        await self.create_session_if_needed()

        try:
            async with self.session.get(
                f"{self.api_url}/workspaces",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    workspaces = [
                        {
                            "id": w.get("id"),
                            "name": w.get("name"),
                            "status": w.get("status")
                        }
                        for w in data.get("workspaces", [])
                    ]

                    logger.info(f"[DAYTONA]  Retrieved {len(workspaces)} workspaces")
                    return workspaces
                else:
                    error = await response.text()
                    logger.error(f"[DAYTONA]  Failed to list workspaces: {error}")
                    return []

        except Exception as e:
            logger.error(f"[DAYTONA]  Error listing workspaces: {e}")
            return []

    async def delete_workspace(
        self,
        workspace_id: Optional[str] = None
    ) -> bool:
        """
        Delete a workspace

        Args:
            workspace_id: Workspace ID (uses default if not provided)

        Returns:
            True if deleted successfully
        """
        await self.create_session_if_needed()

        workspace_id = workspace_id or self.workspace_id
        if not workspace_id:
            raise ValueError("No workspace ID provided")

        try:
            async with self.session.delete(
                f"{self.api_url}/workspaces/{workspace_id}",
                headers=self.headers
            ) as response:
                if response.status == 204:
                    logger.info(f"[DAYTONA]  Deleted workspace {workspace_id}")
                    return True
                else:
                    error = await response.text()
                    logger.error(f"[DAYTONA]  Failed to delete: {error}")
                    return False

        except Exception as e:
            logger.error(f"[DAYTONA]  Error deleting workspace: {e}")
            return False


async def test_daytona():
    """Test Daytona client"""
    try:
        async with DaytonaClient() as client:
            # Test listing workspaces
            workspaces = await client.list_workspaces()
            print(f" Retrieved {len(workspaces)} workspaces")

            if workspaces:
                print(f"   First workspace: {workspaces[0]['name']}")

            # If we have a workspace, get its status
            if client.workspace_id:
                status = await client.get_workspace_status()
                print(f" Workspace status: {status['status']}")
            else:
                print("  No default workspace configured")

            return True

    except ValueError as e:
        print(f"  Daytona credentials not configured: {e}")
        print("   See COMPLETE_SETUP_GUIDE.md Section 5")
        return False
    except Exception as e:
        print(f" Daytona test failed: {e}")
        return False


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_daytona())
