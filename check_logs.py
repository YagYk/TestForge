import os
import sys

def find_log_file():
    log_dirs = ["logs", "."]
    log_files = ["server.log", "app.log"]
    
    for directory in log_dirs:
        for filename in log_files:
            path = os.path.join(directory, filename)
            if os.path.exists(path):
                return path
    
    return None

def print_recent_log_entries(log_file, num_lines=50):
    """Print the last num_lines lines from the log file"""
    if not log_file or not os.path.exists(log_file):
        print(f"Log file not found: {log_file}")
        return
    
    print(f"Reading last {num_lines} lines from {log_file}")
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if not lines:
            print("Log file is empty")
            return
            
        # Get the last num_lines or all if fewer
        recent_lines = lines[-num_lines:] if len(lines) > num_lines else lines
        
        print("\n".join(recent_lines))
    except Exception as e:
        print(f"Error reading log file: {e}")

if __name__ == "__main__":
    # Check if a log file is specified as command line argument
    if len(sys.argv) > 1:
        log_file = sys.argv[1]
    else:
        log_file = find_log_file()
        
    if not log_file:
        print("No log file found. Try specifying the path as an argument.")
        sys.exit(1)
        
    # Check if number of lines is specified
    num_lines = 50
    if len(sys.argv) > 2:
        try:
            num_lines = int(sys.argv[2])
        except ValueError:
            pass
            
    print_recent_log_entries(log_file, num_lines) 