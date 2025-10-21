#!/usr/bin/env python3.11
"""
Test Galileo upload with verbose response checking
"""
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def test_verbose_upload():
    """Test Galileo upload and inspect response"""
    print("=" * 80)
    print("GALILEO VERBOSE UPLOAD TEST")
    print("=" * 80)
    print()

    # Load config
    api_key = os.getenv("GALILEO_API_KEY")
    project = os.getenv("GALILEO_PROJECT", "codeswarm-hackathon")
    console_url = os.getenv("GALILEO_CONSOLE_URL", "https://app.galileo.ai")

    print(f"Project: {project}")
    print(f"API Key (last 10 chars): ...{api_key[-10:]}")
    print(f"Console URL: {console_url}")
    print()

    # Set environment variables
    os.environ["GALILEO_API_KEY"] = api_key
    os.environ["GALILEO_CONSOLE_URL"] = console_url

    # Import Galileo Observe
    from galileo_observe import ObserveWorkflows, Message, MessageRole

    # Initialize logger
    logger = ObserveWorkflows(project_name=project)
    print(f"✅ Initialized ObserveWorkflows")
    print()

    # Create test workflow
    print("📝 Creating test workflow...")
    wf = logger.add_workflow(
        input={"task": "verbose test", "agent": "diagnostic"},
        name="CodeSwarm-verbose-test"
    )
    print("✅ Workflow created")
    print()

    # Add LLM call
    print("🤖 Adding test LLM call...")
    wf.add_llm(
        input=Message(content="Test prompt for verbose upload", role=MessageRole.user),
        output=Message(content="Test response from model", role=MessageRole.assistant),
        model="claude-sonnet-4.5",
        input_tokens=15,
        output_tokens=25,
        metadata={
            "agent": "diagnostic",
            "test": "verbose",
            "env": "production"
        },
        name="verbose-diagnostic-test"
    )
    print("✅ LLM call added")
    print()

    # Conclude workflow
    print("✅ Concluding workflow...")
    wf.conclude(output={"result": "verbose test successful"})
    print("✅ Workflow concluded")
    print()

    # Check workflows before upload
    print(f"📦 Workflows in logger: {len(logger.workflows)}")
    if logger.workflows:
        print(f"   Workflow names: {[w.name for w in logger.workflows]}")
    print()

    # Try async upload first
    print("📤 Attempting ASYNC upload...")
    try:
        result = await logger.async_upload_workflows()
        print("✅ ASYNC Upload completed!")
        print(f"   Result type: {type(result)}")
        print(f"   Result: {result}")
    except Exception as e:
        print(f"❌ ASYNC Upload failed: {e}")
        import traceback
        traceback.print_exc()
        print()

        # Fallback to sync upload
        print("📤 Attempting SYNC upload (fallback)...")
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, logger.upload_workflows
            )
            print("✅ SYNC Upload completed!")
            print(f"   Result type: {type(result)}")
            print(f"   Result: {result}")
        except Exception as e2:
            print(f"❌ SYNC Upload also failed: {e2}")
            import traceback
            traceback.print_exc()
            return

    print()
    print("=" * 80)
    print("UPLOAD SUCCESSFUL")
    print("=" * 80)
    print()
    print(f"🌐 Check Galileo at: {console_url}")
    print(f"   Project: {project}")
    print()
    print("If data still doesn't appear:")
    print("  1. Wait 2-5 minutes for processing")
    print("  2. Check the CONSOLE URL is correct")
    print("  3. Verify project name matches exactly (case-sensitive)")
    print("  4. Check if you're in the right workspace/organization")
    print()


if __name__ == "__main__":
    asyncio.run(test_verbose_upload())
