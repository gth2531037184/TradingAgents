# ========================================
# MT5 高频交易系统 - 主程序
# ========================================

import logging
import time
from datetime import datetime, timedelta

# 导入配置和各个模块
from config import TRADING_CONFIG, TRADING_HOURS, ACCOUNT_INFO, LOG_CONFIG
from mt5_connector import MT5Connector
from order_manager import OrderManager
from scalping_strategy import ScalpingStrategy
from risk_manager import RiskManager

# ========================================
# 配置日志
# ========================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_CONFIG["log_file"]),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========================================
# 主交易类
# ========================================

class TradingAgent:
    """高频���易代理"""
    
    def __init__(self):
        """初始化交易代理"""
        logger.info("初始化交易代理...")
        
        # 初始化各个组件
        self.mt5_connector = MT5Connector(ACCOUNT_INFO)
        self.order_manager = OrderManager(self.mt5_connector, TRADING_CONFIG)
        self.strategy = ScalpingStrategy(self.order_manager, TRADING_CONFIG)
        self.risk_manager = RiskManager(TRADING_CONFIG)
        
        # 交易状态
        self.running = False
        self.last_prices = []
        self.max_price_history = 100  # 保留最后100个价格
        
    def start(self):
        """启动交易系统"""
        logger.info("启动交易系统...")
        
        # 连接到MT5
        if not self.mt5_connector.connect():
            logger.error("无法连接到MT5，退出")
            return False
        
        # 获取账户信息
        account_info = self.mt5_connector.get_account_info()
        if account_info:
            logger.info(f"账户余额: ${account_info['balance']:.2f}")
            logger.info(f"账户净值: ${account_info['equity']:.2f}")
            logger.info(f"可用保证金: ${account_info['free_margin']:.2f}")
        
        # 获取品种信息
        symbol_info = self.mt5_connector.get_symbol_info(TRADING_CONFIG["symbol"])
        if symbol_info:
            logger.info(f"品种: {symbol_info.name}")
            logger.info(f"最小交易量: {symbol_info.volume_min}")
            logger.info(f"最大交易量: {symbol_info.volume_max}")
        
        self.running = True
        logger.info("交易系统已启动")
        return True
    
    def stop(self):
        """停止交易系统"""
        logger.info("停止交易系统...")
        self.running = False
        
        # 打印统计信息
        self.strategy.print_statistics()
        self.risk_manager.print_risk_status()
        
        # 断开MT5连接
        self.mt5_connector.disconnect()
        logger.info("交易系统已停止")
    
    def run_loop(self, check_interval=60):
        """主交易循环
        
        Args:
            check_interval: 检查间隔（秒）
        """
        logger.info(f"进入主交易循环，检查间隔: {check_interval}秒")
        
        try:
            while self.running:
                try:
                    # 获取当前价格
                    price_info = self.mt5_connector.get_current_price(TRADING_CONFIG["symbol"])
                    
                    if price_info is None:
                        logger.warning("无法获取价格，跳过本次循环")
                        time.sleep(check_interval)
                        continue
                    
                    # 更新价格历史
                    self.last_prices.append(price_info["bid"])
                    if len(self.last_prices) > self.max_price_history:
                        self.last_prices.pop(0)
                    
                    # 打印当前价格
                    logger.info(f"当前价格 - 买入: {price_info['bid']:.2f}, 卖出: {price_info['ask']:.2f}")
                    
                    # 检查风险
                    if not self.risk_manager.check_daily_loss_limit():
                        logger.warning("已达到日亏损限制，停止交易")
                        break
                    
                    # 执行策略
                    self.strategy.execute_strategy(
                        price_info,
                        self.last_prices,
                        TRADING_HOURS
                    )
                    
                    # 检查持仓
                    open_positions = self.order_manager.get_open_positions()
                    if open_positions:
                        logger.info(f"当前持仓数: {len(open_positions)}")
                        for position in open_positions:
                            logger.info(f"  持仓ID: {position.ticket}, 类型: {'买入' if position.type == 0 else '卖出'}, 数量: {position.volume}, 价格: {position.price_open:.2f}")
                    
                    # 等待下一个检查周期
                    time.sleep(check_interval)
                    
                except KeyboardInterrupt:
                    logger.info("收到中断信号")
                    self.running = False
                    break
                except Exception as e:
                    logger.error(f"交易循环异常: {str(e)}")
                    time.sleep(check_interval)
                    continue
                    
        finally:
            self.stop()
    
    def print_help(self):
        """打印帮助信息"""
        print("\n" + "=" * 60)
        print("MT5 高频交易系统 - 使用说明")
        print("=" * 60)
        print("\n【重要】在运行前，请完成以下配置：")
        print("\n1. 打开 config.py 文��，填入你的MT5账户信息：")
        print("   - login: 你的MT5账户号")
        print("   - password: 你的MT5密码")
        print("   - server: 你的MT5服务器")
        print("\n2. 根据需要调整交易参数：")
        print(f"   - 交易品种: {TRADING_CONFIG['symbol']}")
        print(f"   - 交易量: {TRADING_CONFIG['lot_size']}手（可调整）")
        print(f"   - 盈利目标: {TRADING_CONFIG['take_profit']}美元")
        print(f"   - 止损点数: {TRADING_CONFIG['stop_loss']}美元")
        print(f"   - 日最大亏损: ${TRADING_CONFIG['max_daily_loss']}")
        print("\n3. 交易时间配置：")
        print(f"   - 启用时间限制: {TRADING_HOURS['enabled']}")
        print(f"   - 交易开始时间: {TRADING_HOURS['start_hour']}:00")
        print(f"   - 交易结束时间: {TRADING_HOURS['end_hour']}:00")
        print("\n4. 运行程序：")
        print("   python main.py")
        print("\n【操作说明】")
        print("- 按 Ctrl+C 可以随时停止程序")
        print("- 日志会保存到 trading_log.txt")
        print("- 程序会显示实时的交易信息和账户状态")
        print("\n【策略说明】")
        print("- 使用头皮交易（Scalping）策略")
        print("- 快速进出，及时获利了结")
        print("- 当价格上升时买入，当价格下降时卖出")
        print("- 自动止盈和止损")
        print("\n【风险提示】")
        print("⚠️  这是示例程序，仅用于学习目的")
        print("⚠️  请先在模拟盘上充分测试")
        print("⚠️  真实交易前请充分理解风险")
        print("⚠️  建议从小额开始")
        print("\n" + "=" * 60 + "\n")

# ========================================
# 主函数
# ========================================

def main():
    """主函数"""
    
    # 创建交易代理
    agent = TradingAgent()
    
    # 打印帮助信息
    agent.print_help()
    
    # 启动交易系统
    if agent.start():
        # 运行交易循环（每60秒检查一次）
        agent.run_loop(check_interval=60)
    else:
        logger.error("无法启动交易系统")

if __name__ == "__main__":
    main()
