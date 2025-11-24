"""
Setup script to automatically start AI OMR processing on Windows startup.
"""

import os
import sys
import winreg
from pathlib import Path

def add_to_startup():
    """Add the OMR scanner to Windows startup."""
    try:
        # Get the path to the startup script
        script_path = Path(__file__).parent / "start_ai_auto.bat"
        
        if not script_path.exists():
            print(f"❌ Startup script not found: {script_path}")
            return False
        
        # Open the registry key for current user startup programs
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        # Set the registry value
        winreg.SetValueEx(
            key,
            "OMRScannerAI",
            0,
            winreg.REG_SZ,
            str(script_path)
        )
        
        winreg.CloseKey(key)
        
        print("✅ OMR Scanner AI added to Windows startup")
        print(f"   Script path: {script_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to add to startup: {e}")
        return False

def remove_from_startup():
    """Remove the OMR scanner from Windows startup."""
    try:
        # Open the registry key
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        # Delete the registry value
        winreg.DeleteValue(key, "OMRScannerAI")
        winreg.CloseKey(key)
        
        print("✅ OMR Scanner AI removed from Windows startup")
        return True
        
    except FileNotFoundError:
        print("ℹ️  OMR Scanner AI was not in startup")
        return True
    except Exception as e:
        print(f"❌ Failed to remove from startup: {e}")
        return False

def main():
    """Main function."""
    print("🔧 OMR Scanner - Windows Startup Setup")
    print("=" * 40)
    
    print("\nOptions:")
    print("1. Add to startup (automatically start AI OMR on login)")
    print("2. Remove from startup")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "1":
        if add_to_startup():
            print("\n🎉 Successfully added to startup!")
            print("The AI OMR processing will now start automatically when you log in to Windows.")
        else:
            print("\n❌ Failed to add to startup")
    elif choice == "2":
        if remove_from_startup():
            print("\n✅ Successfully removed from startup!")
            print("The AI OMR processing will no longer start automatically.")
        else:
            print("\n❌ Failed to remove from startup")
    else:
        print("\n❌ Invalid choice")

if __name__ == "__main__":
    main()