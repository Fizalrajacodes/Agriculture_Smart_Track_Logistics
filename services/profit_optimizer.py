"""
=============================================================================
LAYER 5: PROFIT OPTIMIZATION ENGINE
=============================================================================

This engine calculates the monetary value of preserved shelf life.

Formula:
Profit_Saved = Food_Value × (Remaining_Shelf_Life / Max_Shelf_Life)

Returns profit in currency format.

Author: AI Engineering Team
For: Agriculture Smart Track Logistics Hackathon
=============================================================================
"""

from typing import Dict, Optional
import locale

class ProfitOptimizer:
    """
    Profit Optimization Engine for Value Preservation
    
    Calculates the monetary value of preserved shelf life
    and tracks savings from optimal logistics decisions.
    """
    
    # Default configuration
    DEFAULT_MAX_SHELF_LIFE = 14  # days
    DEFAULT_CURRENCY = 'USD'
    
    def __init__(self, currency='USD', max_shelf_life=14):
        """
        Initialize profit optimizer
        
        Args:
            currency: Currency code for formatting
            max_shelf_life: Maximum shelf life in days
        """
        self.currency = currency
        self.max_shelf_life = max_shelf_life
        self.history = []
        
        # Currency symbols
        self.currency_symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
            'INR': '₹',
        }
    
    def calculate_profit_saved(self, food_value, remaining_shelf_life, max_shelf_life=None):
        """
        Calculate profit saved based on remaining shelf life
        
        Formula:
        Profit_Saved = Food_Value × (Remaining_Shelf_Life / Max_Shelf_Life)
        
        Args:
            food_value: Original value of the food shipment
            remaining_shelf_life: Remaining shelf life in days
            max_shelf_life: Maximum possible shelf life (optional, uses default)
            
        Returns:
            Dictionary with profit calculations
        """
        if max_shelf_life is None:
            max_shelf_life = self.max_shelf_life
        
        if max_shelf_life <= 0:
            return {
                'profit_saved': 0,
                'profit_saved_formatted': self._format_currency(0),
                'remaining_percent': 0,
                'wasted_value': food_value,
                'wasted_value_formatted': self._format_currency(food_value)
            }
        
        # Calculate percentage of shelf life remaining
        remaining_percent = (remaining_shelf_life / max_shelf_life) * 100
        
        # Calculate profit saved
        profit_saved = food_value * (remaining_shelf_life / max_shelf_life)
        
        # Calculate wasted value (lost potential)
        wasted_value = food_value - profit_saved
        
        return {
            'profit_saved': round(profit_saved, 2),
            'profit_saved_formatted': self._format_currency(profit_saved),
            'remaining_percent': round(remaining_percent, 1),
            'remaining_days': remaining_shelf_life,
            'max_days': max_shelf_life,
            'food_value': food_value,
            'food_value_formatted': self._format_currency(food_value),
            'wasted_value': round(wasted_value, 2),
            'wasted_value_formatted': self._format_currency(wasted_value)
        }
    
    def calculate_savings_from_optimization(self, original_days_left, optimized_days_left, 
                                            food_value, max_shelf_life=None):
        """
        Calculate savings from logistics optimization decisions
        
        Args:
            original_days_left: Days left if no optimization
            optimized_days_left: Days left with optimization
            food_value: Value of the food
            max_shelf_life: Maximum shelf life
            
        Returns:
            Dictionary with savings from optimization
        """
        if max_shelf_life is None:
            max_shelf_life = self.max_shelf_life
        
        # Original value preserved
        original_profit = food_value * (original_days_left / max_shelf_life)
        
        # Optimized value preserved  
        optimized_profit = food_value * (optimized_days_left / max_shelf_life)
        
        # Savings = difference
        savings = optimized_profit - original_profit
        
        return {
            'savings': round(savings, 2),
            'savings_formatted': self._format_currency(savings),
            'improvement_days': round(optimized_days_left - original_days_left, 2),
            'improvement_percent': round(((optimized_days_left - original_days_left) / original_days_left) * 100, 1) if original_days_left > 0 else 0,
            'original_preserved': round(original_profit, 2),
            'optimized_preserved': round(optimized_profit, 2)
        }
    
    def estimate_daily_value(self, food_value, max_shelf_life=None):
        """
        Estimate the daily value of the shipment
        
        Args:
            food_value: Total value of shipment
            max_shelf_life: Maximum shelf life
            
        Returns:
            Daily value in currency
        """
        if max_shelf_life is None:
            max_shelf_life = self.max_shelf_life
            
        if max_shelf_life <= 0:
            return 0
            
        daily_value = food_value / max_shelf_life
        
        return {
            'daily_value': round(daily_value, 2),
            'daily_value_formatted': self._format_currency(daily_value),
            'hourly_value': round(daily_value / 24, 2),
            'hourly_value_formatted': self._format_currency(daily_value / 24)
        }
    
    def _format_currency(self, amount):
        """
        Format amount as currency
        
        Args:
            amount: Amount to format
            
        Returns:
            Formatted currency string
        """
        symbol = self.currency_symbols.get(self.currency, '$')
        
        if self.currency == 'JPY':
            return f"{symbol}{int(amount):,}"
        else:
            return f"{symbol}{amount:,.2f}"
    
    def add_to_history(self, profit_data):
        """
        Add profit calculation to history
        
        Args:
            profit_data: Profit calculation dictionary
        """
        self.history.append(profit_data)
        
        # Keep history bounded
        if len(self.history) > 100:
            self.history.pop(0)
    
    def get_total_savings(self):
        """
        Get total savings from history
        
        Returns:
            Total savings dictionary
        """
        if not self.history:
            return {
                'total_savings': 0,
                'total_savings_formatted': self._format_currency(0),
                'transactions': 0
            }
        
        total = sum(h.get('profit_saved', 0) for h in self.history)
        
        return {
            'total_savings': round(total, 2),
            'total_savings_formatted': self._format_currency(total),
            'transactions': len(self.history),
            'average_per_transaction': round(total / len(self.history), 2)
        }
    
    def get_grade(self, remaining_percent):
        """
        Get quality grade based on remaining shelf life percentage
        
        Args:
            remaining_percent: Percentage of shelf life remaining
            
        Returns:
            Grade dictionary
        """
        if remaining_percent >= 80:
            return {'grade': 'A', 'label': 'Premium', 'color': '#00cc66'}
        elif remaining_percent >= 60:
            return {'grade': 'B', 'label': 'Good', 'color': '#00d9ff'}
        elif remaining_percent >= 40:
            return {'grade': 'C', 'label': 'Fair', 'color': '#ffaa00'}
        elif remaining_percent >= 20:
            return {'grade': 'D', 'label': 'Poor', 'color': '#ff6600'}
        else:
            return {'grade': 'F', 'label': 'Critical', 'color': '#ff4444'}


# =============================================================================
# HACKATHON DEMO FUNCTION
# =============================================================================

def demo_profit_optimizer():
    """Demo function to test the profit optimizer"""
    optimizer = ProfitOptimizer(currency='USD', max_shelf_life=14)
    
    # Test case 1: Full shelf life
    print("\n" + "="*60)
    print("TEST 1: Fresh shipment - 100% shelf life")
    print("="*60)
    
    result = optimizer.calculate_profit_saved(
        food_value=10000,
        remaining_shelf_life=14,
        max_shelf_life=14
    )
    
    print(f"Food Value: {result['food_value_formatted']}")
    print(f"Remaining: {result['remaining_days']} / {result['max_days']} days ({result['remaining_percent']}%)")
    print(f"\n✓ Profit Preserved: {result['profit_saved_formatted']}")
    print(f"  Wasted Value: {result['wasted_value_formatted']}")
    
    grade = optimizer.get_grade(result['remaining_percent'])
    print(f"  Quality Grade: {grade['grade']} ({grade['label']})")
    
    # Test case 2: Half shelf life
    print("\n" + "="*60)
    print("TEST 2: Partially used - 50% shelf life")
    print("="*60)
    
    result = optimizer.calculate_profit_saved(
        food_value=10000,
        remaining_shelf_life=7,
        max_shelf_life=14
    )
    
    print(f"Food Value: {result['food_value_formatted']}")
    print(f"Remaining: {result['remaining_days']} / {result['max_days']} days ({result['remaining_percent']}%)")
    print(f"\n✓ Profit Preserved: {result['profit_saved_formatted']}")
    print(f"  Wasted Value: {result['wasted_value_formatted']}")
    
    grade = optimizer.get_grade(result['remaining_percent'])
    print(f"  Quality Grade: {grade['grade']} ({grade['label']})")
    
    # Test case 3: Optimization savings
    print("\n" + "="*60)
    print("TEST 3: Optimization savings (rerouting benefit)")
    print("="*60)
    
    # Without optimization: 3 days left
    # With optimization: 6 days left
    savings = optimizer.calculate_savings_from_optimization(
        original_days_left=3,
        optimized_days_left=6,
        food_value=10000,
        max_shelf_life=14
    )
    
    print(f"Original Days Left: {savings['improvement_days'] * -1 + 6} days")
    print(f"Optimized Days Left: {6} days")
    print(f"Improvement: +{savings['improvement_days']} days ({savings['improvement_percent']}%)")
    print(f"\n✓ MONEY SAVED: {savings['savings_formatted']}")
    
    # Test case 4: Daily value estimation
    print("\n" + "="*60)
    print("TEST 4: Time-value analysis")
    print("="*60)
    
    daily = optimizer.estimate_daily_value(10000, 14)
    print(f"Shipment Value: $10,000")
    print(f"Daily Value: {daily['daily_value_formatted']}")
    print(f"Hourly Value: {daily['hourly_value_formatted']}")
    print(f"\n→ Every hour of delay costs: {daily['hourly_value_formatted']}")
    
    # Test case 5: Currency formatting
    print("\n" + "="*60)
    print("TEST 5: Multi-currency support")
    print("="*60)
    
    for curr in ['USD', 'EUR', 'GBP', 'INR']:
        opt = ProfitOptimizer(currency=curr)
        result = opt.calculate_profit_saved(5000, 10, 14)
        print(f"{curr}: {result['profit_saved_formatted']}")


if __name__ == '__main__':
    demo_profit_optimizer()
