# ========================================
# MT5 连接模块
# ========================================

import MetaTrader5 as mt5
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MT5Connector:
    """MT5平台连接器"""
    
    def __init__(self, account_info):
        """初始化MT5连接"""
        self.account_info = account_info
        self.connected = False
        
    def connect(self):
        """连接到MT5"""
        try:
            # 初始化MT5连接
            if not mt5.initialize():
                logger.error("MT5初始化失败")
                return False
            
            self.connected = True
            logger.info(f"MT5连接成功 - 版本: {mt5.version()}")
            return True
            
        except Exception as e:
            logger.error(f"MT5连接错误: {str(e)}")
            return False
    
    def disconnect(self):
        """断开MT5连接"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("MT5已断开连接")
    
    def get_symbol_info(self, symbol):
        """获取品种信息"""
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.error(f"找不到品种: {symbol}")
                return None
            return symbol_info
        except Exception as e:
            logger.error(f"获取品种信息失败: {str(e)}")
            return None
    
    def get_current_price(self, symbol):
        """获取当前价格"""
        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.warning(f"无法获取{symbol}的价格")
                return None
            return {
                "bid": tick.bid,      # 买入价
                "ask": tick.ask,      # 卖出价
                "time": tick.time,
            }
        except Exception as e:
            logger.error(f"获取价格失败: {str(e)}")
            return None
    
    def get_account_info(self):
        """获取账户信息"""
        try:
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("无法获取账户信息")
                return None
            return {
                "balance": account_info.balance,           # 账户余额
                "equity": account_info.equity,             # 账户净值
                "free_margin": account_info.margin_free,   # 可用保证金
                "used_margin": account_info.margin,        # 已用保证金
            }
        except Exception as e:
            logger.error(f"获取账户信息失败: {str(e)}")
            return None
    
    def get_open_positions(self):
        """获取所有开仓"""
        try:
            positions = mt5.positions_get()
            if positions is None:
                return []
            return positions
        except Exception as e:
            logger.error(f"获取持仓失败: {str(e)}")
            return []
    
    def get_klines(self, symbol, timeframe, bars_count):
        """获取K线数据"""
        try:
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars_count)
            if rates is None:
                logger.warning(f"���法获取{symbol}的K线数据")
                return None
            return rates
        except Exception as e:
            logger.error(f"获取K线数据失败: {str(e)}")
            return None
