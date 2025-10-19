#!/usr/bin/env python3.11
"""
Demo: Live Code Generation with File Extraction

This demo:
1. Makes REAL API calls to generate a simple web app
2. Extracts and organizes all generated files
3. Displays the complete file structure
4. Verifies web project detection and launch readiness
"""
import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from integrations import OpenRouterClient
from agents import ImplementationAgent


class LiveGenerationDemo:
    """Live code generation and file extraction demo"""

    def __init__(self):
        self.output_dir = Path(__file__).parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        print(f"📁 Output directory: {self.output_dir}\n")

    async def generate_web_app(self):
        """Generate a real web app using OpenRouter API"""
        print("="*80)
        print("🚀 LIVE CODE GENERATION DEMO".center(80))
        print("="*80)
        print()

        # Initialize OpenRouter client
        print("[1/4] 🔌 Connecting to OpenRouter API...")
        try:
            openrouter = OpenRouterClient()
            print("      ✅ Connected\n")
        except Exception as e:
            print(f"      ❌ Failed: {e}")
            print("\n💡 Make sure OPENROUTER_API_KEY is set in .env file")
            return None

        # Create implementation agent
        print("[2/4] 🤖 Initializing Implementation Agent...")
        impl_agent = ImplementationAgent(
            openrouter_client=openrouter,
            evaluator=None  # Skip evaluation for speed
        )
        print("      ✅ Agent ready\n")

        # Generate code
        task = "Create a simple todo list web app with React, TypeScript, and Vite. Include add, delete, and mark complete functionality."

        print(f"[3/4] 💻 Generating code...")
        print(f"      Task: {task[:60]}...")
        print()

        try:
            result = await impl_agent.execute(
                task=task,
                context={
                    "architecture_output": "Single-page React app with TypeScript and Vite. Use functional components with hooks."
                },
                quality_threshold=70.0,  # Lower threshold for demo speed
                max_iterations=1  # Single pass for speed
            )

            print(f"      ✅ Generation complete!")
            print(f"      📊 Quality Score: {result.galileo_score or 'N/A'}")
            print(f"      ⏱️  Latency: {result.latency_ms}ms")
            print(f"      🔄 Iterations: {result.iterations}")
            print(f"      📝 Code length: {len(result.code):,} characters")
            print()

            return {
                "task": task,
                "implementation": {
                    "code": result.code,
                    "galileo_score": result.galileo_score or 0.0,
                    "latency_ms": result.latency_ms,
                    "iterations": result.iterations
                }
            }

        except Exception as e:
            print(f"      ❌ Generation failed: {e}")
            return None

    def extract_files_from_code(self, code: str) -> dict:
        """Extract individual files from code with file markers"""
        import re

        files = {}

        # Pattern to match "// file: filename" or "# file: filename" (case-insensitive)
        file_pattern = r'^(?://|#)\s*[Ff]ile:\s*(.+)$'

        lines = code.split('\n')
        current_file = None
        current_content = []

        for line in lines:
            match = re.match(file_pattern, line.strip())
            if match:
                # Save previous file
                if current_file and current_content:
                    content = '\n'.join(current_content).strip()
                    # Remove markdown code fences if present
                    if content.startswith('```'):
                        lines_list = content.split('\n')
                        if lines_list[0].startswith('```'):
                            lines_list = lines_list[1:]
                        if lines_list and lines_list[-1].strip() == '```':
                            lines_list = lines_list[:-1]
                        content = '\n'.join(lines_list)
                    files[current_file] = content

                # Start new file
                current_file = match.group(1).strip()
                current_content = []
            elif current_file:
                current_content.append(line)

        # Save last file
        if current_file and current_content:
            content = '\n'.join(current_content).strip()
            # Remove markdown code fences if present
            if content.startswith('```'):
                lines_list = content.split('\n')
                if lines_list[0].startswith('```'):
                    lines_list = lines_list[1:]
                if lines_list and lines_list[-1].strip() == '```':
                    lines_list = lines_list[:-1]
                content = '\n'.join(lines_list)
            files[current_file] = content

        return files

    def save_extracted_files(self, result: dict, timestamp: str):
        """Save extracted files to organized structure"""
        print("[4/4] 💾 Extracting and saving files...")
        print()

        code_dir = self.output_dir / f"demo_{timestamp}"
        impl_dir = code_dir / "implementation"
        impl_dir.mkdir(parents=True, exist_ok=True)

        code = result['implementation']['code']

        # Extract files
        extracted_files = self.extract_files_from_code(code)

        if not extracted_files:
            print("      ⚠️  No file markers found in code")
            print("      💡 Code might be single-file or use different format")

            # Save as single file
            single_file = impl_dir / "implementation.js"
            with open(single_file, 'w') as f:
                f.write(code)

            print(f"      📄 Saved as: implementation.js")
            return code_dir, 1

        # Save each extracted file
        total_files = 0
        for filename, content in extracted_files.items():
            file_path = impl_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w') as f:
                f.write(content)

            print(f"      ✅ {filename} ({len(content):,} chars)")
            total_files += 1

        # Save metadata
        metadata_file = impl_dir / 'METADATA.md'
        with open(metadata_file, 'w') as f:
            f.write(f"# Implementation Output\n\n")
            f.write(f"**Task:** {result['task']}\n\n")
            f.write(f"**Quality Score:** {result['implementation']['galileo_score']:.1f}/100\n")
            f.write(f"**Latency:** {result['implementation']['latency_ms']}ms\n")
            f.write(f"**Iterations:** {result['implementation']['iterations']}\n")
            f.write(f"**Timestamp:** {timestamp}\n")
            f.write(f"**Files Generated:** {total_files}\n\n")

        print()
        print(f"      ✨ Extracted {total_files} files to: {impl_dir.name}/")
        print()

        return code_dir, total_files

    def display_file_tree(self, code_dir: Path):
        """Display complete file structure"""
        print(f"{'='*80}")
        print("📂 GENERATED FILE STRUCTURE".center(80))
        print(f"{'='*80}\n")

        def print_tree(path: Path, prefix: str = "", is_last: bool = True):
            if path.is_file():
                connector = "└── " if is_last else "├── "
                size = path.stat().st_size
                print(f"{prefix}{connector}{path.name} ({size} bytes)")
            elif path.is_dir():
                connector = "└── " if is_last else "├── "
                print(f"{prefix}{connector}{path.name}/")

                items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
                for i, item in enumerate(items):
                    is_last_item = i == len(items) - 1
                    extension = "    " if is_last else "│   "
                    print_tree(item, prefix + extension, is_last_item)

        print(f"{code_dir.name}/")
        items = sorted(code_dir.iterdir(), key=lambda x: (x.is_file(), x.name))
        for i, item in enumerate(items):
            is_last_item = i == len(items) - 1
            print_tree(item, "", is_last_item)

        print()

    def check_web_project_readiness(self, code_dir: Path):
        """Check if web project is ready to launch"""
        print(f"{'='*80}")
        print("🔍 WEB PROJECT DETECTION".center(80))
        print(f"{'='*80}\n")

        impl_dir = code_dir / "implementation"
        package_json = impl_dir / "package.json"

        if package_json.exists():
            print("✅ Web project detected!")
            print()

            # Read and display package.json info
            try:
                with open(package_json, 'r') as f:
                    pkg_data = json.load(f)

                print(f"📦 Package: {pkg_data.get('name', 'N/A')} v{pkg_data.get('version', 'N/A')}")

                if 'scripts' in pkg_data:
                    print(f"\n📜 Available scripts:")
                    for script, command in pkg_data['scripts'].items():
                        print(f"   • npm run {script:<10} → {command}")

                if 'dependencies' in pkg_data:
                    print(f"\n📚 Dependencies: {len(pkg_data['dependencies'])} packages")

                print(f"\n{'='*80}")
                print("🚀 READY TO LAUNCH!".center(80))
                print(f"{'='*80}\n")
                print("To launch this project:\n")
                print(f"  cd {impl_dir}")
                print(f"  npm install")
                print(f"  npm run dev")
                print()

                return True

            except Exception as e:
                print(f"⚠️  Could not parse package.json: {e}")
                return False
        else:
            print("ℹ️  Not a web project (no package.json found)")
            print()
            return False

    async def run(self):
        """Run complete live demo"""
        # Generate code with real API
        result = await self.generate_web_app()

        if not result:
            print("\n❌ Demo failed - could not generate code")
            return

        # Save and extract files
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        code_dir, total_files = self.save_extracted_files(result, timestamp)

        # Display file structure
        self.display_file_tree(code_dir)

        # Check web project readiness
        is_web_project = self.check_web_project_readiness(code_dir)

        # Final summary
        print(f"{'='*80}")
        print("📊 DEMO SUMMARY".center(80))
        print(f"{'='*80}\n")
        print(f"✅ Live code generation:  Complete")
        print(f"✅ File extraction:        {total_files} files")
        print(f"✅ File organization:      implementation/ directory")
        print(f"✅ Web project ready:      {'Yes' if is_web_project else 'No'}")
        print(f"\n📁 Output: {code_dir}")
        print()


async def main():
    """Main entry point"""
    demo = LiveGenerationDemo()
    await demo.run()


if __name__ == "__main__":
    asyncio.run(main())
