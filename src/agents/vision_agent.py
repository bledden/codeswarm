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
            max_tokens=3000
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

Analyze the provided image (sketch/mockup/screenshot) and provide a PIXEL-PERFECT technical specification that will be used to build the exact design shown.

⚠️  CRITICAL: Be extremely specific with measurements, colors, spacing, and layout. The implementation agent will follow your specs EXACTLY.

Your analysis MUST include:

1. **Exact Measurements & Layout**:
   - Overall canvas/viewport size (if discernible)
   - Precise spacing values (margins, padding) in pixels or relative units
   - Exact element positioning (centered, top-left at X,Y, etc.)
   - Grid columns and gaps if applicable
   - Header height, footer height, content area dimensions
   - Container max-width and centering

2. **All Visual Elements** (Do NOT add elements not in the image):
   - List ONLY components visible in the image
   - Exact text content (word-for-word)
   - Component sizes (width x height where measurable)
   - Element hierarchy and nesting structure
   - Z-index layering if elements overlap

3. **Exact Colors** (use hex codes if possible):
   - Background colors (main page, sections, components)
   - Text colors (headers, body, links, labels)
   - Border colors
   - Shadow colors and opacity
   - Button/interactive element colors (default, hover if shown)

4. **Typography Details**:
   - Font families (or closest web-safe alternatives)
   - Exact font sizes in px/rem for each text element
   - Font weights (regular, medium, bold, etc.)
   - Line heights and letter spacing
   - Text alignment (left, center, right)

5. **Spacing System**:
   - Identify consistent spacing scale (8px, 16px, 24px, etc.)
   - Margins between sections
   - Padding inside components
   - Gap between related elements

6. **Borders, Shadows & Effects**:
   - Border thickness, style (solid/dashed), radius
   - Box shadows (offset-x, offset-y, blur, spread, color)
   - Any gradients, patterns, or textures
   - Opacity/transparency values

7. **Simple Implementation Approach**:
   - Recommend the SIMPLEST tech stack that can achieve this design
   - For simple sketches: prefer vanilla HTML/CSS/JS over frameworks
   - For complex apps: suggest React/Next.js/etc.
   - Identify if any animations/interactions are shown
   - Note responsive breakpoints if multiple device views shown

8. **Validation Checklist** (for implementation agent):
   - ✓ All elements from sketch are present
   - ✓ No extra elements added
   - ✓ Colors match exactly
   - ✓ Spacing matches the visual proportions
   - ✓ Layout structure matches (grid, flexbox, positioning)
   - ✓ Text content is word-for-word accurate

Provide a comprehensive technical specification with EXACT values wherever possible. Avoid vague terms like "medium padding" - use "24px padding" instead.

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
