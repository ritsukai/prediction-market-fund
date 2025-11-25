from typing import List, Dict, Any
from src.portfolio_risk_interface import IRiskManager
from src.models import Position, MarketData

class RiskManager(IRiskManager):
    MAX_POSITION_SIZE_RATIO = 0.10  # Cap max position size at 10% of NAV (RISK-001)
    MAX_SECTOR_EXPOSURE_RATIO = 0.30 # Limit sector exposure to 30% of NAV (RISK-001)

    def __init__(self, get_nav_func):
        self.get_nav = get_nav_func # Function to get current NAV from PortfolioManager
        self.sector_mapping: Dict[str, str] = {
            # Example mapping, this would be more dynamic in a real system
            "market_A": "US Politics",
            "market_B": "Crypto Events",
            "market_C": "US Politics"
        }

    def assess_risk(self, portfolio: List[Position]) -> Dict[str, Any]:
        # Placeholder for comprehensive risk assessment
        current_nav = self.get_nav()
        total_portfolio_value = sum(pos.quantity * pos.cost_basis for pos in portfolio) # Using cost_basis for assessment, could be market value
        
        position_exposure: Dict[str, float] = {}
        sector_exposure: Dict[str, float] = {}

        for position in portfolio:
            market_value = position.quantity * position.cost_basis # Simplified for now
            position_exposure[position.market_id] = market_value / current_nav

            sector = self.sector_mapping.get(position.market_id, "Other")
            sector_exposure[sector] = sector_exposure.get(sector, 0.0) + (market_value / current_nav)

        over_max_position_size = {
            mid: exp for mid, exp in position_exposure.items() if exp > self.MAX_POSITION_SIZE_RATIO
        }
        over_max_sector_exposure = {
            sector: exp for sector, exp in sector_exposure.items() if exp > self.MAX_SECTOR_EXPOSURE_RATIO
        }

        return {
            "current_nav": current_nav,
            "position_exposure": position_exposure,
            "sector_exposure": sector_exposure,
            "over_max_position_size": over_max_position_size,
            "over_max_sector_exposure": over_max_sector_exposure,
            "risk_flags": bool(over_max_position_size or over_max_sector_exposure)
        }

    def check_market_exposure(self, market_id: str, proposed_trade_amount: float, current_positions: List[Position]) -> bool:
        current_nav = self.get_nav()
        
        # Check max position size (RISK-001)
        current_position_value = next(
            (pos.quantity * pos.cost_basis for pos in current_positions if pos.market_id == market_id),
            0.0
        )
        # Assuming proposed_trade_amount is in terms of value, not quantity
        projected_position_value = current_position_value + proposed_trade_amount
        if projected_position_value / current_nav > self.MAX_POSITION_SIZE_RATIO:
            return False

        # Check sector exposure (RISK-001)
        sector = self.sector_mapping.get(market_id, "Other")
        current_sector_value = sum(
            pos.quantity * pos.cost_basis 
            for pos in current_positions 
            if self.sector_mapping.get(pos.market_id, "Other") == sector
        )
        projected_sector_value = current_sector_value + proposed_trade_amount
        if projected_sector_value / current_nav > self.MAX_SECTOR_EXPOSURE_RATIO:
            return False
            
        return True
