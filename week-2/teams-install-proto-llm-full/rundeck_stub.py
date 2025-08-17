import time
import random

def simulate_installation(request):
    """
    Simulate the installation process for an application request.
    
    Args:
        request: Request object containing application details
    """
    print(f"Starting installation simulation for request {request.request_id}")
    print(f"Application: {request.application}")
    print(f"Version: {request.version or 'Latest'}")
    
    # Simulate installation process with some delay
    installation_steps = [
        "Preparing installation environment",
        "Downloading application packages",
        "Verifying package integrity",
        "Installing application components",
        "Configuring application settings",
        "Running post-installation scripts",
        "Performing health checks"
    ]
    
    for step in installation_steps:
        # Simulate time taken for each step (1-3 seconds)
        delay = random.uniform(1, 3)
        print(f"  - {step}...")
        time.sleep(delay)
    
    print(f"Installation completed successfully for request {request.request_id}")