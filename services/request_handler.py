"""
Thread-safe request handler for concurrent generation requests
"""
import logging
import threading
from queue import Queue
from typing import Dict, Any

logger = logging.getLogger(__name__)


class RequestHandler:
    """Handles concurrent generation requests safely"""
    
    def __init__(self, max_queue_size=100):
        """
        Initialize the request handler
        
        Args:
            max_queue_size: Maximum number of requests in queue
        """
        self.request_queue = Queue(maxsize=max_queue_size)
        self.lock = threading.Lock()
        self.active_requests = {}
        self.request_counter = 0
    
    def queue_request(self, request_id: str, request_data: Dict[str, Any]) -> bool:
        """
        Queue a generation request
        
        Args:
            request_id: Unique request identifier
            request_data: Request parameters
        
        Returns:
            True if queued successfully, False if queue is full
        """
        try:
            self.request_queue.put_nowait((request_id, request_data))
            
            with self.lock:
                self.active_requests[request_id] = 'queued'
                self.request_counter += 1
            
            logger.info(f'Request {request_id} queued')
            return True
            
        except Exception as e:
            logger.error(f'Failed to queue request: {str(e)}')
            return False
    
    def mark_processing(self, request_id: str) -> None:
        """Mark a request as being processed"""
        with self.lock:
            if request_id in self.active_requests:
                self.active_requests[request_id] = 'processing'
    
    def mark_complete(self, request_id: str) -> None:
        """Mark a request as complete"""
        with self.lock:
            if request_id in self.active_requests:
                del self.active_requests[request_id]
    
    def get_queue_size(self) -> int:
        """Get current queue size"""
        return self.request_queue.qsize()
    
    def get_active_count(self) -> int:
        """Get number of active requests"""
        with self.lock:
            return len(self.active_requests)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get request handler statistics"""
        with self.lock:
            return {
                'queue_size': self.request_queue.qsize(),
                'active_requests': len(self.active_requests),
                'total_requests': self.request_counter
            }
