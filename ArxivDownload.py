import arxiv
from datetime import datetime, timedelta
import calendar
from collections import defaultdict
import concurrent.futures
from typing import Tuple, List, Dict
import logging
import os
import time
import urllib.request
from pathlib import Path
from tqdm import tqdm
import threading
from queue import Queue

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class DownloadTracker:
    def __init__(self, total_papers: int):
        self.pbar = tqdm(total=total_papers, desc="Downloading papers", unit="paper")
        self.lock = threading.Lock()
    
    def update(self, n=1):
        with self.lock:
            self.pbar.update(n)
    
    def close(self):
        self.pbar.close()

def sanitize_filename(title: str) -> str:
    """Convert title to a valid filename."""
    invalid_chars = '<>:"/\\|?*'
    filename = ''.join(char if char not in invalid_chars else '_' for char in title)
    return filename[:150]

def download_paper(args: Tuple[arxiv.Result, str, DownloadTracker]) -> bool:
    """
    Download a single paper's PDF.
    """
    paper, base_path, tracker = args
    try:
        month_dir = os.path.join(base_path, paper.published.strftime("%Y-%m"))
        os.makedirs(month_dir, exist_ok=True)
        
        filename = f"{sanitize_filename(paper.title)}.pdf"
        filepath = os.path.join(month_dir, filename)
        
        if os.path.exists(filepath):
            tracker.update()
            return True
        
        # Download with progress monitoring
        response = urllib.request.urlopen(paper.pdf_url)
        file_size = int(response.headers['Content-Length'])
        
        with open(filepath, 'wb') as f:
            f.write(response.read())
        
        tracker.update()
        return True
        
    except Exception as e:
        logging.error(f"Error downloading '{paper.title}': {str(e)}")
        tracker.update()
        return False

def process_papers_batch(papers: List[arxiv.Result], base_path: str, 
                        max_workers: int = 10) -> None:
    """
    Download a batch of papers in parallel with progress tracking.
    """
    tracker = DownloadTracker(len(papers))
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create arguments for each download task
        download_args = [(paper, base_path, tracker) for paper in papers]
        
        # Submit all downloads
        futures = [executor.submit(download_paper, args) for args in download_args]
        concurrent.futures.wait(futures)
    
    tracker.close()

def fetch_month_papers(date_tuple: Tuple[datetime, datetime, int]) -> Tuple[str, List]:
    """Fetch papers for a specific month."""
    start_date, end_date, max_papers = date_tuple
    date_key = start_date.strftime("%Y-%m")
    
    client = arxiv.Client(page_size=100, delay_seconds=1, num_retries=3)
    search = arxiv.Search(
        query=f'cat:cs.* AND submittedDate:[{start_date.strftime("%Y%m%d")} TO {end_date.strftime("%Y%m%d")}]',
        max_results=max_papers,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    try:
        papers = list(client.results(search))
        print(f"\nFetched {len(papers)} papers for {date_key}")
        return date_key, papers
    except Exception as e:
        logging.error(f"Error fetching papers for {date_key}: {str(e)}")
        return date_key, []

def get_papers_by_month(start_date: datetime, end_date: datetime, 
                       max_papers_per_month: int = 200,
                       max_fetch_workers: int = 4, 
                       max_download_workers: int = 10,
                       download_dir: str = "arxiv_papers") -> Dict[str, List]:
    """
    Fetch and download papers within date range using parallel processing.
    """
    os.makedirs(download_dir, exist_ok=True)
    
    # Generate month ranges
    month_ranges = []
    current_date = start_date
    while current_date <= end_date:
        _, last_day = calendar.monthrange(current_date.year, current_date.month)
        month_end = min(datetime(current_date.year, current_date.month, last_day), end_date)
        month_ranges.append((current_date, month_end, max_papers_per_month))
        
        if current_date.month == 12:
            current_date = datetime(current_date.year + 1, 1, 1)
        else:
            current_date = datetime(current_date.year, current_date.month + 1, 1)
    
    papers_by_month = defaultdict(list)
    all_papers = []
    
    # Fetch papers with progress bar
    with tqdm(total=len(month_ranges), desc="Fetching papers", unit="month") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_fetch_workers) as executor:
            future_to_month = {
                executor.submit(fetch_month_papers, month_range): month_range
                for month_range in month_ranges
            }
            
            for future in concurrent.futures.as_completed(future_to_month):
                try:
                    month_key, papers = future.result()
                    papers_by_month[month_key].extend(papers)
                    all_papers.extend(papers)
                    pbar.update(1)
                except Exception as e:
                    logging.error(f"Error in worker: {str(e)}")
                    pbar.update(1)
    
    # Download all papers in parallel
    print("\nStarting parallel downloads...")
    process_papers_batch(all_papers, download_dir, max_download_workers)
    
    return papers_by_month

def main():
    # Example usage
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2022, 12, 30)
    max_papers = 200
    max_fetch_workers = 4
    max_download_workers = 10
    download_dir = "arxiv_papers"
    
    print("Starting paper collection and download...")
    papers = get_papers_by_month(
        start_date, 
        end_date, 
        max_papers, 
        max_fetch_workers,
        max_download_workers,
        download_dir
    )
    print("\nProcess completed!")
    
    # Print summary
    total_papers = 0
    for month, month_papers in papers.items():
        paper_count = len(month_papers)
        total_papers += paper_count
        print(f"\nMonth: {month}")
        print(f"Number of papers: {paper_count}")
        print(f"Download location: {os.path.join(download_dir, month)}")
        
    print(f"\nTotal papers processed: {total_papers}")

if __name__ == "__main__":
    main()