"""Benchmark the download speed of the dataset using python tools and the rust custom method"."""

import asyncio
import gzip
import shutil
import time
from pathlib import Path

import aiohttp
import aiofiles

from pmcollection._lowlevel import download_files as download_files_rust


async def download_file(session, url, cache_folder):
    async with session.get(url) as response:
        response.raise_for_status()
        content = await response.read()

        file_name = url.split("/")[-1]
        file_path = Path(cache_folder) / file_name

        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)

        # Decompress the file
        decompressed_file_path = file_path.with_suffix('')
        with gzip.open(file_path, 'rb') as f_in:
            with open(decompressed_file_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

async def download_files_python(urls, cache_folder, concurrency_limit):
    Path(cache_folder).mkdir(parents=True, exist_ok=True)
    connector = aiohttp.TCPConnector(limit_per_host=concurrency_limit)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [download_file(session, url, cache_folder) for url in urls]
        await asyncio.gather(*tasks)

def measure_time(func):
    start_time = time.time()
    func()
    end_time = time.time()
    return end_time - start_time

async def benchmark_python(urls, cache_folder, concurrency_limit):
    await download_files_python(urls, cache_folder, concurrency_limit)

async def benchmark_rust(urls, cache_folder, concurrency_limit):
    await download_files_rust(urls, cache_folder, concurrency_limit)

def run_benchmarks():
    urls = [
        f"https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/pubmed24n{i:04d}.xml.gz"
        for i in range(1, 21)  # Use the first 10 files for benchmarking
    ]
    cache_folder_python = "./tmp_python"
    cache_folder_rust = "./tmp_rust"
    concurrency_limit = 15
    iterations = 50

    rust_times = []
    python_times = []
    for _ in range(iterations):
        # Benchmark Rust implementation
        rust_time = measure_time(lambda: asyncio.run(benchmark_rust(urls, cache_folder_rust, concurrency_limit)))
        print(rust_time)
        rust_times.append(rust_time)
        # Benchmark Python implementation
        python_time = measure_time(lambda: asyncio.run(benchmark_python(urls, cache_folder_python, concurrency_limit)))
        print(python_time)
        python_times.append(python_time)

    avg_rust_time = sum(rust_times) / len(rust_times)
    print(f"Rust implementation average time over {iterations} runs: {avg_rust_time} seconds")
    avg_python_time = sum(python_times) / len(python_times)
    print(f"Python implementation average time over {iterations} runs: {avg_python_time} seconds")

if __name__ == "__main__":
    run_benchmarks()
