import requests
import psutil
import cpuinfo
import wmi
import configparser

# Function to get the MAC address of the primary network interface
def get_mac_address():
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == psutil.AF_LINK:
                return addr.address
    return None

# Function to get the external IP address
def get_external_ip():
    response = requests.get('https://api.ipify.org?format=json')
    return response.json()['ip']

# Function to get the hardware settings
def get_hardware_settings():
    cpu_info = cpuinfo.get_cpu_info()
    processor = cpu_info['brand_raw']
    
    ram = psutil.virtual_memory().total
    ram_amount = f"{ram // (1024 ** 2)}"  # Converted to MB

    c = wmi.WMI()
    for disk in c.Win32_DiskDrive():
        hdd_id = disk.SerialNumber.strip()  # Get serial number from the Disk #1
        break

    disks = psutil.disk_partitions()
    for disk in disks:
        if disk.fstype:
            disk_use = psutil.disk_usage(disk.mountpoint)
            disk_amount = f"{disk_use.total // (1024 ** 2)}"  # Convert to MB
            break

    return {
        'processor': processor,
        'ram_amount': ram_amount,
        'disk_amount': disk_amount,
        'hdd_id': hdd_id
    }

# Function to validate the license
def validate_license(license_key, license_type, hardware_settings):
    url = 'https://licensechain.app/api/validation.php'
    mac_address = get_mac_address()
    
    data = {
        'license_key': license_key,
        'license_type': license_type,
        **hardware_settings,
        'mac_address': mac_address
    }
    
    response = requests.post(url, data=data)
    return response.json()

def check_license():
    # Get settings
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Validate License
    license_key = config['KEY-CONFIG']['license']
    license_type = config['KEY-CONFIG']['license_type']
    hardware_settings = get_hardware_settings()
    validation_result = validate_license(license_key, license_type, hardware_settings)

    return validation_result
