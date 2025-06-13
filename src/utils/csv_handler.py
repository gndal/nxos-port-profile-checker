import pandas as pd
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def write_to_csv(summary_data, output_dir="output", detailed=False):
    """
    Write port profile summary to CSV file
    
    Args:
        summary_data (list): List of dictionaries containing host results
        output_dir (str): Output directory path
        detailed (bool): If True, include all interface details
    
    Returns:
        str: Path to the generated CSV file
    """
    if detailed:
        return write_detailed_csv(summary_data, output_dir)
    else:
        return write_summary_csv(summary_data, output_dir)

def write_summary_csv(summary_data, output_dir):
    """Write profile-focused summary CSV"""
    try:
        # Ensure output directory exists
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"port_profiles_summary_{timestamp}.csv"
        csv_filepath = output_path / csv_filename
        
        # Create profile-focused summary
        csv_data = []
        
        for entry in summary_data:
            host = entry.get('host', 'Unknown')
            status = entry.get('status', 'Unknown')
            error = entry.get('error', '')
            port_profiles = entry.get('port_profiles', {})
            
            if status == "Success" and port_profiles:
                # Group interfaces by profile
                profile_summary = {}
                
                for key, profile_info in port_profiles.items():
                    profile_name = profile_info.get('profile', 'N/A')
                    
                    if key.startswith('UNUSED_'):
                        # Unused profile
                        profile_summary[profile_name] = {
                            'status': 'Unused',
                            'interface_count': 0,
                            'interfaces': 'None'
                        }
                    else:
                        # Applied profile
                        if profile_name not in profile_summary:
                            profile_summary[profile_name] = {
                                'status': 'Applied',
                                'interface_count': 0,
                                'interfaces': []
                            }
                        profile_summary[profile_name]['interface_count'] += 1
                        profile_summary[profile_name]['interfaces'].append(key)
                
                # Create CSV rows for each profile
                for profile_name, profile_data in profile_summary.items():
                    if profile_data['status'] == 'Applied':
                        # Format interface list (first few interfaces + count)
                        interfaces = profile_data['interfaces']
                        if len(interfaces) <= 3:
                            interface_list = ', '.join(interfaces)
                        else:
                            interface_list = f"{', '.join(interfaces[:3])} ... (+{len(interfaces)-3} more)"
                    else:
                        interface_list = 'None'
                    
                    csv_data.append({
                        'Host': host,
                        'Status': status,
                        'Port_Profile': profile_name,
                        'Profile_Status': profile_data['status'],
                        'Interface_Count': profile_data['interface_count'],
                        'Sample_Interfaces': interface_list,
                        'Error': ''
                    })
            else:
                # Failed connection or no data
                csv_data.append({
                    'Host': host,
                    'Status': status,
                    'Port_Profile': 'N/A',
                    'Profile_Status': 'N/A',
                    'Interface_Count': 0,
                    'Sample_Interfaces': 'N/A',
                    'Error': error
                })
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_filepath, index=False)
        
        logger.info(f"CSV report saved to: {csv_filepath}")
        logger.info(f"Total rows: {len(csv_data)}")
        
        return str(csv_filepath)
        
    except Exception as e:
        logger.error(f"Error writing CSV file: {str(e)}")
        raise

def write_detailed_csv(summary_data, output_dir):
    """Write interface-level detailed CSV"""
    # Placeholder for detailed CSV writing logic
    pass