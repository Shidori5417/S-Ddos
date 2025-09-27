#!/usr/bin/env python3
"""
Linux Setup Script for FsocietyDDoS
Automated installation and configuration for Linux systems
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LinuxSetup:
    """Linux setup and configuration manager"""
    
    def __init__(self):
        self.system_info = {
            'os': platform.system(),
            'distribution': self._get_distribution(),
            'architecture': platform.machine(),
            'python_version': platform.python_version()
        }
        self.required_packages = [
            'python3-dev',
            'python3-pip',
            'build-essential',
            'libssl-dev',
            'libffi-dev',
            'libpcap-dev',
            'net-tools',
            'iptables',
            'tor'
        ]
        
    def _get_distribution(self):
        """Get Linux distribution information"""
        try:
            with open('/etc/os-release', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith('ID='):
                        return line.split('=')[1].strip().strip('"')
        except FileNotFoundError:
            return 'unknown'
        return 'unknown'
    
    def check_system_requirements(self):
        """Check system requirements"""
        logger.info("Checking system requirements...")
        
        # Check OS
        if self.system_info['os'] != 'Linux':
            logger.error(f"This script is for Linux systems only. Detected: {self.system_info['os']}")
            return False
            
        # Check Python version
        python_version = tuple(map(int, self.system_info['python_version'].split('.')))
        if python_version < (3, 7):
            logger.error(f"Python 3.7+ required. Current: {self.system_info['python_version']}")
            return False
            
        # Check root privileges for network operations
        if os.geteuid() != 0:
            logger.warning("Root privileges recommended for network operations")
            
        logger.info("✓ System requirements check passed")
        return True
    
    def install_system_packages(self):
        """Install required system packages"""
        logger.info("Installing system packages...")
        
        distribution = self.system_info['distribution']
        
        if distribution in ['ubuntu', 'debian']:
            self._install_apt_packages()
        elif distribution in ['centos', 'rhel', 'fedora']:
            self._install_yum_packages()
        elif distribution in ['arch', 'manjaro']:
            self._install_pacman_packages()
        else:
            logger.warning(f"Unknown distribution: {distribution}. Manual package installation may be required.")
            
    def _install_apt_packages(self):
        """Install packages using apt (Ubuntu/Debian)"""
        try:
            # Update package list
            subprocess.run(['apt', 'update'], check=True, capture_output=True)
            
            # Install packages
            cmd = ['apt', 'install', '-y'] + self.required_packages
            subprocess.run(cmd, check=True, capture_output=True)
            
            logger.info("✓ APT packages installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install APT packages: {e}")
            
    def _install_yum_packages(self):
        """Install packages using yum/dnf (CentOS/RHEL/Fedora)"""
        try:
            # Determine package manager
            pkg_manager = 'dnf' if shutil.which('dnf') else 'yum'
            
            # Map package names for RHEL-based systems
            rhel_packages = [
                'python3-devel',
                'python3-pip',
                'gcc',
                'gcc-c++',
                'make',
                'openssl-devel',
                'libffi-devel',
                'libpcap-devel',
                'net-tools',
                'iptables',
                'tor'
            ]
            
            cmd = [pkg_manager, 'install', '-y'] + rhel_packages
            subprocess.run(cmd, check=True, capture_output=True)
            
            logger.info(f"✓ {pkg_manager.upper()} packages installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {pkg_manager} packages: {e}")
            
    def _install_pacman_packages(self):
        """Install packages using pacman (Arch Linux)"""
        try:
            # Update package database
            subprocess.run(['pacman', '-Sy'], check=True, capture_output=True)
            
            # Map package names for Arch Linux
            arch_packages = [
                'python',
                'python-pip',
                'base-devel',
                'openssl',
                'libffi',
                'libpcap',
                'net-tools',
                'iptables',
                'tor'
            ]
            
            cmd = ['pacman', '-S', '--noconfirm'] + arch_packages
            subprocess.run(cmd, check=True, capture_output=True)
            
            logger.info("✓ Pacman packages installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install Pacman packages: {e}")
    
    def install_python_dependencies(self):
        """Install Python dependencies"""
        logger.info("Installing Python dependencies...")
        
        try:
            # Upgrade pip
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                         check=True, capture_output=True)
            
            # Install requirements
            requirements_file = Path(__file__).parent / 'requirements.txt'
            if requirements_file.exists():
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)], 
                             check=True, capture_output=True)
                logger.info("✓ Python dependencies installed successfully")
            else:
                logger.error("requirements.txt not found")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install Python dependencies: {e}")
            return False
            
        return True
    
    def configure_network_capabilities(self):
        """Configure network capabilities for raw socket operations"""
        logger.info("Configuring network capabilities...")
        
        try:
            python_path = sys.executable
            
            # Set capabilities for raw socket operations
            subprocess.run(['setcap', 'cap_net_raw+ep', python_path], 
                         check=True, capture_output=True)
            
            logger.info("✓ Network capabilities configured")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to set network capabilities: {e}")
            logger.warning("Raw socket operations may require root privileges")
    
    def setup_tor_service(self):
        """Setup and configure Tor service"""
        logger.info("Setting up Tor service...")
        
        try:
            # Enable and start Tor service
            subprocess.run(['systemctl', 'enable', 'tor'], check=True, capture_output=True)
            subprocess.run(['systemctl', 'start', 'tor'], check=True, capture_output=True)
            
            # Check if Tor is running
            result = subprocess.run(['systemctl', 'is-active', 'tor'], 
                                  capture_output=True, text=True)
            
            if result.stdout.strip() == 'active':
                logger.info("✓ Tor service configured and running")
            else:
                logger.warning("Tor service may not be running properly")
                
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to setup Tor service: {e}")
    
    def create_config_files(self):
        """Create Linux-specific configuration files"""
        logger.info("Creating configuration files...")
        
        config_dir = Path(__file__).parent / 'config'
        config_dir.mkdir(exist_ok=True)
        
        # Linux-specific configuration
        linux_config = {
            'system': {
                'platform': 'linux',
                'use_raw_sockets': True,
                'network_interface': 'auto',
                'enable_capabilities': True
            },
            'security': {
                'drop_privileges': True,
                'use_tor': True,
                'enable_iptables_rules': False
            },
            'logging': {
                'syslog_enabled': True,
                'log_rotation': True,
                'max_log_size': '100MB'
            }
        }
        
        config_file = config_dir / 'linux_config.json'
        with open(config_file, 'w') as f:
            json.dump(linux_config, f, indent=2)
            
        logger.info(f"✓ Configuration file created: {config_file}")
    
    def setup_service_files(self):
        """Create systemd service files (optional)"""
        logger.info("Creating systemd service files...")
        
        service_content = f"""[Unit]
Description=FsocietyDDoS Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={Path(__file__).parent}
ExecStart={sys.executable} fsociety_ddos.py --daemon
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
        
        service_file = Path('/etc/systemd/system/fsociety-ddos.service')
        try:
            with open(service_file, 'w') as f:
                f.write(service_content)
            
            subprocess.run(['systemctl', 'daemon-reload'], check=True, capture_output=True)
            logger.info(f"✓ Systemd service file created: {service_file}")
            
        except (PermissionError, subprocess.CalledProcessError) as e:
            logger.warning(f"Failed to create systemd service: {e}")
    
    def run_setup(self):
        """Run complete setup process"""
        logger.info("Starting FsocietyDDoS Linux setup...")
        
        # Check system requirements
        if not self.check_system_requirements():
            return False
        
        # Install system packages
        self.install_system_packages()
        
        # Install Python dependencies
        if not self.install_python_dependencies():
            return False
        
        # Configure network capabilities
        self.configure_network_capabilities()
        
        # Setup Tor service
        self.setup_tor_service()
        
        # Create configuration files
        self.create_config_files()
        
        # Setup service files
        self.setup_service_files()
        
        logger.info("✓ Linux setup completed successfully!")
        logger.info("You can now run: python3 fsociety_ddos.py")
        
        return True

def main():
    """Main setup function"""
    print("FsocietyDDoS Linux Setup")
    print("=" * 50)
    
    setup = LinuxSetup()
    
    # Display system information
    print(f"OS: {setup.system_info['os']}")
    print(f"Distribution: {setup.system_info['distribution']}")
    print(f"Architecture: {setup.system_info['architecture']}")
    print(f"Python Version: {setup.system_info['python_version']}")
    print()
    
    # Ask for confirmation
    response = input("Continue with setup? (y/N): ").lower()
    if response not in ['y', 'yes']:
        print("Setup cancelled.")
        return
    
    # Run setup
    success = setup.run_setup()
    
    if success:
        print("\n" + "=" * 50)
        print("Setup completed successfully!")
        print("=" * 50)
        print("Next steps:")
        print("1. Review configuration files in config/")
        print("2. Run: python3 fsociety_ddos.py --help")
        print("3. For service mode: systemctl enable fsociety-ddos")
        print("\nRemember: Use this tool responsibly and legally!")
    else:
        print("\n" + "=" * 50)
        print("Setup failed. Please check the logs above.")
        print("=" * 50)

if __name__ == "__main__":
    main()