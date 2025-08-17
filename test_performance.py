#!/usr/bin/env python3
"""
Performance test script for DistComp optimizations
Tests Redis pipeline batching and other performance improvements
"""

import time
import redis
import json
import threading
from concurrent.futures import ThreadPoolExecutor
import statistics

class PerformanceTest:
    def __init__(self, redis_host='localhost', redis_port=6400, redis_pass='cloudlab'):
        self.redis_inst = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_pass,
            decode_responses=True
        )
        
    def test_redis_pipeline_vs_individual(self, num_operations=1000):
        """Test Redis pipeline vs individual operations"""
        print(f"Testing Redis pipeline vs individual operations ({num_operations} operations)")
        
        # Test individual operations
        start_time = time.time()
        for i in range(num_operations):
            self.redis_inst.hset(f"test_key_{i}", f"field_{i}", f"value_{i}")
        individual_time = time.time() - start_time
        
        # Clean up
        for i in range(num_operations):
            self.redis_inst.hdel(f"test_key_{i}")
            
        # Test pipeline operations
        start_time = time.time()
        pipeline = self.redis_inst.pipeline()
        for i in range(num_operations):
            pipeline.hset(f"test_key_{i}", f"field_{i}", f"value_{i}")
        pipeline.execute()
        pipeline_time = time.time() - start_time
        
        # Clean up
        pipeline = self.redis_inst.pipeline()
        for i in range(num_operations):
            pipeline.hdel(f"test_key_{i}")
        pipeline.execute()
        
        # Calculate improvement
        improvement = (individual_time - pipeline_time) / individual_time * 100
        
        print(f"Individual operations: {individual_time:.3f}s")
        print(f"Pipeline operations: {pipeline_time:.3f}s")
        print(f"Performance improvement: {improvement:.1f}%")
        print(f"Speedup: {individual_time/pipeline_time:.1f}x")
        
        return {
            'individual_time': individual_time,
            'pipeline_time': pipeline_time,
            'improvement_percent': improvement,
            'speedup': individual_time/pipeline_time
        }
        
    def test_task_fetching_simulation(self, num_tasks=100, num_workers=10):
        """Simulate task fetching performance"""
        print(f"Testing task fetching simulation ({num_tasks} tasks, {num_workers} workers)")
        
        # Setup test data
        for i in range(num_tasks):
            self.redis_inst.hset("todo_tasks", f"task_{i}", "")
            
        # Test individual fetching (simulating old method)
        start_time = time.time()
        for worker_id in range(num_workers):
            for _ in range(num_tasks // num_workers):
                # Simulate individual Redis calls
                todo = self.redis_inst.hgetall("todo_tasks")
                failed = self.redis_inst.hgetall("failed_tasks")
                # Simulate task processing
                time.sleep(0.001)  # 1ms processing time
        individual_time = time.time() - start_time
        
        # Test pipeline fetching (simulating new method)
        start_time = time.time()
        for worker_id in range(num_workers):
            for _ in range(num_tasks // num_workers):
                # Simulate pipeline Redis calls
                pipeline = self.redis_inst.pipeline()
                pipeline.hgetall("todo_tasks")
                pipeline.hgetall("failed_tasks")
                todo, failed = pipeline.execute()
                # Simulate task processing
                time.sleep(0.001)  # 1ms processing time
        pipeline_time = time.time() - start_time
        
        # Clean up
        self.redis_inst.delete("todo_tasks")
        self.redis_inst.delete("failed_tasks")
        
        improvement = (individual_time - pipeline_time) / individual_time * 100
        
        print(f"Individual fetching: {individual_time:.3f}s")
        print(f"Pipeline fetching: {pipeline_time:.3f}s")
        print(f"Performance improvement: {improvement:.1f}%")
        print(f"Speedup: {individual_time/pipeline_time:.1f}x")
        
        return {
            'individual_time': individual_time,
            'pipeline_time': pipeline_time,
            'improvement_percent': improvement,
            'speedup': individual_time/pipeline_time
        }
        
    def test_concurrent_workers(self, num_workers=20, operations_per_worker=100):
        """Test concurrent worker performance"""
        print(f"Testing concurrent workers ({num_workers} workers, {operations_per_worker} ops each)")
        
        def worker_task(worker_id):
            results = []
            for i in range(operations_per_worker):
                start_time = time.time()
                # Simulate task fetching with pipeline
                pipeline = self.redis_inst.pipeline()
                pipeline.hgetall("todo_tasks")
                pipeline.hgetall("failed_tasks")
                pipeline.execute()
                end_time = time.time()
                results.append(end_time - start_time)
            return results
            
        # Run concurrent workers
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(worker_task, i) for i in range(num_workers)]
            all_results = []
            for future in futures:
                all_results.extend(future.result())
        total_time = time.time() - start_time
        
        # Calculate statistics
        avg_latency = statistics.mean(all_results) * 1000  # Convert to ms
        p95_latency = statistics.quantiles(all_results, n=20)[18] * 1000  # 95th percentile
        p99_latency = statistics.quantiles(all_results, n=100)[98] * 1000  # 99th percentile
        
        print(f"Total time: {total_time:.3f}s")
        print(f"Average latency: {avg_latency:.2f}ms")
        print(f"95th percentile latency: {p95_latency:.2f}ms")
        print(f"99th percentile latency: {p99_latency:.2f}ms")
        print(f"Total operations: {num_workers * operations_per_worker}")
        print(f"Operations per second: {num_workers * operations_per_worker / total_time:.1f}")
        
        return {
            'total_time': total_time,
            'avg_latency_ms': avg_latency,
            'p95_latency_ms': p95_latency,
            'p99_latency_ms': p99_latency,
            'ops_per_second': num_workers * operations_per_worker / total_time
        }

def main():
    """Main test function"""
    print("=" * 60)
    print("DistComp Performance Test Suite")
    print("=" * 60)
    
    try:
        test = PerformanceTest()
        
        # Test 1: Basic Redis pipeline performance
        print("\n1. Basic Redis Pipeline Performance Test")
        print("-" * 40)
        test.test_redis_pipeline_vs_individual(1000)
        
        # Test 2: Task fetching simulation
        print("\n2. Task Fetching Simulation Test")
        print("-" * 40)
        test.test_task_fetching_simulation(100, 10)
        
        # Test 3: Concurrent workers
        print("\n3. Concurrent Workers Test")
        print("-" * 40)
        test.test_concurrent_workers(20, 50)
        
        print("\n" + "=" * 60)
        print("Performance tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error during performance testing: {e}")
        print("Make sure Redis server is running and accessible")

if __name__ == "__main__":
    main()
