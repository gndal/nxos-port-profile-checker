from nornir_netmiko.tasks import netmiko_send_command
import logging
import re

logger = logging.getLogger(__name__)

def check_port_profiles(task):
    """
    Check all port profiles on NXOS devices (both applied and unused)
    
    Returns:
        dict: Dictionary containing all port profile information
    """
    try:
        # Get port profile usage information
        usage_result = task.run(
            task=netmiko_send_command,
            command_string="show port-profile usage"
        )
        
        # Get all port profiles (including unused ones)
        all_profiles_result = task.run(
            task=netmiko_send_command,
            command_string="show port-profile"
        )
        
        # Log to file only, not console
        logger.debug(f"Port profile usage output from {task.host}:\n{usage_result.result}")
        logger.debug(f"All port profiles output from {task.host}:\n{all_profiles_result.result}")
        
        # Parse both outputs
        applied_profiles = parse_port_profile_usage_output(usage_result.result)
        all_profiles = parse_all_port_profiles_output(all_profiles_result.result)
        
        # Combine the results
        combined_profiles = combine_profile_data(applied_profiles, all_profiles)
        
        return combined_profiles
        
    except Exception as e:
        logger.error(f"Error checking port profiles on {task.host}: {str(e)}")
        raise

def parse_port_profile_usage_output(output):
    """Parse the 'show port-profile usage' command output"""
    applied_profiles = {}
    
    if not output:
        return applied_profiles
    
    lines = output.split('\n')
    current_profile = None
    
    for line in lines:
        if line.strip().startswith('port-profile'):
            current_profile = line.strip().replace('port-profile', '').strip()
            
        elif line.startswith(' ') and 'Ethernet' in line:
            interface = line.strip()
            if current_profile and interface:
                applied_profiles[interface] = {
                    'profile': current_profile,
                    'vlan': 'N/A',
                    'description': f'Applied via port-profile {current_profile}',
                    'status': 'Applied'
                }
    
    return applied_profiles

def parse_all_port_profiles_output(output):
    """Parse the 'show port-profile' command output to get all profiles"""
    all_profiles = {}
    
    if not output:
        return all_profiles
    
    lines = output.split('\n')
    current_profile = None
    profile_config = []
    
    for line in lines:
        if line.strip().startswith('port-profile'):
            # Save previous profile if exists
            if current_profile:
                all_profiles[current_profile] = {
                    'profile': current_profile,
                    'config': '\n'.join(profile_config),
                    'status': 'Defined'
                }
            
            # Start new profile
            current_profile = line.strip().replace('port-profile', '').strip()
            profile_config = []
            
        elif current_profile and line.strip():
            profile_config.append(line.strip())
    
    # Save last profile
    if current_profile:
        all_profiles[current_profile] = {
            'profile': current_profile,
            'config': '\n'.join(profile_config),
            'status': 'Defined'
        }
    
    return all_profiles

def combine_profile_data(applied_profiles, all_profiles):
    """Combine applied and all profiles data"""
    combined = {}
    
    # Add all applied profiles (interface-based)
    for interface, profile_data in applied_profiles.items():
        combined[interface] = profile_data
    
    # Add unused profiles (profile-based)
    for profile_name, profile_data in all_profiles.items():
        # Check if this profile is applied to any interface
        is_applied = any(data['profile'] == profile_name for data in applied_profiles.values())
        
        if not is_applied:
            combined[f"UNUSED_{profile_name}"] = {
                'profile': profile_name,
                'vlan': 'N/A',
                'description': f'Port-profile {profile_name} defined but not applied',
                'status': 'Unused'
            }
    
    return combined

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