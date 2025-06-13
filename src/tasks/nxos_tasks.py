from nornir_netmiko.tasks import netmiko_send_command
from nornir import InitNornir
import logging
import pandas as pd

logger = logging.getLogger(__name__)

def check_port_profiles(task):
    """
    Check active port profiles on NXOS devices
    
    Returns:
        dict: Dictionary containing port profile information per interface
    """
    try:
        # Get port profile information
        result = task.run(
            task=netmiko_send_command,
            command_string="show port-profile usage"
        )
        
        # Parse the output (simplified parsing - adjust based on actual output format)
        port_profiles = parse_port_profile_output(result.result)
        
        return port_profiles
        
    except Exception as e:
        logger.error(f"Error checking port profiles on {task.host}: {str(e)}")
        raise

def parse_port_profile_output(output):
    """
    Parse the port profile command output
    
    Args:
        output (str): Raw command output
        
    Returns:
        dict: Parsed port profile data
    """
    # This is a simplified parser - you'll need to adjust based on actual NXOS output
    profiles = {}
    
    lines = output.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('-') and 'Interface' not in line:
            # Basic parsing - adjust based on your actual command output format
            parts = line.split()
            if len(parts) >= 2:
                interface = parts[0]
                profile = parts[1] if len(parts) > 1 else 'N/A'
                
                profiles[interface] = {
                    'profile': profile,
                    'vlan': 'N/A',  # Add VLAN parsing if available
                    'description': 'N/A'  # Add description parsing if available
                }
    
    return profiles

def summarize_port_profiles(nr):
    summary = []
    for host in nr.inventory.hosts.values():
        summary.append({
            "Host": host.name,
            "Port Profiles": host.get("port_profiles", "N/A")
        })
    return summary

def main():
    nr = InitNornir(config_file="src/config/nornir_config.yaml")
    results = nr.run(task=check_port_profiles)
    print_result(results)

    summary = summarize_port_profiles(nr)
    df = pd.DataFrame(summary)
    df.to_csv("output/port_profiles_summary.csv", index=False)

if __name__ == "__main__":
    main()