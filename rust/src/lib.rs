use pyo3::prelude::*;

mod http_client;
mod models;
mod errors;

use http_client::HttpClient;
use models::HttpResponse;

#[pymodule]
fn pyaibridge_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<HttpClient>()?;
    m.add_class::<HttpResponse>()?;
    Ok(())
}