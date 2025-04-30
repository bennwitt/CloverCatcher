# Last modified: 2024-12-08 10:24:35
# Version: 0.0.2
import os
import sys

def add_subdirectories_to_sys_path(root_dir):
    """
    Recursively add all subdirectories of the given root directory to sys.path.
    
    Args:
        root_dir (str): The root directory to include and scan for subdirectories.
    """
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if dirpath not in sys.path:
            sys.path.append(dirpath)

# Get the absolute path of the current script
current_file_path = os.path.abspath(__file__)

# Derive the application root directory (e.g., /ai/aiApps/APPLICATIONNAME)
app_root = os.path.abspath(os.path.join(os.path.dirname(current_file_path), "."))

# Add the application root and all its subdirectories to sys.path
add_subdirectories_to_sys_path(app_root)

# Optional: Verify all added paths for debugging
print("Updated sys.path with subdirectories:")
for path in sys.path:
    print(f" - {path}")
