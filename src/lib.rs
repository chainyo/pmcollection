use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3_asyncio::tokio::future_into_py;
use tokio::sync::Semaphore;
use reqwest::Client;
use futures::stream::{self, StreamExt};
use std::fs;
use std::path::Path;
use std::sync::Arc;

#[pyfunction]
fn download_files(py: Python, urls: Vec<String>, cache_folder: String, concurrency_limit: usize) -> PyResult<&PyAny> {
    future_into_py(py, async move {
        let client = Client::new();
        let semaphore = Arc::new(Semaphore::new(concurrency_limit));
        let cache_folder = Path::new(&cache_folder);
        fs::create_dir_all(cache_folder).unwrap();

        let fetches = stream::iter(urls)
            .map(|url| {
                let client = client.clone();
                let semaphore = semaphore.clone();
                let cache_folder = cache_folder.to_path_buf();
                async move {
                    let _permit = semaphore.acquire().await.unwrap();
                    match fetch_and_save(&client, &url, &cache_folder).await {
                        Ok(_) => println!("Downloaded: {}", url),
                        Err(e) => eprintln!("Failed to download {}: {}", url, e),
                    }
                }
            })
            .buffer_unordered(concurrency_limit);

        fetches.collect::<Vec<()>>().await;

        Ok(())
    })
}

async fn fetch_and_save(client: &Client, url: &str, cache_folder: &Path) -> Result<(), reqwest::Error> {
    let response = client.get(url).send().await?.bytes().await?;
    let file_name = url.split('/').last().unwrap();
    let file_path = cache_folder.join(file_name);

    tokio::fs::write(file_path, &response).await?;

    Ok(())
}

#[pymodule]
fn download_utils(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(download_files, m)?)?;
    Ok(())
}
