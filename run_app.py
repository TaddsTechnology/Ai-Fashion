import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
import signal

# Global variables to track processes
backend_process = None
frontend_process = None

def setup_environment():
    """Set up the environment by creating necessary directories and checking for required packages"""
    print("Setting up environment...")
    
    # Create processed_data directory if it doesn't exist
    processed_data_dir = Path("processed_data")
    processed_data_dir.mkdir(exist_ok=True)
    
    # Create backend data directory if it doesn't exist
    backend_data_dir = Path("backend/prods_fastapi/data")
    backend_data_dir.mkdir(exist_ok=True, parents=True)
    
    # Check for required packages
    required_packages = ["pandas", "fastapi", "uvicorn"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    # Install missing packages if any
    if missing_packages:
        print(f"Installing missing packages: {', '.join(missing_packages)}")
        requirements_file = Path("backend/requirements.txt")
        
        if requirements_file.exists():
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], check=True)
        else:
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages, check=True)

def process_datasets():
    """Process all datasets before starting the server"""
    print("Processing datasets...")
    
    # Change to backend directory
    os.chdir("backend")
    
    # Run the process_datasets.py script
    try:
        subprocess.run([sys.executable, "process_datasets.py"], check=True)
        print("Datasets processed successfully!")
        
        # Change back to the root directory
        os.chdir("..")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error processing datasets: {e}")
        
        # Change back to the root directory
        os.chdir("..")
        return False

def start_backend_server():
    """Start the FastAPI backend server"""
    global backend_process
    
    print("Starting backend server...")
    
    # Change to the backend/prods_fastapi directory
    os.chdir("backend/prods_fastapi")
    
    try:
        # Start the server using uvicorn
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for the server to start
        time.sleep(2)
        
        # Check if the server started successfully
        if backend_process.poll() is None:
            print("Backend server started successfully!")
            print("API is available at http://localhost:8000")
            
            # Change back to the root directory
            os.chdir("../..")
            return True
        else:
            stdout, stderr = backend_process.communicate()
            print(f"Server failed to start: {stderr}")
            
            # Change back to the root directory
            os.chdir("../..")
            return False
    except Exception as e:
        print(f"Error starting backend server: {e}")
        
        # Change back to the root directory
        os.chdir("../..")
        return False

def start_frontend_server():
    """Start the frontend development server"""
    global frontend_process
    
    print("Starting frontend server...")
    
    # Change to the frontend directory
    os.chdir("frontend")
    
    try:
        # Start the frontend server using npm
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for the server to start
        time.sleep(5)
        
        # Check if the server started successfully
        if frontend_process.poll() is None:
            print("Frontend server started successfully!")
            print("Frontend is available at http://localhost:5173")
            
            # Change back to the root directory
            os.chdir("..")
            return True
        else:
            stdout, stderr = frontend_process.communicate()
            print(f"Frontend server failed to start: {stderr}")
            
            # Change back to the root directory
            os.chdir("..")
            return False
    except Exception as e:
        print(f"Error starting frontend server: {e}")
        
        # Change back to the root directory
        os.chdir("..")
        return False

def open_browser():
    """Open the default web browser to the frontend URL"""
    try:
        print("Opening browser...")
        webbrowser.open("http://localhost:5173")
        return True
    except Exception as e:
        print(f"Error opening browser: {e}")
        return False

def stop_servers():
    """Stop the backend and frontend servers"""
    global backend_process, frontend_process
    
    print("Stopping servers...")
    
    # Stop the backend server
    if backend_process is not None:
        print("Stopping backend server...")
        backend_process.terminate()
        backend_process.wait()
        print("Backend server stopped.")
    
    # Stop the frontend server
    if frontend_process is not None:
        print("Stopping frontend server...")
        frontend_process.terminate()
        frontend_process.wait()
        print("Frontend server stopped.")

def signal_handler(sig, frame):
    """Handle Ctrl+C signal to stop servers gracefully"""
    print("\nReceived interrupt signal. Shutting down...")
    stop_servers()
    sys.exit(0)

def main():
    """Main function to run the HueMatch application"""
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Starting HueMatch application...")
    
    # Setup environment
    setup_environment()
    
    # Process datasets
    if not process_datasets():
        print("Failed to process datasets. Exiting.")
        return
    
    # Start backend server
    if not start_backend_server():
        print("Failed to start backend server. Exiting.")
        return
    
    # Ask user if they want to start the frontend
    start_frontend = input("Do you want to start the frontend server? (y/n): ").lower().strip() == 'y'
    
    if start_frontend:
        # Start frontend server
        if not start_frontend_server():
            print("Failed to start frontend server.")
            stop_servers()
            return
        
        # Ask user if they want to open the browser
        open_browser_prompt = input("Do you want to open the frontend in your browser? (y/n): ").lower().strip() == 'y'
        
        if open_browser_prompt:
            open_browser()
    
    print("\nHueMatch application is running!")
    print("Press Ctrl+C to stop the servers.")
    
    try:
        # Keep the script running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt. Shutting down...")
    finally:
        stop_servers()

if __name__ == "__main__":
    main() 