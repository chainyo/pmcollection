use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3_asyncio::tokio::future_into_py;
use tokio::sync::Semaphore;
use reqwest::Client;
use std::fs;
use std::path::Path;
use std::sync::Arc;
use tokio::io::AsyncWriteExt;


#[pyfunction]
fn download_files(py: Python, urls: Vec<String>, cache_folder: String, concurrency_limit: usize) -> PyResult<&PyAny> {
    future_into_py(py, async move {
        let client = Arc::new(Client::new());
        let semaphore = Arc::new(Semaphore::new(concurrency_limit));
        let cache_folder = Path::new(&cache_folder);
        fs::create_dir_all(cache_folder).unwrap();

        let mut handles = vec![];

        for url in urls {
            let client = Arc::clone(&client);
            let semaphore = Arc::clone(&semaphore);
            let cache_folder = cache_folder.to_path_buf();
            
            let handle = tokio::spawn(async move {
                let _permit = semaphore.acquire().await.unwrap();
                match fetch_and_save(&client, &url, &cache_folder).await {
                    Ok(_) => 1,
                    Err(_) => 0,
                }
            });

            handles.push(handle);
        }

        let mut success_count = 0;
        let mut failure_count = 0;

        for handle in handles {
            match handle.await {
                Ok(result) => {
                    if result == 1 {
                        success_count += 1;
                    } else {
                        failure_count += 1;
                    }
                },
                Err(_) => failure_count += 1,
            }
        }

        println!("Downloaded {} files successfully.", success_count);
        println!("Failed to download {} files.", failure_count);

        Ok(())
    })
}


async fn fetch_and_save(client: &Client, url: &str, cache_folder: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let response = client.get(url).send().await?.bytes().await?;
    let file_name = url.split('/').last().unwrap();
    let file_path = cache_folder.join(file_name);

    let mut file = tokio::fs::File::create(file_path).await?;
    file.write_all(&response).await?;
    file.flush().await?;

    Ok(())
}


#[pymodule]
#[pyo3(name="_lowlevel")]
fn pmcollection(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(download_files, m)?)?;

    Ok(())
}
