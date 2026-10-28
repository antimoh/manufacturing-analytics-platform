# Dataset Documentation

## UCI AI4I 2020 Predictive Maintenance Dataset

### Source Information

- **Name:** AI4I 2020 Predictive Maintenance Dataset
- **Source:** UCI Machine Learning Repository
- **URL:** https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset
- **DOI:** https://doi.org/10.24432/C5HS5C
- **License:** CC BY 4.0

### Dataset Nature

This is a **synthetic dataset** designed for predictive maintenance research and educational purposes. It was created to reflect realistic industrial operating conditions and failure patterns.

**Important:** This is not real production data. It was generated to simulate manufacturing scenarios for research purposes.

### Dataset Characteristics

| Property | Value |
|----------|-------|
| Rows | 10,000 |
| Columns | 12 |
| Missing Values | 0 |
| Duplicate Rows | 0 |
| Machine Failures | 339 (3.39%) |

### Columns

| Column Name | Description | Type |
|-------------|-------------|------|
| Type | Machine type (L, M, H) | Categorical |
| Air temperature [K] | Air temperature in Kelvin | Numeric |
| Process temperature [K] | Process temperature in Kelvin | Numeric |
| Rotational speed [rpm] | Rotational speed in RPM | Numeric |
| Torque [Nm] | Torque in Newton-meters | Numeric |
| Tool wear [min] | Tool wear in minutes | Numeric |
| Machine failure | Binary failure indicator (0/1) | Binary |
| TWF | Tool Wear Failure indicator | Binary |
| HDF | Heat Dissipation Failure indicator | Binary |
| PWF | Power Failure indicator | Binary |
| OSF | Overstrain Failure indicator | Binary |
| RNF | Random Failure indicator | Binary |

### Machine Types

- **L:** Low quality variant (50% of data)
- **M:** Medium quality variant (30% of data)
- **H:** High quality variant (20% of data)

### Failure Modes

1. **TWF (Tool Wear Failure):** The tool will be replaced or fail at randomly selected tool wear times between 200-240 minutes.

2. **HDF (Heat Dissipation Failure):** Heat dissipation causes process failure if the difference between air and process temperature is below 8.6 K and rotational speed is below 1380 rpm.

3. **PWF (Power Failure):** Power = Torque × Rotational Speed. Process fails if power is below 3500 W or above 9000 W.

4. **OSF (Overstrain Failure):** If the product of tool wear and torque exceeds certain thresholds depending on machine type.

5. **RNF (Random Failure):** Each process has a 0.1% chance of random failure regardless of parameters.

### Attribution

When using this dataset, please cite:

> UCI Machine Learning Repository. AI4I 2020 Predictive Maintenance Dataset. 
> https://doi.org/10.24432/C5HS5C

### Usage Notes

- The failure rate is low (3.39%), which is realistic for industrial settings but requires careful analysis approaches.
- The `Machine failure` column indicates overall failure; specific failure modes are indicated in the TWF, HDF, PWF, OSF, and RNF columns.
- A machine can fail (Machine failure = 1) even when all specific failure mode indicators are 0 (documented dataset behavior).
- All sensor readings are synthetic and calibrated to realistic industrial ranges.
