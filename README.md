# Bangalore Cab Fare Prediction

An end-to-end machine learning system for predicting Uber cab fares in Bangalore using automated route enrichment, fare data collection, temporal features, and a production-style prediction pipeline.

The project combines OpenStreetMap-based location data, GraphHopper routing, automated Uber fare collection, exploratory data analysis, time-aware model evaluation, and a Streamlit prediction application.

## Project Pipeline

```text
Trip Locations
      ↓
Trip Pair Generation
      ↓
GraphHopper Route Enrichment
      ↓
Validated Uber Routes
      ↓
Uber Fare Collection
      ↓
Processed Fare Dataset
      ↓
EDA & Feature Engineering
      ↓
Model Training & Evaluation
      ↓
Final Random Forest Model
      ↓
Streamlit Prediction App
```

## Project Scale

| Component | Scale |
|---|---:|
| Trip pairs generated | 25,000 |
| Bangalore locations | 247+ |
| Fare observations | 15,300+ |
| Routes represented | 750 |
| Uber ride types | 23 |
| Final test observations | 5,987 |

## Features

- Bangalore pickup and dropoff location selection
- Automatic route lookup
- Road distance and travel time
- Automatic current day/time detection
- Time-slot based fare prediction
- Predictions for 23 Uber ride types
- Log-transformed target modeling
- Date/time-aware cross-validation
- Missing-value and outlier analysis
- Model error analysis
- Interactive Streamlit interface
- Sorted fare comparison table
- Automated route enrichment using GraphHopper
- Automated Uber fare collection using Playwright

## Dataset

The processed fare dataset contains information including both modeling features and auxiliary fare-collection fields:

- Timestamp
- Time slot
- Day of week
- Pickup and dropoff
- Pickup and dropoff categories
- Road distance
- Travel time
- Ride type
- Seats
- Uber ETA
- Current fare

### Final Model Features

```text
road_distance_km
travel_time_minutes
ride_name
pickup_category
drop_category
time_slot
day_of_week
pickup
dropoff
```

Target:

```text
current_price
```

`seats` and `eta_minutes` were retained in the processed dataset for analysis but were excluded from the final model.

## Exploratory Data Analysis

The EDA covered:

- Dataset structure and cardinality
- Missing-value analysis
- Target distribution
- Numerical feature distributions
- Correlation analysis
- Ride-type analysis
- Pickup/dropoff analysis
- Temporal patterns
- Route frequency
- Outlier analysis
- Zero-fare investigation
- Feature importance
- Feature selection

A single zero-fare observation was identified as anomalous and removed before modeling.

`seats` and `eta_minutes` were excluded because of substantial/systematic missingness and prediction-time availability considerations.

## Machine Learning

### Final Model

The final model is a **Random Forest Regressor with a log-transformed target**.

The target is transformed using:

```python
np.log1p(y)
```

and converted back using:

```python
np.expm1(prediction)
```

The transformation helps handle the right-skewed fare distribution.

### Validation Strategy

Because fare observations were collected over time and routes can have repeated observations, chronological/date-based evaluation was used instead of relying only on a random train-test split.

The dataset was divided into:

```text
Full Dataset
      │
      ├── Development Data
      │       │
      │       └── 4 Expanding Date-Based CV Folds
      │
      └── Chronological Test Set
```

The development data was evaluated using four expanding date-based cross-validation folds followed by a held-out chronological test set.

This approach better reflects the intended use case of predicting future fares using information available up to the prediction time.

## Model Performance

Final 9-feature log-target Random Forest:

| Metric | Test Performance |
|---|---:|
| MAE | ₹67.38 |
| RMSE | ₹129.48 |
| R² | 0.9262 |

The model achieved an R² of approximately 0.93 on the held-out test set.

## Error Analysis

The final model was evaluated using more than aggregate metrics.

Key observations:

- 62.99% of test predictions had an absolute error ≤ ₹50.
- 81.38% had an absolute error ≤ ₹100.
- 92.30% had an absolute error ≤ ₹200.
- Larger errors were concentrated more heavily among high-fare observations.
- Some rental and premium ride types showed larger errors.
- Very expensive and longer-distance trips were generally harder to predict accurately.

## Feature Importance

Feature importance analysis showed that the model relied primarily on:

1. Ride type
2. Road distance
3. Travel time
4. Time slot
5. Pickup location
6. Dropoff location
7. Day of week
8. Pickup category
9. Dropoff category

The strongest individual predictive signals came from **ride type** and **road distance**, followed by travel time and temporal/location information.

## Streamlit Application

The application is located at:

```text
app.py
```

Users can:

1. Select a pickup location.
2. Select a compatible dropoff location.
3. View the automatically retrieved route distance and travel time.
4. Automatically determine the current day/time and corresponding model time slot.
5. Predict fares for all supported ride types.
6. Compare predicted fares in a sorted table.

### Run the Application

```bash
streamlit run app.py
```

## Automated Data Collection Pipeline

The project includes an automated pipeline for generating routes and collecting Uber fare observations.

### Location Data

Bangalore pickup and dropoff locations are based on **OpenStreetMap (OSM)** data.

### Trip Pair Generation

The project generates pickup/dropoff trip pairs from the available Bangalore locations.

### Route Enrichment

Trip pairs are enriched with:

- Road distance
- Estimated travel time

using the **GraphHopper Routing API**.

### Uber Route Validation

Candidate routes are validated before being added to the pool of routes used for fare collection.

### Uber Fare Collection

Uber fare observations are collected automatically using **Playwright**.

The collected observations include information such as:

- Timestamp
- Time slot
- Day of week
- Pickup
- Dropoff
- Ride type
- Current price
- Original price
- ETA
- Promotion information

The collected fare observations are subsequently processed and merged with route metadata to create the modeling dataset.

## Project Structure

```text
Bangalore_Cab_Fare_Prediction/
│
├── app.py
│
├── collector/
│   ├── collectors/
│   ├── services/
│   ├── scripts/
│   ├── parsers/
│   ├── validators/
│   └── ...
│
├── config/
│   ├── collection_schedule.py
│   ├── routing.py
│   ├── sampling.py
│   └── ...
│
├── data/
│   ├── processed/
│   │   ├── fares/
│   │   │   └── uber_fares_processed.csv
│   │   │
│   │   └── routes/
│   │       ├── routes.csv
│   │       ├── uber_validated_routes.csv
│   │       └── uber_rejected_routes.csv
│   │
│   └── training/
│
├── models/
│   ├── fare_estimate.py
│   └── final_fare_prediction_model.joblib
│
├── notebooks/
│   ├── 01_eda_fare_dataset.ipynb
│   └── 02_baseline_model.ipynb
│
├── research/
│
├── tests/
│
├── requirements.txt
├── .gitignore
├── .gitattributes
└── README.md
```

## Model Artifact

The trained model is saved as:

```text
models/final_fare_prediction_model.joblib
```

The saved model contains the required preprocessing and Random Forest prediction pipeline.

Since the model predicts the log-transformed target, predictions are converted back to the original fare scale using:

```python
predicted_fares = np.expm1(predicted_log_fares)
```

### Git LFS

The trained model is approximately 1 GB and is stored using **Git Large File Storage (Git LFS)**.

After cloning the repository, initialize Git LFS and download the model:

```bash
git lfs install
git lfs pull
```

## Technologies Used

### Data Collection & Routing

- Python
- OpenStreetMap (OSM)
- GraphHopper Routing API
- Playwright
- Automated Uber fare collection

### Data Processing & Machine Learning

- Pandas
- NumPy
- Scikit-learn
- Random Forest
- Joblib
- Jupyter Notebook

### Application

- Streamlit

### Development & Testing

- Git
- Git LFS
- Python virtual environments
- Automated test scripts

## Key Engineering Decisions

### Automatic Route Information

Users do not manually enter distance or travel time. The application retrieves route information from the validated route dataset based on the selected pickup/dropoff pair.

### Multiple Ride Types

The application predicts fares for all supported ride types so their estimated prices can be compared.

### Time-Aware Evaluation

Fare behavior changes over time, so chronological/date-based evaluation was used to better reflect future prediction behavior.

### Log-Transformed Target

The fare distribution is positively skewed with a small number of expensive trips. A log transformation was used for the final Random Forest model.

### Route Feature Selection

Route-level information was evaluated during model development but was not included as a final model feature because route is effectively represented by the combination of pickup and dropoff locations and introduces additional high-cardinality information.

## Limitations

- Predictions are estimates and may differ from real-time Uber prices.
- Surge pricing and rapidly changing market conditions may not be fully captured.
- Very high-fare observations are harder to predict accurately.
- Model performance depends on the coverage of the collected dataset.
- New pickup/dropoff combinations outside the validated route pool are not currently selectable.

## Future Improvements

- Collect a larger historical dataset
- Increase Bangalore location coverage
- Add additional ride providers
- Incorporate real-time traffic information
- Model surge/price multipliers explicitly
- Experiment with XGBoost or LightGBM
- Add prediction intervals
- Deploy the Streamlit application publicly

## How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/Mac-Works137/Bangalore-Cab-Fare-Prediction.git
cd Bangalore-Cab-Fare-Prediction
```

### 2. Initialize Git LFS

```bash
git lfs install
git lfs pull
```

### 3. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the Application

```bash
streamlit run app.py
```

The application will be available at the local Streamlit URL shown in the terminal.

## Notes on Data

The repository contains processed datasets required to understand the modeling workflow.

Raw collected fare data and local browser/session artifacts are intentionally excluded from version control.

The trained final model is included through Git LFS so that the Streamlit application can be run without retraining the model.

## Author

**Mayank Sharma**

M.E. Computer Science  
BITS Pilani, Goa Campus
