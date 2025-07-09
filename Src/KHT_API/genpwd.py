# top level module to create encrypted password
import sys   
from testing_cache import my_hash

# Accessing command-line arguments   
arguments = sys.argv  # List of arguments   
script_name = sys.argv[0]  # Name of the script   

# Checking if an argument is provided before accessing it   
if len(sys.argv) > 1:   
  plain_pwd = sys.argv[1]  # First argument 
  print(my_hash(plain_pwd))  
else:   
  print("Usage: genpwd [plain-text]")
