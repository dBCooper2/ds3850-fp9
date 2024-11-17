import time
from collections import deque
from threading import Lock

class RateLimiter:
    def __init__(self, requests_per_minute=3, burst_limit=5):
        """
        Initialize rate limiter with configurable limits
        
        Args:
            requests_per_minute (int): Number of requests allowed per minute
            burst_limit (int): Maximum number of requests allowed in quick succession
        """
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.request_times = deque(maxlen=max(requests_per_minute, burst_limit))
        self.lock = Lock()
    
    def wait_if_needed(self):
        """
        Check if we need to wait before making another request.
        If necessary, sleep for the required duration.
        """
        with self.lock:
            now = time.time()
            
            # Clean up old requests
            while self.request_times and now - self.request_times[0] > 60:
                self.request_times.popleft()
            
            # Check burst limit
            if len(self.request_times) >= self.burst_limit:
                sleep_time = self.request_times[-self.burst_limit] + 60 - now
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            # Check requests per minute
            if len(self.request_times) >= self.requests_per_minute:
                sleep_time = self.request_times[0] + 60 - now
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            # Record this request
            self.request_times.append(now)