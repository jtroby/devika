#!/usr/bin/env python3
"""
performance_tests.py

This module runs performance tests to benchmark CPU, memory, disk I/O, network throughput,
and GPU utilization. It outputs results in JSON format, saves results to CSV for persistence,
and also provides an interactive menu for convenience.

New Features in this version (v1.1):
- Extended GPU metrics using nvidia-smi (utilization, temperature, memory usage).
- External configuration loading from config.json.
- Data persistence: benchmark results are appended to a CSV file.
- Dashboard integration is marked for future refinement.

Usage:
    python3 performance_tests.py --all
    python3 performance_tests.py --menu
    Or specify individual tests with --cpu, --memory, --disk, --network, --gpu

Future enhancements:
- Integrate more granular GPU metrics (e.g., power consumption) and push to a dashboard.
- Add realistic network tests using speedtest-cli or iperf.
- Allow configuration via an external JSON/YAML file (implemented in this version).
- Save benchmark results for trend analysis (CSV persistence added).
- Integrate a web-based dashboard for real-time visualization (needs refinement).
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
import csv

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]"
)
logger = logging.getLogger("performance_tests")

# ===============================
# External Configuration
# ===============================
DEFAULT_CONFIG = {
    "CPU_ITERATIONS": 1000000,
    "MEMORY_MATRIX_SIZE": [10000, 10000],
    "DISK_TEST_SIZE_MB": 100
}

def load_config(config_file="config.json"):
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
            logger.info("Loaded configuration from %s", config_file)
            return config
        except Exception as e:
            logger.error("Error loading config file: %s", e)
            return DEFAULT_CONFIG
    else:
        logger.info("Config file %s not found. Using default configuration.", config_file)
        return DEFAULT_CONFIG

config = load_config()
CPU_ITERATIONS = config.get("CPU_ITERATIONS", DEFAULT_CONFIG["CPU_ITERATIONS"])
MEMORY_MATRIX_SIZE = tuple(config.get("MEMORY_MATRIX_SIZE", DEFAULT_CONFIG["MEMORY_MATRIX_SIZE"]))
DISK_TEST_SIZE_MB = config.get("DISK_TEST_SIZE_MB", DEFAULT_CONFIG["DISK_TEST_SIZE_MB"])

# Global constant for disk test file location
DISK_TEST_FILE = "/tmp/disk_test.bin"

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

def benchmark_gpu_details():
    """
    🎮 Extended GPU Benchmark:
    Captures GPU metrics such as utilization, temperature, and memory usage.
    Returns a dictionary of detailed GPU metrics.
    Note: The extended GPU metrics collected here can be integrated with a web-based dashboard.
          This integration is marked for future refinement.
    """
    try:
        # GPU Utilization
        utilization = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
            text=True
        ).strip()
        
        # GPU Temperature
        temperature = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
            text=True
        ).strip()
        
        # GPU Memory Usage (used and total)
        mem_usage = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
            text=True
        ).strip()
        mem_used, mem_total = [int(x.strip()) for x in mem_usage.split(",")]
        
        metrics = {
            "utilization": int(utilization),
            "temperature": int(temperature),
            "memory_used": mem_used,
            "memory_total": mem_total
        }
        logger.info("Extended GPU metrics: %s", metrics)
        return metrics
    except Exception as e:
        logger.error("Extended GPU benchmark failed: %s", e)
        return None

# ===============================
# Data Persistence: Save Results to CSV
# ===============================
def save_results_to_csv(results, csv_file="benchmark_results.csv"):
    """
    Saves benchmark results to a CSV file.
    If the file does not exist, it will be created with headers.
    """
    file_exists = os.path.isfile(csv_file)
    headers = ["timestamp", "cpu", "memory", "disk_write", "disk_read", "gpu", "gpu_details"]
    try:
        with open(csv_file, mode='a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(headers)
            disk_result = results.get("disk", {})
            gpu_details = results.get("gpu_details", {})
            writer.writerow([
                results.get("timestamp", datetime.now().isoformat()),
                results.get("cpu", ""),
                results.get("memory", ""),
                disk_result.get("write", ""),
                disk_result.get("read", ""),
                results.get("gpu", ""),
                gpu_details
            ])
        logger.info("Results saved to %s", csv_file)
    except Exception as e:
        logger.error("Failed to save results to CSV: %s", e)

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
        "gpu": benchmark_gpu(),
        "gpu_details": benchmark_gpu_details()
    }
    save_results_to_csv(results)
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
        "6": "Run Extended GPU Benchmark",
        "7": "Run All Benchmarks",
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
            gpu_details = benchmark_gpu_details()
            print(json.dumps({"gpu_details": gpu_details}, indent=4))
        elif choice == "7":
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
            results["gpu_details"] = benchmark_gpu_details()
        print(json.dumps(results, indent=4))
        # Optionally save results if not using the --menu option:
        if args.all:
            save_results_to_csv(results)

if __name__ == "__main__":
    main()

