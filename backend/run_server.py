import os
import subprocess
import sys
from pathlib import Path

def process_datasets():
    """Process all datasets before starting the server"""
    print("Processing datasets...")
    
    # Get the current directory
    current_dir = Path.cwd()
    
    # Create processed_data directory if it doesn't exist
    processed_data_dir = current_dir / "processed_data"
    processed_data_dir.mkdir(exist_ok=True)
    
    # Run the process_datasets.py script
    try:
        subprocess.run([sys.executable, "process_datasets.py"], check=True)
        print("Datasets processed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error processing datasets: {e}")
        return False

def start_server():
    """Start the FastAPI server using uvicorn"""
    print("Starting backend server...")
    
    # Change to the prods_fastapi directory
    os.chdir("prods_fastapi")
    
    # Start the server
    try:
        # Get port from environment variable (defaults to 10000 for Render compatibility)
        port = os.environ.get('PORT', '10000')
        
        # Use uvicorn to run the FastAPI app
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", "--host", "0.0.0.0", "--port", port, 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")

def main():
    """Main function to process datasets and start the server"""
    # Process datasets first
    if process_datasets():
        # Start the server
        start_server()
    else:
        print("Failed to process datasets. Server not started.")

if __name__ == "__main__":
    main() 