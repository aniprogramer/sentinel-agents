import docker
import hashlib
import json
import os

CACHE_FILE = "execution_cache.json"
client = docker.from_env()

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        execution_cache = json.load(f)
else:
    execution_cache = {}

def get_script_hash(script_content, target_file_path):
    """Hashes the exploit AND the current state of the target code."""
    with open(target_file_path, "r") as f:
        target_code = f.read()
    # Combine them so if either changes, the cache invalidates
    combined_state = script_content + target_code
    return hashlib.sha256(combined_state.encode('utf-8')).hexdigest()    

def save_cache():
    with open(CACHE_FILE, "w") as f:
        json.dump(execution_cache, f, indent=4)

def run_exploit_in_sandbox(script_content, target_file_path):
    # Pass BOTH arguments to the hash function now
    script_hash = get_script_hash(script_content, target_file_path)
    
    if script_hash in execution_cache:
        print("[⚡ CACHE HIT] Bypassing Docker. Returning previous execution logs.")
        return execution_cache[script_hash]

    print("[🐳 DOCKER] New exploit detected. Spinning up sandbox...")
    
    exploit_filename = "temp_exploit.py"
    temp_dir = os.path.abspath("temp")
    temp_path = os.path.join(temp_dir, exploit_filename)
    
    os.makedirs(temp_dir, exist_ok=True)
    
    with open(temp_path, "w") as f:
        f.write(script_content)

    mount_dir = os.path.abspath(os.path.join("..", "target_code"))
    
    try:
        container = client.containers.run(
            image="sentinel_sandbox:latest",
            # MOVED TIMEOUT HERE: using Alpine's native timeout command
            command=f"timeout 15 python /app/{exploit_filename}",
            volumes={
                mount_dir: {'bind': '/target', 'mode': 'ro'},
                temp_dir: {'bind': '/app', 'mode': 'ro'}
            },
            network_disabled=True, 
            mem_limit="128m",      
            detach=False,
            remove=True
            # Removed the invalid timeout=15 argument from here!
        )
        output = container.decode('utf-8')
        success = True
        
    except docker.errors.ContainerError as e:
        # If it times out, Alpine kills it and throws an error here, which we catch perfectly!
        output = e.stderr.decode('utf-8') if e.stderr else str(e)
        success = False
    except Exception as e:
        output = f"Execution failed: {str(e)}"
        success = False
    result = {
        "success": success,
        "logs": output
    }
    execution_cache[script_hash] = result
    save_cache()
    
    if os.path.exists(temp_path):
        os.remove(temp_path)

    return result

# --- SANITY CHECK TEST ---
if __name__ == "__main__":
    test_script = """
import os
print('Exploit running inside Docker!')
print('Target directory contents:', os.listdir('/target'))
    """
    
    target_dir = os.path.abspath(os.path.join("..", "target_code"))
    os.makedirs(target_dir, exist_ok=True)
    with open(os.path.join(target_dir, "sample_vuln.py"), "w") as f:
        f.write("print('Vulnerable Code')")

    result = run_exploit_in_sandbox(test_script, os.path.join(target_dir, "sample_vuln.py"))
    print("\n--- SANDBOX RESULT ---")
    print(f"Success: {result['success']}")
    print(f"Logs:\n{result['logs']}")