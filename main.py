import os
import sys

def main():
    print("=" * 50)
    print("Image Steganography - GUI")
    print("=" * 50)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(current_dir, "src")
    
    if not os.path.exists(src_path):
        print(f"❌ BŁĄD: Brak folderu 'src'")
        input("Naciśnij Enter...")
        return
    
    # Dodaj potrzebne ścieżki
    sys.path.insert(0, src_path)
    sys.path.insert(0, os.path.join(src_path, "imagesteganography"))
    
    print(f"📁 Projekt: {current_dir}")
    print(f"✅ Ścieżki skonfigurowane")
    
    try:
        # Partner ma GUI w: imagesteganography.UX.gui
        from imagesteganography.UX.gui import main as gui_main
        print("✅ GUI zaimportowany")
        print("-" * 50)
        
        gui_main()
        
    except ImportError as e:
        print(f"❌ BŁĄD: {e}")
        
        # Diagnostyka
        print("\n🔍 Struktura src/:")
        for root, dirs, files in os.walk(src_path):
            level = root.replace(src_path, "").count(os.sep)
            indent = "  " * level
            basename = os.path.basename(root) or "src"
            
            # Pokaż tylko ważne foldery
            if "imagesteganography" in root or root == src_path:
                print(f"{indent}{basename}/")
                
                # Pokaż pliki .py
                py_files = [f for f in files if f.endswith('.py')]
                for f in py_files[:3]:  # max 3
                    print(f"{indent}  📄 {f}")
                    
        input("\nNaciśnij Enter...")

if __name__ == "__main__":
    main()