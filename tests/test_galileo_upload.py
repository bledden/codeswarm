#!/usr/bin/env python3.11
"""
Test Galileo Observe upload to verify data is reaching the platform
"""
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def test_galileo_upload():
    """Test minimal Galileo workflow upload"""
    print("=" * 80)
    print("GALILEO OBSERVE UPLOAD TEST")
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
    try:
        from galileo_observe import ObserveWorkflows, Message, MessageRole
        print("✅ Galileo Observe SDK imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Galileo Observe: {e}")
        return

    print()

    # Initialize logger
    try:
        logger = ObserveWorkflows(project_name=project)
        print(f"✅ Initialized ObserveWorkflows for project: {project}")
    except Exception as e:
        print(f"❌ Failed to initialize ObserveWorkflows: {e}")
        import traceback
        traceback.print_exc()
        return

    print()

    # Create test workflow
    try:
        print("📝 Creating test workflow...")
        wf = logger.add_workflow(
            input={"task": "test galileo upload", "agent": "diagnostic"},
            name="CodeSwarm-diagnostic-test"
        )
        print("✅ Workflow created")
    except Exception as e:
        print(f"❌ Failed to create workflow: {e}")
        import traceback
        traceback.print_exc()
        return

    print()

    # Add LLM call
    try:
        print("🤖 Adding test LLM call...")
        wf.add_llm(
            input=Message(content="Test prompt", role=MessageRole.user),
            output=Message(content="Test response", role=MessageRole.assistant),
            model="test-model",
            input_tokens=10,
            output_tokens=20,
            metadata={
                "agent": "diagnostic",
                "test": "true"
            },
            name="diagnostic-test"
        )
        print("✅ LLM call added")
    except Exception as e:
        print(f"❌ Failed to add LLM call: {e}")
        import traceback
        traceback.print_exc()
        return

    print()

    # Conclude workflow
    try:
        print("✅ Concluding workflow...")
        wf.conclude(output={"result": "test successful"})
        print("✅ Workflow concluded")
    except Exception as e:
        print(f"❌ Failed to conclude workflow: {e}")
        import traceback
        traceback.print_exc()
        return

    print()

    # Upload workflows
    try:
        print("📤 Uploading workflows to Galileo...")
        await asyncio.get_event_loop().run_in_executor(
            None, logger.upload_workflows
        )
        print("✅ Upload completed successfully!")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print()
    print("=" * 80)
    print(f"🌐 Check Galileo dashboard at: {console_url}")
    print(f"   Project: {project}")
    print("=" * 80)
    print()
    print("If you still see 0 experiments, possible causes:")
    print("  1. Data processing delay (wait 1-2 minutes)")
    print("  2. Project name mismatch (check exact spelling)")
    print("  3. API key permissions issue")
    print("  4. Galileo Observe version incompatibility")
    print()

    # Check SDK version
    try:
        import galileo_observe
        version = getattr(galileo_observe, '__version__', 'unknown')
        print(f"📦 galileo-observe version: {version}")
    except:
        print("⚠️  Could not determine galileo-observe version")


if __name__ == "__main__":
    asyncio.run(test_galileo_upload())
