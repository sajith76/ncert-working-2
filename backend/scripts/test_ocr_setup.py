"""
Test OCR Setup - Verify Tesseract and Poppler are installed correctly
"""

import sys

print("=" * 70)
print("  🔍 Testing OCR Setup")
print("=" * 70)

# Test 1: Check if pytesseract is installed
print("\n1️⃣  Testing pytesseract import...")
try:
    import pytesseract
    print("   ✓ pytesseract imported successfully")
except ImportError as e:
    print(f"   ✗ Failed to import pytesseract: {e}")
    sys.exit(1)

# Test 2: Check if Tesseract executable is accessible
print("\n2️⃣  Testing Tesseract executable...")
try:
    version = pytesseract.get_tesseract_version()
    print(f"   ✓ Tesseract version: {version}")
except Exception as e:
    print(f"   ✗ Tesseract not found: {e}")
    print("\n   💡 Install Tesseract from:")
    print("      https://github.com/UB-Mannheim/tesseract/wiki")
    print("   💡 Or add to PATH: C:\\Program Files\\Tesseract-OCR")
    sys.exit(1)

# Test 3: Check if pdf2image is installed
print("\n3️⃣  Testing pdf2image import...")
try:
    from pdf2image import convert_from_path
    print("   ✓ pdf2image imported successfully")
except ImportError as e:
    print(f"   ✗ Failed to import pdf2image: {e}")
    sys.exit(1)

# Test 4: Check if Poppler is accessible
print("\n4️⃣  Testing Poppler (pdftoppm)...")
try:
    from pdf2image.exceptions import PDFInfoNotInstalledError
    import subprocess
    result = subprocess.run(['pdftoppm', '-v'], capture_output=True, text=True)
    print(f"   ✓ Poppler found: {result.stderr.split()[2] if result.stderr else 'installed'}")
except FileNotFoundError:
    print("   ✗ Poppler not found in PATH")
    print("\n   💡 Download Poppler from:")
    print("      https://github.com/oschwartz10612/poppler-windows/releases")
    print("   💡 Extract to C:\\poppler and add to PATH: C:\\poppler\\Library\\bin")
    sys.exit(1)
except Exception as e:
    print(f"   ⚠️  Warning: {e}")

# Test 5: Check other dependencies
print("\n5️⃣  Testing other dependencies...")
try:
    import PyPDF2
    print("   ✓ PyPDF2 imported")
except ImportError:
    print("   ✗ PyPDF2 not installed")

try:
    from PIL import Image
    print("   ✓ Pillow (PIL) imported")
except ImportError:
    print("   ✗ Pillow not installed")

try:
    import cv2
    print("   ✓ OpenCV imported")
except ImportError:
    print("   ✗ OpenCV not installed")

try:
    import numpy as np
    print("   ✓ NumPy imported")
except ImportError:
    print("   ✗ NumPy not installed")

# Test 6: Simple OCR test
print("\n6️⃣  Testing OCR on sample image...")
try:
    from PIL import Image
    import numpy as np
    
    # Create a simple test image with text
    img = Image.new('RGB', (200, 50), color='white')
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    try:
        # Try to use a font, fallback to default if not available
        font = ImageFont.load_default()
        draw.text((10, 10), "Hello OCR", fill='black', font=font)
    except:
        draw.text((10, 10), "Hello OCR", fill='black')
    
    # Run OCR
    text = pytesseract.image_to_string(img)
    
    if "Hello" in text or "OCR" in text:
        print(f"   ✓ OCR test passed! Detected: '{text.strip()}'")
    else:
        print(f"   ⚠️  OCR test unclear. Detected: '{text.strip()}'")
        print("      (This might still work fine with real PDFs)")
    
except Exception as e:
    print(f"   ✗ OCR test failed: {e}")

print("\n" + "=" * 70)
print("  ✅ Setup verification complete!")
print("=" * 70)
print("\n💡 Next step: Run the upload script")
print("   python scripts/upload_pdfs_to_pinecone.py")
print("=" * 70)
