import sqlglot
import re

class SQLValidator:
    @staticmethod
    def validate_sql(sql: str) -> bool:
        """Check SQL is SELECT only and safe"""
        try:
            # Clean up the SQL
            sql = sql.strip()
            
            # Remove comments
            sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
            sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
            
            # Check if it contains any dangerous keywords
            sql_upper = sql.upper()
            
            # These are the ONLY operations we allow
            dangerous_keywords = [
                'DROP', 'DELETE', 'UPDATE', 'ALTER', 'INSERT', 
                'TRUNCATE', 'CREATE', 'REPLACE', 'GRANT', 'REVOKE'
            ]
            
            for keyword in dangerous_keywords:
                if keyword in sql_upper:
                    return False
            
            # Must start with SELECT
            if not sql_upper.strip().startswith('SELECT'):
                return False
            
            # Check for multiple statements (semicolons)
            if sql.count(';') > 1:
                return False
            
            return True
            
        except Exception as e:
            # If parsing fails, do basic checks
            sql_upper = sql.upper()
            dangerous = ['DROP', 'DELETE', 'UPDATE', 'ALTER', 'INSERT', 'TRUNCATE', 'CREATE']
            for word in dangerous:
                if word in sql_upper:
                    return False
            return True
    
    @staticmethod
    def sanitize_sql(sql: str) -> str:
        """Clean up SQL string"""
        # Remove extra whitespace
        sql = ' '.join(sql.split())
        return sql