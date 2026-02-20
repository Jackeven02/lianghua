"""
数据存储模块
负责数据的持久化存储和管理
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DataStorage:
    """数据存储类"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """初始化数据库"""
        # 创建数据库目录
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        # 创建数据表
        self.create_tables()
        
    def get_connection(self):
        """获取数据库连接"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def create_tables(self):
        """创建数据表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 创建股票数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                date DATE NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                amount REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(stock_code, date)
            )
        ''')
        
        # 创建基金数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fund_code TEXT NOT NULL,
                date DATE NOT NULL,
                nav REAL,
                accumulated_nav REAL,
                daily_return REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fund_code, date)
            )
        ''')
        
        # 创建技术指标表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS technical_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                date DATE NOT NULL,
                indicator_name TEXT NOT NULL,
                indicator_value REAL,
                parameters TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(stock_code, date, indicator_name)
            )
        ''')
        
        # 创建回测结果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                stock_code TEXT,
                start_date DATE,
                end_date DATE,
                initial_capital REAL,
                final_capital REAL,
                total_return REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                win_rate REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建用户收藏表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                stock_code TEXT NOT NULL,
                stock_name TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建查询历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_type TEXT NOT NULL,
                query_params TEXT,
                result_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("数据库表创建完成")
    
    def save_stock_data(self, stock_code: str, data: pd.DataFrame):
        """保存股票数据"""
        if data.empty:
            return
            
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            for _, row in data.iterrows():
                cursor.execute('''
                    INSERT OR REPLACE INTO stock_data 
                    (stock_code, date, open, high, low, close, volume, amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    stock_code,
                    row['date'].strftime('%Y-%m-%d') if 'date' in row else None,
                    row.get('open'),
                    row.get('high'),
                    row.get('low'),
                    row.get('close'),
                    row.get('volume'),
                    row.get('amount')
                ))
                
            conn.commit()
            logger.info(f"成功保存股票 {stock_code} 数据 {len(data)} 条记录")
            
        except Exception as e:
            logger.error(f"保存股票数据失败: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_stock_data(self, stock_code: str, 
                      start_date: Optional[str] = None,
                      end_date: Optional[str] = None) -> pd.DataFrame:
        """获取股票数据"""
        conn = self.get_connection()
        
        try:
            query = "SELECT * FROM stock_data WHERE stock_code = ?"
            params = [stock_code]
            
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
                
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
                
            query += " ORDER BY date"
            
            df = pd.read_sql_query(query, conn, params=params)
            
            if not df.empty and 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                
            logger.info(f"成功获取股票 {stock_code} 数据 {len(df)} 条记录")
            return df
            
        except Exception as e:
            logger.error(f"获取股票数据失败: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def save_technical_indicators(self, stock_code: str, date: str,
                                indicators: Dict[str, float], parameters: str = None):
        """保存技术指标"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            for indicator_name, indicator_value in indicators.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO technical_indicators 
                    (stock_code, date, indicator_name, indicator_value, parameters)
                    VALUES (?, ?, ?, ?, ?)
                ''', (stock_code, date, indicator_name, indicator_value, parameters))
                
            conn.commit()
            logger.info(f"成功保存股票 {stock_code} 技术指标")
            
        except Exception as e:
            logger.error(f"保存技术指标失败: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_technical_indicators(self, stock_code: str, 
                               start_date: Optional[str] = None,
                               end_date: Optional[str] = None) -> pd.DataFrame:
        """获取技术指标"""
        conn = self.get_connection()
        
        try:
            query = "SELECT * FROM technical_indicators WHERE stock_code = ?"
            params = [stock_code]
            
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
                
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
                
            query += " ORDER BY date, indicator_name"
            
            df = pd.read_sql_query(query, conn, params=params)
            
            if not df.empty and 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                
            return df
            
        except Exception as e:
            logger.error(f"获取技术指标失败: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def save_backtest_result(self, result: Dict[str, Any]):
        """保存回测结果"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO backtest_results 
                (strategy_name, stock_code, start_date, end_date, initial_capital,
                 final_capital, total_return, sharpe_ratio, max_drawdown, win_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.get('strategy_name'),
                result.get('stock_code'),
                result.get('start_date'),
                result.get('end_date'),
                result.get('initial_capital'),
                result.get('final_capital'),
                result.get('total_return'),
                result.get('sharpe_ratio'),
                result.get('max_drawdown'),
                result.get('win_rate')
            ))
            
            conn.commit()
            logger.info("成功保存回测结果")
            
        except Exception as e:
            logger.error(f"保存回测结果失败: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_backtest_results(self, strategy_name: Optional[str] = None) -> pd.DataFrame:
        """获取回测结果"""
        conn = self.get_connection()
        
        try:
            query = "SELECT * FROM backtest_results"
            params = []
            
            if strategy_name:
                query += " WHERE strategy_name = ?"
                params.append(strategy_name)
                
            query += " ORDER BY created_at DESC"
            
            df = pd.read_sql_query(query, conn, params=params)
            return df
            
        except Exception as e:
            logger.error(f"获取回测结果失败: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def add_favorite(self, stock_code: str, stock_name: str = None):
        """添加收藏"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO user_favorites (stock_code, stock_name)
                VALUES (?, ?)
            ''', (stock_code, stock_name))
            
            conn.commit()
            logger.info(f"成功添加收藏: {stock_code}")
            
        except Exception as e:
            logger.error(f"添加收藏失败: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_favorites(self) -> pd.DataFrame:
        """获取收藏列表"""
        conn = self.get_connection()
        
        try:
            df = pd.read_sql_query(
                "SELECT * FROM user_favorites ORDER BY added_at DESC",
                conn
            )
            return df
            
        except Exception as e:
            logger.error(f"获取收藏列表失败: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def remove_favorite(self, stock_code: str):
        """移除收藏"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "DELETE FROM user_favorites WHERE stock_code = ?",
                (stock_code,)
            )
            
            conn.commit()
            logger.info(f"成功移除收藏: {stock_code}")
            
        except Exception as e:
            logger.error(f"移除收藏失败: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def save_query_history(self, query_type: str, query_params: str, result_count: int):
        """保存查询历史"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO query_history (query_type, query_params, result_count)
                VALUES (?, ?, ?)
            ''', (query_type, query_params, result_count))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"保存查询历史失败: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_query_history(self, limit: int = 100) -> pd.DataFrame:
        """获取查询历史"""
        conn = self.get_connection()
        
        try:
            df = pd.read_sql_query(
                f"SELECT * FROM query_history ORDER BY created_at DESC LIMIT {limit}",
                conn
            )
            return df
            
        except Exception as e:
            logger.error(f"获取查询历史失败: {e}")
            return pd.DataFrame()
        finally:
            conn.close()