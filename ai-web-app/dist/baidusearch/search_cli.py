import argparse
from baidu_spider import BaiduSearchSpider


def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='百度搜索爬虫命令行工具')
    
    # 添加命令行参数
    parser.add_argument('--wd', type=str, required=True, help='搜索关键词')
    parser.add_argument('--page', type=int, default=1, help='页码')
    parser.add_argument('--limit', type=int, default=10, help='每页结果数量')
    parser.add_argument('--save', type=str, help='保存结果的JSON文件路径')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 创建百度搜索爬虫实例
    spider = BaiduSearchSpider()
    
    # 执行搜索
    print(f"正在搜索: {args.wd} (第 {args.page} 页，每页 {args.limit} 条)")
    results = spider.search_with_retry(args.wd, args.page, args.limit)
    
    # 打印搜索结果
    if results:
        print(f"\n共找到 {len(results)} 条结果:")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"\n结果 {i}:")
            print(f"标题: {result['title']}")
            print(f"链接: {result['url']}")
            if 'abstract' in result:
                print(f"摘要: {result['abstract']}")
            if 'source' in result:
                print(f"来源: {result['source']}")
            print("-" * 80)
        
        # 保存结果到文件
        if args.save:
            spider.save_results(results, args.save)
    else:
        print("未找到相关结果")


if __name__ == '__main__':
    main()