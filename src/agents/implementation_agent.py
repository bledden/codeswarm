"""
Implementation Agent - GPT-5 Pro

Specialization: Code generation, implementation of architecture
Role: Generate production-quality code based on architecture
Model: openai/gpt-5-pro (flagship code generation)
"""

from typing import Dict, Any, Tuple, List
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
            max_tokens=6000  # More tokens for longer code
        )
        # Track validation errors across iterations for improvement feedback
        self._last_validation_error = None

    async def execute(
        self,
        task: str,
        context: Dict[str, Any],
        quality_threshold: float = 90.0,
        max_iterations: int = 3
    ):
        """
        Override base execute() to add file validation after code generation.

        Validates that:
        1. Code can be parsed into individual files
        2. All imports/references point to files that exist

        If validation fails, adds error to context and retries.
        """
        from .base_agent import AgentOutput
        import time

        print(f"\n[{self.name.upper()}]  Starting execution with file validation...")

        iteration = 0
        best_output = None
        best_score = 0.0

        while iteration < max_iterations:
            iteration += 1
            print(f"[{self.name.upper()}]  Iteration {iteration}/{max_iterations}")

            start_time = time.time()

            # Build prompt (add validation error feedback if retrying)
            if iteration == 1 or best_output is None:
                # First iteration OR previous iteration failed validation (no output created)
                user_prompt = self.build_user_prompt(task, context)

                # If retrying after validation failure, add error feedback
                if iteration > 1 and self._last_validation_error:
                    error = self._last_validation_error

                    if "missing_files" in error:
                        missing_files = error["missing_files"]
                        user_prompt += f"""

❌ PREVIOUS ATTEMPT FAILED VALIDATION:
Your code references {len(missing_files)} files that you did not create!

Missing files:
"""
                        for source_file, missing_import in missing_files[:5]:
                            user_prompt += f"  - {source_file} imports '{missing_import}' (FILE NOT FOUND)\n"

                        if len(missing_files) > 5:
                            user_prompt += f"  ... and {len(missing_files) - 5} more\n"

                        user_prompt += """
FIX REQUIRED:
1. Generate ALL files that are referenced in imports, links, or requires
2. If you import "../css/responsive.css", you MUST create "# File: css/responsive.css"
3. If HTML references <script src="../js/main.js">, you MUST create "# File: js/main.js"
4. Do NOT reference files you haven't created
5. Every import/require MUST point to an actual file you generated
"""

                    elif "parsing_error" in error:
                        user_prompt += f"""

❌ PREVIOUS ATTEMPT FAILED PARSING:
Your code could not be parsed into files!

Error: {error["parsing_error"]}

FIX REQUIRED:
1. Use proper file markers: "# File: filename.ext" or "// File: filename.ext"
2. Each file MUST start with a file marker
3. Follow the format shown in the system prompt exactly
"""
            else:
                # Normal improvement iteration (has previous successful output)
                user_prompt = self._build_improvement_prompt(
                    task, context, best_output, best_score
                )

            # Call model
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": user_prompt}
            ]

            response = await self.client.complete(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            latency_ms = int((time.time() - start_time) * 1000)

            # Parse response
            content = response["choices"][0]["message"]["content"]
            code, reasoning = self._parse_response(content)

            # CRITICAL VALIDATION: Check for empty outputs
            if not code or not code.strip():
                print(f"[{self.name.upper()}]  ❌ ERROR: Empty code output detected!")
                if iteration >= max_iterations:
                    raise ValueError(f"{self.name} agent produced empty code after {max_iterations} iterations")
                print(f"[{self.name.upper()}]  Retrying in next iteration...")
                continue

            if not reasoning or not reasoning.strip():
                print(f"[{self.name.upper()}]  ⚠️  WARNING: Empty reasoning (code is present, continuing)")

            # CRITICAL: Parse and validate files BEFORE creating output
            try:
                parsed_files = self._parse_code_to_files(code)

                # Validate imports
                missing_files = self._validate_file_imports(parsed_files)

                if missing_files:
                    # Validation failed - prepare for retry
                    print(f"[{self.name.upper()}]  ❌ VALIDATION FAILED: {len(missing_files)} missing file references!")
                    for source_file, missing_import in missing_files:
                        print(f"[{self.name.upper()}]      {source_file} → {missing_import}")

                    # Store error for next iteration
                    self._last_validation_error = {
                        "missing_files": missing_files,
                        "message": f"Generated code references {len(missing_files)} files that don't exist"
                    }

                    # If this is the last iteration, raise error
                    if iteration >= max_iterations:
                        raise ValueError(
                            f"Implementation generated incomplete code after {max_iterations} attempts. "
                            f"Missing {len(missing_files)} file references: {missing_files[:3]}"
                        )

                    # Otherwise, continue to next iteration
                    print(f"[{self.name.upper()}]  🔄 Retrying with validation feedback...")
                    continue

                # Validation passed!
                print(f"[{self.name.upper()}]  ✅ File validation passed ({len(parsed_files)} files, all imports valid)")
                self._last_validation_error = None  # Clear error

            except ValueError as e:
                # Parsing failed
                print(f"[{self.name.upper()}]  ❌ FILE PARSING FAILED: {e}")

                self._last_validation_error = {
                    "parsing_error": str(e),
                    "message": "Failed to parse code into files"
                }

                if iteration >= max_iterations:
                    raise ValueError(f"Implementation failed to generate parseable code after {max_iterations} attempts: {e}")

                print(f"[{self.name.upper()}]  🔄 Retrying with parsing feedback...")
                continue

            # Create output with parsed_files
            output = AgentOutput(
                agent_name=self.name,
                code=code,
                reasoning=reasoning,
                confidence=0.85,
                latency_ms=latency_ms,
                model_used=self.model,
                iterations=iteration,
                parsed_files=parsed_files  # Include validated files
            )

            # Evaluate with Galileo if available
            if self.evaluator:
                try:
                    usage = response.get("usage", {})
                    input_tokens = usage.get("prompt_tokens", 0)
                    output_tokens = usage.get("completion_tokens", 0)

                    score = await self.evaluator.evaluate(
                        task=task,
                        output=code,
                        agent=self.name,
                        model=self.model,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        latency_ms=latency_ms
                    )
                    output.galileo_score = score
                    print(f"[{self.name.upper()}]  Galileo score: {score:.1f}/100")

                    # Update best if better
                    if score > best_score:
                        best_score = score
                        best_output = output

                    # Check quality threshold
                    if score >= quality_threshold:
                        print(f"[{self.name.upper()}]  Quality threshold met ({score:.1f} >= {quality_threshold})")
                        return output

                except Exception as e:
                    print(f"[{self.name.upper()}]  Galileo evaluation failed: {e}")
                    output.galileo_score = 85.0
            else:
                output.galileo_score = 85.0
                return output

        # Max iterations reached
        print(f"[{self.name.upper()}] ⏸  Max iterations reached. Best score: {best_score:.1f}/100")
        return best_output if best_output else output

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

        # Architecture is REQUIRED - this prevents synthesis conflicts
        if architecture:
            prompt += f"""Architecture Specification (MUST FOLLOW):
{architecture}

"""
        else:
            prompt += """  WARNING: No architecture specification provided.
You MUST create a simple, working implementation that follows best practices.

"""

        # Add vision analysis if available
        if vision_analysis:
            prompt += f"""Vision Analysis (from sketch/mockup):
{vision_analysis}

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

    def _build_improvement_prompt(
        self,
        task: str,
        context: Dict[str, Any],
        previous_output,
        previous_score: float
    ) -> str:
        """Build improvement prompt with validation error feedback"""
        base_prompt = self.build_user_prompt(task, context)

        improvement = f"""
PREVIOUS ATTEMPT (Score: {previous_score:.1f}/100):
```
{previous_output.code[:500]}...
```

Your previous code scored {previous_score:.1f}/100, which is below the quality threshold of 90.
"""

        # Add validation error feedback if present
        if self._last_validation_error:
            error = self._last_validation_error

            if "missing_files" in error:
                missing_files = error["missing_files"]
                improvement += f"""
❌ CRITICAL FILE VALIDATION ERROR:
Your code references {len(missing_files)} files that you did not create!

Missing files:
"""
                for source_file, missing_import in missing_files[:5]:  # Show first 5
                    improvement += f"  - {source_file} imports '{missing_import}' (FILE NOT FOUND)\n"

                if len(missing_files) > 5:
                    improvement += f"  ... and {len(missing_files) - 5} more\n"

                improvement += """
FIX REQUIRED:
1. Generate ALL files that are referenced in imports, links, or requires
2. If you import "./styles.css", you MUST create a file marked as "# File: styles.css"
3. If HTML references <script src="app.js">, you MUST create "# File: app.js"
4. Do NOT reference files you haven't created
5. Every import/require MUST point to an actual file you generated

"""

            elif "parsing_error" in error:
                improvement += f"""
❌ CRITICAL PARSING ERROR:
Your code could not be parsed into individual files!

Error: {error["parsing_error"]}

FIX REQUIRED:
1. Use proper file markers: "# File: filename.ext" or "// File: filename.ext"
2. Each file MUST start with a file marker
3. Follow the format shown in the system prompt exactly

"""

        improvement += f"""
IMPROVEMENT REQUIRED:
1. Review your previous attempt and the errors above
2. Generate COMPLETE code with ALL referenced files
3. Ensure ALL imports/requires point to files you create
4. Follow proper file marker format
5. Ensure score >= 90/100

{base_prompt}
"""
        return improvement

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
                    # Skip external imports (URLs, node_modules, absolute packages)
                    if any(skip in import_path for skip in [
                        'http://', 'https://', 'node_modules', '@/',
                        'react', 'vue', 'next', 'vite', 'express'
                    ]):
                        continue

                    # Skip absolute imports (e.g., Python standard library)
                    if not import_path.startswith('.') and not import_path.startswith('/'):
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
                        if import_path.startswith('.') or (
                            source_file.endswith('.html') and
                            not import_path.startswith('http') and
                            any(import_path.endswith(ext) for ext in ['.css', '.js', '.png', '.jpg', '.svg'])
                        ):
                            missing_files.append((source_file, import_path))

        return missing_files
