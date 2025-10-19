# Auto-Extract and Launch Feature

## Overview

CodeSwarm now **automatically extracts and sets up web projects** after code generation, then **prompts the user** to launch the development server immediately!

## How It Works

### 1. Automatic Detection
After code generation completes, CodeSwarm automatically:
- Detects if the generated code is a web project (checks for `package.json`)
- Extracts all files from the consolidated `implementation.js` into proper project structure
- Installs dependencies via `npm install`
- Creates a convenient `launch.sh` script

### 2. User Prompt
Once extraction and setup is complete, the user sees:

```
================================================================================
                        ✅ PROJECT READY TO LAUNCH!
================================================================================

📁 Project location: output/project_20251018_233128

🚀 Would you like to launch the development server now? (y/n):
```

### 3. Options

**If user types 'y':**
- Development server starts immediately
- Website opens at http://localhost:3000
- User sees live output in terminal
- Press Ctrl+C to stop

**If user types 'n':**
- Instructions are provided for manual launch later:
  ```
  📝 To launch later, run:
     cd output/project_20251018_233128
     ./launch.sh

     OR:
     npm run dev
  ```

## What Gets Created

When CodeSwarm extracts a project, it creates:

```
output/
├── code_TIMESTAMP/              # Original output (preserved)
│   └── implementation.js
└── project_TIMESTAMP/           # Extracted, runnable project
    ├── package.json
    ├── next.config.js
    ├── launch.sh              # One-command launcher
    ├── node_modules/          # Dependencies installed
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   ├── styles/
    │   └── ...
    └── ...
```

## User Experience Flow

### Before (Manual Process):
1. ✅ Run: `codeswarm generate "Create a website"`
2. ⏳ Wait for generation...
3. ❌ **STOPPED HERE** - User has files but can't run them
4. 😕 User needs to manually:
   - Find the implementation.js file
   - Parse and extract all files
   - Create proper directory structure
   - Run `npm install`
   - Run `npm run dev`

### After (Automatic):
1. ✅ Run: `codeswarm generate "Create a website"`
2. ⏳ Wait for generation...
3. ✅ **Auto-extraction happens**
4. ✅ **Dependencies installed**
5. ✅ **Prompted to launch**
6. 🚀 Type 'y' → Website running!

## Technical Implementation

### Location
The feature is integrated into `codeswarm_cli.py`:
- **Method**: `_extract_and_prompt_launch()`
- **Called from**: `save_code_files()` (after all files are saved)
- **Lines**: 390-519

### Key Features

#### Smart File Extraction
```python
# Detects file markers like:
// file: package.json
// file: src/components/Header.tsx
// file: next.config.js

# Extracts to proper paths:
project_TIMESTAMP/package.json
project_TIMESTAMP/src/components/Header.tsx
project_TIMESTAMP/next.config.js
```

#### Automatic Dependency Installation
```python
# Runs npm install with:
- 5-minute timeout
- Error handling for missing npm
- Graceful degradation if install fails
```

#### Launch Script Generation
Creates a `launch.sh` that:
- Checks for dependencies
- Runs `npm install` if needed
- Starts dev server
- Shows helpful messages

### Edge Cases Handled

1. **Non-web projects**: Silently skips (no prompt)
2. **Missing npm**: Shows install instructions
3. **Install timeout**: Continues anyway (user can install manually)
4. **User interruption**: Clean Ctrl+C handling
5. **Both old/new format**: Supports files in root or `implementation/` subdirectory

## Benefits

### For Users
✅ **Zero friction** from generation to running website
✅ **No manual file extraction** needed
✅ **Automatic dependency setup**
✅ **One-command launch** anytime via `launch.sh`
✅ **Clear instructions** if choosing to launch later

### For Demo/Hackathon
🎯 **Instant wow factor** - "Generate → Type 'y' → See it running!"
🎯 **Removes setup barrier** - Non-technical users can generate & launch
🎯 **Professional UX** - Polished, production-ready experience

## Example Output

```
📁 Code saved to: output/code_20251018_233128/
   Total files: 15
   ✅ implementation/implementation.js
   ✅ architecture/architecture.md
   ✅ security/security.md
   ✅ testing/testing.test.js

================================================================================
                        🚀 WEB PROJECT DETECTED!
================================================================================

📦 Extracting project files to: output/project_20251018_233128/

  ✅ package.json
  ✅ next.config.js
  ✅ tailwind.config.ts
  ✅ src/components/Header.tsx
  ✅ src/components/Footer.tsx
  ✅ src/pages/index.tsx
  ✅ src/styles/globals.css
  ... (15 files total)

✨ Extracted 15 files!

📦 Installing dependencies...
✅ Dependencies installed!

================================================================================
                        ✅ PROJECT READY TO LAUNCH!
================================================================================

📁 Project location: output/project_20251018_233128

🚀 Would you like to launch the development server now? (y/n): y

🌐 Launching development server at http://localhost:3000
   Press Ctrl+C to stop

> next dev
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
event - compiled client and server successfully
```

## Future Enhancements

Potential improvements:
- [ ] Auto-open browser to localhost:3000
- [ ] Support for Python/Django projects
- [ ] Support for other frameworks (Vue, Svelte, etc.)
- [ ] Optional Docker containerization
- [ ] Deploy to staging option (Vercel, Netlify)

## Testing

To test the feature manually:

```bash
# Generate a web project
cd /Users/bledden/Documents/codeswarm
./codeswarm generate "Create a simple landing page with Next.js"

# Wait for generation to complete
# You'll automatically see the extraction + prompt!
```

## Standalone Script

A standalone extraction script is also available:

```bash
python3 extract_and_launch.py output/code_TIMESTAMP
```

This can be used to extract older generated code that didn't have auto-extraction.

---

**Status**: ✅ Implemented and integrated into `codeswarm_cli.py`
**Version**: Added Oct 18, 2025
**Author**: CodeSwarm Team
