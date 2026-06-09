# ========================================
# 风险管理模块
# ========================================

import logging

logger = logging.getLogger(__name__)

class RiskManager:
    """风险管理器"""
    
    def __init__(self, config):
        """初始化风险管理器"""
        self.config = config
        self.max_daily_loss = config.get("max_daily_loss", 100)
        self.daily_loss = 0.0
        self.daily_win = 0.0
    
    def check_daily_loss_limit(self):
        """检查日亏损限制"""
        if self.daily_loss >= self.max_daily_loss:
            logger.warning(f"已达到日亏损限制: ${self.daily_loss:.2f} >= ${self.max_daily_loss:.2f}")
            return False
        return True
    
    def check_position_size(self, lot_size):
        """检查交易量是否合理"""
        # 这里可以根据账户余额动态调整交易量
        # 简单起见，这里只检查是否为正数
        if lot_size <= 0:
            logger.error(f"无效的交易量: {lot_size}")
            return False
        return True
    
    def check_spread(self, spread, max_spread=0.5):
        """检查点差是否过大"""
        if spread > max_spread:
            logger.warning(f"点差过大: {spread:.4f}, 跳过交易")
            return False
        return True
    
    def update_daily_loss(self, profit_loss):
        """更新日亏损"""
        if profit_loss < 0:
            self.daily_loss += abs(profit_loss)
        else:
            self.daily_win += profit_loss
        
        logger.info(f"日收益: ${self.daily_win:.2f}, 日亏损: ${self.daily_loss:.2f}")
    
    def reset_daily_stats(self):
        """重置日统计"""
        self.daily_loss = 0.0
        self.daily_win = 0.0
        logger.info("日统计已重置")
    
    def get_risk_status(self):
        """获取风险状态"""
        return {
            "daily_loss": self.daily_loss,
            "daily_win": self.daily_win,
            "max_daily_loss": self.max_daily_loss,
            "remaining_loss_limit": self.max_daily_loss - self.daily_loss,
            "can_trade": self.check_daily_loss_limit(),
        }
    
    def print_risk_status(self):
        """打印风险状态"""
        status = self.get_risk_status()
        logger.info("=" * 50)
        logger.info("风险管理状态")
        logger.info("=" * 50)
        logger.info(f"日赢利: ${status['daily_win']:.2f}")
        logger.info(f"日亏损: ${status['daily_loss']:.2f}")
        logger.info(f"日亏损限制: ${status['max_daily_loss']:.2f}")
        logger.info(f"剩余亏损额度: ${status['remaining_loss_limit']:.2f}")
        logger.info(f"可交易: {status['can_trade']}")
        logger.info("=" * 50)
