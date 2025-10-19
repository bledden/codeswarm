#!/usr/bin/env python3.11
"""
CodeSwarm CLI - Interactive Command-Line Interface

Usage:
    codeswarm generate "Create a REST API for user authentication"
    codeswarm status
    codeswarm history
    codeswarm configure
"""
import asyncio
import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import argparse
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from integrations import OpenRouterClient, Neo4jRAGClient, WorkOSAuthClient, DaytonaClient, BrowserUseClient
from evaluation import GalileoEvaluator
from orchestration import FullCodeSwarmWorkflow

# Initialize Weave for observability (if available)
try:
    import weave
    # Check if WANDB_API_KEY is set before initializing
    if os.getenv("WANDB_API_KEY"):
        weave.init(project_name="codeswarm")
except ImportError:
    # Weave not installed, continue without observability
    pass
except Exception:
    # Weave init failed, continue without observability
    pass


class CodeSwarmCLI:
    """Interactive CLI for CodeSwarm"""

    def __init__(self):
        self.history_file = Path("cache/cli_history.json")
        self.config_file = Path("cache/cli_config.json")
        self.output_dir = Path("output")

        # Ensure directories exist
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load config
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load CLI configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {
            "quality_threshold": 90.0,
            "max_iterations": 3,
            "auto_deploy": True,  # Enabled for demo
            "scrape_docs": True,
            "user_id": "cli-user"
        }

    def _save_config(self):
        """Save CLI configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def _load_history(self) -> list:
        """Load generation history"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []

    def _save_to_history(self, task: str, result: Dict[str, Any]):
        """Save generation to history"""
        history = self._load_history()

        entry = {
            "id": len(history) + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "task": task,
            "avg_score": result.get("avg_score", 0),
            "quality_met": result.get("quality_threshold_met", False),
            "pattern_id": result.get("pattern_id"),
            "output_file": result.get("output_file")
        }

        history.append(entry)

        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2, default=str)

    def print_banner(self):
        """Print CodeSwarm banner"""
        print("\n" + "="*80)
        print("🐝 CODESWARM - Multi-Agent AI Coding System".center(80))
        print("="*80 + "\n")

    def print_section(self, title: str):
        """Print section header"""
        print(f"\n{'─'*80}")
        print(f"  {title}")
        print(f"{'─'*80}\n")

    async def generate(self, task: str, image_path: Optional[str] = None, deploy: bool = False, scrape_docs: bool = True):
        """Generate code from task description"""
        self.print_banner()
        print(f"📝 Task: {task}\n")

        if image_path:
            print(f"🖼️  Image: {image_path}\n")
        if deploy:
            print("🚀 Deployment: Enabled\n")
        if not scrape_docs:
            print("📚 Documentation scraping: Disabled\n")

        # Initialize services
        print("⚙️  Initializing services...")

        services_initialized = []

        try:
            async with OpenRouterClient() as openrouter:
                services_initialized.append("OpenRouter")
                print("  ✅ OpenRouter connected")

                try:
                    async with Neo4jRAGClient() as neo4j:
                        services_initialized.append("Neo4j")
                        print("  ✅ Neo4j connected")

                        galileo = None
                        try:
                            galileo = GalileoEvaluator()
                            services_initialized.append("Galileo")
                            print("  ✅ Galileo initialized")
                        except Exception as e:
                            print(f"  ⚠️  Galileo unavailable: {e}")

                        workos = None
                        try:
                            workos = WorkOSAuthClient()
                            services_initialized.append("WorkOS")
                            print("  ✅ WorkOS initialized")
                        except Exception as e:
                            print(f"  ⚠️  WorkOS unavailable: {e}")

                        daytona = None
                        try:
                            async with DaytonaClient() as daytona_client:
                                daytona = daytona_client
                                services_initialized.append("Daytona")
                                print("  ✅ Daytona connected")
                        except Exception as e:
                            print(f"  ⚠️  Daytona unavailable: {e}")

                        # Initialize Browser Use (6th service - doc scraping)
                        browser_use = None
                        try:
                            browser_use = BrowserUseClient()
                            services_initialized.append("Browser Use")
                            print("  ✅ Browser Use connected")
                        except Exception as e:
                            print(f"  ⚠️  Browser Use unavailable: {e}")

                        print(f"\n🎯 {len(services_initialized)}/6 services active")

                        # Create workflow
                        workflow = FullCodeSwarmWorkflow(
                            openrouter_client=openrouter,
                            neo4j_client=neo4j,
                            galileo_evaluator=galileo,
                            workos_client=workos,
                            daytona_client=daytona,
                            browser_use_client=browser_use,
                            quality_threshold=self.config["quality_threshold"],
                            max_iterations=self.config["max_iterations"]
                        )

                        # Execute
                        self.print_section("GENERATING CODE")

                        # Command-line args override config
                        result = await workflow.execute(
                            task=task,
                            user_id=self.config["user_id"],
                            image_path=image_path,
                            scrape_docs=scrape_docs,  # Use parameter instead of config
                            deploy=deploy  # Use parameter instead of config
                        )

                        # Save results
                        self.print_section("SAVING RESULTS")

                        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                        output_file = self.output_dir / f"generation_{timestamp}.json"

                        with open(output_file, 'w') as f:
                            json.dump(result, f, indent=2, default=str)

                        result["output_file"] = str(output_file)

                        # Save to history
                        self._save_to_history(task, result)

                        # Display results
                        self.display_results(result)

                        # Save code files
                        self.save_code_files(result, timestamp)

                        return result

                except Exception as e:
                    print(f"\n❌ Error: {e}")
                    return None

        except Exception as e:
            print(f"\n❌ Failed to initialize OpenRouter: {e}")
            return None

    def display_results(self, result: Dict[str, Any]):
        """Display generation results"""
        self.print_section("📊 RESULTS")

        print(f"Task: {result['task']}\n")

        print("Quality Scores:")
        print(f"  Architecture:    {result['architecture']['galileo_score']:.1f}/100")
        print(f"  Implementation:  {result['implementation']['galileo_score']:.1f}/100")
        print(f"  Security:        {result['security']['galileo_score']:.1f}/100")
        print(f"  Testing:         {result['testing']['galileo_score']:.1f}/100")
        print(f"  {'─'*40}")
        print(f"  Average:         {result['avg_score']:.1f}/100")
        print()

        threshold_status = "✅ MET" if result['quality_threshold_met'] else "❌ NOT MET"
        print(f"Quality Threshold: {threshold_status} ({self.config['quality_threshold']}+)")
        print()

        print("Code Generated:")
        print(f"  Architecture:    {len(result['architecture']['code']):,} characters")
        print(f"  Implementation:  {len(result['implementation']['code']):,} characters")
        print(f"  Security:        {len(result['security']['code']):,} characters")
        print(f"  Testing:         {len(result['testing']['code']):,} characters")
        total_chars = sum(len(result[k]['code']) for k in ['architecture', 'implementation', 'security', 'testing'])
        print(f"  {'─'*40}")
        print(f"  Total:           {total_chars:,} characters")
        print()

        if result.get('pattern_id'):
            print(f"📦 Pattern stored in Neo4j: {result['pattern_id']}")

        if result.get('rag_patterns_used', 0) > 0:
            print(f"🔍 Used {result['rag_patterns_used']} similar patterns from RAG")

        # Display Daytona deployment info if available
        if result.get('deployment'):
            deployment = result['deployment']
            print()
            print(f"{'='*60}")
            print("🚀 DAYTONA DEPLOYMENT".center(60))
            print(f"{'='*60}")
            print(f"Workspace: {deployment.get('workspace_name', 'N/A')}")
            print(f"Status:    {deployment.get('status', 'unknown')}")
            if deployment.get('url'):
                print(f"URL:       {deployment['url']}")
                print()
                print(f"🌐 View your deployed project at:")
                print(f"   {deployment['url']}")
            print(f"{'='*60}")

        print()
        print(f"💾 Results saved to: {result['output_file']}")
        print()

    def save_code_files(self, result: Dict[str, Any], timestamp: str):
        """Save generated code to separate files with proper extensions and structure"""
        code_dir = self.output_dir / f"code_{timestamp}"
        code_dir.mkdir(exist_ok=True)

        def extract_files_from_code(code: str) -> dict:
            """Extract individual files from multi-file code output"""
            files = {}
            current_file = None
            current_content = []

            for line in code.split('\n'):
                # Check for file markers like "// filename.ext" or "# filename.ext"
                if line.strip().startswith(('// ', '# ')) and any(ext in line for ext in ['.json', '.js', '.ts', '.tsx', '.jsx', '.py', '.html', '.css', '.md', '.yml', '.yaml', '.env', '.txt']):
                    # Save previous file
                    if current_file:
                        files[current_file] = '\n'.join(current_content)

                    # Extract filename
                    current_file = line.strip().lstrip('/#').strip()
                    current_content = []
                elif current_file:
                    current_content.append(line)

            # Save last file
            if current_file:
                files[current_file] = '\n'.join(current_content)

            return files

        def get_extension(code: str, agent: str) -> str:
            """Detect file extension based on content"""
            code_lower = code.lower()

            # Architecture and security are markdown
            if agent in ['architecture', 'security']:
                return '.md'

            # Testing
            if agent == 'testing':
                if 'pytest' in code_lower or 'unittest' in code_lower:
                    return '.py'
                elif 'jest' in code_lower or 'describe(' in code_lower:
                    return '.test.js'
                return '.py'

            # Implementation - detect language
            if 'package.json' in code or 'import React' in code or 'from react' in code_lower:
                return '.js'  # Multi-file JS project
            elif 'import ' in code and 'def ' in code:
                return '.py'
            elif 'const ' in code or 'let ' in code:
                return '.js'
            elif 'interface ' in code and ': ' in code:
                return '.ts'
            elif 'package main' in code:
                return '.go'
            elif 'public class' in code:
                return '.java'

            return '.md'

        # Save each agent's output
        files_saved = []
        total_files = 0

        for agent in ['architecture', 'implementation', 'security', 'testing']:
            if not result[agent]['code']:
                continue

            agent_dir = code_dir / agent
            agent_dir.mkdir(exist_ok=True)

            code = result[agent]['code']

            # Add metadata file
            metadata_file = agent_dir / 'METADATA.md'
            with open(metadata_file, 'w') as f:
                f.write(f"# {agent.upper()} Output\n\n")
                f.write(f"**Quality Score:** {result[agent]['galileo_score']:.1f}/100  \n")
                f.write(f"**Latency:** {result[agent]['latency_ms']}ms  \n")
                f.write(f"**Iterations:** {result[agent]['iterations']}  \n")
                f.write(f"**Timestamp:** {timestamp}  \n\n")

            # Try to extract individual files from the output
            extracted_files = extract_files_from_code(code)

            if extracted_files:
                # Multi-file output - save each file separately
                for filename, content in extracted_files.items():
                    file_path = agent_dir / filename
                    file_path.parent.mkdir(parents=True, exist_ok=True)

                    with open(file_path, 'w') as f:
                        f.write(content.strip())

                    total_files += 1

                files_saved.append(f"{agent}/ ({len(extracted_files)} files)")
            else:
                # Single file output
                extension = get_extension(code, agent)
                filename = agent_dir / f"{agent}{extension}"

                with open(filename, 'w') as f:
                    f.write(code)

                files_saved.append(f"{agent}/{agent}{extension}")
                total_files += 1

        print(f"\n📁 Code saved to: {code_dir}/")
        print(f"   Total files: {total_files}")
        for item in files_saved:
            print(f"   ✅ {item}")

        # Auto-extract and prompt for launch if it's a web project
        self._extract_and_prompt_launch(code_dir, timestamp)

    def _extract_and_prompt_launch(self, code_dir: Path, timestamp: str):
        """Extract project files and prompt user to launch"""
        import re
        import subprocess

        # Check if we have a web project - two possible formats:
        # 1. Already extracted files in implementation/ subdirectory (current format)
        # 2. Consolidated implementation.js file (old format)

        impl_dir = code_dir / "implementation"
        package_json_file = impl_dir / "package.json"

        # Case 1: Files already extracted - check for package.json
        if package_json_file.exists():
            # Files are already extracted! Just need to set up and prompt
            self._setup_and_prompt_extracted_project(impl_dir, code_dir, timestamp)
            return

        # Case 2: Check for consolidated implementation.js file (existing logic)
        impl_file = code_dir / "implementation.js"
        if not impl_file.exists():
            impl_file = code_dir / "implementation" / "implementation.js"
            if not impl_file.exists():
                return

        # Check if it's a Node.js/web project
        with open(impl_file, 'r') as f:
            content = f.read()
            if 'package.json' not in content:
                return  # Not a web project

        print(f"\n{'='*80}")
        print("🚀 WEB PROJECT DETECTED!".center(80))
        print(f"{'='*80}\n")

        # Extract files automatically
        project_name = f"project_{timestamp}"
        project_dir = code_dir.parent / project_name

        print(f"📦 Extracting project files to: {project_dir}/\n")

        # Create project directory
        project_dir.mkdir(exist_ok=True)

        # Parse and extract files
        file_pattern = r'^// file: (.+?)$'
        files = re.findall(file_pattern, content, re.MULTILINE)
        sections = re.split(r'^// file: .+?$', content, flags=re.MULTILINE)
        sections = sections[1:]  # Skip header

        extracted_count = 0
        for filename, file_content in zip(files, sections):
            # Clean up content
            file_content = file_content.strip()

            # Remove markdown code fences if present
            if file_content.startswith('```') or file_content.startswith('tsx'):
                lines = file_content.split('\n')
                if lines[0].strip() in ['tsx', 'typescript', 'javascript', 'json', '```tsx', '```javascript', '```json', '```']:
                    lines = lines[1:]
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                file_content = '\n'.join(lines)

            # Create full path
            full_path = project_dir / filename
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(full_path, 'w') as f:
                f.write(file_content)

            print(f"  ✅ {filename}")
            extracted_count += 1

        print(f"\n✨ Extracted {extracted_count} files!\n")

        # Install dependencies
        package_json = project_dir / "package.json"
        if package_json.exists():
            print("📦 Installing dependencies...")
            try:
                result = subprocess.run(
                    ["npm", "install"],
                    cwd=project_dir,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode == 0:
                    print("✅ Dependencies installed!\n")
                else:
                    print(f"⚠️  npm install had warnings (project may still work)\n")
            except subprocess.TimeoutExpired:
                print("⚠️  npm install timed out (you can run it manually)\n")
            except FileNotFoundError:
                print("⚠️  npm not found. Install Node.js from https://nodejs.org/\n")

        # Create launch script
        launch_script = project_dir / "launch.sh"
        script_content = f"""#!/bin/bash
# Launch script for {project_name}

echo "🚀 Starting development server..."
echo "📍 Project will be available at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")"

if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

npm run dev
"""
        with open(launch_script, 'w') as f:
            f.write(script_content)
        os.chmod(launch_script, 0o755)

        # Prompt user to launch
        print(f"{'='*80}")
        print("✅ PROJECT READY TO LAUNCH!".center(80))
        print(f"{'='*80}\n")
        print(f"📁 Project location: {project_dir}\n")

        response = input("🚀 Would you like to launch the development server now? (y/n): ").strip().lower()

        if response == 'y':
            print(f"\n🌐 Launching development server at http://localhost:3000")
            print("   Press Ctrl+C to stop\n")
            try:
                subprocess.run(["npm", "run", "dev"], cwd=project_dir)
            except KeyboardInterrupt:
                print("\n\n👋 Server stopped")
            except Exception as e:
                print(f"\n❌ Failed to start server: {e}")
        else:
            print("\n📝 To launch later, run:")
            print(f"   cd {project_dir}")
            print(f"   ./launch.sh")
            print(f"\n   OR:")
            print(f"   npm run dev\n")

    def _setup_and_prompt_extracted_project(self, impl_dir: Path, code_dir: Path, timestamp: str):
        """Set up and prompt user to launch an already-extracted web project"""
        import subprocess

        print(f"\n{'='*80}")
        print("🚀 WEB PROJECT DETECTED!".center(80))
        print(f"{'='*80}\n")

        # The project is already in the implementation/ directory
        # We'll use it directly instead of copying
        project_dir = impl_dir

        print(f"📁 Project location: {project_dir}\n")

        # Install dependencies
        package_json = project_dir / "package.json"
        if package_json.exists():
            print("📦 Installing dependencies...")
            try:
                result = subprocess.run(
                    ["npm", "install"],
                    cwd=project_dir,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode == 0:
                    print("✅ Dependencies installed!\n")
                else:
                    print(f"⚠️  npm install had warnings (project may still work)\n")
            except subprocess.TimeoutExpired:
                print("⚠️  npm install timed out (you can run it manually)\n")
            except FileNotFoundError:
                print("⚠️  npm not found. Install Node.js from https://nodejs.org/\n")

        # Create launch script
        project_name = f"project_{timestamp}"
        launch_script = project_dir / "launch.sh"
        script_content = f"""#!/bin/bash
# Launch script for {project_name}

echo "🚀 Starting development server..."
echo "📍 Project will be available at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")"

if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

npm run dev
"""
        with open(launch_script, 'w') as f:
            f.write(script_content)
        os.chmod(launch_script, 0o755)

        # Prompt user to launch
        print(f"{'='*80}")
        print("✅ PROJECT READY TO LAUNCH!".center(80))
        print(f"{'='*80}\n")

        response = input("🚀 Would you like to launch the development server now? (y/n): ").strip().lower()

        if response == 'y':
            print(f"\n🌐 Launching development server at http://localhost:3000")
            print("   Press Ctrl+C to stop\n")
            try:
                subprocess.run(["npm", "run", "dev"], cwd=project_dir)
            except KeyboardInterrupt:
                print("\n\n👋 Server stopped")
            except Exception as e:
                print(f"\n❌ Failed to start server: {e}")
        else:
            print("\n📝 To launch later, run:")
            print(f"   cd {project_dir}")
            print(f"   ./launch.sh")
            print(f"\n   OR:")
            print(f"   npm run dev\n")

    def status(self):
        """Show current configuration and service status"""
        self.print_banner()
        self.print_section("⚙️  CONFIGURATION")

        print(f"Quality Threshold:  {self.config['quality_threshold']}")
        print(f"Max Iterations:     {self.config['max_iterations']}")
        print(f"Auto Deploy:        {'Enabled' if self.config['auto_deploy'] else 'Disabled'}")
        print(f"Scrape Docs:        {'Enabled' if self.config['scrape_docs'] else 'Disabled'}")
        print(f"User ID:            {self.config['user_id']}")

        self.print_section("📊 STATISTICS")

        history = self._load_history()
        if history:
            total = len(history)
            successful = sum(1 for h in history if h['quality_met'])
            avg_score = sum(h['avg_score'] for h in history) / total if total > 0 else 0

            print(f"Total Generations:  {total}")
            print(f"Successful:         {successful} ({successful/total*100:.1f}%)")
            print(f"Average Score:      {avg_score:.1f}/100")
            print(f"Patterns Stored:    {sum(1 for h in history if h.get('pattern_id'))}")
        else:
            print("No generations yet")

        print()

    def history(self, limit: int = 10):
        """Show generation history"""
        self.print_banner()
        self.print_section("📜 GENERATION HISTORY")

        history = self._load_history()

        if not history:
            print("No generations yet. Run 'codeswarm generate <task>' to get started!")
            return

        # Show most recent first
        for entry in reversed(history[-limit:]):
            status = "✅" if entry['quality_met'] else "❌"
            print(f"{status} #{entry['id']} - {entry['timestamp'][:19]}")
            print(f"   Task: {entry['task'][:60]}...")
            print(f"   Score: {entry['avg_score']:.1f}/100")
            if entry.get('pattern_id'):
                print(f"   Pattern: {entry['pattern_id']}")
            print()

    def configure(self):
        """Interactive configuration"""
        self.print_banner()
        self.print_section("⚙️  CONFIGURATION")

        print("Current settings:\n")
        print(f"1. Quality Threshold: {self.config['quality_threshold']}")
        print(f"2. Max Iterations: {self.config['max_iterations']}")
        print(f"3. Auto Deploy: {self.config['auto_deploy']}")
        print(f"4. Scrape Docs: {self.config['scrape_docs']}")
        print(f"5. User ID: {self.config['user_id']}")
        print("\nEnter number to change (or 'done' to finish):\n")

        while True:
            try:
                choice = input("> ").strip().lower()

                if choice == 'done' or choice == '':
                    break

                if choice == '1':
                    threshold = float(input("Quality threshold (0-100): "))
                    self.config['quality_threshold'] = max(0, min(100, threshold))
                    print(f"✅ Set to {self.config['quality_threshold']}")

                elif choice == '2':
                    iterations = int(input("Max iterations (1-5): "))
                    self.config['max_iterations'] = max(1, min(5, iterations))
                    print(f"✅ Set to {self.config['max_iterations']}")

                elif choice == '3':
                    deploy = input("Auto deploy (y/n): ").lower() == 'y'
                    self.config['auto_deploy'] = deploy
                    print(f"✅ Set to {deploy}")

                elif choice == '4':
                    scrape = input("Scrape docs (y/n): ").lower() == 'y'
                    self.config['scrape_docs'] = scrape
                    print(f"✅ Set to {scrape}")

                elif choice == '5':
                    user_id = input("User ID: ").strip()
                    self.config['user_id'] = user_id
                    print(f"✅ Set to {user_id}")

            except (ValueError, KeyboardInterrupt):
                print("\nCancelled")
                break

        self._save_config()
        print("\n✅ Configuration saved")


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="CodeSwarm - Multi-Agent AI Coding System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  codeswarm generate "Create a REST API for user management"
  codeswarm generate "Build a chat application" --image sketch.png
  codeswarm status
  codeswarm history
  codeswarm configure
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate code from task description')
    generate_parser.add_argument('task', help='Task description')
    generate_parser.add_argument('--image', '-i', help='Path to image/sketch (optional)')
    generate_parser.add_argument('--deploy', action='store_true', help='Deploy to Daytona workspace after generation')
    generate_parser.add_argument('--no-scrape', action='store_true', help='Skip documentation scraping')

    # Status command
    subparsers.add_parser('status', help='Show configuration and statistics')

    # History command
    history_parser = subparsers.add_parser('history', help='Show generation history')
    history_parser.add_argument('--limit', '-n', type=int, default=10, help='Number of entries to show')

    # Configure command
    subparsers.add_parser('configure', help='Configure CLI settings')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = CodeSwarmCLI()

    try:
        if args.command == 'generate':
            deploy = args.deploy if hasattr(args, 'deploy') else False
            scrape_docs = not args.no_scrape if hasattr(args, 'no_scrape') else True
            await cli.generate(args.task, args.image, deploy=deploy, scrape_docs=scrape_docs)

        elif args.command == 'status':
            cli.status()

        elif args.command == 'history':
            cli.history(args.limit)

        elif args.command == 'configure':
            cli.configure()

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
