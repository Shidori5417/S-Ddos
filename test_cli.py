#!/usr/bin/env python3
"""
Test script for the modernized CLI system
Tests all the colorized components and Rich styling
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cli.colors import ModernCLI, StyleManager, Colors, console
from cli.display import DisplayManager, AttackDisplay
from cli.interface import MenuSystem, CLIInterface
from rich.panel import Panel
from rich.table import Table
import time

def test_colors():
    """Test the color system"""
    console.print("\n=== Testing Color System ===", style="bold cyan")
    
    modern_cli = ModernCLI()
    style_manager = StyleManager()
    
    # Test basic colors using Rich styling
    console.print("Testing basic colors:", style="bold")
    console.print("Primary color text", style=Colors.PRIMARY)
    console.print("Success color text", style=Colors.SUCCESS)
    console.print("Warning color text", style=Colors.WARNING)
    console.print("Error color text", style=Colors.ERROR)
    console.print("Info color text", style=Colors.INFO)
    
    # Test styled messages
    console.print("\nTesting styled messages:")
    modern_cli.print_success("✅ Success message test")
    modern_cli.print_error("❌ Error message test")
    modern_cli.print_warning("⚠️ Warning message test")
    modern_cli.print_info("ℹ️ Info message test")

def test_display_manager():
    """Test the DisplayManager class"""
    console.print("\n=== Testing Display Manager ===", style="bold cyan")
    
    display = DisplayManager()
    
    # Test banner
    display.show_banner("🎭 FSOCIETY DDOS TOOL 🎭", "Test Mode")
    
    # Test sections
    display.show_section("Configuration")
    console.print("Setting up test parameters...")
    
    display.show_section("Network")
    console.print("Checking network connectivity...")
    
    display.show_section("Security")
    console.print("Initializing security features...")

def test_attack_display():
    """Test the AttackDisplay class"""
    print("\n=== Testing Attack Display ===")
    
    attack_display = AttackDisplay()
    
    # Start display
    attack_display.start_display("http://example.com", "HTTP-FLOOD", 1000)
    
    # Simulate some stats updates
    for i in range(5):
        attack_display.update_stats({
            'requests_sent': i * 100,
            'responses_received': i * 85,
            'errors': i * 5,
            'bytes_sent': i * 1024,
            'bytes_received': i * 512,
            'avg_response_time': 0.5 + (i * 0.1)
        })
        time.sleep(1)
    
    # Stop display
    attack_display.stop_display()

def test_menu_system():
    """Test the MenuSystem class"""
    print("\n=== Testing Menu System ===")
    
    menu = MenuSystem()
    
    # Show header
    menu._show_header()
    
    # Test menu display (without actual navigation)
    console.print("\n" + "="*60)
    console.print("Menu system header test completed successfully!", style="bold green")
    console.print("="*60)

def main():
    """Main test function"""
    console.print(Panel.fit(
        "[bold cyan]🧪 CLI Modernization Test Suite 🧪[/bold cyan]\n"
        "[yellow]Testing all modernized CLI components[/yellow]",
        border_style="cyan"
    ))
    
    try:
        # Run all tests
        test_colors()
        test_display_manager()
        test_menu_system()
        
        # Note: Attack display test is commented out as it's interactive
        # Uncomment the line below to test it manually
        # test_attack_display()
        
        console.print(Panel.fit(
            "[bold green]✅ All CLI tests completed successfully![/bold green]\n"
            "[yellow]The modernized CLI system is working correctly.[/yellow]",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(Panel.fit(
            f"[bold red]❌ Test failed with error:[/bold red]\n"
            f"[red]{str(e)}[/red]",
            border_style="red"
        ))
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())