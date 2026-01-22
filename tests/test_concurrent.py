"""
Property-based tests for concurrent request handling
Feature: music-generation-gui, Property 28: Concurrent Request Safety
Validates: Requirements 5.5
"""
import pytest
import threading
import time
from hypothesis import given, strategies as st, settings, HealthCheck
from app import app
from services.request_handler import RequestHandler

request_handler = RequestHandler()


@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestConcurrentRequests:
    """Unit tests for concurrent request handling"""

    def test_request_handler_initialization(self):
        """Test request handler initializes correctly"""
        handler = RequestHandler()
        assert handler.get_queue_size() == 0
        assert handler.get_active_count() == 0

    def test_queue_request(self):
        """Test queuing a request"""
        handler = RequestHandler()
        result = handler.queue_request('req1', {'seed': 'X:1', 'temperature': 1.0, 'length': 250})
        assert result is True
        assert handler.get_queue_size() == 1

    def test_mark_processing(self):
        """Test marking request as processing"""
        handler = RequestHandler()
        handler.queue_request('req1', {'seed': 'X:1', 'temperature': 1.0, 'length': 250})
        handler.mark_processing('req1')
        stats = handler.get_stats()
        assert stats['active_requests'] == 1

    def test_mark_complete(self):
        """Test marking request as complete"""
        handler = RequestHandler()
        handler.queue_request('req1', {'seed': 'X:1', 'temperature': 1.0, 'length': 250})
        handler.mark_processing('req1')
        handler.mark_complete('req1')
        assert handler.get_active_count() == 0

    def test_multiple_concurrent_requests(self):
        """Test handling multiple concurrent requests"""
        handler = RequestHandler()
        
        # Queue multiple requests
        for i in range(5):
            result = handler.queue_request(f'req{i}', {
                'seed': 'X:1',
                'temperature': 1.0,
                'length': 250
            })
            assert result is True
        
        assert handler.get_queue_size() == 5

    def test_request_isolation(self):
        """Test that concurrent requests don't share state"""
        handler = RequestHandler()
        
        # Queue requests with different parameters
        handler.queue_request('req1', {'seed': 'seed1', 'temperature': 0.5, 'length': 100})
        handler.queue_request('req2', {'seed': 'seed2', 'temperature': 1.5, 'length': 300})
        
        # Verify both are queued
        assert handler.get_queue_size() == 2
        
        # Both should be active after queuing
        assert handler.get_active_count() == 2
        
        # Complete first
        handler.mark_complete('req1')
        assert handler.get_active_count() == 1
        
        # Complete second
        handler.mark_complete('req2')
        assert handler.get_active_count() == 0


class TestConcurrentRequestsProperties:
    """Property-based tests for concurrent request handling"""

    @given(
        num_requests=st.integers(min_value=1, max_value=10)
    )
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=20)
    def test_multiple_requests_queued_safely(self, num_requests):
        """
        Property 28: Concurrent Request Safety
        For any number of concurrent requests, all SHALL be queued without data corruption
        """
        handler = RequestHandler()
        
        # Queue multiple requests
        for i in range(num_requests):
            result = handler.queue_request(f'req{i}', {
                'seed': f'seed{i}',
                'temperature': 1.0,
                'length': 250
            })
            assert result is True
        
        # Verify all queued
        assert handler.get_queue_size() == num_requests

    @given(
        num_requests=st.integers(min_value=1, max_value=10)
    )
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=20)
    def test_concurrent_processing_no_interference(self, num_requests):
        """For any number of concurrent requests, processing SHALL not interfere"""
        handler = RequestHandler()
        
        # Queue and process requests
        for i in range(num_requests):
            handler.queue_request(f'req{i}', {
                'seed': f'seed{i}',
                'temperature': 1.0,
                'length': 250
            })
            handler.mark_processing(f'req{i}')
        
        # All should be active
        assert handler.get_active_count() == num_requests
        
        # Complete all
        for i in range(num_requests):
            handler.mark_complete(f'req{i}')
        
        # All should be complete
        assert handler.get_active_count() == 0

    @given(
        num_threads=st.integers(min_value=2, max_value=5)
    )
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=10)
    def test_thread_safe_concurrent_operations(self, num_threads):
        """For any number of concurrent threads, operations SHALL be thread-safe"""
        handler = RequestHandler()
        errors = []
        
        def worker(thread_id):
            try:
                for i in range(3):
                    req_id = f'thread{thread_id}_req{i}'
                    handler.queue_request(req_id, {
                        'seed': f'seed{i}',
                        'temperature': 1.0,
                        'length': 250
                    })
                    handler.mark_processing(req_id)
                    handler.mark_complete(req_id)
            except Exception as e:
                errors.append(str(e))
        
        # Create and start threads
        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # Verify no errors
        assert len(errors) == 0
        assert handler.get_active_count() == 0
