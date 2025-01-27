import os
import shutil
import sys

# Configuration
SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))  # Current directory with git repo
ABAQUS_PLUGIN_DIR = r"C:\SIMULIA\Abaqus\6.14-1\code\python2.7\lib\abaqus_plugins\homtools-perso"

# Files to sync
FILES_TO_SYNC = [
    "envelope_Enrichment_homtoolsDB.py",
    "envelope_Enrichment_homtools_plugin.py",
    "periodicBoundary_env.py"
]

def sync_plugin():
    print(f"Syncing files to {ABAQUS_PLUGIN_DIR}")
    
    # Create plugin directory if it doesn't exist
    if not os.path.exists(ABAQUS_PLUGIN_DIR):
        os.makedirs(ABAQUS_PLUGIN_DIR)
        print(f"Created directory: {ABAQUS_PLUGIN_DIR}")

    # Copy each file
    for file in FILES_TO_SYNC:
        source = os.path.join(SOURCE_DIR, "abaqus_plugin", file)
        destination = os.path.join(ABAQUS_PLUGIN_DIR, file)
        
        try:
            shutil.copy2(source, destination)
            print(f"Successfully copied: {file}")
        except Exception as e:
            print(f"Error copying {file}: {str(e)}")

if __name__ == "__main__":
    # Check if running with admin privileges
    try:
        sync_plugin()
        print("\nSync completed successfully!")
        input("Press Enter to exit...")
    except PermissionError:
        print("Error: Administrative privileges required!")
        print("Please run this script as administrator.")
        input("Press Enter to exit...")