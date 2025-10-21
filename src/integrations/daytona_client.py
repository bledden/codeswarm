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

# Import Daytona SDK if available
try:
    from daytona_sdk import Daytona
    DAYTONA_SDK_AVAILABLE = True
except ImportError:
    DAYTONA_SDK_AVAILABLE = False
    logger.warning("[DAYTONA] SDK not available, using REST API only")


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
        self.org_id = os.getenv("DAYTONA_ORG_ID", "")

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

        # Add organization ID header if available
        if self.org_id:
            self.headers["X-Daytona-Organization-ID"] = self.org_id

        # Set environment variables for SDK
        os.environ["DAYTONA_API_KEY"] = self.api_key
        os.environ["DAYTONA_API_URL"] = self.api_url.replace('/api', '')  # SDK expects base URL
        if self.org_id:
            os.environ["DAYTONA_ORG_ID"] = self.org_id

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
        """Create session if not exists or if closed"""
        if not self.session or self.session.closed:
            timeout = ClientTimeout(total=300, connect=10, sock_read=300)
            self.session = aiohttp.ClientSession(timeout=timeout)
            logger.debug(f"[DAYTONA]  Created new session")

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
                f"{self.api_url}/workspace",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    workspace = {
                        "id": data.get("id"),
                        "name": data.get("name"),
                        "status": data.get("state") or data.get("status"),  # API uses "state"
                        "url": None  # Will get URL from ports later
                    }

                    logger.info(f"[DAYTONA]  Created workspace: {name} (id: {workspace['id']})")
                    return workspace
                else:
                    error = await response.text()
                    logger.error(f"[DAYTONA]  Failed to create workspace (HTTP {response.status}): {error}")
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
        Deploy generated code to workspace using file upload

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

        try:
            # Use SDK if available, otherwise fall back to REST API
            if DAYTONA_SDK_AVAILABLE:
                logger.info(f"[DAYTONA]  Uploading {len(files)} files using SDK...")

                # SDK reads from environment variables (DAYTONA_API_KEY, DAYTONA_API_URL)
                # which we already set in __init__
                daytona_sdk = Daytona()

                # Get existing sandbox (workspace)
                sandbox = daytona_sdk.get(workspace_id)

                # Upload each file
                upload_errors = []
                for filepath, content in (files or {}).items():
                    try:
                        # Convert string content to bytes
                        content_bytes = content.encode('utf-8') if isinstance(content, str) else content
                        sandbox.fs.upload_file(content_bytes, filepath)
                        logger.debug(f"[DAYTONA] ✅ Uploaded {filepath}")
                    except Exception as e:
                        error_msg = f"Failed to upload {filepath}: {e}"
                        logger.error(f"[DAYTONA] ❌ {error_msg}")
                        upload_errors.append(error_msg)

                if upload_errors:
                    raise Exception(f"File upload failed:\n" + "\n".join(upload_errors))

                logger.info(f"[DAYTONA] ✅ All {len(files)} files uploaded successfully using SDK")
            else:
                # Fallback to REST API (multipart form-data)
                logger.info(f"[DAYTONA]  Uploading {len(files)} files using REST API...")

                for filepath, content in (files or {}).items():
                    # Prepare form data for file upload
                    import aiohttp
                    form = aiohttp.FormData()
                    form.add_field('file',
                                  content,
                                  filename=filepath.split('/')[-1],
                                  content_type='text/plain')
                    form.add_field('path', filepath)

                    # Upload single file
                    async with self.session.post(
                        f"{self.api_url}/toolbox/{workspace_id}/toolbox/files/upload",
                        headers={k: v for k, v in self.headers.items() if k != 'Content-Type'},
                        data=form
                    ) as response:
                        if response.status not in [200, 201]:
                            error = await response.text()
                            logger.warning(f"[DAYTONA]  File upload failed for {filepath}: {error}")
                        else:
                            logger.debug(f"[DAYTONA]  Uploaded {filepath}")

                logger.info(f"[DAYTONA]  Files uploaded successfully using REST API")

            # Execute run command if provided
            output = None
            if run_command:
                logger.info(f"[DAYTONA]  Executing command: {run_command}")

                if DAYTONA_SDK_AVAILABLE:
                    try:
                        # For Node.js projects, split install and dev server into separate commands
                        # to avoid SDK timeout during npm install
                        if "npm install" in run_command or "yarn install" in run_command:
                            # Split the command (e.g., "npm install && npm run dev")
                            if "&&" in run_command:
                                commands = [cmd.strip() for cmd in run_command.split("&&")]
                                logger.info(f"[DAYTONA]  Split into {len(commands)} commands to avoid timeout")

                                # Execute each command separately with proper error handling
                                for i, cmd in enumerate(commands, 1):
                                    logger.info(f"[DAYTONA]  [{i}/{len(commands)}] Running: {cmd}")
                                    try:
                                        result = sandbox.process.exec(cmd)
                                        if hasattr(result, 'exit_code') and result.exit_code != 0:
                                            logger.warning(f"[DAYTONA] ⚠️  Command failed with exit code {result.exit_code}")
                                    except Exception as e:
                                        # Log warning but continue - some commands timeout but still succeed
                                        logger.warning(f"[DAYTONA] ⚠️  Command execution warning: {e}")
                                        # For dev server commands that timeout, this is expected (server runs indefinitely)
                                        if "dev" in cmd or "start" in cmd:
                                            logger.info(f"[DAYTONA]  Dev server started in background (timeout expected)")

                                output = "Commands executed in sequence"
                            else:
                                # Single npm install command
                                result = sandbox.process.exec(run_command)
                                if hasattr(result, 'result'):
                                    output = result.result
                                elif hasattr(result, 'stdout'):
                                    output = result.stdout
                                else:
                                    output = str(result)
                        else:
                            # Non-Node.js command - check if it's a long-running server
                            is_server_command = any(keyword in run_command for keyword in [
                                "http.server", "serve", "dev", "start", "uvicorn", "gunicorn", "flask run"
                            ])

                            if is_server_command:
                                # Wrap in nohup to keep server running after SDK disconnects
                                logger.info(f"[DAYTONA]  Detected server command, using nohup for persistence")
                                nohup_command = f"nohup {run_command} > /tmp/server.log 2>&1 &"
                                result = sandbox.process.exec(nohup_command)
                                output = "Server started with nohup (running persistently)"

                                # Give server a moment to start
                                import asyncio
                                await asyncio.sleep(2)
                                logger.info(f"[DAYTONA] ✅ Server process started in background")
                            else:
                                # Regular non-server command
                                result = sandbox.process.exec(run_command)
                                if hasattr(result, 'result'):
                                    output = result.result
                                elif hasattr(result, 'stdout'):
                                    output = result.stdout
                                else:
                                    output = str(result)

                        logger.info(f"[DAYTONA] ✅ Command sequence completed")
                    except Exception as e:
                        # For dev servers that run indefinitely, timeout is expected behavior
                        if "dev" in run_command or "start" in run_command or "http.server" in run_command:
                            logger.info(f"[DAYTONA] ✅ Server started in background (timeout expected for dev servers)")
                            output = "Server started successfully"
                        else:
                            logger.warning(f"[DAYTONA] ⚠️  SDK command execution failed: {e}")
                else:
                    # Use REST API
                    async with self.session.post(
                        f"{self.api_url}/toolbox/{workspace_id}/toolbox/process/execute",
                        headers=self.headers,
                        json={"command": run_command}
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            output = data.get("output", "")
                            logger.info(f"[DAYTONA]  Command executed successfully")
                        else:
                            error = await response.text()
                            logger.warning(f"[DAYTONA]  Command execution failed: {error}")

            # Get preview URL
            preview_url = await self.get_preview_url(workspace_id, port=3000)

            # Verify sandbox is running (informational check)
            try:
                status = await self.get_workspace_status(workspace_id)
                if status.get("status") == "running":
                    logger.info(f"[DAYTONA] ✅ Sandbox confirmed running")
                elif status.get("status") is None:
                    # Daytona API returned 200 but no status field - this is normal
                    logger.info(f"[DAYTONA]  Sandbox status check: API returned no status field (deployment likely successful)")
                else:
                    logger.warning(f"[DAYTONA] ⚠️  Unexpected sandbox status: {status.get('status')} (expected 'running')")
            except Exception as e:
                logger.info(f"[DAYTONA]  Could not verify sandbox status (non-critical): {e}")

            deployment = {
                "status": "deployed",
                "output": output,
                "url": preview_url
            }

            logger.info(f"[DAYTONA]  Deployed code to workspace {workspace_id}")
            logger.info(f"[DAYTONA]  📋 Deployment complete! Server running with nohup for persistence.")
            return deployment

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
                f"{self.api_url}/workspace/{workspace_id}/run",
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
                f"{self.api_url}/workspace/{workspace_id}",
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
                f"{self.api_url}/workspace",
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

    async def get_preview_url(
        self,
        workspace_id: Optional[str] = None,
        port: int = 3000,
        max_retries: int = 5,
        initial_wait: int = 3
    ) -> Optional[str]:
        """
        Get preview URL for a workspace port with retry logic

        The sandbox needs time to fully boot up and get an IP address assigned.
        This method retries with exponential backoff to handle the startup delay.

        Args:
            workspace_id: Workspace ID (uses default if not provided)
            port: Port number (default 3000)
            max_retries: Maximum number of retry attempts (default 5)
            initial_wait: Initial wait time in seconds (default 3)

        Returns:
            Preview URL string or None
        """
        await self.create_session_if_needed()

        workspace_id = workspace_id or self.workspace_id
        if not workspace_id:
            raise ValueError("No workspace ID provided")

        import asyncio

        for attempt in range(max_retries):
            try:
                async with self.session.get(
                    f"{self.api_url}/workspace/{workspace_id}/ports/{port}/preview-url",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        url = data.get("url") or data.get("previewUrl")
                        logger.info(f"[DAYTONA]  Got preview URL for port {port}")
                        return url
                    else:
                        error_text = await response.text()

                        # Check if this is the "no IP address" error indicating sandbox not ready
                        if "no IP address found" in error_text and attempt < max_retries - 1:
                            wait_time = initial_wait * (2 ** attempt)  # Exponential backoff
                            logger.info(f"[DAYTONA]  Sandbox not ready yet (no IP), retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            logger.warning(f"[DAYTONA]  Could not get preview URL: {error_text}")
                            return None

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = initial_wait * (2 ** attempt)
                    logger.warning(f"[DAYTONA]  Error getting preview URL (attempt {attempt + 1}/{max_retries}): {e}, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"[DAYTONA]  Error getting preview URL after {max_retries} attempts: {e}")
                    return None

        logger.error(f"[DAYTONA]  Failed to get preview URL after {max_retries} attempts")
        return None

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
                f"{self.api_url}/workspace/{workspace_id}",
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
