import os

ALLOWED_PATHS = []

def is_path_allowed(path):
    if not ALLOWED_PATHS:
        return True
    for allowed_path in ALLOWED_PATHS:
        if os.path.abspath(path).startswith(os.path.abspath(allowed_path)):
            return True
    return False

def file_read_tool(file_path):
    if not is_path_allowed(file_path):
        return {"error": f"Access denied: Reading file '{file_path}' "
                         "is not allowed."}
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        return {"error": f"Error reading file '{file_path}': {e}"}


def file_write_tool(file_path, content):
    if not is_path_allowed(file_path):
        return {"error": f"Access denied: Writing to file '{file_path}' "
                         "is not allowed."}
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return {"success": f"File '{file_path}' written successfully."}
    except Exception as e:
        return {"error": f"Error writing to file '{file_path}': {e}"}

def directory_listing_tool(dir_path):
    if not is_path_allowed(dir_path):
        return {"error": f"Access denied: Listing directory '{dir_path}' "
                         "is not allowed."}
    try:
        return os.listdir(dir_path)
    except Exception as e:
        return {"error": f"Error listing directory '{dir_path}': {e}"}
