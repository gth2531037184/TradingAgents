# ========================================
# 头皮交易策略 (Scalping Strategy)
# ========================================

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ScalpingStrategy:
    """头皮交易策略 - 快速进出，及时获利"""
    
    def __init__(self, order_manager, config):
        """初始化策略"""
        self.order_manager = order_manager
        self.config = config
        self.symbol = config["symbol"]
        self.lot_size = config["lot_size"]
        self.take_profit = config["take_profit"]
        self.stop_loss = config["stop_loss"]
        self.max_positions = config.get("max_positions", 1)
        
        # 统计信息
        self.trades_today = 0
        self.wins = 0
        self.losses = 0
        self.total_profit = 0.0
        
    def check_trading_hours(self, trading_hours_config):
        """检查是否在交易时间内"""
        if not trading_hours_config.get("enabled", False):
            return True
        
        current_hour = datetime.now().hour
        start_hour = trading_hours_config.get("start_hour", 0)
        end_hour = trading_hours_config.get("end_hour", 23)
        
        return start_hour <= current_hour <= end_hour
    
    def analyze_market(self, price_info):
        """分析市场 - 简单的价格变化分析"""
        if price_info is None:
            return None
        
        bid = price_info["bid"]
        ask = price_info["ask"]
        spread = ask - bid
        
        # 返回市场信息
        return {
            "bid": bid,
            "ask": ask,
            "spread": spread,
            "mid_price": (bid + ask) / 2,
        }
    
    def generate_signal(self, market_info, last_prices=None):
        """生成交易信号
        
        简单策略：
        - 价格上升 -> 买入信号 (BUY)
        - 价格下降 -> 卖出信号 (SELL)
        - 无明显方向 -> 不交易 (HOLD)
        """
        if market_info is None:
            return "HOLD"
        
        if last_prices is None or len(last_prices) < 2:
            return "HOLD"
        
        # 比较最后两个价格
        current_price = market_info["mid_price"]
        previous_price = last_prices[-1]
        
        # 简单的趋势判断
        price_change = current_price - previous_price
        
        if price_change > 0.01:  # 价格上升
            return "BUY"
        elif price_change < -0.01:  # 价格下降
            return "SELL"
        else:  # 无明显方向
            return "HOLD"
    
    def execute_buy(self):
        """执行买入"""
        try:
            # 检查是否已达到最大持仓数
            open_positions = self.order_manager.get_open_positions()
            if len(open_positions) >= self.max_positions:
                logger.warning("已达到最大持仓数，跳过买入")
                return False
            
            # 发送买入订单
            order_id = self.order_manager.send_buy_order(
                self.symbol,
                self.lot_size,
                self.stop_loss,
                self.take_profit
            )
            
            if order_id is not None:
                self.trades_today += 1
                logger.info(f"执行买入 - 订单ID: {order_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"执行买入异常: {str(e)}")
            return False
    
    def execute_sell(self):
        """执行卖出"""
        try:
            # 检查是否已达到最大持仓数
            open_positions = self.order_manager.get_open_positions()
            if len(open_positions) >= self.max_positions:
                logger.warning("已达到最大持仓数，跳过卖出")
                return False
            
            # 发送卖出订单
            order_id = self.order_manager.send_sell_order(
                self.symbol,
                self.lot_size,
                self.stop_loss,
                self.take_profit
            )
            
            if order_id is not None:
                self.trades_today += 1
                logger.info(f"执行卖出 - 订单ID: {order_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"执行卖出异常: {str(e)}")
            return False
    
    def execute_strategy(self, price_info, last_prices, trading_hours_config):
        """执行交易策略"""
        
        # 1. 检查交易时间
        if not self.check_trading_hours(trading_hours_config):
            logger.debug("不在交易时间内，跳过")
            return False
        
        # 2. 分析市场
        market_info = self.analyze_market(price_info)
        if market_info is None:
            return False
        
        # 3. 生成信号
        signal = self.generate_signal(market_info, last_prices)
        logger.info(f"交易信号: {signal}")
        
        # 4. 执行交易
        if signal == "BUY":
            return self.execute_buy()
        elif signal == "SELL":
            return self.execute_sell()
        else:
            return False
    
    def print_statistics(self):
        """打印统计信息"""
        logger.info("=" * 50)
        logger.info("交易统计信息")
        logger.info("=" * 50)
        logger.info(f"今日交易次数: {self.trades_today}")
        logger.info(f"获胜次数: {self.wins}")
        logger.info(f"亏损次数: {self.losses}")
        logger.info(f"总利润: ${self.total_profit:.2f}")
        if self.trades_today > 0:
            win_rate = (self.wins / self.trades_today) * 100
            logger.info(f"胜率: {win_rate:.2f}%")
        logger.info("=" * 50)
