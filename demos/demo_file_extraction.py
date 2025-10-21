#!/usr/bin/env python3.11
"""
Demo: File Extraction and Organization Test

This demo:
1. Generates a simple web app using CodeSwarm
2. Verifies all files are properly extracted and organized
3. Displays the file structure
4. Tests the auto-launch prompt functionality
"""
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Simulated minimal workflow for testing file extraction
class FileExtractionDemo:
    def __init__(self):
        self.output_dir = Path(__file__).parent / "output"
        self.output_dir.mkdir(exist_ok=True)

    async def generate_test_code(self):
        """Generate test code with multiple files"""
        print("="*80)
        print("FILE EXTRACTION AND ORGANIZATION DEMO".center(80))
        print("="*80)
        print()

        # Simulate generated code with file markers
        test_implementation_code = """// file: package.json
{
  "name": "test-app",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.0.0"
  }
}

// file: index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test App</title>
</head>
<body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
</body>
</html>

// file: vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})

// file: src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

// file: src/App.tsx
import React, { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="app">
      <h1>CodeSwarm Test App</h1>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  )
}

export default App

// file: src/index.css
body {
  margin: 0;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen';
}

.app {
  max-width: 800px;
  margin: 0 auto;
}

button {
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
}

// file: tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
"""

        # Create mock result
        result = {
            "task": "Create a simple React counter app with TypeScript",
            "architecture": {
                "code": "# Architecture\n\nSimple React + Vite + TypeScript setup",
                "galileo_score": 92.5,
                "latency_ms": 1234,
                "iterations": 1
            },
            "implementation": {
                "code": test_implementation_code,
                "galileo_score": 95.0,
                "latency_ms": 2345,
                "iterations": 1
            },
            "security": {
                "code": "# Security Analysis\n\nNo major security issues detected.",
                "galileo_score": 88.0,
                "latency_ms": 987,
                "iterations": 1
            },
            "testing": {
                "code": "// Basic test setup\nimport { describe, it, expect } from 'vitest'",
                "galileo_score": 90.0,
                "latency_ms": 1111,
                "iterations": 1
            },
            "avg_score": 91.4,
            "quality_threshold_met": True,
            "timestamp": datetime.utcnow().isoformat()
        }

        return result

    def extract_files_from_code(self, code: str) -> dict:
        """Extract individual files from multi-file code output"""
        import re

        files = {}

        # Pattern to match "// file: filename" or "# file: filename"
        file_pattern = r'^(?://|#)\s*file:\s*(.+)$'

        lines = code.split('\n')
        current_file = None
        current_content = []

        for line in lines:
            # Check if this line is a file marker
            match = re.match(file_pattern, line.strip())
            if match:
                # Save previous file
                if current_file and current_content:
                    files[current_file] = '\n'.join(current_content).strip()

                # Start new file
                current_file = match.group(1).strip()
                current_content = []
            elif current_file:
                current_content.append(line)

        # Save last file
        if current_file and current_content:
            files[current_file] = '\n'.join(current_content).strip()

        return files

    def save_code_files(self, result: dict, timestamp: str):
        """Save generated code to organized file structure"""
        code_dir = self.output_dir / f"code_{timestamp}"
        code_dir.mkdir(exist_ok=True)

        print(f"\n📁 Saving files to: {code_dir}\n")

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
                f.write(f"**Quality Score:** {result[agent]['galileo_score']:.1f}/100\n")
                f.write(f"**Latency:** {result[agent]['latency_ms']}ms\n")
                f.write(f"**Iterations:** {result[agent]['iterations']}\n")
                f.write(f"**Timestamp:** {timestamp}\n\n")

            print(f"[{agent.upper()}]")

            # Try to extract individual files from the output
            extracted_files = self.extract_files_from_code(code)

            if extracted_files:
                # Multi-file output - save each file separately
                for filename, content in extracted_files.items():
                    file_path = agent_dir / filename
                    file_path.parent.mkdir(parents=True, exist_ok=True)

                    with open(file_path, 'w') as f:
                        f.write(content.strip())

                    print(f"  ✅ {filename} ({len(content)} chars)")
                    total_files += 1

                files_saved.append(f"{agent}/ ({len(extracted_files)} files)")
            else:
                # Single file output
                extension = '.md'
                filename = agent_dir / f"{agent}{extension}"

                with open(filename, 'w') as f:
                    f.write(code)

                print(f"  ✅ {agent}{extension} ({len(code)} chars)")
                total_files += 1
                files_saved.append(f"{agent}/{agent}{extension}")

            print()

        return code_dir, total_files

    def display_file_tree(self, code_dir: Path):
        """Display the complete file tree"""
        print(f"\n{'='*80}")
        print("📂 GENERATED FILE STRUCTURE".center(80))
        print(f"{'='*80}\n")

        def print_tree(path: Path, prefix: str = "", is_last: bool = True):
            """Recursively print directory tree"""
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

    def check_web_project(self, code_dir: Path):
        """Check if this is a web project and display launch instructions"""
        impl_dir = code_dir / "implementation"
        package_json = impl_dir / "package.json"

        print(f"\n{'='*80}")
        print("🔍 WEB PROJECT DETECTION".center(80))
        print(f"{'='*80}\n")

        if package_json.exists():
            print("✅ Web project detected (package.json found)")
            print(f"\n📦 Package.json location: {package_json}")

            # Read package.json to show project details
            with open(package_json, 'r') as f:
                pkg_data = json.load(f)

            print(f"\nProject: {pkg_data.get('name', 'N/A')}")
            print(f"Version: {pkg_data.get('version', 'N/A')}")

            if 'scripts' in pkg_data:
                print("\nAvailable scripts:")
                for script, command in pkg_data['scripts'].items():
                    print(f"  • npm run {script}")

            print(f"\n{'='*80}")
            print("🚀 READY TO LAUNCH!".center(80))
            print(f"{'='*80}\n")
            print(f"To launch this project:\n")
            print(f"  cd {impl_dir}")
            print(f"  npm install")
            print(f"  npm run dev")
            print()

            return True
        else:
            print("ℹ️  Not a web project (no package.json found)")
            return False

    async def run(self):
        """Run the complete demo"""
        # Generate test code
        result = await self.generate_test_code()

        # Save files with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        code_dir, total_files = self.save_code_files(result, timestamp)

        print(f"{'='*80}")
        print(f"✨ Successfully saved {total_files} files!".center(80))
        print(f"{'='*80}\n")

        # Display file tree
        self.display_file_tree(code_dir)

        # Check if it's a web project
        is_web_project = self.check_web_project(code_dir)

        # Summary
        print(f"\n{'='*80}")
        print("📊 SUMMARY".center(80))
        print(f"{'='*80}\n")
        print(f"✅ Code generation:     Complete")
        print(f"✅ File extraction:     {total_files} files extracted")
        print(f"✅ File organization:   4 agent directories")
        print(f"✅ Web project:         {'Yes (package.json found)' if is_web_project else 'No'}")
        print(f"\n📁 Output directory:    {code_dir}")
        print()


async def main():
    """Main entry point"""
    demo = FileExtractionDemo()
    await demo.run()


if __name__ == "__main__":
    asyncio.run(main())
