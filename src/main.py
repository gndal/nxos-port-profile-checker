import getpass
import logging
import yaml
from pathlib import Path
from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from utils.csv_handler import write_to_csv
from tasks.nxos_tasks import check_port_profiles

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/nxos_checker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_inventory_files_from_txt(txt_file):
    """Create YAML inventory files from text file"""
    with open(txt_file, 'r') as f:
        hostnames = [line.strip() for line in f if line.strip()]
    
    # Create hosts.yaml
    hosts = {}
    for hostname in hostnames:
        # Use hostname without dots for the key
        host_key = hostname.replace('.', '_')
        hosts[host_key] = {
            'hostname': hostname,
            'groups': ['nxos_devices']
        }
    
    # Create groups.yaml
    groups = {
        'nxos_devices': {
            'platform': 'nxos',
            'connection_options': {
                'netmiko': {
                    'platform': 'cisco_nxos'
                }
            }
        }
    }
    
    # Create defaults.yaml
    defaults = {
        'platform': 'nxos'
    }
    
    # Write YAML files
    inventory_dir = Path('src/inventory')
    inventory_dir.mkdir(exist_ok=True)
    
    with open(inventory_dir / 'hosts.yaml', 'w') as f:
        yaml.dump(hosts, f, default_flow_style=False)
    
    with open(inventory_dir / 'groups.yaml', 'w') as f:
        yaml.dump(groups, f, default_flow_style=False)
        
    with open(inventory_dir / 'defaults.yaml', 'w') as f:
        yaml.dump(defaults, f, default_flow_style=False)
    
    return len(hostnames)

def main():
    try:
        # Prompt for credentials
        print("NXOS Port Profile Checker")
        print("-" * 30)
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        
        if not username or not password:
            logger.error("Username and password are required")
            return
        
        # Create inventory files from text file
        num_hosts = create_inventory_files_from_txt('src/inventory/hostnames.txt')
        logger.info(f"Created inventory for {num_hosts} hosts")
        
        # Initialize Nornir with simple inventory
        nr = InitNornir(
            runner={"plugin": "threaded", "options": {"num_workers": 5}},
            inventory={
                "plugin": "SimpleInventory",
                "options": {
                    "host_file": "src/inventory/hosts.yaml",
                    "group_file": "src/inventory/groups.yaml",
                    "defaults_file": "src/inventory/defaults.yaml"
                }
            },
            logging={"level": "INFO"}
        )
        
        logger.info(f"Initialized Nornir with {len(nr.inventory.hosts)} devices")
        
        # Set credentials for all devices
        for host in nr.inventory.hosts.values():
            host.username = username
            host.password = password
        
        # Execute the task to check active port profiles
        logger.info("Starting port profile collection...")
        results = nr.run(task=check_port_profiles)
        
        # Print results for debugging
        print_result(results)
        
        # Process results and generate CSV
        summary = process_results(results)
        output_file = write_to_csv(summary)
        
        logger.info(f"CSV report generated: {output_file}")
        
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise

def process_results(results):
    """Process Nornir results into summary format"""
    summary = []
    successful_hosts = 0
    failed_hosts = 0
    
    for host, result in results.items():
        if result.failed:
            failed_hosts += 1
            error_msg = str(result.exception) if result.exception else "Unknown error"
            summary.append({
                "host": host, 
                "status": "Failed", 
                "error": error_msg,
                "port_profiles": None
            })
        else:
            successful_hosts += 1
            port_profiles = result.result if hasattr(result, 'result') else result[0].result
            summary.append({
                "host": host, 
                "status": "Success", 
                "port_profiles": port_profiles,
                "error": None
            })
    
    print(f"\nSummary: {successful_hosts} successful, {failed_hosts} failed")
    return summary

if __name__ == "__main__":
    main()