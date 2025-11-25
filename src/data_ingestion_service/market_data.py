from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

@dataclass
class MarketData:
    """
    Standardized MarketData object as defined in ARCHITECTURE.md.
    Includes market probabilities, timestamps, and source-verified information.
    """
    market_id: str
    timestamp: datetime
    probability: float
    source_name: str
    source_integrity_score: float  # Score from 0.0 to 1.0, indicating source reliability
    raw_data: Optional[Dict[str, Any]] = None  # Optional field for raw data from the source
