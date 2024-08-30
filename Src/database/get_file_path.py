import os

'''
Function to get the file path
Arguments
    filename    - name of the file
Returns the file path
'''
def find_file_insensitive(file_name, directory='.'):
    # Normalize the target file name to lowercase
    target_file_name = file_name.lower()
    
    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        for name in files:
            # Check if the current file matches the target file name (case-insensitive and underscore-insensitive) 
            file_name = name.lower().replace(' ', '_')
            if file_name == target_file_name: 
                return os.path.join(root, name)
    
    return None # If the file is not found, return None

def get_file_path(file_name, directory='.'):
    # Find the file case-insensitively
    file_path = find_file_insensitive(file_name, directory)
    print(file_path)
    if file_path:
        return file_path
    else:
        raise FileNotFoundError(f"File '{file_name}' not found in directory '{directory}'.")