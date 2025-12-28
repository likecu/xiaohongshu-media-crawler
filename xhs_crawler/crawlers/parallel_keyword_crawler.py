#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书多关键词并行爬虫
使用 ThreadPoolExecutor 实现关键词并行爬取，大幅提升爬取效率
"""

import time
import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures._base import TimeoutError
from dataclasses import dataclass
from datetime import datetime
import threading

from xhs_crawler.core.base_crawler import BaseCrawler
from xhs_crawler.core.config import get_output_dir, get_html_file_path, DEFAULT_CRAWLER_CONFIG

logger = logging.getLogger(__name__)


@dataclass
class CrawlResult:
    """爬取结果数据类"""
    keyword: str
    success: bool
    notes: List[Dict[str, Any]]
    error: Optional[str] = None
    duration: float = 0.0
    pages_crawled: int = 0


class ParallelKeywordCrawler(BaseCrawler):
    """
    多关键词并行爬虫
    
    使用 ThreadPoolExecutor 实现关键词级别的并行爬取，
    同时支持批量获取帖子详情，显著提升爬取效率。
    
    Features:
        - 关键词级别并行爬取
        - 帖子详情批量并发获取
        - 智能超时控制
        - 进度实时跟踪
        - 错误自动恢复
    """
    
    def __init__(
        self,
        max_workers: int = 5,
        detail_concurrency: int = 10,
        timeout_per_keyword: float = 120.0,
        timeout_per_detail: float = 30.0
    ):
        """
        初始化并行爬虫
        
        Args:
            max_workers: 最大并行工作线程数（关键词爬取）
            detail_concurrency: 详情获取并发数
            timeout_per_keyword: 每个关键词的超时时间（秒）
            timeout_per_detail: 每个详情请求的超时时间（秒）
        """
        output_dir = get_output_dir("parallel_multi_keyword")
        super().__init__(output_dir)
        self.html_file = get_html_file_path("parallel_multi_keyword")
        self.config = DEFAULT_CRAWLER_CONFIG
        
        self.max_workers = max_workers
        self.detail_concurrency = detail_concurrency
        self.timeout_per_keyword = timeout_per_keyword
        self.timeout_per_detail = timeout_per_detail
        
        self._total_notes_lock = threading.Lock()
        self._progress_lock = threading.Lock()
        self._total_notes: List[Dict[str, Any]] = []
        self._crawl_stats = {
            "keywords_processed": 0,
            "keywords_failed": 0,
            "total_pages": 0,
            "total_notes": 0,
            "start_time": None,
            "end_time": None
        }
    
    def _crawl_single_keyword(
        self,
        keyword: str,
        max_pages: int,
        page_size: int
    ) -> CrawlResult:
        """
        爬取单个关键词的所有页面
        
        Args:
            keyword: 搜索关键词
            max_pages: 最大爬取页数
            page_size: 每页数量
            
        Returns:
            CrawlResult: 爬取结果
        """
        start_time = time.time()
        notes = []
        pages_crawled = 0
        
        try:
            for page_num in range(1, max_pages + 1):
                page_start = time.time()
                
                result = self.search_posts(keyword, page_num=page_num, page_size=page_size)
                page_notes = result if isinstance(result, list) else []
                
                if not page_notes:
                    logger.info(f"关键词 '{keyword}' 第 {page_num} 页无数据，停止爬取")
                    break
                
                notes.extend(page_notes)
                pages_crawled += 1
                
                page_duration = time.time() - page_start
                logger.info(
                    f"关键词 '{keyword}' 第 {page_num}/{max_pages} 页: "
                    f"获取 {len(page_notes)} 篇笔记 (耗时: {page_duration:.2f}s)"
                )
                
                time.sleep(self.config["sleep_time"])
            
            duration = time.time() - start_time
            return CrawlResult(
                keyword=keyword,
                success=True,
                notes=notes,
                duration=duration,
                pages_crawled=pages_crawled
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"关键词 '{keyword}' 爬取失败: {e}")
            return CrawlResult(
                keyword=keyword,
                success=False,
                notes=[],
                error=str(e),
                duration=duration,
                pages_crawled=pages_crawled
            )
    
    def _get_single_detail(
        self,
        note: Dict[str, Any],
        index: int,
        total: int
    ) -> Optional[Dict[str, Any]]:
        """
        获取单个帖子详情
        
        Args:
            note: 帖子基本信息
            index: 当前索引
            total: 总数
            
        Returns:
            Optional[Dict]: 帖子详情
        """
        note_id = note.get("note_id")
        if not note_id:
            return None
        
        try:
            detail = self.get_post_detail(
                note_id=note_id,
                xsec_token=note.get("xsec_token", ""),
                xsec_source=note.get("xsec_source", "pc_feed")
            )
            
            if detail:
                logger.debug(f"详情获取成功: {note_id} ({index}/{total})")
                return {
                    "basic_info": note,
                    "detail": detail
                }
            return None
            
        except Exception as e:
            logger.warning(f"详情获取失败: {note_id}, 错误: {e}")
            return None
    
    def _batch_fetch_details(
        self,
        notes: List[Dict[str, Any]],
        concurrency: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        批量获取帖子详情
        
        Args:
            notes: 帖子列表
            concurrency: 并发数，默认使用实例配置
            
        Returns:
            List[Dict]: 包含详情的帖子列表
        """
        if not notes:
            return []
        
        max_workers = concurrency or self.detail_concurrency
        posts = []
        
        logger.info(f"开始批量获取 {len(notes)} 篇帖子详情，并发数: {max_workers}")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_note = {
                executor.submit(
                    self._get_single_detail,
                    note,
                    i + 1,
                    len(notes)
                ): note for i, note in enumerate(notes)
            }
            
            completed = 0
            total = len(future_to_note)
            
            for future in as_completed(future_to_note):
                completed += 1
                
                try:
                    result = future.result(timeout=self.timeout_per_detail)
                    if result:
                        posts.append(result)
                except TimeoutError:
                    logger.warning(f"详情获取超时 (索引 {completed}/{total})")
                except Exception as e:
                    logger.error(f"详情处理异常: {e}")
                
                if completed % 10 == 0 or completed == total:
                    progress = (completed / total) * 100
                    logger.info(f"详情获取进度: {completed}/{total} ({progress:.1f}%)")
        
        logger.info(f"详情获取完成: 成功 {len(posts)}/{len(notes)} 篇")
        return posts
    
    def run(
        self,
        keywords: Optional[List[str]] = None,
        max_pages: Optional[int] = None,
        page_size: Optional[int] = None,
        max_workers: Optional[int] = None,
        detail_concurrency: Optional[int] = None,
        enable_detail_fetch: bool = True
    ) -> Dict[str, Any]:
        """
        运行并行爬虫
        
        Args:
            keywords: 搜索关键词列表
            max_pages: 每个关键词爬取的最大页数
            page_size: 每页结果数量
            max_workers: 最大并行工作线程数
            detail_concurrency: 详情获取并发数
            enable_detail_fetch: 是否获取帖子详情
            
        Returns:
            Dict: 爬取结果统计
        """
        self._crawl_stats["start_time"] = datetime.now()
        
        if keywords is None:
            keywords = ["大模型", "面试", "经验分享"]
        if max_pages is None:
            max_pages = self.config["max_pages"]
        if page_size is None:
            page_size = self.config["page_size"]
        if max_workers is None:
            max_workers = self.max_workers
        if detail_concurrency is None:
            detail_concurrency = self.detail_concurrency
        
        max_workers = min(max_workers, len(keywords))
        
        logger.info("=" * 60)
        logger.info("🚀 启动小红书多关键词并行爬虫")
        logger.info(f"📝 关键词数量: {len(keywords)}")
        logger.info(f"⚡ 最大并行数: {max_workers}")
        logger.info(f"📄 每页数量: {page_size}")
        logger.info(f"📑 最大页数/关键词: {max_pages}")
        if enable_detail_fetch:
            logger.info(f"🔗 详情并发数: {detail_concurrency}")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        all_results: List[CrawlResult] = []
        
        logger.info("\n📊 第一阶段: 并行爬取搜索结果")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_keyword = {}
            
            for keyword in keywords:
                future = executor.submit(
                    self._crawl_single_keyword,
                    keyword,
                    max_pages,
                    page_size
                )
                future_to_keyword[future] = keyword
            
            for future in as_completed(future_to_keyword):
                keyword = future_to_keyword[future]
                
                try:
                    result = future.result(timeout=self.timeout_per_keyword)
                    all_results.append(result)
                    
                    with self._progress_lock:
                        self._crawl_stats["keywords_processed"] += 1
                        self._crawl_stats["total_pages"] += result.pages_crawled
                        self._crawl_stats["total_notes"] += len(result.notes)
                    
                    if result.success:
                        logger.info(
                            f"✅ 关键词 '{keyword}' 完成: "
                            f"{result.pages_crawled} 页, {len(result.notes)} 篇笔记, "
                            f"耗时 {result.duration:.2f}s"
                        )
                    else:
                        with self._progress_lock:
                            self._crawl_stats["keywords_failed"] += 1
                        logger.warning(
                            f"❌ 关键词 '{keyword}' 失败: {result.error}, "
                            f"耗时 {result.duration:.2f}s"
                        )
                            
                except TimeoutError:
                    logger.error(f"⏰ 关键词 '{keyword}' 超时")
                    all_results.append(CrawlResult(
                        keyword=keyword,
                        success=False,
                        notes=[],
                        error="Timeout",
                        pages_crawled=0
                    ))
                    with self._progress_lock:
                        self._crawl_stats["keywords_failed"] += 1
                        
                except Exception as e:
                    logger.error(f"💥 关键词 '{keyword}' 异常: {e}")
                    all_results.append(CrawlResult(
                        keyword=keyword,
                        success=False,
                        notes=[],
                        error=str(e),
                        pages_crawled=0
                    ))
                    with self._progress_lock:
                        self._crawl_stats["keywords_failed"] += 1
        
        for result in all_results:
            self._total_notes.extend(result.notes)
        
        unique_notes = self.deduplicate_notes(self._total_notes)
        
        logger.info(
            f"\n📈 搜索阶段完成: {len(self._total_notes)} 篇 -> 去重后 {len(unique_notes)} 篇"
        )
        
        posts = []
        if enable_detail_fetch and unique_notes:
            logger.info(f"\n🔗 第二阶段: 并行获取帖子详情 (并发数: {detail_concurrency})")
            detail_start = time.time()
            
            posts = self._batch_fetch_details(unique_notes, detail_concurrency)
            
            detail_duration = time.time() - detail_start
            logger.info(f"详情获取耗时: {detail_duration:.2f}s")
            
            for i, post in enumerate(posts):
                title = post.get("basic_info", {}).get("title", f"帖子{i+1}")
                clean_title = self._clean_filename(title)
                filename = f"{i+1:03d}_{clean_title}_detail.json"
                self._save_json_data(post, f"{self.detail_dir}/{filename}")
        
        self._crawl_stats["end_time"] = datetime.now()
        total_duration = time.time() - start_time
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 爬虫完成!")
        logger.info(f"📊 总耗时: {total_duration:.2f} 秒")
        logger.info(f"📝 处理关键词: {len(keywords)} 个")
        logger.info(f"✅ 成功关键词: {self._crawl_stats['keywords_processed'] - self._crawl_stats['keywords_failed']} 个")
        logger.info(f"❌ 失败关键词: {self._crawl_stats['keywords_failed']} 个")
        logger.info(f"📄 总页数: {self._crawl_stats['total_pages']}")
        logger.info(f"📝 总笔记数: {self._crawl_stats['total_notes']} 篇")
        logger.info(f"🔗 获取详情: {len(posts)} 篇")
        logger.info(f"📁 结果保存目录: {self.output_dir}")
        logger.info("=" * 60)
        
        if posts:
            self.generate_html_page(posts, self.html_file, "大模型面试经验分享 - 并行爬取")
            logger(f"🌐 HTML网页: {self.html_file}")
        
        return {
            "status": "success",
            "total_duration": total_duration,
            "keywords": {
                "total": len(keywords),
                "successful": self._crawl_stats["keywords_processed"] - self._crawl_stats["keywords_failed"],
                "failed": self._crawl_stats["keywords_failed"]
            },
            "pages": self._crawl_stats["total_pages"],
            "notes": {
                "total": self._crawl_stats["total_notes"],
                "unique": len(unique_notes),
                "with_details": len(posts)
            },
            "output_dir": self.output_dir,
            "html_file": self.html_file if posts else None
        }
    
    def run_async(
        self,
        keywords: List[str],
        max_pages: int = 2,
        page_size: int = 10,
        max_workers: int = 5
    ) -> Dict[str, Any]:
        """
        异步运行并行爬虫（非阻塞版本）
        
        Args:
            keywords: 搜索关键词列表
            max_pages: 每个关键词爬取的最大页数
            page_size: 每页结果数量
            max_workers: 最大并行工作线程数
            
        Returns:
            Dict: 任务信息（不阻塞等待完成）
        """
        import concurrent.futures
        
        executor = ThreadPoolExecutor(max_workers=max_workers)
        
        future = executor.submit(
            self.run,
            keywords=keywords,
            max_pages=max_pages,
            page_size=page_size,
            max_workers=max_workers
        )
        
        return {
            "executor": executor,
            "future": future,
            "status": "running"
        }
    
    def wait_for_result(self, task_info: Dict[str, Any], timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        等待异步任务完成并获取结果
        
        Args:
            task_info: 任务信息字典
            timeout: 超时时间
            
        Returns:
            Dict: 爬取结果
        """
        future = task_info.get("future")
        executor = task_info.get("executor")
        
        if not future:
            return {"error": "Invalid task info"}
        
        try:
            result = future.result(timeout=timeout)
            if executor:
                executor.shutdown(wait=False)
            return result
        except TimeoutError:
            return {"error": "Task timeout"}
        except Exception as e:
            return {"error": str(e)}


def run_parallel_crawler(
    keywords: Optional[List[str]] = None,
    max_pages: int = 2,
    page_size: int = 10,
    max_workers: int = 5,
    detail_concurrency: int = 10
) -> Dict[str, Any]:
    """
    便捷函数：运行并行爬虫
    
    Args:
        keywords: 搜索关键词列表
        max_pages: 每个关键词爬取的最大页数
        page_size: 每页结果数量
        max_workers: 最大并行工作线程数
        detail_concurrency: 详情获取并发数
        
    Returns:
        Dict: 爬取结果统计
    """
    crawler = ParallelKeywordCrawler(
        max_workers=max_workers,
        detail_concurrency=detail_concurrency
    )
    return crawler.run(
        keywords=keywords,
        max_pages=max_pages,
        page_size=page_size,
        enable_detail_fetch=True
    )


if __name__ == "__main__":
    import json
    
    print("\n" + "=" * 60)
    print("🚀 小红书多关键词并行爬虫演示")
    print("=" * 60)
    
    result = run_parallel_crawler(
        keywords=["大模型面试", "Transformer面试", "深度学习面试"],
        max_pages=2,
        page_size=10,
        max_workers=3,
        detail_concurrency=5
    )
    
    print("\n📊 最终结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
