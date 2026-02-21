"""
Agriculture Smart Track Logistics - Advanced Services Layer
============================================================

This package contains all the intelligent logistics engines:
- Hybrid Physics + ML Engine (Layer 2)
- Future Prediction Engine (Layer 3)
- Survival Margin Optimizer (Layer 4)
- Profit Optimization Engine (Layer 5)
- Driver Recommendation Engine (Layer 6)
- Countdown Timer Service (Layer 7)
- Transport Trust Score (Layer 8)
- Liability Engine (Layer 9)
- Explainable AI Engine (Layer 10)

Each service is modular and can be used independently.

Author: AI Engineering Team
For: Agriculture Smart Track Logistics Hackathon
"""

# Import all services for easy access
from .hybrid_engine import HybridEngine
from .future_prediction import FuturePredictionEngine
from .survival_optimizer import SurvivalMarginOptimizer
from .profit_optimizer import ProfitOptimizer
from .driver_recommender import DriverRecommender
from .countdown_timer import CountdownTimer
from .trust_score import TrustScoreEngine
from .liability_engine import LiabilityEngine
from .explainable_ai import ExplainableAI

__all__ = [
    'HybridEngine',
    'FuturePredictionEngine',
    'SurvivalMarginOptimizer',
    'ProfitOptimizer',
    'DriverRecommender',
    'CountdownTimer',
    'TrustScoreEngine',
    'LiabilityEngine',
    'ExplainableAI'
]

__version__ = '2.0.0'
__author__ = 'Agriculture Smart Track Logistics Team'
