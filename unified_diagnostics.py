#!/usr/bin/env python3
"""
performance_tests.py

This module runs performance tests to benchmark CPU, memory, disk I/O, network throughput,
and GPU utilization. It outputs results in JSON format and also provides an interactive menu
for convenience.

Usage:
    python3 performance_tests.py --all
    python3 performance_tests.py --menu
    Or specify individual tests with --cpu, --memory, --disk, --network, --gpu

Future enhancements:
- Integrate more granular GPU metrics (e.g., temperature, memory usage, power consumption).
- Add realistic network tests using speedtest-cli or iperf.
- Allow configuration via an external JSON/YAML file.
- Save benchmark results for trend analysis.
- Integrate a web-based dashboard for real-time visualization.
"""

import argparse
import json
import time
import psutil
import subprocess
import numpy as np
import os
import logging
from datetime import datetime
import sys

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]"
)
logger = logging.getLogger("performance_tests")

# Global configuration defaults (can be moved to a config file later)
CPU_ITERATIONS = 1_000_000
MEMORY_MATRIX_SIZE = (10000, 10000)  # Adjust for testing memory allocation speed
DISK_TEST_FILE = "/tmp/disk_test.bin"
DISK_TEST_SIZE_MB = 100

# ===============================
# Benchmark Functions
# ===============================
def benchmark_cpu(iterations=CPU_ITERATIONS):
    """
    🚀 CPU Benchmark:
    Runs a CPU-intensive arithmetic loop and returns the execution time in seconds.
    """
    logger.info("Starting CPU benchmark with %d iterations...", iterations)
    start_time = time.time()
    total = 0
    for i in range(iterations):
        total += i * i
    duration = time.time() - start_time
    logger.info("CPU benchmark completed in %.4f seconds", duration)
    return duration

def benchmark_memory(matrix_size=MEMORY_MATRIX_SIZE):
    """
    💾 Memory Benchmark:
    Measures the time required to allocate a large random matrix using NumPy.
    Returns the allocation time in seconds.
    """
    logger.info("Starting memory benchmark with matrix size %s...", str(matrix_size))
    start_time = time.time()
    try:
        arr = np.random.rand(*matrix_size)
    except Exception as e:
        logger.error("Memory allocation failed: %s", e)
        return None
    duration = time.time() - start_time
    logger.info("Memory allocation completed in %.4f seconds", duration)
    return duration

def benchmark_disk(file_path=DISK_TEST_FILE, size_mb=DISK_TEST_SIZE_MB):
    """
    💽 Disk I/O Benchmark:
    Writes and then reads a file to test disk I/O performance.
    Returns a dictionary with write and read durations in seconds.
    """
    logger.info("Starting disk I/O benchmark: %d MB test file", size_mb)
    data = b'0' * (size_mb * 1024 * 1024)
    try:
        start_time = time.time()
        with open(file_path, "wb") as f:
            f.write(data)
        write_duration = time.time() - start_time

        start_time = time.time()
        with open(file_path, "rb") as f:
            _ = f.read()
        read_duration = time.time() - start_time
    except Exception as e:
        logger.error("Disk I/O benchmark failed: %s", e)
        return None
    finally:
        try:
            os.remove(file_path)
        except Exception:
            pass
    logger.info("Disk benchmark: Write %.4f sec, Read %.4f sec", write_duration, read_duration)
    return {"write": write_duration, "read": read_duration}

def benchmark_network():
    """
    🌐 Network Benchmark:
    Placeholder for network performance tests.
    Returns None for now.
    """
    logger.info("Starting network benchmark... (Not implemented)")
    # TODO: Integrate network performance testing (e.g., using speedtest-cli or iperf)
    return None

def benchmark_gpu():
    """
    🎮 GPU Benchmark:
    Queries nvidia-smi to obtain GPU utilization percentage.
    Returns the GPU utilization as an integer.
    """
    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
            text=True
        )
        gpu_util = int(output.strip())
        logger.info("GPU utilization: %d%%", gpu_util)
        return gpu_util
    except Exception as e:
        logger.error("GPU benchmark failed: %s", e)
        return None

# ===============================
# Run All Benchmarks
# ===============================
def run_all_benchmarks():
    """
    📊 Runs all available benchmarks and returns results as a dictionary.
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "cpu": benchmark_cpu(),
        "memory": benchmark_memory(),
        "disk": benchmark_disk(),
        "network": benchmark_network(),
        "gpu": benchmark_gpu()
    }
    return results

# ===============================
# Interactive Menu for Performance Tests
# ===============================
def performance_menu():
    """
    Displays an interactive menu for running performance benchmarks.
    """
    menu_options = {
        "1": "Run CPU Benchmark",
        "2": "Run Memory Benchmark",
        "3": "Run Disk I/O Benchmark",
        "4": "Run Network Benchmark",
        "5": "Run GPU Benchmark",
        "6": "Run All Benchmarks",
        "0": "Exit"
    }
    while True:
        print("\n=== Performance Test Suite Menu ===")
        for key, value in sorted(menu_options.items()):
            print(f"{key}. {value}")
        choice = input("Select an option: ").strip()
        
        if choice == "1":
            cpu_time = benchmark_cpu()
            print(json.dumps({"cpu": cpu_time}, indent=4))
        elif choice == "2":
            mem_time = benchmark_memory()
            print(json.dumps({"memory": mem_time}, indent=4))
        elif choice == "3":
            disk_result = benchmark_disk()
            print(json.dumps({"disk": disk_result}, indent=4))
        elif choice == "4":
            net_result = benchmark_network()
            print("Network benchmark result:")
            print(json.dumps({"network": net_result}, indent=4))
        elif choice == "5":
            gpu_util = benchmark_gpu()
            print(json.dumps({"gpu": gpu_util}, indent=4))
        elif choice == "6":
            results = run_all_benchmarks()
            print("All Benchmark Results:")
            print(json.dumps(results, indent=4))
        elif choice == "0":
            print("Exiting Performance Test Suite.")
            break
        else:
            print("Invalid selection. Please try again.")

# ===============================
# Main Entry Point for Performance Test Suite
# ===============================
def main():
    parser = argparse.ArgumentParser(description="Performance Test Suite")
    parser.add_argument("--menu", action="store_true", help="Launch interactive performance menu")
    parser.add_argument("--cpu", action="store_true", help="Run CPU benchmark")
    parser.add_argument("--memory", action="store_true", help="Run memory benchmark")
    parser.add_argument("--disk", action="store_true", help="Run disk I/O benchmark")
    parser.add_argument("--network", action="store_true", help="Run network benchmark")
    parser.add_argument("--gpu", action="store_true", help="Run GPU benchmark")
    parser.add_argument("--all", action="store_true", help="Run all benchmarks")
    
    args = parser.parse_args()
    results = {}
    
    if args.menu:
        performance_menu()
    else:
        if args.all or args.cpu:
            results["cpu"] = benchmark_cpu()
        if args.all or args.memory:
            results["memory"] = benchmark_memory()
        if args.all or args.disk:
            results["disk"] = benchmark_disk()
        if args.all or args.network:
            results["network"] = benchmark_network()
        if args.all or args.gpu:
            results["gpu"] = benchmark_gpu()
        print(json.dumps(results, indent=4))

if __name__ == "__main__":
    main()

