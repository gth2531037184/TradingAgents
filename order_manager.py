# ========================================
# 订单管理模块
# ========================================

import MetaTrader5 as mt5
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class OrderManager:
    """订单管理器"""
    
    def __init__(self, mt5_connector, config):
        """初始化订单管理器"""
        self.connector = mt5_connector
        self.config = config
        self.open_orders = {}
    
    def send_buy_order(self, symbol, lot_size, stop_loss, take_profit):
        """发送买入订单"""
        try:
            price_info = self.connector.get_current_price(symbol)
            if price_info is None:
                logger.error("无法获取价格，买入订单失败")
                return None
            
            # 计算止损和止盈价格
            entry_price = price_info["ask"]
            sl_price = entry_price - stop_loss
            tp_price = entry_price + take_profit
            
            # 准备订单请求
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": mt5.ORDER_TYPE_BUY,
                "price": entry_price,
                "sl": sl_price,
                "tp": tp_price,
                "deviation": 20,
                "magic": 12345,
                "comment": "HFT Scalping Buy",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
            
            # 发送订单
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"买入订单失败: {result.comment}")
                return None
            
            logger.info(f"买入订单成功 - 数量: {lot_size}, 价格: {entry_price:.2f}")
            self.open_orders[result.order] = {
                "symbol": symbol,
                "type": "BUY",
                "volume": lot_size,
                "entry_price": entry_price,
                "sl": sl_price,
                "tp": tp_price,
                "time": datetime.now(),
            }
            
            return result.order
            
        except Exception as e:
            logger.error(f"发送买入订单异常: {str(e)}")
            return None
    
    def send_sell_order(self, symbol, lot_size, stop_loss, take_profit):
        """发送卖出订单"""
        try:
            price_info = self.connector.get_current_price(symbol)
            if price_info is None:
                logger.error("无法获取价格，卖出订单失败")
                return None
            
            # 计算止损和止盈价格
            entry_price = price_info["bid"]
            sl_price = entry_price + stop_loss
            tp_price = entry_price - take_profit
            
            # 准备订单请求
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": mt5.ORDER_TYPE_SELL,
                "price": entry_price,
                "sl": sl_price,
                "tp": tp_price,
                "deviation": 20,
                "magic": 12345,
                "comment": "HFT Scalping Sell",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
            
            # 发送订单
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"卖出订单失败: {result.comment}")
                return None
            
            logger.info(f"卖出订单成功 - 数量: {lot_size}, 价格: {entry_price:.2f}")
            self.open_orders[result.order] = {
                "symbol": symbol,
                "type": "SELL",
                "volume": lot_size,
                "entry_price": entry_price,
                "sl": sl_price,
                "tp": tp_price,
                "time": datetime.now(),
            }
            
            return result.order
            
        except Exception as e:
            logger.error(f"发送卖出订单异常: {str(e)}")
            return None
    
    def close_position(self, position_id, symbol, volume):
        """平仓订单"""
        try:
            position = mt5.positions_get(ticket=position_id)
            if not position:
                logger.warning(f"找不到持仓: {position_id}")
                return False
            
            # 获取当前价格
            price_info = self.connector.get_current_price(symbol)
            if price_info is None:
                logger.error("无法获取价格，平仓失败")
                return False
            
            # 判断持仓方向
            if position[0].type == 0:  # 买入持仓
                close_price = price_info["bid"]
                order_type = mt5.ORDER_TYPE_SELL
            else:  # 卖出持仓
                close_price = price_info["ask"]
                order_type = mt5.ORDER_TYPE_BUY
            
            # 准备平仓请求
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": order_type,
                "position": position_id,
                "price": close_price,
                "deviation": 20,
                "magic": 12345,
                "comment": "HFT Scalping Close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
            
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"平仓失败: {result.comment}")
                return False
            
            logger.info(f"平仓成功 - 持仓ID: {position_id}, 数量: {volume}")
            return True
            
        except Exception as e:
            logger.error(f"平仓异常: {str(e)}")
            return False
    
    def get_open_positions(self):
        """获取所有开仓"""
        return self.connector.get_open_positions()
    
    def update_order_info(self, position_id, stop_loss=None, take_profit=None):
        """更新止损止盈"""
        try:
            if position_id in self.open_orders:
                if stop_loss:
                    self.open_orders[position_id]["sl"] = stop_loss
                if take_profit:
                    self.open_orders[position_id]["tp"] = take_profit
                return True
            return False
        except Exception as e:
            logger.error(f"更新订单信息失败: {str(e)}")
            return False
