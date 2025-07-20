use pyo3::prelude::*;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum HttpError {
    #[error("Request failed: {0}")]
    RequestFailed(#[from] reqwest::Error),
    
    #[error("JSON serialization failed: {0}")]
    JsonError(#[from] serde_json::Error),
    
    #[error("Invalid URL: {0}")]
    InvalidUrl(String),
    
    #[error("Timeout: {0}")]
    Timeout(String),
    
    #[error("Rate limited: {0}")]
    RateLimited(String),
}

impl From<HttpError> for PyErr {
    fn from(err: HttpError) -> PyErr {
        match err {
            HttpError::RequestFailed(e) => {
                pyo3::exceptions::PyConnectionError::new_err(e.to_string())
            }
            HttpError::JsonError(e) => {
                pyo3::exceptions::PyValueError::new_err(e.to_string())
            }
            HttpError::InvalidUrl(e) => {
                pyo3::exceptions::PyValueError::new_err(e)
            }
            HttpError::Timeout(e) => {
                pyo3::exceptions::PyTimeoutError::new_err(e)
            }
            HttpError::RateLimited(e) => {
                pyo3::exceptions::PyRuntimeError::new_err(e)
            }
        }
    }
}