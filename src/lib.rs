use core::f64;

use pyo3::prelude::*;
use rand::{Rng,SeedableRng};
use rand::rngs::StdRng;


#[pyclass]
#[derive(Debug)]
struct Lattice {
    #[pyo3(get)]
    width: usize,
    #[pyo3(get)]
    height: usize,
    sites: Vec<i8>,
    #[pyo3(get, set)]
    temperature: f64,
    #[pyo3(get, set)]
    h_z: f64,
    rng: StdRng
}

#[pymethods]
impl Lattice {
    #[new]
    pub fn new(width: usize, height: usize, temperature: f64, h_z: f64) -> Self {
        let mut rng = StdRng::from_os_rng();
        let sites: Vec<i8> = (0..width*height).map(|_| if rng.random_bool(0.5) {1} else {-1} ).collect();
        Self {
            width,
            height,
            sites,
            temperature,
            h_z,
            rng
        }
    }

    fn flat_to_idx(&self, flat_idx: usize) -> [usize; 2] {
        if flat_idx >= self.width * self.height { panic!("Accessing out of bounds!") }
        [flat_idx/self.width,flat_idx%self.width]
    }

    fn idx_to_flat(&self, row: usize, col: usize) -> usize {
        if row >= self.height || col >= self.width { panic!("Accessing out of bounds!") }
        row * self.width + col
    }
    
    fn get_nearest_neighbors(&self, flat_idx: usize) -> [usize; 4] {
        if flat_idx >= self.width * self.height {
            panic!("Accessing out of bounds!")
        }
        let [row, col] = self.flat_to_idx(flat_idx);
        let w = self.width;
        let h = self.height;

        let up    = (row + h - 1) % h;
        let down  = (row + 1) % h;
        let left  = (col + w - 1) % w;
        let right = (col + 1) % w;

        [
            self.idx_to_flat(row, left),
            self.idx_to_flat(up, col),
            self.idx_to_flat(row, right),
            self.idx_to_flat(down, col),
        ]
    }
    fn get_energy(&self) -> f64 {
        let mut energy = 0.0;
        for idx in 0..self.sites.len() {
            let s_i = self.sites[idx] as f64;
            let neighbors = self.get_nearest_neighbors(idx);
            let neighbor_sum: f64 = neighbors.iter().map(|&n| self.sites[n] as f64).sum();
            energy += - s_i * neighbor_sum / 2.0 - self.h_z * s_i;
        }
        energy
    }

    fn get_energy_diff_from_flip(&self, flat_idx: usize) -> f64 {
        let s_i = self.sites[flat_idx] as f64;
        let neighbor_sum: f64 = self.
            get_nearest_neighbors(flat_idx).
            into_iter().
            map(|idx| self.sites[idx] as f64).
            sum();

        2.0 * s_i * (neighbor_sum + self.h_z)
    }

    pub fn simulation_step(&mut self) {
        let flat_idx = self.rng.random_range(0..self.width*self.height);
        let energy_diff = self.get_energy_diff_from_flip(flat_idx);
        if energy_diff <= 0.0 || self.rng.random::<f64>() < (-energy_diff /
            self.temperature).exp() {
            self.sites[flat_idx] *= -1;
        }
    }

    fn get_total_magnetization(&self) -> f64 {
        self.sites.iter().map(|&s| s as f64).sum()
    }

    fn average_magnetization(&self) -> f64 {
        self.get_total_magnetization() as f64 / (self.width * self.height) as f64
    }

    fn as_array(&self) -> Vec<i8> {
        self.sites.clone()
    }

    fn __repr__(&self) -> String {
        format!("{:?}", self)
    }
}

#[pymodule]
fn ising_model(m : &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Lattice>()?;

    Ok(())
}

