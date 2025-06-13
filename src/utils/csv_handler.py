import pandas as pd
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def write_to_csv(summary_data, output_dir="output"):
    """
    Write port profile summary to CSV file
    
    Args:
        summary_data (list): List of dictionaries containing host results
        output_dir (str): Output directory path
    
    Returns:
        str: Path to the generated CSV file
    """
    try:
        # Ensure output directory exists
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"port_profiles_summary_{timestamp}.csv"
        csv_filepath = output_path / csv_filename
        
        # Flatten the data for CSV export
        csv_data = []
        
        for entry in summary_data:
            host = entry.get('host', 'Unknown')
            status = entry.get('status', 'Unknown')
            error = entry.get('error', '')
            port_profiles = entry.get('port_profiles', {})
            
            if status == "Success" and port_profiles:
                # If we have port profile data, create rows for each interface
                for interface, profile_info in port_profiles.items():
                    csv_data.append({
                        'Host': host,
                        'Status': status,
                        'Interface': interface,
                        'Port_Profile': profile_info.get('profile', 'N/A'),
                        'VLAN': profile_info.get('vlan', 'N/A'),
                        'Description': profile_info.get('description', 'N/A'),
                        'Error': ''
                    })
            else:
                # Failed connection or no data
                csv_data.append({
                    'Host': host,
                    'Status': status,
                    'Interface': 'N/A',
                    'Port_Profile': 'N/A',
                    'VLAN': 'N/A',
                    'Description': 'N/A',
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