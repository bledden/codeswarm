"""
Implementation Agent - GPT-5 Pro

Specialization: Code generation, implementation of architecture
Role: Generate production-quality code based on architecture
Model: openai/gpt-5-pro (flagship code generation)
"""

from typing import Dict, Any, Tuple, List, Optional
import re
from .base_agent import BaseAgent


class ImplementationAgent(BaseAgent):
    """
    Implementation Agent using GPT-5 Pro

    Responsibilities:
    - Implement code based on architecture specification
    - Generate clean, well-documented code
    - Follow best practices and coding standards
    - Ensure code quality and maintainability
    - Handle edge cases and error conditions

    Input: Architecture from Architecture Agent
    Output: Production-ready code implementation
    """

    def __init__(self, openrouter_client, evaluator=None):
        super().__init__(
            name="implementation",
            model="gpt-5-pro",
            openrouter_client=openrouter_client,
            evaluator=evaluator,
            temperature=0.5,  # Lower temperature for more consistent code
            max_tokens=16000  # Increased for modern multi-file projects (React/TypeScript)
        )

    async def _validate_output(
        self,
        code: str,
        reasoning: str,
        context: Dict[str, Any],
        task: str
    ) -> Optional[Dict[str, Any]]:
        """
        Validate that generated code can be parsed into files
        and all imports/references point to existing files.

        Returns:
            None if validation passes, or error dict if validation fails
        """
        try:
            # Parse code into files
            parsed_files = self._parse_code_to_files(code)

            # Validate imports
            missing_files = self._validate_file_imports(parsed_files)

            if missing_files:
                # Validation failed
                print(f"[{self.name.upper()}]  ❌ VALIDATION FAILED: {len(missing_files)} missing file references!")
                for source_file, missing_import in missing_files[:5]:  # Show first 5
                    print(f"[{self.name.upper()}]      {source_file} → {missing_import}")

                if len(missing_files) > 5:
                    print(f"[{self.name.upper()}]      ... and {len(missing_files) - 5} more")

                return {
                    "missing_files": missing_files,
                    "message": f"Generated code references {len(missing_files)} files that don't exist"
                }

            # Validate minimum required files for framework
            missing_required = self._validate_required_files(parsed_files)

            if missing_required:
                # Validation failed - missing critical files
                print(f"[{self.name.upper()}]  ❌ VALIDATION FAILED: Missing {len(missing_required)} required files!")
                for required_file in missing_required[:5]:
                    print(f"[{self.name.upper()}]      Missing: {required_file}")

                if len(missing_required) > 5:
                    print(f"[{self.name.upper()}]      ... and {len(missing_required) - 5} more")

                return {
                    "missing_required_files": missing_required,
                    "message": f"Project is missing {len(missing_required)} required files and won't run"
                }

            # Validation passed - store parsed files for deployment
            print(f"[{self.name.upper()}]  ✅ File validation passed ({len(parsed_files)} files, all imports valid)")
            self._parsed_files = parsed_files
            return None

        except ValueError as e:
            # Parsing failed
            print(f"[{self.name.upper()}]  ❌ FILE PARSING FAILED: {e}")
            return {
                "parsing_error": str(e),
                "message": "Failed to parse code into files"
            }

    def get_system_prompt(self) -> str:
        return """You are an expert software engineer with mastery of:
- Multiple programming languages (Python, JavaScript/TypeScript, Java, Go, Rust, etc.)
- Clean code principles and best practices
- Design patterns and SOLID principles
- Error handling and edge case management
- Code documentation and readability
- Performance optimization

Your role: Implement production-quality code based on the provided architecture.

Output Format - MUST use file markers for each file:

// file: index.html
```html
[HTML code here]
```

// file: styles.css
```css
[CSS code here]
```

// file: app.js
```javascript
[JavaScript code here]
```

Reasoning: [Explain your implementation choices, algorithms used, and how you handled edge cases]

CRITICAL FILE STRUCTURE RULES:
1. ALWAYS start each file with: // file: filename.ext (or # file: filename.ext for Python)
2. For web projects, create separate files: HTML, CSS, JavaScript
3. Follow the architecture specification exactly
4. Write clean, readable, well-documented code
5. Include proper error handling
6. Add comments for complex logic
7. Ensure code is production-ready and testable
8. Handle all edge cases
9. Use appropriate design patterns

EXAMPLE OUTPUT:
// file: index.html
```html
<!DOCTYPE html>
<html>
...
</html>
```

// file: styles.css
```css
body { ... }
```

// file: script.js
```javascript
console.log('Hello');
```"""

    def build_user_prompt(self, task: str, context: Dict[str, Any]) -> str:
        # Get architecture from context (critical!)
        architecture = context.get("architecture_output", "")
        rag_patterns = context.get("rag_patterns", [])
        vision_analysis = context.get("vision_analysis", "")

        prompt = f"""Task: {task}

"""

        # PRIORITY: Vision analysis comes FIRST for image-to-code tasks
        if vision_analysis:
            prompt += f"""🎨 PIXEL-PERFECT DESIGN SPECIFICATION (YOUR PRIMARY SOURCE OF TRUTH):
{vision_analysis}

⚠️  CRITICAL IMPLEMENTATION RULES:
1. Match the design EXACTLY - this is your PRIMARY requirement
2. Use EXACT values from the spec (colors, spacing, sizes)
3. Include ONLY elements shown in the design - DO NOT add extras
4. Follow the specified tech stack (simple HTML/CSS/JS if recommended)
5. Do NOT over-engineer - keep it simple if the design is simple
6. Text must be word-for-word from the specification
7. Layout must match the visual proportions precisely

🚫 COMMON MISTAKES TO AVOID:
- Adding extra features not in the design (fancy animations, complex state management)
- Using Next.js/React for simple static designs
- Adding components not shown in the sketch (extra buttons, navbars, footers)
- Deviating from specified colors/fonts/spacing
- Over-complicating simple designs

✅ BEFORE SUBMITTING, VERIFY:
- All elements from spec are present (no missing components)
- No extra elements added (only what's in the sketch)
- Colors match exactly (use hex codes from spec)
- Spacing/sizing matches visual proportions
- Text content is word-for-word accurate
- Tech stack matches recommendation (don't use React if vanilla JS was recommended)

"""

        # Architecture is REQUIRED - this prevents synthesis conflicts
        if architecture:
            prompt += f"""Architecture Specification (MUST FOLLOW):
{architecture}

"""
        else:
            prompt += """  WARNING: No architecture specification provided.
You MUST create a simple, working implementation that follows best practices.

"""

        # Add code patterns from RAG
        if rag_patterns:
            prompt += f"""Proven Code Patterns (reference for inspiration):
"""
            for i, pattern in enumerate(rag_patterns[:2], 1):
                code_snippet = pattern.get("code_snippet", "")
                if code_snippet:
                    prompt += f"{i}. {code_snippet[:300]}...\n"
            prompt += "\n"

        prompt += """Implement production-quality code for this system.

Your implementation should:
1. **Follow Architecture**: Strictly implement the architecture specification
2. **Complete Implementation**: Include all necessary components and functions
3. **Error Handling**: Proper try-catch, validation, and error messages
4. **Documentation**: Clear comments and docstrings
5. **Best Practices**: Clean code, SOLID principles, appropriate patterns
6. **Edge Cases**: Handle all edge cases and invalid inputs
7. **Testing Hooks**: Structure code to be easily testable

Provide complete, runnable, production-ready code."""

        return prompt

    # NOTE: _build_improvement_prompt removed - base class now handles validation error feedback

    def _parse_response(self, content: str) -> Tuple[str, str]:
        """
        Override base parser to handle multi-file outputs with file markers.

        Expected format:
        // file: index.html
        ```html
        code here
        ```

        // file: styles.css
        ```css
        code here
        ```

        Reasoning: explanation here
        """
        # Pattern to match file markers (// file: or # file:)
        file_pattern = r'^(?://|#)\s*[Ff]ile:\s*(.+?)$'

        # Check if response contains file markers
        has_file_markers = re.search(file_pattern, content, re.MULTILINE)

        if has_file_markers:
            # Multi-file output - concatenate all files
            combined_code = []
            reasoning = ""

            # Split by file markers
            file_sections = re.split(file_pattern, content, flags=re.MULTILINE)

            # Process each file section
            i = 1  # Skip first element (content before first file marker)
            while i < len(file_sections):
                if i >= len(file_sections):
                    break

                filename = file_sections[i].strip()
                file_content = file_sections[i + 1] if i + 1 < len(file_sections) else ""

                # Extract code from code blocks
                if "```" in file_content:
                    parts = file_content.split("```")
                    if len(parts) >= 2:
                        code_block = parts[1]
                        # Remove language identifier
                        lines = code_block.split("\n")
                        # Comprehensive list of language identifiers
                        language_identifiers = [
                            # Web
                            "html", "css", "scss", "sass", "less",
                            "javascript", "js", "jsx", "typescript", "ts", "tsx",
                            # Backend
                            "python", "py", "java", "kotlin", "kt",
                            "go", "rust", "rs", "c", "cpp", "c++", "csharp", "cs",
                            "php", "ruby", "rb", "perl", "swift",
                            # Shell/Config
                            "bash", "sh", "shell", "zsh", "fish",
                            "json", "yaml", "yml", "toml", "xml", "ini", "env",
                            # Database
                            "sql", "postgresql", "mysql", "sqlite",
                            # Mobile
                            "dart", "flutter", "vue", "svelte",
                            # Other
                            "markdown", "md", "txt", "dockerfile", "makefile",
                            "graphql", "proto", "protobuf"
                        ]
                        if lines and lines[0].strip().lower() in language_identifiers:
                            code = "\n".join(lines[1:])
                        else:
                            code = code_block

                        # Add file marker and code to combined output
                        combined_code.append(f"# File: {filename}")
                        combined_code.append(code.strip())
                        combined_code.append("")  # Blank line between files
                else:
                    # No code block, use entire section
                    combined_code.append(f"# File: {filename}")
                    combined_code.append(file_content.strip())
                    combined_code.append("")

                i += 2  # Move to next filename (skip content we just processed)

            # Extract reasoning (text after last code block or file section)
            # Look for "Reasoning:" or text after all files
            reasoning_match = re.search(r'Reasoning:\s*(.+)', content, re.DOTALL | re.IGNORECASE)
            if reasoning_match:
                reasoning = reasoning_match.group(1).strip()
            elif len(file_sections) > 0:
                # Use any text at the end
                last_section = file_sections[-1]
                if "```" in last_section:
                    parts = last_section.split("```")
                    if len(parts) >= 3:
                        reasoning = parts[-1].strip()

            code_output = "\n".join(combined_code).strip()

            # Validation: Check if we actually extracted any code
            if not code_output or code_output == "":
                error_msg = (
                    f"[{self.name.upper()}]  ❌ CRITICAL: Multi-file parsing produced empty code!\n"
                    f"[{self.name.upper()}]  This means file markers were found but no code was extracted.\n"
                    f"[{self.name.upper()}]  Content preview: {content[:500]}..."
                )
                print(error_msg)
                raise ValueError("Implementation agent produced empty code despite having file markers")

            # Debug logging
            print(f"[{self.name.upper()}]  🔍 DEBUG: Parsed multi-file output")
            print(f"[{self.name.upper()}]  🔍 DEBUG: Output length: {len(code_output)} chars")
            print(f"[{self.name.upper()}]  🔍 DEBUG: First 300 chars:\n{code_output[:300]}")

            return code_output, reasoning
        else:
            # No file markers found - this is a critical error for multi-file projects
            print(f"[{self.name.upper()}]  ❌ CRITICAL: No file markers found in response!")
            print(f"[{self.name.upper()}]  Expected format: '# File: path/to/file.ext' or '// File: path/to/file.ext'")
            print(f"[{self.name.upper()}]  Response preview: {content[:300]}...")

            # Try base parser as last resort
            print(f"[{self.name.upper()}]  Attempting single-file fallback parser...")
            code, reasoning = super()._parse_response(content)

            # Warn if fallback succeeded (means agent didn't follow format)
            if code and code.strip():
                print(f"[{self.name.upper()}]  ⚠️  WARNING: Fallback parser extracted code, but agent should use file markers!")
                print(f"[{self.name.upper()}]  Agent needs to be retrained on proper output format.")

                # CRITICAL FIX: Add file marker to extracted code so deployment parsing works
                # Detect file type from code content
                file_extension = "html"  # Default to HTML for web projects
                if "<!DOCTYPE html>" in code or "<html" in code:
                    file_extension = "html"
                elif "function" in code or "const " in code or "let " in code or "var " in code:
                    file_extension = "js"
                elif "def " in code or "import " in code or "class " in code and ":" in code:
                    file_extension = "py"

                # Wrap code with file marker
                code_with_marker = f"# File: index.{file_extension}\n{code}"

                print(f"[{self.name.upper()}]  ✅ Added file marker: index.{file_extension}")
                return code_with_marker, reasoning

            return code, reasoning

    def _parse_code_to_files(self, code: str) -> Dict[str, str]:
        """
        Parse generated code into individual files

        Handles markers like:
        - # File: src/index.html
        - // File: app.js
        - # file: package.json
        - /* File: styles.css */

        Supports ALL common file types
        """
        import re
        import os

        print(f"[{self.name.upper()}]  🔍 Parsing code into files...")
        print(f"[{self.name.upper()}]  🔍 Code length: {len(code)} chars")

        files = {}

        # Enhanced pattern to match file markers with multiple comment styles
        file_pattern = r'^(?://|#|/\*)\s*[Ff]ile:\s*(.+?)(?:\s*\*/)?$'

        lines = code.split('\n')
        current_file = None
        current_content = []

        for line in lines:
            # Check if this line is a file marker
            match = re.match(file_pattern, line.strip())
            if match:
                # Save previous file
                if current_file and current_content:
                    content = '\n'.join(current_content).strip()
                    if content:  # Only save non-empty files
                        files[current_file] = content
                    else:
                        print(f"[{self.name.upper()}]  ⚠️  Skipping empty file: {current_file}")

                # Start new file
                current_file = match.group(1).strip()
                current_content = []

                print(f"[{self.name.upper()}]  📄 Extracted: {current_file}")
            elif current_file:
                current_content.append(line)

        # Save last file
        if current_file and current_content:
            content = '\n'.join(current_content).strip()
            if content:
                files[current_file] = content
            else:
                print(f"[{self.name.upper()}]  ⚠️  Skipping empty file: {current_file}")

        # Validation and reporting
        if files:
            print(f"[{self.name.upper()}]  ✅ Total: {len(files)} files extracted")

            # Validate file paths
            for filepath in list(files.keys()):
                # Check for suspicious patterns
                if filepath.startswith("File:") or filepath.startswith("file:"):
                    print(f"[{self.name.upper()}]  ⚠️  WARNING: Malformed path '{filepath}'")

                # Validate no absolute paths (security)
                if filepath.startswith("/") or (len(filepath) > 1 and filepath[1] == ":"):
                    print(f"[{self.name.upper()}]  ⚠️  WARNING: Absolute path detected '{filepath}' - converting")
                    filepath_clean = filepath.lstrip("/").split(":", 1)[-1].lstrip("/")
                    files[filepath_clean] = files.pop(filepath)
        else:
            print(f"[{self.name.upper()}]  ❌ ERROR: No files extracted from generated code!")
            raise ValueError("File parsing failed - no files extracted from implementation output")

        return files

    def _validate_file_imports(self, files: Dict[str, str]) -> List[Tuple[str, str]]:
        """
        Validate that all imported/required files actually exist in the generated code.

        Returns:
            List of (source_file, missing_import) tuples for any missing files
        """
        import re
        import os

        missing_files = []

        # Patterns to match various import styles
        import_patterns = [
            # JavaScript/TypeScript: import X from "./file"
            r'import\s+.+?\s+from\s+["\'](.+?)["\']',
            # JavaScript: require("./file")
            r'require\s*\(["\'](.+?)["\']\)',
            # CSS: @import "file.css"
            r'@import\s+["\'](.+?)["\']',
            # Python: from module import X
            r'from\s+\.(.+?)\s+import',
            # HTML: <link href="file.css"> or <script src="file.js">
            r'(?:href|src)\s*=\s*["\'](.+?)["\']',
        ]

        for source_file, content in files.items():
            # Get directory of source file for relative path resolution
            source_dir = os.path.dirname(source_file) if '/' in source_file else ''

            for pattern in import_patterns:
                matches = re.findall(pattern, content)

                for import_path in matches:
                    original_import = import_path  # Store for error reporting
                    is_path_alias = False

                    # Skip external imports (URLs, node_modules, absolute packages)
                    if any(skip in import_path for skip in [
                        'http://', 'https://', 'node_modules',
                        'react', 'vue', 'next', 'vite', 'express', '@vercel', '@sentry', '@upstash'
                    ]):
                        continue

                    # Handle TypeScript path aliases (@/ → resolve to project root)
                    if import_path.startswith('@/'):
                        # @/ typically maps to the project root or src/
                        # Convert @/components/Header to components/Header
                        import_path = import_path[2:]  # Remove @/
                        is_path_alias = True

                    # Skip absolute imports (e.g., Python standard library)
                    if not import_path.startswith('.') and not import_path.startswith('/') and not is_path_alias:
                        # Unless it's a local file reference in HTML
                        if source_file.endswith('.html') and not import_path.startswith('http'):
                            pass  # Check these
                        else:
                            continue

                    # Resolve relative path
                    if import_path.startswith('./') or import_path.startswith('../'):
                        clean_path = import_path
                        if source_dir:
                            full_path = os.path.normpath(os.path.join(source_dir, import_path))
                        else:
                            full_path = import_path.lstrip('./')
                    else:
                        full_path = import_path

                    # Add common extensions if not present
                    possible_paths = [full_path]
                    if not any(full_path.endswith(ext) for ext in ['.js', '.jsx', '.ts', '.tsx', '.css', '.py']):
                        possible_paths.extend([
                            f"{full_path}.js",
                            f"{full_path}.jsx",
                            f"{full_path}.ts",
                            f"{full_path}.tsx",
                            f"{full_path}/index.js",
                            f"{full_path}/index.jsx",
                            f"{full_path}/index.ts",  # TypeScript index files
                            f"{full_path}/index.tsx",  # TypeScript React index files
                        ])

                    # Check if any variant exists in generated files
                    found = False
                    for possible_path in possible_paths:
                        normalized_path = possible_path.replace('\\', '/')

                        if normalized_path in files or f"src/{normalized_path}" in files:
                            found = True
                            break

                        check_paths = [
                            normalized_path.lstrip('./'),
                            normalized_path.lstrip('src/'),
                            f"src/{normalized_path.lstrip('./')}"
                        ]

                        if any(cp in files for cp in check_paths):
                            found = True
                            break

                    if not found:
                        # Only report if it looks like a local file import
                        if import_path.startswith('.') or is_path_alias or (
                            source_file.endswith('.html') and
                            not import_path.startswith('http') and
                            any(import_path.endswith(ext) for ext in ['.css', '.js', '.png', '.jpg', '.svg'])
                        ):
                            # Report using original import path (with @/ if it had one)
                            missing_files.append((source_file, original_import))

        return missing_files

    def _validate_required_files(self, files: Dict[str, str]) -> List[str]:
        """
        Validate that the project has minimum required files to actually run.

        Detects project type and checks for critical files that must exist.
        This prevents deploying incomplete projects (e.g., Next.js with only config files).

        Returns:
            List of missing required files (empty list if all present)
        """
        filenames = list(files.keys())
        missing = []

        # Detect Next.js project
        if 'package.json' in filenames and 'next' in files['package.json'].lower():
            # Next.js requires at minimum:
            # - app/page.tsx or pages/index.tsx (entry point)
            # - app/layout.tsx or pages/_app.tsx (layout/wrapper)

            has_app_router = any(f.startswith('app/') or f.startswith('src/app/') for f in filenames)
            has_pages_router = any(f.startswith('pages/') or f.startswith('src/pages/') for f in filenames)

            if has_app_router or not has_pages_router:
                # Using App Router (Next.js 13+)
                has_page = any(
                    f in filenames
                    for f in ['app/page.tsx', 'app/page.jsx', 'src/app/page.tsx', 'src/app/page.jsx']
                )
                has_layout = any(
                    f in filenames
                    for f in ['app/layout.tsx', 'app/layout.jsx', 'src/app/layout.tsx', 'src/app/layout.jsx']
                )

                if not has_page:
                    missing.append('app/page.tsx (or src/app/page.tsx)')
                if not has_layout:
                    missing.append('app/layout.tsx (or src/app/layout.tsx)')
            else:
                # Using Pages Router (Next.js <13)
                has_index = any(
                    f in filenames
                    for f in ['pages/index.tsx', 'pages/index.jsx', 'src/pages/index.tsx', 'src/pages/index.jsx']
                )

                if not has_index:
                    missing.append('pages/index.tsx (or src/pages/index.tsx)')

        # Detect static HTML project
        elif any(f.endswith('.html') for f in filenames):
            # Static HTML requires at least one .html file (already have it)
            pass

        # Detect React/Vite project
        elif 'package.json' in filenames and 'vite' in files['package.json'].lower():
            # Vite requires index.html and src/main.tsx
            if 'index.html' not in filenames:
                missing.append('index.html')

            has_main = any(
                f in filenames
                for f in ['src/main.tsx', 'src/main.jsx', 'src/index.tsx', 'src/index.jsx']
            )
            if not has_main:
                missing.append('src/main.tsx (or src/main.jsx)')

        # Detect Express API
        elif 'package.json' in filenames and 'express' in files['package.json'].lower():
            # Express requires server file
            has_server = any(
                f in filenames
                for f in ['server.js', 'index.js', 'app.js', 'src/server.js', 'src/index.js']
            )
            if not has_server:
                missing.append('server.js (or index.js/app.js)')

        # Detect Python projects
        elif any(f.endswith('.py') for f in filenames):
            # Python web apps should have main/app/server file
            # But allow any .py file for flexibility
            pass

        return missing
