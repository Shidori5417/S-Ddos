"""
Modern CLI Color System for FsocietyDDoS
Advanced styling and color management using Rich library
"""

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.align import Align
from rich.box import ROUNDED, DOUBLE, HEAVY
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.syntax import Syntax
from rich.tree import Tree
from rich.rule import Rule
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.layout import Layout
from rich.padding import Padding
import colorama
from colorama import Fore, Back, Style
import time
from typing import Optional, List, Dict, Any
import platform

# Initialize colorama for cross-platform compatibility
if platform.system() == "Windows":
    try:
        import colorama
        colorama.init()
    except ImportError:
        pass  # Colorama not available on this system

# Global console instance
console = Console(force_terminal=True, width=120)

class Colors:
    """Modern color scheme for FsocietyDDoS CLI"""
    
    # Primary colors
    PRIMARY = "#00ff41"      # Matrix green
    SECONDARY = "#ff6b35"    # Orange accent
    ACCENT = "#7209b7"       # Purple accent
    
    # Status colors
    SUCCESS = "#00ff41"      # Green
    WARNING = "#ffb000"      # Yellow
    ERROR = "#ff073a"        # Red
    INFO = "#00bfff"         # Blue
    
    # UI colors
    HEADER = "#ffffff"       # White
    SUBHEADER = "#b0b0b0"    # Light gray
    TEXT = "#e0e0e0"         # Light text
    DIM = "#808080"          # Dim text
    
    # Special effects
    GLOW = "#00ff41"         # Glowing effect
    CYBER = "#00ffff"        # Cyber blue
    MATRIX = "#00ff41"       # Matrix green

class StyleManager:
    """Advanced styling manager for CLI elements"""
    
    @staticmethod
    def create_banner(title: str, subtitle: str = "", width: int = 100) -> Panel:
        """Create a modern banner with cyber styling"""
        banner_text = Text()
        
        # Main title with glow effect
        banner_text.append("🎭 ", style=f"bold {Colors.ACCENT}")
        banner_text.append(title, style=f"bold {Colors.PRIMARY}")
        banner_text.append(" 🎭", style=f"bold {Colors.ACCENT}")
        
        if subtitle:
            banner_text.append("\n")
            banner_text.append(subtitle, style=f"italic {Colors.SUBHEADER}")
        
        # Add decorative elements
        banner_text.append("\n\n")
        banner_text.append("⚡ ", style=f"bold {Colors.CYBER}")
        banner_text.append("ADVANCED PROFESSIONAL EDITION", style=f"bold {Colors.SECONDARY}")
        banner_text.append(" ⚡", style=f"bold {Colors.CYBER}")
        
        return Panel(
            Align.center(banner_text),
            box=DOUBLE,
            border_style=Colors.PRIMARY,
            padding=(1, 2),
            width=width
        )
    
    @staticmethod
    def create_help_section(title: str, content: str, icon: str = "📋") -> Panel:
        """Create a styled help section"""
        section_text = Text()
        section_text.append(f"{icon} ", style=f"bold {Colors.ACCENT}")
        section_text.append(title, style=f"bold {Colors.HEADER}")
        section_text.append("\n\n")
        section_text.append(content, style=Colors.TEXT)
        
        return Panel(
            section_text,
            box=ROUNDED,
            border_style=Colors.INFO,
            padding=(0, 1)
        )
    
    @staticmethod
    def create_command_table(commands: Dict[str, str]) -> Table:
        """Create a styled command table"""
        table = Table(
            title="🚀 Available Commands",
            title_style=f"bold {Colors.PRIMARY}",
            box=ROUNDED,
            border_style=Colors.CYBER,
            header_style=f"bold {Colors.HEADER}",
            show_lines=True
        )
        
        table.add_column("Command", style=f"bold {Colors.SUCCESS}", width=20)
        table.add_column("Description", style=Colors.TEXT, width=50)
        table.add_column("Status", style=f"bold {Colors.ACCENT}", width=15)
        
        for cmd, desc in commands.items():
            # Add status indicator
            status = "✅ Active" if cmd in ['help', 'attack', 'scan'] else "🔧 Ready"
            table.add_row(cmd, desc, status)
        
        return table
    
    @staticmethod
    def create_example_section(examples: List[Dict[str, str]]) -> Panel:
        """Create styled examples section"""
        content = Text()
        content.append("💡 ", style=f"bold {Colors.WARNING}")
        content.append("Usage Examples", style=f"bold {Colors.HEADER}")
        content.append("\n\n")
        
        for i, example in enumerate(examples, 1):
            content.append(f"{i}. ", style=f"bold {Colors.ACCENT}")
            content.append(example['title'], style=f"bold {Colors.SUCCESS}")
            content.append("\n   ")
            content.append(example['command'], style=f"italic {Colors.CYBER}")
            content.append("\n   ")
            content.append(example['description'], style=Colors.DIM)
            content.append("\n\n")
        
        return Panel(
            content,
            box=ROUNDED,
            border_style=Colors.WARNING,
            padding=(1, 2)
        )
    
    @staticmethod
    def create_status_indicator(status: str, message: str) -> Text:
        """Create a styled status indicator"""
        text = Text()
        
        status_styles = {
            'success': (Colors.SUCCESS, '✅'),
            'warning': (Colors.WARNING, '⚠️'),
            'error': (Colors.ERROR, '❌'),
            'info': (Colors.INFO, 'ℹ️'),
            'loading': (Colors.CYBER, '⏳'),
            'attack': (Colors.ERROR, '🔥'),
            'scan': (Colors.INFO, '🔍'),
            'stealth': (Colors.ACCENT, '🥷')
        }
        
        color, icon = status_styles.get(status.lower(), (Colors.TEXT, '•'))
        
        text.append(f"{icon} ", style=f"bold {color}")
        text.append(message, style=color)
        
        return text
    
    @staticmethod
    def create_progress_display(title: str, current: int, total: int, rate: float = 0) -> Panel:
        """Create a modern progress display"""
        progress_text = Text()
        
        # Title
        progress_text.append("⚡ ", style=f"bold {Colors.CYBER}")
        progress_text.append(title, style=f"bold {Colors.HEADER}")
        progress_text.append("\n\n")
        
        # Progress bar
        percentage = (current / total * 100) if total > 0 else 0
        bar_width = 40
        filled = int(bar_width * percentage / 100)
        
        progress_text.append("Progress: [", style=Colors.TEXT)
        progress_text.append("█" * filled, style=f"bold {Colors.SUCCESS}")
        progress_text.append("░" * (bar_width - filled), style=Colors.DIM)
        progress_text.append(f"] {percentage:.1f}%", style=Colors.TEXT)
        
        # Stats
        progress_text.append(f"\n\nCurrent: {current:,} / {total:,}", style=Colors.INFO)
        if rate > 0:
            progress_text.append(f"\nRate: {rate:.1f}/s", style=Colors.ACCENT)
        
        return Panel(
            progress_text,
            box=ROUNDED,
            border_style=Colors.PRIMARY,
            padding=(1, 2)
        )

class ModernCLI:
    """Modern CLI interface with advanced styling"""
    
    def __init__(self):
        self.console = console
        self.style_manager = StyleManager()
    
    def show_welcome(self):
        """Show modern welcome screen"""
        self.console.clear()
        
        # Main banner
        banner = self.style_manager.create_banner(
            "FSOCIETY DDOS TOOL",
            "Advanced Network Testing & Security Research Platform"
        )
        self.console.print(banner)
        
        # Warning panel
        warning = Panel(
            Text("⚠️  SADECE EĞİTİM VE TEST AMAÇLI KULLANINIZ  ⚠️\n"
                 "Kendi sunucularınızda test etmek için tasarlanmıştır\n"
                 "Yetkisiz kullanım yasaktır ve yasal sorumluluk kullanıcıya aittir",
                 style=f"bold {Colors.WARNING}", justify="center"),
            box=HEAVY,
            border_style=Colors.ERROR,
            padding=(1, 2)
        )
        self.console.print(warning)
        
        # Features showcase
        features = [
            "🔥 Gelişmiş Layer 4/7 Saldırı Metodları",
            "🛡️ WAF Bypass ve Evasion Teknikleri", 
            "🔒 Trafik Şifreleme ve Gizlilik Özellikleri",
            "📊 Gerçek Zamanlı İstatistikler ve Monitoring",
            "🌐 Dağıtık Saldırı Koordinasyonu",
            "🧅 Tor Proxy Desteği",
            "🎯 Profesyonel Proxy Yönetimi"
        ]
        
        feature_text = Text()
        for feature in features:
            feature_text.append(f"  {feature}\n", style=Colors.TEXT)
        
        features_panel = Panel(
            feature_text,
            title="🚀 Features",
            title_style=f"bold {Colors.PRIMARY}",
            box=ROUNDED,
            border_style=Colors.CYBER
        )
        self.console.print(features_panel)
        
        # Quick start
        self.console.print(Rule(f"[bold {Colors.ACCENT}]Quick Start[/]"))
        self.console.print(f"[{Colors.INFO}]Type[/] [bold {Colors.SUCCESS}]help[/] [{Colors.INFO}]to see available commands[/]")
        self.console.print()
    
    def print_colored(self, text: str, style: str = Colors.TEXT):
        """Print colored text"""
        self.console.print(text, style=style)
    
    def print_status(self, status: str, message: str):
        """Print status message"""
        status_text = self.style_manager.create_status_indicator(status, message)
        self.console.print(status_text)
    
    def show_loading(self, message: str, duration: float = 2.0):
        """Show loading animation"""
        with console.status(f"[bold {Colors.CYBER}]{message}...", spinner="dots"):
            time.sleep(duration)
    
    def print_success(self, message: str):
        """Print success message"""
        self.console.print(f"[bold {Colors.SUCCESS}]{message}[/]")
    
    def print_error(self, message: str):
        """Print error message"""
        self.console.print(f"[bold {Colors.ERROR}]{message}[/]")
    
    def print_warning(self, message: str):
        """Print warning message"""
        self.console.print(f"[bold {Colors.WARNING}]{message}[/]")
    
    def print_info(self, message: str):
        """Print info message"""
        self.console.print(f"[bold {Colors.INFO}]{message}[/]")

# Global CLI instance
modern_cli = ModernCLI()