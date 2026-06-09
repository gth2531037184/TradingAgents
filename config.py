# ========================================
# MT5 高频交易系统 - 配置文件
# ========================================

# MT5 连接配置
MT5_SYMBOL = "XAUUSD"  # 黄金交易对
MT5_TIMEFRAME = 1      # 1分钟K线

# 交易参数配置
TRADING_CONFIG = {
    "symbol": "XAUUSD",           # 交易品种：黄金
    "lot_size": 0.1,              # 交易量：0.1手（可调整）
    "take_profit": 0.1,           # 盈利目标：0.1美元
    "stop_loss": 0.1,             # 止损点数：0.1美元
    "max_positions": 1,           # 最大持仓数
    "max_daily_loss": 50,         # 日最大亏损额（美元）
}

# 交易时间配置（24小时制）
TRADING_HOURS = {
    "enabled": True,              # 是否启用时间限制
    "start_hour": 0,              # 开始时间：0点（可调整）
    "end_hour": 23,               # 结束时间：23点（可调整）
}

# 日志配置
LOG_CONFIG = {
    "log_file": "trading_log.txt",
    "log_level": "INFO",
}

# MT5 账户信息（需要填写你的账户）
ACCOUNT_INFO = {
    "login": 0,                   # 你的MT5账户号
    "password": "",               # 你的MT5密码
    "server": "",                 # 你的MT5服务器
}
