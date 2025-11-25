import logging
from datetime import datetime
from typing import List

from src.prediction_market_fund.interfaces.strategy_engine_interface import IStrategyEngine, InvestmentMemo
from src.prediction_market_fund.portfolio_and_risk_service.models import PortfolioState, TradeOrder, Position
from src.data_ingestion_service.market_data import MarketData

logger = logging.getLogger(__name__)

from abc import ABC, abstractmethod

import logging

from datetime import datetime

from typing import List



from src.prediction_market_fund.interfaces.strategy_engine_interface import IStrategyEngine, InvestmentMemo

from src.prediction_market_fund.interfaces.market_data_interface import IMarketDataService, MarketData, MarketPriceData

from src.prediction_market_fund.interfaces.portfolio_risk_interface import IPortfolioManager, IRiskManager, PortfolioState, Position, TradeOrder



logger = logging.getLogger(__name__)



class StrategyEngine(IStrategyEngine):

    """

    Implements the trading strategy, generating investment decisions based on

    market data and portfolio state.

    """



    def __init__(self,

                 market_data_service: IMarketDataService,

                 portfolio_manager: IPortfolioManager,

                 risk_manager: IRiskManager,

                 min_conviction_for_trade: float = 0.7,

                 trade_amount_per_decision: float = 100.0,

                 profit_take_threshold: float = 0.1,

                 stop_loss_threshold: float = 0.05):

        """

        Initializes the StrategyEngine with necessary services and parameters.



        Args:

            market_data_service: Service to fetch market data.

            portfolio_manager: Service to interact with the portfolio.

            risk_manager: Service to assess trade risks.

            min_conviction_for_trade: Minimum conviction level to consider a trade.

            trade_amount_per_decision: Default monetary amount to trade for a new position.

            profit_take_threshold: Percentage gain at which to consider taking profit.

            stop_loss_threshold: Percentage loss at which to consider cutting losses.

        """

        self.market_data_service = market_data_service

        self.portfolio_manager = portfolio_manager

        self.risk_manager = risk_manager

        self.min_conviction_for_trade = min_conviction_for_trade

        self.trade_amount_per_decision = trade_amount_per_decision

        self.profit_take_threshold = profit_take_threshold

        self.stop_loss_threshold = stop_loss_threshold



    def run_strategy(self, market_data: MarketData, portfolio_state: PortfolioState) -> tuple[List[TradeOrder], List[InvestmentMemo]]:

        """

        Executes the trading strategy, including active position management.



        Args:

            market_data: The latest market data (can be ignored if using market_data_service).

            portfolio_state: The current state of the portfolio (can be ignored if using portfolio_manager).



        Returns:

            A tuple containing:

            - A list of proposed TradeOrder objects.

            - A list of corresponding InvestmentMemo objects justifying each trade.

        """

        proposed_orders: List[TradeOrder] = []

        investment_memos: List[InvestmentMemo] = []

        current_time = datetime.now()



        # Fetch latest portfolio state

        current_portfolio_state = self.portfolio_manager.get_portfolio_state()



        # 1. Active Position Management (STRAT-001)

        self._manage_existing_positions(current_portfolio_state, proposed_orders, investment_memos, current_time)



        # 2. Identify new trading opportunities

        self._identify_new_opportunities(current_portfolio_state, proposed_orders, investment_memos, current_time)



        return proposed_orders, investment_memos



    def _manage_existing_positions(self, portfolio_state: PortfolioState,

                                   proposed_orders: List[TradeOrder], investment_memos: List[InvestmentMemo],

                                   current_time: datetime):

        """

        Manages existing positions, looking for profit-taking or stop-loss opportunities.

        """

        for position in portfolio_state.positions.values():

            market_price_data: MarketPriceData = self.market_data_service.get_market_price(position.market_id, position.asset)

            if market_price_data is None:

                logger.warning(f"No market price data for position {position.market_id}/{position.asset}. Skipping active management.")

                continue



            current_price = market_price_data.price

            cost_basis = position.cost_basis

            

            if cost_basis == 0: # Avoid division by zero if cost_basis is 0

                logger.warning(f"Cost basis for position {position.market_id}/{position.asset} is zero. Skipping active management for this position.")

                continue



            unrealized_pnl_percentage = (current_price - cost_basis) / cost_basis



            # Profit-taking

            if unrealized_pnl_percentage >= self.profit_take_threshold:

                quantity_to_sell = position.quantity

                memo = self._generate_investment_memo(

                    current_time, position.market_id, "SELL", position.asset, quantity_to_sell, current_price,

                    0.9, 0.9, f"Profit-taking: Price {current_price} is {unrealized_pnl_percentage:.2%} above cost basis {cost_basis}. (STRAT-001)",

                    ["internal_strategy_logic"]

                )

                trade_order = TradeOrder(position.market_id, "SELL", position.asset, quantity_to_sell, current_price, current_time)

                if self.risk_manager.assess_trade_risk(trade_order, portfolio_state):

                    proposed_orders.append(trade_order)

                    investment_memos.append(memo)

                    logger.info(f"Profit-taking for {position.market_id}/{position.asset}. Selling {quantity_to_sell} at {current_price}.")

                else:

                    logger.warning(f"Risk manager rejected profit-taking trade for {position.market_id}/{position.asset}.")





            # Stop-loss

            elif unrealized_pnl_percentage <= -self.stop_loss_threshold:

                quantity_to_sell = position.quantity

                memo = self._generate_investment_memo(

                    current_time, position.market_id, "SELL", position.asset, quantity_to_sell, current_price,

                    0.1, 0.1, f"Stop-loss: Price {current_price} is {abs(unrealized_pnl_percentage):.2%} below cost basis {cost_basis}. Thesis invalidated. (STRAT-001)",

                    ["internal_strategy_logic"]

                )

                trade_order = TradeOrder(position.market_id, "SELL", position.asset, quantity_to_sell, current_price, current_time)

                if self.risk_manager.assess_trade_risk(trade_order, portfolio_state):

                    proposed_orders.append(trade_order)

                    investment_memos.append(memo)

                    logger.warning(f"Stop-loss for {position.market_id}/{position.asset}. Selling {quantity_to_sell} at {current_price}.")

                else:

                    logger.warning(f"Risk manager rejected stop-loss trade for {position.market_id}/{position.asset}.")



    def _identify_new_opportunities(self, portfolio_state: PortfolioState,

                                    proposed_orders: List[TradeOrder], investment_memos: List[InvestmentMemo],

                                    current_time: datetime):

        """

        Identifies new trading opportunities based on market data.

        """

        all_market_data = self.market_data_service.get_all_market_data()

        for market in all_market_data:

            # Placeholder for new opportunity identification logic

            # This is a highly simplified placeholder for actual EV calculation

            calculated_ev, conviction = self._calculate_ev_and_conviction(market)



            if conviction >= self.min_conviction_for_trade:

                # Assuming we are always interested in the 'yes' asset for simplicity in this placeholder

                asset_to_trade = 'yes'

                market_price_data = self.market_data_service.get_market_price(market.market_id, asset_to_trade)



                if market_price_data is None:

                    logger.warning(f"No market price data for market {market.market_id}/{asset_to_trade}. Skipping new opportunity for this market.")

                    continue



                entry_price = market_price_data.price



                # Simple example: if EV > current_price and we don't have a position

                # This logic is simplified; a real strategy would be more nuanced.

                if calculated_ev > entry_price and not portfolio_state.has_position(market.market_id, asset_to_trade):

                    quantity_to_buy = self.trade_amount_per_decision / entry_price # Buy a fixed dollar amount worth



                    memo = self._generate_investment_memo(

                        current_time, market.market_id, "BUY", asset_to_trade, quantity_to_buy, entry_price,

                        calculated_ev, conviction,

                        f"New opportunity: Calculated EV for '{asset_to_trade}' is {calculated_ev:.2f} (conviction: {conviction:.2f}), above current price {entry_price:.2f}. (EXP-001)",

                        [f"polymarket_data_for_{market.market_id}"]

                    )

                    trade_order = TradeOrder(market.market_id, "BUY", asset_to_trade, quantity_to_buy, entry_price, current_time)



                    if self.risk_manager.assess_trade_risk(trade_order, portfolio_state):

                        proposed_orders.append(trade_order)

                        investment_memos.append(memo)

                        logger.info(f"New opportunity for {market.market_id}/{asset_to_trade}. Buying {quantity_to_buy} at {entry_price}.")

                    else:

                        logger.warning(f"Risk manager rejected new opportunity trade for {market.market_id}/{asset_to_trade}.")



    def _calculate_ev_and_conviction(self, market: MarketData) -> tuple[float, float]:

        """

        Placeholder for Expected Value (EV) and conviction calculation.

        This method would contain the core prediction logic.

        For demonstration, a simplified calculation is used.

        """

        # Example: EV is simply the current price plus a small factor based on volume

        # Conviction is higher for higher volume markets

        ev = market.current_price + (market.volume_24h / (market.volume_24h + 1000)) * 0.1

        conviction = 0.5 + (market.volume_24h / (market.volume_24h + 5000)) * 0.5

        return ev, conviction



    def _generate_investment_memo(self, timestamp: datetime, market_id: str, action: str, asset: str,

                                 quantity: float, price: float, calculated_ev: float, conviction: float,

                                 rationale: str, data_sources: List[str]) -> InvestmentMemo:

        """

        Generates an InvestmentMemo for a trade decision. (EXP-001)

        """

        return InvestmentMemo(

            timestamp=timestamp,

            market_id=market_id,

            action=action,

            asset=asset,

            quantity=quantity,

            price=price,

            calculated_ev=calculated_ev,

            conviction=conviction,

            rationale=rationale,

            data_sources=data_sources

        )