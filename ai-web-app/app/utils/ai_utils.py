import re
import jieba
import jieba.analyse
from datetime import datetime

class AIUtils:
    @staticmethod
    def preprocess_text(text):
        """预处理文本数据"""
        if not text:
            return ""
        
        # 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 去除特殊字符
        text = re.sub(r'[^一-龥a-zA-Z0-9\s]', '', text)
        
        # 去除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def extract_keywords(text, top_k=10):
        """提取文本关键词"""
        if not text:
            return []
        
        # 使用jieba提取关键词
        keywords = jieba.analyse.extract_tags(text, topK=top_k, withWeight=True)
        
        # 转换为列表格式
        return [{'word': word, 'weight': weight} for word, weight in keywords]
    
    @staticmethod
    def segment_text(text):
        """中文文本分词"""
        if not text:
            return []
        
        return list(jieba.cut(text))
    
    @staticmethod
    def calculate_sentiment_score(text):
        """计算文本情感得分（简单实现，实际项目中可使用专业模型）"""
        if not text:
            return 0.0
        
        # 简单的情感词典匹配（示例）
        positive_words = ['好', '优秀', '出色', '成功', '满意', '增长', '创新']
        negative_words = ['差', '失败', '不满', '下降', '问题', '错误', '缺陷']
        
        words = AIUtils.segment_text(text)
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total = max(len(words), 1)
        score = (positive_count - negative_count) / total
        
        return score
    
    @staticmethod
    def format_timestamp(timestamp):
        """格式化时间戳"""
        if not timestamp:
            return ""
        
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def validate_json_structure(data, required_fields):
        """验证JSON数据结构"""
        if not isinstance(data, dict):
            return False
        
        for field in required_fields:
            if field not in data:
                return False
        
        return True

# 创建AI工具实例
ai_utils = AIUtils()