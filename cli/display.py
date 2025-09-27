"""
Display utilities for CLI interface
"""

import sys
import time
import threading
from typing import Optional, List, Dict, Any
from core.utils import format_bytes, format_duration
from cli.colors import ModernCLI, StyleManager, Colors, console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.text import Text


class ProgressBar:
    """Advanced progress bar with statistics"""
    
    def __init__(self, total: int = 100, width: int = 50, title: str = "Progress"):
        self.total = total
        self.width = width
        self.title = title
        self.current = 0
        self.start_time = time.time()
        self.last_update = 0
        self.running = False
        self.thread = None
        
        # Statistics
        self.stats = {
            'rate': 0,
            'eta': 0,
            'elapsed': 0
        }
    
    def start(self):
        """Start progress bar display"""
        self.running = True
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._display_loop, daemon=True)
        self.thread.start()
    
    def update(self, value: int, stats: Optional[Dict[str, Any]] = None):
        """Update progress bar"""
        self.current = min(value, self.total)
        
        # Update statistics
        elapsed = time.time() - self.start_time
        self.stats['elapsed'] = elapsed
        
        if elapsed > 0:
            self.stats['rate'] = self.current / elapsed
            if self.stats['rate'] > 0:
                remaining = self.total - self.current
                self.stats['eta'] = remaining / self.stats['rate']
        
        if stats:
            self.stats.update(stats)
    
    def _display_loop(self):
        """Display loop for progress bar"""
        while self.running:
            self._render()
            time.sleep(0.1)
    
    def _render(self):
        """Render progress bar"""
        if time.time() - self.last_update < 0.1:
            return
        
        self.last_update = time.time()
        
        # Calculate progress
        progress = self.current / self.total if self.total > 0 else 0
        filled_width = int(self.width * progress)
        
        # Create bar
        bar = '█' * filled_width + '░' * (self.width - filled_width)
        percentage = progress * 100
        
        # Format statistics
        rate_str = f"{self.stats['rate']:.1f}/s" if self.stats['rate'] > 0 else "0/s"
        elapsed_str = format_duration(self.stats['elapsed'])
        eta_str = format_duration(self.stats['eta']) if self.stats['eta'] > 0 else "∞"
        
        # Build display line
        line = f"\r  {self.title}: [{bar}] {percentage:5.1f}% | "
        line += f"{self.current}/{self.total} | "
        line += f"Rate: {rate_str} | "
        line += f"Elapsed: {elapsed_str} | "
        line += f"ETA: {eta_str}"
        
        # Print with padding to clear previous line
        sys.stdout.write(line + " " * 10)
        sys.stdout.flush()
    
    def finish(self):
        """Finish progress bar"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        
        # Final render
        self.current = self.total
        self._render()
        print()  # New line


class DisplayManager:
    """Manages all CLI display operations"""
    
    def __init__(self):
        self.modern_cli = ModernCLI()
        self.style_manager = StyleManager()
    
    def show_banner(self, title: str, subtitle: str = "", width: int = 60):
        """Show modern styled banner"""
        banner_text = f"[bold {Colors.CYBER}]{title}[/]"
        if subtitle:
            banner_text += f"\n[dim {Colors.ACCENT}]{subtitle}[/]"
        
        console.print(Panel(banner_text, style=f"bold {Colors.PRIMARY}", width=width))
    
    def show_section(self, title: str, width: int = 60):
        """Show modern section header"""
        console.print(f"\n[bold {Colors.ACCENT}]{'═' * width}[/]")
        console.print(f"[bold {Colors.PRIMARY}]{title.center(width)}[/]")
        console.print(f"[bold {Colors.ACCENT}]{'═' * width}[/]\n")
    
    def show_table(self, headers: List[str], rows: List[List[str]], title: Optional[str] = None):
        """Show modern colorized table"""
        if not rows:
            console.print(f"[{Colors.WARNING}]No data to display[/]")
            return
        
        table = Table(
            title=f"[bold {Colors.ACCENT}]{title}[/]" if title else None,
            style=f"{Colors.BORDER}",
            header_style=f"bold {Colors.CYBER}",
            show_lines=True
        )
        
        # Add columns
        for header in headers:
            table.add_column(header, style=f"{Colors.TEXT}")
        
        # Add rows
        for row in rows:
            styled_row = []
            for i, cell in enumerate(row):
                if i == 0:  # First column - highlight
                    styled_row.append(f"[bold {Colors.SUCCESS}]{cell}[/]")
                else:
                    styled_row.append(str(cell))
            table.add_row(*styled_row)
        
        console.print(table)
    
    def show_stats(self, stats: Dict[str, Any], title: str = "Statistics"):
        """Show modern colorized statistics"""
        stats_table = Table(
            title=f"[bold {Colors.ACCENT}]{title}[/]",
            style=f"{Colors.BORDER}",
            show_header=False,
            show_lines=True,
            padding=(0, 1)
        )
        
        stats_table.add_column("Metric", style=f"bold {Colors.INFO}")
        stats_table.add_column("Value", style=f"bold {Colors.SUCCESS}")
        
        for key, value in stats.items():
            # Format value based on type
            if isinstance(value, float):
                if 'rate' in key.lower() or 'speed' in key.lower():
                    formatted_value = f"{value:.2f}/s"
                elif 'time' in key.lower() or 'duration' in key.lower():
                    formatted_value = format_duration(value)
                else:
                    formatted_value = f"{value:.2f}"
            elif isinstance(value, int):
                if 'bytes' in key.lower() or 'size' in key.lower():
                    formatted_value = format_bytes(value)
                else:
                    formatted_value = f"{value:,}"
            else:
                formatted_value = str(value)
            
            metric_name = key.replace('_', ' ').title()
            stats_table.add_row(metric_name, formatted_value)
        
        console.print(stats_table)
    
    def show_list(self, items: List[str], title: str, numbered: bool = True):
        """Show modern colorized list"""
        if not items:
            console.print(f"[{Colors.WARNING}]No items to display[/]")
            return
        
        list_content = []
        for i, item in enumerate(items, 1):
            if numbered:
                list_content.append(f"[bold {Colors.ACCENT}][{i:2d}][/] {item}")
            else:
                list_content.append(f"[bold {Colors.ACCENT}]•[/] {item}")
        
        list_panel = Panel(
            "\n".join(list_content),
            title=f"[bold {Colors.CYBER}]{title}[/]",
            style=f"{Colors.BORDER}",
            padding=(1, 2)
        )
        console.print(list_panel)
    
    def show_status(self, status: str, message: str, color: bool = True):
        """Show modern colorized status message"""
        if color:
            status_colors = {
                'success': Colors.SUCCESS,
                'error': Colors.ERROR,
                'warning': Colors.WARNING,
                'info': Colors.INFO
            }
            
            status_color = status_colors.get(status.lower(), Colors.TEXT)
            status_icon = {
                'success': '✅',
                'error': '❌',
                'warning': '⚠️',
                'info': 'ℹ️'
            }.get(status.lower(), '•')
            
            console.print(f"{status_icon} [bold {status_color}][{status.upper()}][/] {message}")
        else:
            console.print(f"[{status.upper()}] {message}")
    
    def show_attack_info(self, attack_type: str, target: str, config: Dict[str, Any]):
        """Show modern colorized attack information"""
        self.show_banner(f"ATTACK CONFIGURATION - {attack_type.upper()}", f"Target: {target}")
        
        # Create attack config table
        config_table = Table(
            title=f"[bold {Colors.CYBER}]Attack Parameters[/]",
            style=f"{Colors.BORDER}",
            show_header=False,
            show_lines=True
        )
        
        config_table.add_column("Parameter", style=f"bold {Colors.INFO}")
        config_table.add_column("Value", style=f"bold {Colors.SUCCESS}")
        
        config_table.add_row("Target", f"[bold {Colors.ERROR}]{target}[/]")
        config_table.add_row("Attack Type", f"[bold {Colors.WARNING}]{attack_type}[/]")
        
        for key, value in config.items():
            if key not in ['target', 'attack_type']:
                param_name = key.replace('_', ' ').title()
                config_table.add_row(param_name, str(value))
        
        console.print(config_table)
    
    def show_real_time_stats(self, stats_callback: callable, duration: int = 60):
        """Show modern real-time statistics with live updates"""
        start_time = time.time()
        
        with Live(console=console, refresh_per_second=2) as live:
            try:
                while time.time() - start_time < duration:
                    # Get current stats
                    stats = stats_callback()
                    
                    # Create stats display
                    stats_table = Table(
                        title=f"[bold {Colors.CYBER}]Real-time Statistics[/]",
                        style=f"{Colors.BORDER}",
                        show_header=False,
                        show_lines=True
                    )
                    
                    stats_table.add_column("Metric", style=f"bold {Colors.INFO}")
                    stats_table.add_column("Value", style=f"bold {Colors.SUCCESS}")
                    
                    for key, value in stats.items():
                        formatted_value = self._format_stat_value(key, value)
                        metric_name = key.replace('_', ' ').title()
                        stats_table.add_row(metric_name, formatted_value)
                    
                    # Add timing info
                    elapsed = time.time() - start_time
                    remaining = duration - elapsed
                    stats_table.add_row("Elapsed Time", format_duration(elapsed))
                    stats_table.add_row("Remaining Time", format_duration(remaining))
                    
                    live.update(stats_table)
                    time.sleep(0.5)
                    
            except KeyboardInterrupt:
                console.print(f"\n[{Colors.WARNING}]Statistics display interrupted by user[/]")
    
    def _format_stat_value(self, key: str, value: Any) -> str:
        """Format statistic value based on type and key"""
        if isinstance(value, float):
            if 'rate' in key.lower() or 'speed' in key.lower():
                return f"{value:.2f}/s"
            elif 'time' in key.lower() or 'duration' in key.lower():
                return format_duration(value)
            else:
                return f"{value:.2f}"
        elif isinstance(value, int):
            if 'bytes' in key.lower() or 'size' in key.lower():
                return format_bytes(value)
            else:
                return f"{value:,}"
        else:
            return str(value)
    
    def confirm_action(self, message: str, default: bool = False) -> bool:
        """Get modern colorized user confirmation"""
        default_str = f"[bold {Colors.SUCCESS}]Y[/]/[{Colors.TEXT}]n[/]" if default else f"[{Colors.TEXT}]y[/]/[bold {Colors.ERROR}]N[/]"
        
        try:
            console.print(f"[bold {Colors.WARNING}]❓ {message}[/] [{default_str}]", end=" ")
            response = input().strip().lower()
            
            if not response:
                return default
            
            return response in ['y', 'yes', '1', 'true']
            
        except KeyboardInterrupt:
            console.print(f"\n[{Colors.ERROR}]Action cancelled by user[/]")
            return False
    
    def get_input(self, prompt: str, default: Optional[str] = None, validator: Optional[callable] = None) -> Optional[str]:
        """Get modern colorized validated user input"""
        try:
            if default:
                full_prompt = f"[bold {Colors.INFO}]📝 {prompt}[/] [[bold {Colors.ACCENT}]{default}[/]]: "
            else:
                full_prompt = f"[bold {Colors.INFO}]📝 {prompt}[/]: "
            
            while True:
                console.print(full_prompt, end="")
                response = input().strip()
                
                if not response and default:
                    response = default
                
                if not response:
                    continue
                
                if validator:
                    if validator(response):
                        return response
                    else:
                        console.print(f"[{Colors.ERROR}]❌ Invalid input. Please try again.[/]")
                        continue
                
                return response
                
        except KeyboardInterrupt:
            console.print(f"\n[{Colors.ERROR}]Input cancelled by user[/]")
            return None
    
    def show_loading(self, message: str, duration: float = 2.0):
        """Show modern loading animation"""
        with console.status(f"[bold {Colors.CYBER}]{message}[/]", spinner="dots") as status:
            time.sleep(duration)


class AttackDisplay:
    """Specialized display for attack operations with modern styling"""
    
    def __init__(self, attack_type: str, target: str):
        self.attack_type = attack_type
        self.target = target
        self.start_time = time.time()
        self.stats = {
            'requests_sent': 0,
            'responses_received': 0,
            'errors': 0,
            'bytes_sent': 0,
            'bytes_received': 0
        }
        
        self.progress_bar = None
        self.display_thread = None
        self.running = False
        self.modern_cli = ModernCLI()
    
    def start_display(self):
        """Start modern attack display"""
        self.running = True
        
        # Modern banner for attack
        banner_text = f"[bold {Colors.ERROR}]⚡ ATTACK IN PROGRESS ⚡[/]\n"
        banner_text += f"[bold {Colors.CYBER}]{self.attack_type.upper()}[/]"
        console.print(Panel(banner_text, style=f"bold {Colors.PRIMARY}", width=60))
        
        # Target info
        console.print(f"[bold {Colors.ACCENT}]Target:[/] [bold {Colors.WARNING}]{self.target}[/]")
        console.print(f"[bold {Colors.ACCENT}]Started:[/] [bold {Colors.SUCCESS}]{time.strftime('%H:%M:%S')}[/]\n")
        
        self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
        self.display_thread.start()
    
    def update_stats(self, **kwargs):
        """Update attack statistics"""
        for key, value in kwargs.items():
            if key in self.stats:
                self.stats[key] += value
    
    def _display_loop(self):
        """Display loop for attack statistics"""
        while self.running:
            self._render_stats()
            time.sleep(1)
    
    def _render_stats(self):
        """Render modern attack statistics"""
        elapsed = time.time() - self.start_time
        
        # Calculate rates
        req_rate = self.stats['requests_sent'] / elapsed if elapsed > 0 else 0
        resp_rate = self.stats['responses_received'] / elapsed if elapsed > 0 else 0
        error_rate = self.stats['errors'] / elapsed if elapsed > 0 else 0
        
        # Create stats table
        table = Table(title=f"[bold {Colors.CYBER}]Attack Statistics[/]", show_header=False)
        table.add_column("Metric", style=f"bold {Colors.ACCENT}")
        table.add_column("Value", style=f"bold {Colors.SUCCESS}")
        table.add_column("Rate", style=f"dim {Colors.WARNING}")
        
        table.add_row("Requests Sent", f"{self.stats['requests_sent']:,}", f"({req_rate:.1f}/s)")
        table.add_row("Responses Received", f"{self.stats['responses_received']:,}", f"({resp_rate:.1f}/s)")
        table.add_row("Errors", f"{self.stats['errors']:,}", f"({error_rate:.1f}/s)")
        table.add_row("Bytes Sent", format_bytes(self.stats['bytes_sent']), "")
        table.add_row("Bytes Received", format_bytes(self.stats['bytes_received']), "")
        table.add_row("Elapsed Time", format_duration(elapsed), "")
        table.add_row("Success Rate", f"{self._calculate_success_rate():.1f}%", "")
        
        console.clear()
        console.print(table)
    
    def _calculate_success_rate(self) -> float:
        """Calculate success rate"""
        total = self.stats['requests_sent']
        if total == 0:
            return 0.0
        
        successful = self.stats['responses_received']
        return (successful / total) * 100
    
    def stop_display(self):
        """Stop attack display with modern summary"""
        self.running = False
        if self.display_thread:
            self.display_thread.join(timeout=1)
        
        # Show final stats
        elapsed = time.time() - self.start_time
        
        summary_text = f"[bold {Colors.SUCCESS}]✓ Attack Completed[/]\n"
        summary_text += f"[bold {Colors.ACCENT}]Duration:[/] {format_duration(elapsed)}\n"
        summary_text += f"[bold {Colors.ACCENT}]Success Rate:[/] {self._calculate_success_rate():.1f}%"
        
        console.print(Panel(summary_text, style=f"bold {Colors.BORDER}", title="[bold]Final Results[/]"))