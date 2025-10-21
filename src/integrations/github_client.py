"""
GitHub Client for Repository Management
Uses GitHub CLI (gh) for simple, reliable GitHub integration
"""
import os
import subprocess
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class GitHubClient:
    """
    Client for GitHub repository operations using GitHub CLI (gh)

    Provides:
    1. Authentication check
    2. Repository creation
    3. Code push
    4. Repository URL retrieval

    Requires: GitHub CLI (gh) installed and authenticated
    """

    def __init__(self):
        """Initialize GitHub client"""
        self.gh_available = self._check_gh_cli()

    def _check_gh_cli(self) -> bool:
        """Check if GitHub CLI is installed and authenticated"""
        try:
            # Check if gh is installed
            result = subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                logger.warning("[GITHUB]  GitHub CLI (gh) not installed")
                return False

            # Check if authenticated
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                logger.warning("[GITHUB]  GitHub CLI not authenticated. Run: gh auth login")
                return False

            logger.info("[GITHUB]  GitHub CLI available and authenticated")
            return True

        except FileNotFoundError:
            logger.warning("[GITHUB]  GitHub CLI (gh) not found in PATH")
            return False
        except Exception as e:
            logger.warning(f"[GITHUB]  Error checking GitHub CLI: {e}")
            return False

    def is_authenticated(self) -> bool:
        """Check if user is authenticated with GitHub"""
        return self.gh_available

    async def create_and_push_repository(
        self,
        repo_name: str,
        files: Dict[str, str],
        description: str,
        private: bool = False,
        task: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create GitHub repository and push code

        Args:
            repo_name: Repository name
            files: Dict of {filepath: content}
            description: Repository description
            private: Make repository private
            task: Original task description (for commit message)

        Returns:
            Dict with {success, url, error}
        """
        if not self.gh_available:
            return {
                "success": False,
                "error": "GitHub CLI not available or not authenticated",
                "url": None
            }

        import tempfile
        import shutil

        # Create temporary directory for git operations
        temp_dir = tempfile.mkdtemp(prefix="codeswarm_")

        try:
            logger.info(f"[GITHUB]  Creating repository: {repo_name}")

            # Write files to temp directory
            for filepath, content in files.items():
                full_path = os.path.join(temp_dir, filepath)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w') as f:
                    f.write(content)

            # Initialize git repo
            subprocess.run(
                ["git", "init"],
                cwd=temp_dir,
                capture_output=True,
                check=True
            )

            # Add all files
            subprocess.run(
                ["git", "add", "."],
                cwd=temp_dir,
                capture_output=True,
                check=True
            )

            # Create commit
            commit_msg = f"Initial commit: {task if task else description}\n\n🤖 Generated with CodeSwarm"
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=temp_dir,
                capture_output=True,
                check=True
            )

            # Create GitHub repository
            visibility = "--private" if private else "--public"
            result = subprocess.run(
                ["gh", "repo", "create", repo_name, visibility,
                 "--description", description,
                 "--source", temp_dir,
                 "--push"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                logger.error(f"[GITHUB]  Failed to create repository: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "url": None
                }

            # Get repository URL
            result = subprocess.run(
                ["gh", "repo", "view", "--json", "url", "-q", ".url"],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=10
            )

            repo_url = result.stdout.strip() if result.returncode == 0 else None

            logger.info(f"[GITHUB] ✅ Repository created: {repo_url}")

            return {
                "success": True,
                "url": repo_url,
                "error": None
            }

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"[GITHUB]  Git command failed: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "url": None
            }
        except Exception as e:
            logger.error(f"[GITHUB]  Error creating repository: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": None
            }
        finally:
            # Clean up temp directory
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"[GITHUB]  Could not clean up temp dir: {e}")

    def prompt_authentication(self) -> bool:
        """
        Prompt user to authenticate with GitHub CLI interactively

        Runs `gh auth login` and checks if authentication succeeds.

        Returns:
            True if authentication successful, False otherwise
        """
        print("\n" + "=" * 80)
        print("  🔐 GITHUB AUTHENTICATION")
        print("=" * 80)
        print()
        print("CodeSwarm will now launch GitHub authentication.")
        print("Follow the prompts to authenticate with your GitHub account.")
        print()
        print("Press Enter to continue...")
        input()

        try:
            # Run gh auth login interactively
            # This will open browser or prompt for token
            result = subprocess.run(
                ["gh", "auth", "login"],
                timeout=300  # 5 minute timeout for user to complete auth
            )

            if result.returncode == 0:
                # Verify authentication worked
                self.gh_available = self._check_gh_cli()
                if self.gh_available:
                    print("\n✅ GitHub authentication successful!")
                    print("=" * 80)
                    print()
                    return True
                else:
                    print("\n❌ Authentication failed. Please try again.")
                    print("=" * 80)
                    print()
                    return False
            else:
                print("\n❌ Authentication cancelled or failed.")
                print("=" * 80)
                print()
                return False

        except subprocess.TimeoutExpired:
            print("\n⏱️  Authentication timed out. Please try again.")
            print("=" * 80)
            print()
            return False
        except FileNotFoundError:
            print("\n❌ GitHub CLI not installed.")
            print("Install it from: https://cli.github.com/")
            print("=" * 80)
            print()
            return False
        except Exception as e:
            print(f"\n❌ Authentication error: {e}")
            print("=" * 80)
            print()
            return False
