#!/usr/bin/env python3
"""
Service Orchestrator - Start all AI Fashion microservices
"""

import subprocess
import time
import sys
import os
from pathlib import Path
import requests

# Service configurations
SERVICES = [
    {
        "name": "Detection Service",
        "port": 8001,
        "file": "detection_service.py",
        "description": "AI skin tone analysis with season classification"
    },
    {
        "name": "Palette Service", 
        "port": 8002,
        "file": "palette_service.py",
        "description": "Season-based color palette retrieval"
    },
    {
        "name": "Recommendation Service",
        "port": 8003,
        "file": "recommendation_service.py", 
        "description": "Smart product recommendations with scoring"
    }
]

def check_service_health(port: int, timeout: int = 30) -> bool:
    """Check if service is running and healthy"""
    url = f"http://localhost:{port}/health"
    
    for attempt in range(timeout):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(1)
    
    return False

def start_service(service_config: dict):
    """Start a single service"""
    service_name = service_config["name"]
    port = service_config["port"]
    file_path = service_config["file"]
    
    print(f"\n🚀 Starting {service_name} on port {port}...")
    print(f"   Description: {service_config['description']}")
    
    # Start service as subprocess
    try:
        process = subprocess.Popen([
            sys.executable, file_path
        ], cwd=Path(__file__).parent)
        
        # Wait for service to be healthy
        print(f"   Waiting for {service_name} to start...")
        if check_service_health(port):
            print(f"   ✅ {service_name} is running and healthy!")
            return process
        else:
            print(f"   ❌ {service_name} failed to start or become healthy")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"   ❌ Failed to start {service_name}: {e}")
        return None

def main():
    """Main orchestrator function"""
    print("🎨 AI Fashion Microservices Orchestrator")
    print("=" * 50)
    
    # Check if we're in the right directory
    services_dir = Path(__file__).parent
    if not services_dir.exists():
        print("❌ Services directory not found!")
        return False
    
    processes = []
    failed_services = []
    
    # Start all services
    for service in SERVICES:
        service_file = services_dir / service["file"]
        
        if not service_file.exists():
            print(f"❌ Service file not found: {service_file}")
            failed_services.append(service["name"])
            continue
            
        process = start_service(service)
        if process:
            processes.append((service, process))
        else:
            failed_services.append(service["name"])
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 Service Status Summary:")
    print("-" * 30)
    
    for service, process in processes:
        print(f"✅ {service['name']} - Port {service['port']} - PID {process.pid}")
    
    if failed_services:
        print(f"❌ Failed services: {', '.join(failed_services)}")
    
    if processes:
        print(f"\n🌐 API Endpoints:")
        print("-" * 20)
        for service, _ in processes:
            port = service['port']
            print(f"   {service['name']}: http://localhost:{port}")
            print(f"   Health Check: http://localhost:{port}/health")
            print(f"   API Docs: http://localhost:{port}/docs")
            print()
        
        print("🔄 Service Communication Flow:")
        print("   Frontend → Detection Service → Palette Service → Recommendation Service → Frontend")
        print()
        print("📊 Database Integration:")
        print("   • mst_master_palette - Color palettes by Monk tone")
        print("   • perfect_unified_outfits - 513 outfit products")
        print("   • perfect_unified_makeup - 2571 makeup products")
        print("   • skin_tone_mappings - Monk to seasonal type mapping")
        print()
        print("⏳ Services are running. Press Ctrl+C to stop all services.")
        
        try:
            # Keep services running
            while True:
                time.sleep(1)
                
                # Check if any process has died
                for i, (service, process) in enumerate(processes):
                    if process.poll() is not None:
                        print(f"\n⚠️  {service['name']} has stopped unexpectedly!")
                        processes.pop(i)
                        break
                
                if not processes:
                    print("\n❌ All services have stopped. Exiting...")
                    break
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping all services...")
            for service, process in processes:
                print(f"   Stopping {service['name']}...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"   Force killing {service['name']}...")
                    process.kill()
            
            print("✅ All services stopped.")
            
    else:
        print("❌ No services started successfully!")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
