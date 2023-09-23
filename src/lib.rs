use std::time::{Duration, Instant};

use pyo3::prelude::*;
use pyo3::types;
use rspotify::prelude::*;
use rspotify::AuthCodeSpotify;
use tokio::time::sleep;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
fn spotidl_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    Ok(())
}

fn generate_client(token: String) -> AuthCodeSpotify {
    let access_token = rspotify::Token {
        access_token: token,
        expires_in: chrono::Duration::seconds(3600),
        ..Default::default()
    };
    rspotify::AuthCodeSpotify::from_token(access_token)
}
