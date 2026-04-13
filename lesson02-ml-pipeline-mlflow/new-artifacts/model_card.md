
# Model Card - Hospital Readmission

## Objective

Predict the probability of readmission within 30 days.

## Features

- age
- length_of_stay
- num_comorbidities
- num_medications

## Primary Metrics

- Accuracy: 0.6600
- F1-score: 0.7763
- Training size: 400
- Test size: 100

## Limitations

- Synthetic data; does not replace validation with real data.
- MLflow tracking is optional and depends on the local environment.
