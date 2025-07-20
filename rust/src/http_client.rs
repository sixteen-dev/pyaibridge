use pyo3::prelude::*;
use pyo3::types::{PyDict, PyAny};
use pyo3_asyncio::tokio::future_into_py;
use reqwest::Client;
use serde_json::Value;
use std::collections::HashMap;
use std::time::Duration;
use futures_util::StreamExt;

use crate::errors::HttpError;
use crate::models::HttpResponse;

#[pyclass]
pub struct HttpClient {
    client: Client,
}

#[pymethods]
impl HttpClient {
    #[new]
    fn new() -> PyResult<Self> {
        let client = Client::builder()
            .timeout(Duration::from_secs(30))
            .pool_max_idle_per_host(10)
            .pool_idle_timeout(Duration::from_secs(90))
            .build()
            .map_err(|e| HttpError::RequestFailed(e))?;

        Ok(HttpClient { client })
    }

    #[pyo3(signature = (url, json_data=None, headers=None, timeout=None))]
    fn post<'py>(
        &self,
        py: Python<'py>,
        url: String,
        json_data: Option<&PyDict>,
        headers: Option<HashMap<String, String>>,
        timeout: Option<u64>,
    ) -> PyResult<&'py PyAny> {
        let client = self.client.clone();
        
        // Convert PyDict to serde_json::Value before async block to avoid Send issues
        let json_string = if let Some(json_data) = json_data {
            let json_value: Value = pythonize::depythonize(json_data)
                .map_err(|e| HttpError::JsonError(serde_json::Error::io(std::io::Error::new(std::io::ErrorKind::InvalidData, e))))?;
            Some(serde_json::to_string(&json_value).map_err(HttpError::JsonError)?)
        } else {
            None
        };
        
        future_into_py(py, async move {
            let mut request_builder = client.post(&url);

            // Add headers
            if let Some(headers) = headers {
                for (key, value) in headers {
                    request_builder = request_builder.header(&key, &value);
                }
            }

            // Add JSON body
            if let Some(json_str) = json_string {
                request_builder = request_builder
                    .header("Content-Type", "application/json")
                    .body(json_str);
            }

            // Set timeout
            if let Some(timeout_secs) = timeout {
                request_builder = request_builder.timeout(Duration::from_secs(timeout_secs));
            }

            // Execute request
            let response = request_builder
                .send()
                .await
                .map_err(HttpError::RequestFailed)?;

            // Convert headers
            let mut response_headers = HashMap::new();
            for (key, value) in response.headers() {
                if let Ok(value_str) = value.to_str() {
                    response_headers.insert(key.to_string(), value_str.to_string());
                }
            }

            let status = response.status().as_u16();
            let body = response.text().await.map_err(HttpError::RequestFailed)?;

            Ok(HttpResponse {
                status,
                headers: response_headers,
                body,
            })
        })
    }

    #[pyo3(signature = (url, headers=None, timeout=None))]
    fn get<'py>(
        &self,
        py: Python<'py>,
        url: String,
        headers: Option<HashMap<String, String>>,
        timeout: Option<u64>,
    ) -> PyResult<&'py PyAny> {
        let client = self.client.clone();
        
        future_into_py(py, async move {
            let mut request_builder = client.get(&url);

            // Add headers
            if let Some(headers) = headers {
                for (key, value) in headers {
                    request_builder = request_builder.header(&key, &value);
                }
            }

            // Set timeout
            if let Some(timeout_secs) = timeout {
                request_builder = request_builder.timeout(Duration::from_secs(timeout_secs));
            }

            // Execute request
            let response = request_builder
                .send()
                .await
                .map_err(HttpError::RequestFailed)?;

            // Convert headers
            let mut response_headers = HashMap::new();
            for (key, value) in response.headers() {
                if let Ok(value_str) = value.to_str() {
                    response_headers.insert(key.to_string(), value_str.to_string());
                }
            }

            let status = response.status().as_u16();
            let body = response.text().await.map_err(HttpError::RequestFailed)?;

            Ok(HttpResponse {
                status,
                headers: response_headers,
                body,
            })
        })
    }

    #[pyo3(signature = (url, json_data=None, headers=None, timeout=None))]
    fn post_stream<'py>(
        &self,
        py: Python<'py>,
        url: String,
        json_data: Option<&PyDict>,
        headers: Option<HashMap<String, String>>,
        timeout: Option<u64>,
    ) -> PyResult<&'py PyAny> {
        let client = self.client.clone();
        
        // Convert PyDict to serde_json::Value before async block to avoid Send issues
        let json_string = if let Some(json_data) = json_data {
            let json_value: Value = pythonize::depythonize(json_data)
                .map_err(|e| HttpError::JsonError(serde_json::Error::io(std::io::Error::new(std::io::ErrorKind::InvalidData, e))))?;
            Some(serde_json::to_string(&json_value).map_err(HttpError::JsonError)?)
        } else {
            None
        };
        
        future_into_py(py, async move {
            let mut request_builder = client.post(&url);

            // Add headers
            if let Some(headers) = headers {
                for (key, value) in headers {
                    request_builder = request_builder.header(&key, &value);
                }
            }

            // Add JSON body
            if let Some(json_str) = json_string {
                request_builder = request_builder
                    .header("Content-Type", "application/json")
                    .body(json_str);
            }

            // Set timeout
            if let Some(timeout_secs) = timeout {
                request_builder = request_builder.timeout(Duration::from_secs(timeout_secs));
            }

            // Execute request and get response
            let response = request_builder
                .send()
                .await
                .map_err(|e| PyErr::from(HttpError::RequestFailed(e)))?;

            // Get response metadata
            let mut response_headers = HashMap::new();
            for (key, value) in response.headers() {
                if let Ok(value_str) = value.to_str() {
                    response_headers.insert(key.to_string(), value_str.to_string());
                }
            }

            let status = response.status().as_u16();

            // Create a stream that yields text chunks
            let mut stream = response.bytes_stream();
            let mut chunks = Vec::new();
            
            while let Some(chunk) = stream.next().await {
                match chunk {
                    Ok(bytes) => {
                        if let Ok(text) = String::from_utf8(bytes.to_vec()) {
                            chunks.push(text);
                        }
                    }
                    Err(e) => return Err(HttpError::RequestFailed(e).into()),
                }
            }

            // For now, return all chunks joined together
            // In a real streaming implementation, we'd need to yield each chunk
            let body = chunks.join("");

            Ok(HttpResponse {
                status,
                headers: response_headers,
                body,
            })
        })
    }
}