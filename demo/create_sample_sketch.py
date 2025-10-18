"""
Create a sample sketch image for demo

Since we can't hand-draw, this creates a text-based wireframe
that can be converted to an image, or provides instructions for creating one.
"""

from pathlib import Path

def create_text_wireframe():
    """Create ASCII art wireframe of a landing page"""

    wireframe = """

                                                                
  LOGO                    Home   Features   Pricing   Contact  
                                                                

                                                                
                    Welcome to Our SaaS Product                 
                                                                
          The best solution for your business needs             
                                                                
              [Get Started]    [Learn More]                     
                                                                
                     [Hero Image]                               
                                                                

                                                                
                          Features                              
                                                                
        
                                                        
     [Icon 1]          [Icon 2]          [Icon 3]       
                                                        
     Feature 1         Feature 2         Feature 3      
     Description       Description       Description    
                                                        
        
                                                                

                                                                
                          Pricing                               
                                                                
                          
    BASIC            PRO           ENTERPRISE            
                                                         
    $9/mo           $29/mo          $99/mo               
                                                         
   [Button]        [Button]        [Button]              
                          
                                                                

                                                                
                      Contact Us                                
                                                                
              Name:     [________________]                      
              Email:    [________________]                      
              Message:  [________________]                      
                        [________________]                      
                                                                
                        [Submit]                                
                                                                

                                                                
  © 2025 SaaS Product | Privacy | Terms | Social Links          
                                                                

"""

    return wireframe


def save_wireframe():
    """Save wireframe to file"""
    demo_dir = Path("demo")
    demo_dir.mkdir(exist_ok=True)

    wireframe = create_text_wireframe()

    # Save as text file
    wireframe_file = demo_dir / "wireframe.txt"
    with open(wireframe_file, "w") as f:
        f.write(wireframe)

    print(f" Wireframe saved to: {wireframe_file}")
    print("\n" + wireframe)

    # Create instructions for creating actual image
    instructions_file = demo_dir / "SKETCH_INSTRUCTIONS.md"
    instructions = """# How to Create Demo Sketch Image

## Option 1: Use This Text Description (NO IMAGE NEEDED)

You can run the demo WITHOUT an image by providing this detailed description:

```
Create a modern SaaS landing page with:

1. Header:
   - Logo on left
   - Navigation: Home, Features, Pricing, Contact

2. Hero Section:
   - Large headline: "Welcome to Our SaaS Product"
   - Subheading: "The best solution for your business needs"
   - Two CTAs: "Get Started" (primary) and "Learn More" (secondary)
   - Hero image placeholder

3. Features Section:
   - Title: "Features"
   - 3 feature cards in a row:
     - Each with icon, title, and description
     - Cards have borders and padding

4. Pricing Section:
   - Title: "Pricing"
   - 3 pricing tiers:
     - Basic: $9/mo
     - Pro: $29/mo (highlighted)
     - Enterprise: $99/mo
   - Each with a "Choose Plan" button

5. Contact Form:
   - Title: "Contact Us"
   - Fields: Name, Email, Message
   - Submit button

6. Footer:
   - Copyright notice
   - Links: Privacy, Terms
   - Social media icons

Color scheme: Blue primary, white background, dark text
```

Run demo with: `python3 demo.py` (no image needed)

---

## Option 2: Create a Quick Digital Sketch

### Using Excalidraw (Recommended - Free)
1. Go to https://excalidraw.com
2. Draw boxes for each section above
3. Add labels and text
4. Export as PNG
5. Save as `demo/sketch.jpg`

### Using Figma (If you have it)
1. Create new file
2. Add rectangles for sections
3. Add text labels
4. Export as PNG
5. Save as `demo/sketch.jpg`

### Using Photos (Hand-drawn)
1. Draw the wireframe on paper following the layout above
2. Take a clear photo with your phone
3. Make sure it's well-lit and in focus
4. Transfer to computer
5. Save as `demo/sketch.jpg`

---

## Option 3: Use Placeholder Image

We've included a text wireframe in `demo/wireframe.txt` that describes the layout.
The Vision agent can work with text descriptions if no image is available.

---

## Testing Without Image

The demo works perfectly WITHOUT an image:

```bash
python3 demo.py
```

The system will skip vision analysis and proceed with text-only mode.
This is actually fine for the hackathon demo!
"""

    with open(instructions_file, "w") as f:
        f.write(instructions)

    print(f"\n Instructions saved to: {instructions_file}")


if __name__ == "__main__":
    print(" Creating sample sketch materials for CodeSwarm demo\n")
    save_wireframe()
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. Review demo/wireframe.txt")
    print("2. EITHER:")
    print("   a) Create image following demo/SKETCH_INSTRUCTIONS.md")
    print("   b) Run demo WITHOUT image: python3 demo.py")
    print("\nThe demo works great without an image too!")
    print("="*70)
