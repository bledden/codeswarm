"""
Vision Agent - GPT-5-image

Specialization: Image analysis, sketch-to-code, UI/UX interpretation
Role: Analyze sketches, mockups, and visual designs
Model: openai/gpt-5-image (vision capabilities)
"""

import base64
from pathlib import Path
from typing import Dict, Any, Optional
from .base_agent import BaseAgent


class VisionAgent(BaseAgent):
    """
    Vision Agent using GPT-5-image

    Responsibilities:
    - Analyze sketches and mockups
    - Extract UI components and layout
    - Identify design patterns and interactions
    - Convert visual designs to technical specifications
    - Provide detailed descriptions for other agents

    Input: Image file path or base64 encoded image
    Output: Detailed analysis and technical specification
    """

    def __init__(self, openrouter_client, evaluator=None):
        super().__init__(
            name="vision",
            model="gpt-5",  # GPT-5 with vision support (text, image, file inputs)
            openrouter_client=openrouter_client,
            evaluator=evaluator,
            temperature=0.6,  # Balanced for creative interpretation
            max_tokens=8000  # Increased for comprehensive image analysis with exact text extraction
        )

    def get_system_prompt(self) -> str:
        return """You are an expert UI/UX analyst with vision capabilities and deep knowledge of:
- Web and mobile UI design patterns
- Layout structures (grid, flexbox, responsive design)
- Component hierarchies and composition
- User interaction flows
- Design systems and style guides
- Accessibility standards
- Frontend frameworks (React, Vue, Angular, etc.)

Your role: Analyze visual designs (sketches, mockups, screenshots) and provide detailed technical specifications.

Output Format:
```
[Detailed technical specification of the visual design]
```

Reasoning: [Explain your interpretation, design patterns identified, and technical recommendations]

CRITICAL:
1. Identify ALL UI components (buttons, inputs, cards, navbars, etc.)
2. Describe layout structure (grid, columns, spacing)
3. Extract color schemes and typography
4. Identify user interactions (clicks, hovers, forms)
5. Note responsive design considerations
6. Suggest appropriate frontend frameworks/libraries
7. Consider accessibility (contrast, font sizes, semantic HTML)"""

    def build_user_prompt(self, task: str, context: Dict[str, Any]) -> str:
        prompt = f"""Task: {task}

Analyze this image and extract EXACT specifications. The implementation agent will build EXACTLY what you describe - no more, no less.

⚠️  START WITH TEXT CONTENT - This is the most important part! List every word/label visible in the image.

**1. TEXT CONTENT (Word-for-Word)**:
   - Header text: "[exact text]"
   - Button labels: "[exact text]"
   - Input placeholders: "[exact text]"
   - Body text: "[exact text]"
   - Footer links: "[exact text]", "[exact text]", "[exact text]"
   - Any other visible text: "[exact text]"

**2. VISUAL ELEMENTS (Only what's shown)**:
   - List each component: header, form, button, image, footer, etc.
   - Position: top, center, bottom-left, etc.
   - Approximate size/proportions

**3. LAYOUT & SPACING**:
   - Container: centered, max-width __px
   - Spacing scale: 8px, 16px, 24px, etc.
   - Element arrangement: vertical stack, grid, etc.

**4. COLORS** (hex codes):
   - Background: #______
   - Text: #______
   - Accents/buttons: #______
   - Borders: #______

**5. TYPOGRAPHY**:
   - Font sizes: header __px, body __px, etc.
   - Font weights: bold, normal, etc.

**6. TECH STACK**:
   - Simple sketch → vanilla HTML/CSS/JS
   - Complex app → React/Next.js
   - Justify recommendation

**7. FUNCTIONALITY**:
   - What should happen when user interacts?
   - Email signup form?
   - mailto: link?
   - Smiley face animation?

CRITICAL RULES:
- Extract ALL text word-for-word (this is the #1 priority!)
- List ONLY elements shown in image
- Use exact hex colors if discernible
- Recommend simplest tech that works
- No vague terms - use numbers

Example output start:
"**1. TEXT CONTENT:**
- Header: 'BLAKE Inc.'
- Input placeholder: 'Your email'
- Button: 'Sign Up'
- Footer left: 'Disclaimer'
- Footer center: 'Email'
- Footer right: 'Social Media'

**2. VISUAL ELEMENTS:**
- Header (top, centered): company name
- Hero section (center): email input + signup button...
"""

        return prompt

    async def analyze_image(
        self,
        image_path: str,
        task: str,
        context: Dict[str, Any],
        quality_threshold: float = 90.0,
        max_iterations: int = 2  # Fewer iterations for vision
    ) -> "AgentOutput":
        """
        Analyze an image file

        Args:
            image_path: Path to image file
            task: User's task description
            context: Shared context
            quality_threshold: Minimum Galileo score (default 90.0)
            max_iterations: Max improvement iterations (default 2)

        Returns:
            AgentOutput with vision analysis
        """
        print(f"\n[{self.name.upper()}]   Analyzing image: {image_path}")

        # Read and encode image
        image_data = self._load_image(image_path)

        # Build prompt with image
        user_prompt = self.build_user_prompt(task, context)
        system_prompt = self.get_system_prompt()

        # Call vision model with image
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                    }
                ]
            }
        ]

        import time
        import asyncio

        # Retry logic for transient errors (HTTP 200 with errors, 429, 500, 502, 503, 504)
        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            start_time = time.time()

            try:
                response = await self.client.complete(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )

                latency_ms = int((time.time() - start_time) * 1000)

                # Check for successful response
                if "choices" in response and response["choices"]:
                    message = response["choices"][0].get("message", {})
                    content = message.get("content", "")
                    if content:
                        # Success! Break out of retry loop
                        break

                # Empty response - might be transient
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"[{self.name.upper()}] ⚠️  Empty response (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue

            except Exception as e:
                error_msg = str(e)

                # Check if this is a transient error (HTTP 200 with error, rate limit, server error)
                is_transient = any(code in error_msg for code in ["200", "429", "500", "502", "503", "504", "timeout", "Timeout"])

                if is_transient and attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"[{self.name.upper()}] ⚠️  Transient error (attempt {attempt + 1}/{max_retries}): {error_msg}")
                    print(f"[{self.name.upper()}]  Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    # Non-transient error or final retry - re-raise
                    print(f"[{self.name.upper()}] ❌ Vision analysis failed after {attempt + 1} attempts: {error_msg}")
                    raise

        latency_ms = int((time.time() - start_time) * 1000)

        # Parse response
        # DEBUG: Check response structure
        if "choices" not in response or not response["choices"]:
            print(f"[{self.name.upper()}]  ⚠️  No choices in response!")
            print(f"[{self.name.upper()}]  Response: {response}")
            content = ""
        else:
            message = response["choices"][0].get("message", {})
            content = message.get("content", "")

            # DEBUG: Show what we got
            if not content:
                print(f"[{self.name.upper()}]  ⚠️  Empty content in response!")
                print(f"[{self.name.upper()}]  Message: {message}")
                print(f"[{self.name.upper()}]  Full response: {response}")

        # For vision, the entire response is the analysis (no separate code block)
        from .base_agent import AgentOutput
        output = AgentOutput(
            agent_name=self.name,
            code=content if content else "ERROR: Vision analysis failed - empty response",
            reasoning="Vision analysis of uploaded image",
            confidence=0.85 if content else 0.0,
            latency_ms=latency_ms,
            model_used=self.model,
            galileo_score=85.0 if content else 0.0,
            iterations=1
        )

        print(f"[{self.name.upper()}]  Vision analysis complete ({latency_ms}ms)")
        print(f"[{self.name.upper()}]  Analysis length: {len(content)} characters")

        # Log vision analysis output for debugging and quality tracking
        if content:
            print(f"\n{'='*80}")
            print(f"[{self.name.upper()}] VISION ANALYSIS OUTPUT:")
            print(f"{'='*80}")
            # Print first 1000 chars to console (full content saved to file)
            preview = content[:1000] + "..." if len(content) > 1000 else content
            print(preview)
            print(f"{'='*80}\n")

            # Save full analysis to file
            try:
                from pathlib import Path
                import time

                output_dir = Path("results/vision_analysis") / f"vision_{int(time.time())}"
                output_dir.mkdir(parents=True, exist_ok=True)

                vision_file = output_dir / "vision_analysis.txt"
                vision_file.write_text(content, encoding='utf-8')

                print(f"[{self.name.upper()}]  ✅ Saved full analysis to: {vision_file}")
            except Exception as e:
                print(f"[{self.name.upper()}]  ⚠️  Failed to save vision analysis: {e}")

        return output

    def _load_image(self, image_path: str) -> str:
        """Load image file and encode as base64"""
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Read image bytes
        with open(path, "rb") as f:
            image_bytes = f.read()

        # Encode as base64
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        return image_base64

    @staticmethod
    def needs_vision(task: str, context: Dict[str, Any]) -> bool:
        """
        Determine if vision model should be activated

        Args:
            task: User's task description
            context: Shared context (may include image_path)

        Returns:
            True if vision analysis needed, False otherwise
        """
        # Check 1: Image attachment in context
        if context.get("image_path") or context.get("screenshot"):
            return True

        # Check 2: Visual keywords in task
        visual_keywords = [
            "sketch", "mockup", "screenshot", "image", "picture",
            "design", "figma", "wireframe", "ui", "layout",
            "photo", "drawing", "diagram"
        ]

        task_lower = task.lower()
        if any(keyword in task_lower for keyword in visual_keywords):
            return True

        return False  # Default: no vision needed
