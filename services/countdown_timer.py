"""
=============================================================================
LAYER 7: COUNTDOWN TIMER
=============================================================================

This service converts shelf-life days into a human-readable countdown.

Converts Days_Left into:
- Hours + Minutes countdown

Display format:
FOOD EXPIRING IN:
X hr Y min

Auto-update every second (via frontend).

Author: AI Engineering Team
For: Agriculture Smart Track Logistics Hackathon
=============================================================================
"""

from typing import Dict, Optional
import time

class CountdownTimer:
    """
    Countdown Timer Service for Shelf-Life Display
    
    Converts remaining shelf life in days to hours and minutes
    for real-time countdown display.
    """
    
    # Constants
    HOURS_PER_DAY = 24
    MINUTES_PER_HOUR = 60
    SECONDS_PER_MINUTE = 60
    
    def __init__(self):
        """Initialize the countdown timer"""
        self.start_time = None
        self.start_days_left = None
        
    def convert_days_to_countdown(self, days_left: float) -> Dict:
        """
        Convert days to countdown format
        
        Args:
            days_left: Remaining shelf life in days
            
        Returns:
            Dictionary with countdown components
        """
        if days_left <= 0:
            return {
                'days': 0,
                'hours': 0,
                'minutes': 0,
                'seconds': 0,
                'total_seconds': 0,
                'display': 'EXPIRED',
                'display_verbose': 'PRODUCT EXPIRED',
                'urgency': 'CRITICAL'
            }
        
        # Calculate total hours
        total_hours = days_left * self.HOURS_PER_DAY
        
        # Extract whole days, hours, minutes, seconds
        days = int(days_left)
        remaining_hours = total_hours - (days * self.HOURS_PER_DAY)
        hours = int(remaining_hours)
        remaining_minutes = (remaining_hours - hours) * self.MINUTES_PER_HOUR
        minutes = int(remaining_minutes)
        seconds = int((remaining_minutes - minutes) * self.SECONDS_PER_MINUTE)
        
        # Determine urgency level
        urgency = self._determine_urgency(days, hours)
        
        # Format display strings
        if days > 0:
            display = f"{days}d {hours}h {minutes}m"
            display_verbose = f"FOOD EXPIRING IN: {days} day {hours} hr {minutes} min"
        elif hours > 0:
            display = f"{hours}h {minutes}m"
            display_verbose = f"FOOD EXPIRING IN: {hours} hr {minutes} min"
        else:
            display = f"{minutes}m {seconds}s"
            display_verbose = f"FOOD EXPIRING IN: {minutes} min {seconds} sec"
        
        return {
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'total_hours': round(total_hours, 2),
            'total_minutes': round(total_hours * 60, 1),
            'total_seconds': int(total_hours * 3600),
            'display': display,
            'display_verbose': display_verbose,
            'urgency': urgency,
            'progress_percent': min(100, (days_left / 14) * 100)  # Assuming 14 day max
        }
    
    def _determine_urgency(self, days: int, hours: int) -> str:
        """Determine urgency level based on remaining time"""
        total_hours = days * 24 + hours
        
        if total_hours < 24:  # Less than 1 day
            return 'CRITICAL'
        elif total_hours < 72:  # Less than 3 days
            return 'WARNING'
        else:
            return 'NORMAL'
    
    def get_countdown_string(self, days_left: float, format: str = 'short') -> str:
        """
        Get countdown as formatted string
        
        Args:
            days_left: Remaining shelf life in days
            format: 'short' or 'verbose'
            
        Returns:
            Formatted countdown string
        """
        countdown = self.convert_days_to_countdown(days_left)
        
        if format == 'verbose':
            return countdown['display_verbose']
        return countdown['display']
    
    def get_progress_bar(self, days_left: float, max_days: float = 14, width: int = 20) -> str:
        """
        Generate ASCII progress bar
        
        Args:
            days_left: Remaining shelf life
            max_days: Maximum shelf life
            width: Width of progress bar
            
        Returns:
            Progress bar string
        """
        if max_days <= 0:
            return '[' + '█' * width + '] 0%'
        
        percent = min(100, (days_left / max_days) * 100)
        filled = int((percent / 100) * width)
        empty = width - filled
        
        # Choose bar character based on percent
        if percent > 60:
            bar_char = '█'
            color = 'green'
        elif percent > 30:
            bar_char = '▓'
            color = 'yellow'
        else:
            bar_char = '▒'
            color = 'red'
        
        bar = '█' * filled + '░' * empty
        
        return f"[{bar}] {percent:.0f}%"
    
    def start_countdown(self, days_left: float):
        """
        Start a countdown timer
        
        Args:
            days_left: Initial days left
        """
        self.start_time = time.time()
        self.start_days_left = days_left
        
    def get_elapsed(self) -> Optional[float]:
        """
        Get elapsed time since countdown started
        
        Returns:
            Elapsed time in seconds, or None if not started
        """
        if self.start_time is None:
            return None
        return time.time() - self.start_time
    
    def get_remaining(self) -> Optional[float]:
        """
        Get remaining time based on elapsed time
        
        Returns:
            Remaining days, or None if not started
        """
        if self.start_time is None or self.start_days_left is None:
            return None
            
        elapsed = self.get_elapsed()
        elapsed_days = elapsed / (24 * 3600)  # Convert seconds to days
        
        remaining = self.start_days_left - elapsed_days
        return max(0, remaining)
    
    def format_countdown_components(self, days_left: float) -> Dict:
        """
        Get countdown components for frontend display
        
        Args:
            days_left: Remaining shelf life in days
            
        Returns:
            Dictionary with all display components
        """
        countdown = self.convert_days_to_countdown(days_left)
        
        # Add progress bar
        countdown['progress_bar'] = self.get_progress_bar(days_left)
        
        # Add CSS class for styling
        urgency_classes = {
            'CRITICAL': 'countdown-critical',
            'WARNING': 'countdown-warning', 
            'NORMAL': 'countdown-normal'
        }
        countdown['css_class'] = urgency_classes.get(countdown['urgency'], 'countdown-normal')
        
        return countdown
    
    def get_estimated_expiry_time(self, days_left: float) -> Dict:
        """
        Get estimated expiry timestamp
        
        Args:
            days_left: Remaining shelf life in days
            
        Returns:
            Dictionary with expiry time info
        """
        import datetime
        
        # Current time
        now = datetime.datetime.now()
        
        # Add remaining time
        hours_to_add = days_left * 24
        expiry = now + datetime.timedelta(hours=hours_to_add)
        
        return {
            'estimated_expiry': expiry.isoformat(),
            'estimated_expiry_formatted': expiry.strftime('%Y-%m-%d %H:%M:%S'),
            'countdown_hours': round(hours_to_add, 1),
            'countdown_days': round(days_left, 2)
        }


# =============================================================================
# HACKATHON DEMO FUNCTION
# =============================================================================

def demo_countdown_timer():
    """Demo function to test the countdown timer"""
    timer = CountdownTimer()
    
    # Test case 1: Several days left
    print("\n" + "="*60)
    print("TEST 1: 10 days remaining")
    print("="*60)
    
    result = timer.convert_days_to_countdown(10.5)
    print(f"Days Left: 10.5")
    print(f"\nCountdown: {result['display']}")
    print(f"Verbose: {result['display_verbose']}")
    print(f"Breakdown: {result['days']} days, {result['hours']} hours, {result['minutes']} minutes, {result['seconds']} seconds")
    print(f"Urgency: {result['urgency']}")
    print(f"Progress: {result['progress_percent']:.0f}%")
    print(f"\nProgress Bar: {timer.get_progress_bar(10.5)}")
    
    # Test case 2: Less than a day
    print("\n" + "="*60)
    print("TEST 2: Less than 1 day remaining")
    print("="*60)
    
    result = timer.convert_days_to_countdown(0.75)
    print(f"Days Left: 0.75")
    print(f"\nCountdown: {result['display']}")
    print(f"Verbose: {result['display_verbose']}")
    print(f"Total Hours: {result['total_hours']}")
    print(f"Urgency: {result['urgency']}")
    
    # Test case 3: Critical - hours only
    print("\n" + "="*60)
    print("TEST 3: Critical - 12 hours remaining")
    print("="*60)
    
    result = timer.convert_days_to_countdown(0.5)
    print(f"Days Left: 0.5")
    print(f"\nCountdown: {result['display']}")
    print(f"Verbose: {result['display_verbose']}")
    print(f"Breakdown: {result['hours']} hours, {result['minutes']} minutes")
    print(f"Urgency: {result['urgency']}")
    
    # Test case 4: Minutes only
    print("\n" + "="*60)
    print("TEST 4: Critical - 45 minutes remaining")
    print("="*60)
    
    result = timer.convert_days_to_countdown(0.03125)  # ~45 minutes
    print(f"Days Left: 0.03125 (~45 minutes)")
    print(f"\nCountdown: {result['display']}")
    print(f"Verbose: {result['display_verbose']}")
    
    # Test case 5: Expired
    print("\n" + "="*60)
    print("TEST 5: Product expired")
    print("="*60)
    
    result = timer.convert_days_to_countdown(0)
    print(f"Days Left: 0")
    print(f"\nDisplay: {result['display']}")
    print(f"Verbose: {result['display_verbose']}")
    print(f"Urgency: {result['urgency']}")
    
    # Test case 6: Frontend components
    print("\n" + "="*60)
    print("TEST 6: Frontend component format")
    print("="*60)
    
    result = timer.format_countdown_components(5.5)
    print(f"Days Left: 5.5")
    print(f"Display: {result['display']}")
    print(f"CSS Class: {result['css_class']}")
    print(f"Progress Bar: {result['progress_bar']}")
    print(f"Total Seconds: {result['total_seconds']}")
    
    # Test case 7: Expiry estimation
    print("\n" + "="*60)
    print("TEST 7: Expiry time estimation")
    print("="*60)
    
    expiry = timer.get_estimated_expiry_time(3.5)
    print(f"Current shelf life: 3.5 days")
    print(f"Estimated Expiry: {expiry['estimated_expiry_formatted']}")


if __name__ == '__main__':
    demo_countdown_timer()
