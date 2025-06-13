# NXOS Port Profile Checker

A Python automation tool that connects to multiple Cisco NXOS devices to collect and analyze active port profiles, generating comprehensive CSV reports for network documentation and auditing.

## Overview

This tool uses the Nornir automation framework to:
- Connect to multiple NXOS devices simultaneously
- Execute port profile commands via SSH
- Parse and structure the collected data
- Generate timestamped CSV reports for analysis

## Features

- **Multi-device Support**: Process multiple NXOS switches in parallel
- **Interactive Authentication**: Secure password prompting (no hardcoded credentials)
- **Flexible Inventory**: Simple text file input for device lists
- **Detailed Reporting**: CSV output with interface-level port profile mapping
- **Error Handling**: Comprehensive logging and failure tracking
- **Timestamped Output**: Unique reports for each execution

## Project Structure

```
nxos-port-profile-checker/
├── src/
│   ├── main.py                     # Main execution script
│   ├── inventory/
│   │   ├── hostnames.txt          # Input: List of device IPs/hostnames
│   │   ├── hosts.yaml             # Generated: Nornir host inventory
│   │   ├── groups.yaml            # Generated: Device group configuration
│   │   └── defaults.yaml          # Generated: Default connection settings
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── nxos_tasks.py          # NXOS-specific automation tasks
│   └── utils/
│       ├── __init__.py
│       └── csv_handler.py         # CSV report generation
├── output/                        # Generated CSV reports
├── logs/                          # Execution logs
├── requirements.txt               # Python dependencies
└── README.md
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd nxos-port-profile-checker
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Mac/Linux
   # or
   .venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Device Inventory

Add your NXOS device IPs or hostnames to the inventory file:

```bash
# Edit the hostnames file
nano src/inventory/hostnames.txt
```

Example content:
```
192.168.1.10
192.168.1.11
nxos-switch-01.company.com
nexus-core-01.company.com
```

## Usage

### Basic Execution

```bash
cd nxos-port-profile-checker
python3 src/main.py
```

The script will:
1. Prompt for SSH username and password
2. Create inventory files from your hostnames.txt
3. Connect to all devices in parallel
4. Execute port profile commands
5. Generate a timestamped CSV report

### Example Output

```
NXOS Port Profile Checker
------------------------------
Username: admin
Password: [hidden]
2025-06-13 10:58:28,637 - __main__ - INFO - Created inventory for 3 hosts
2025-06-13 10:58:28,983 - __main__ - INFO - Initialized Nornir with 3 devices
2025-06-13 10:58:28,983 - __main__ - INFO - Starting port profile collection...
2025-06-13 10:58:29,941 - __main__ - INFO - CSV report generated: output/port_profiles_summary_20250613_105829.csv

Summary: 3 successful, 0 failed
```

## CSV Report Format

The generated CSV contains:

| Column | Description |
|--------|-------------|
| Host | Device hostname/IP |
| Status | Success/Failed |
| Interface | Switch interface (e.g., Eth1/1) |
| Port_Profile | Active port profile name |
| VLAN | Associated VLAN |
| Description | Interface description |
| Error | Error message (if failed) |

## Dependencies

- **nornir**: Automation framework core
- **nornir_netmiko**: SSH connectivity for network devices
- **nornir_utils**: Utility functions and result formatting
- **pandas**: Data manipulation and CSV generation
- **pyyaml**: YAML file processing

## Logging

Execution logs are saved to `logs/nxos_checker.log` with detailed information about:
- Device connections
- Authentication status
- Command execution
- Error details
- Report generation

## Troubleshooting

### Common Issues

1. **Authentication Failures**:
   - Verify SSH credentials
   - Check device SSH configuration
   - Ensure management IP connectivity

2. **Command Parsing Issues**:
   - Review `nxos_tasks.py` parsing logic
   - Check NXOS command output format
   - Adjust parser for your device version

3. **Network Connectivity**:
   - Verify device reachability
   - Check firewall rules
   - Validate DNS resolution (if using hostnames)

### Debug Mode

For detailed debugging, check the log files:
```bash
tail -f logs/nxos_checker.log
```

## Security Notes

- Credentials are prompted interactively (not stored)
- No sensitive data in configuration files
- SSH connections use secure authentication
- Logs may contain device information (review before sharing)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with your NXOS environment
5. Submit a pull request

## License

[Add your license information here]