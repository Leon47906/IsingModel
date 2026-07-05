use pyo3::prelude::*;
use rand::Rng;

#[pyfunction]
fn print_random_number() {
    let random_number = rand::rng().random_range(1..101);
    println!("The random number is {random_number}!");
}

#[pymodule]
fn ising_model(m : &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(print_random_number,m)?)?;

    Ok(())
}
