import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import datasets
from evidently.report import Report
from evidently.metrics import DataDriftTable
from evidently.metrics import DatasetDriftMetric


def k_s_drift_detector(baseline_data, new_data):
    ''' Kolmogorov-Smirnov Test '''
    baseline_data = np.random.normal(loc=0.0, scale=1.0, size=1000)
    new_data = np.random.normal(loc=2.0, scale=1.0, size=1000)

    plt.figure(figsize=(10, 5))
    sns.kdeplot(baseline_data, label='Baseline Data (N(0,1))', linewidth=2)
    sns.kdeplot(new_data, label='New Data (N(2,1))', linewidth=2)
    plt.title("Baseline vs. New Data Distribution")
    plt.xlabel("Feature Value")
    plt.ylabel("Density")
    plt.legend()
    plt.tight_layout()
    plt.show()

    ks_statistic, ks_pvalue = ks_2samp(baseline_data, new_data)
    print("Kolmogorov-Smirnov Test Result:")
    print(f"Statistic: {ks_statistic:.4f}")
    print(f"P-value  : {ks_pvalue:.4f}")

    # P-value < 0.05, then we can say significant drift is detected.
    if ks_pvalue < 0.05:
        print("Drift Detected (p < 0.05)")
    else:
        print("No Significant Drift Detected")

# Using Evidently open source software to calculate data drift
def evidently_drift_detection():
    ''' create ref and cur dataset for drift detection '''
    adult_data = datasets.fetch_openml(name='adult', version=2, as_frame='auto')
    adult = adult_data.frame
    adult_ref = adult[~adult.education.isin(['Some-college', 'HS-grad', 'Bachelors'])]
    adult_cur = adult[adult.education.isin(['Some-college', 'HS-grad', 'Bachelors'])]
    adult_cur.iloc[:2000, 3:5] = np.nan
    #dataset-level metrics
    data_drift_dataset_report = Report(
        metrics=[
            DatasetDriftMetric(),
            DataDriftTable()
        ]
    )
    data_drift_dataset_report.run(reference_data=adult_ref, current_data=adult_cur)
    #data_drift_dataset_report
    #report in a JSON format
    data_drift_dataset_report.json()
    data_drift_dataset_report.as_dict()
