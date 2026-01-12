import requests
from bs4 import BeautifulSoup
import json
import time
import random

class BaiduSearchSpider:
    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "close",          # 关键：不要 keep-alive
        }

        self.search_url = "https://www.baidu.com/s"
        self.home_url = "https://www.baidu.com/"
        self.timeout = 5                  # 不要太大
        self.retry_count = 3

        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # 关键一步：预热 session，获取 Cookie
        self._warm_up()
    
    def _warm_up(self):
        """
        预热session，获取Cookie
        """
        try:
            self.session.get(self.home_url, timeout=5)
            time.sleep(random.uniform(0.5, 1.2))
        except Exception:
            pass
    
    def search(self, keyword, page=1, limit=10):
        """
        百度搜索功能
        :param keyword: 搜索关键词
        :param page: 页码
        :param limit: 每页结果数量
        :return: 搜索结果列表
        """
        results = []

        start = (page - 1) * 10
        params = {
            "wd": keyword,
            "pn": start,
            "ie": "utf-8"
        }

        try:
            resp = self.session.get(
                self.search_url,
                params=params,
                timeout=self.timeout
            )
            resp.raise_for_status()

        except requests.exceptions.Timeout:
            print("❌ 请求超时（百度可能在限速）")
            return []

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
            return []

        soup = BeautifulSoup(resp.text, "lxml")

        # 百度当前比较稳定的容器
        result_items = soup.select("div.c-container")

        print(f"找到 {len(result_items)} 个结果项")

        for item in result_items[:limit]:
            result = {}

            # 标题 + 链接
            title_tag = item.select_one("h3 a")
            if not title_tag:
                continue

            result["title"] = title_tag.get_text(strip=True)
            result["url"] = title_tag.get("href")

            # 摘要（能有就有，没有就算了）
            abstract_tag = item.select_one(".c-abstract")
            if abstract_tag:
                result["abstract"] = abstract_tag.get_text(strip=True)

            # 来源（备用）
            source_tag = item.select_one(".c-color-gray")
            if source_tag:
                result["source"] = source_tag.get_text(strip=True)

            results.append(result)

        return results
    
    def search_with_retry(self, keyword, page=1, limit=10):
        """
        带重试机制的搜索功能
        """
        for i in range(self.retry_count):
            results = self.search(keyword, page, limit)
            if results:
                return results
            if i < self.retry_count - 1:
                print(f"搜索失败，正在重试 ({i+2}/{self.retry_count})...")
                time.sleep(random.uniform(1, 3))
        return []
    
    def run(self, params):
        """
        统一的爬虫运行方法，支持通过params字典传递参数
        
        Args:
            params: 参数字典，包含以下可选键：
                - keyword: 搜索关键词
                - wd: 搜索关键词（与keyword同义）
                - page: 页码
                - pn: 起始位置（与page对应）
                - limit: 结果数量限制
                - ie: 编码方式
        
        Returns:
            list: 搜索结果列表
        """
        # 从params中提取参数
        # 优先使用wd参数（爬虫配置中的参数），然后才是keyword参数（前端传递的参数）
        keyword = params.get('wd', params.get('keyword', 'Python'))
        page = int(params.get('page', (int(params.get('pn', 0)) // 10) + 1))
        limit = int(params.get('limit', 10))
        
        print(f"百度爬虫run方法: 关键词='{keyword}', 页码={page}, 限制={limit}")
        
        # 调用原有的搜索方法
        return self.search_with_retry(keyword, page, limit)
    
    def save_results(self, results, filename='search_results.json'):
        """
        保存搜索结果到JSON文件
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"搜索结果已保存到 {filename}")
        except Exception as e:
            print(f"保存结果失败: {e}")

if __name__ == '__main__':
    spider = BaiduSearchSpider()
    results = spider.search_with_retry('四川美食', page=1, limit=5)
    for i, result in enumerate(results, 1):
        print(f"\n结果 {i}:")
        print(f"标题: {result['title']}")
        print(f"链接: {result['url']}")
        if 'abstract' in result:
            print(f"摘要: {result['abstract']}")
        if 'source' in result:
            print(f"来源: {result['source']}")
    
    spider.save_results(results, 'baike_search_results.json')