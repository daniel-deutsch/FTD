def ADF_test(series, significance_level='5%'):
    results = {}

    critical_values = { '1%': -4.04, '5%': -3.45, '10%': -3.15 }
    adf_res = smt.adfuller(series.dropna(), regression='ct', maxlag=12)
    if abs(adf_res[0]) >= abs(critical_values[significance_level]):
        return "The series is I(0)"
    else:
        critical_values = { '1%': 3.53, '5%': 2.79, '10%': 2.38 }
        adf_res = smt.adfuller(series.dropna(), regression='c', maxlag=12)
        if abs(adf_res[0]) >= abs(critical_values[significance_level]): # b1 is significant
            critical_values = { '1%': -2.33, '5%': -1.64, '10%': -1.3 }
            adf_res = smt.adfuller(series.dropna(), regression='ct', maxlag=12)  # Should be normal distribution
            if abs(adf_res[0]) >= abs(critical_values[significance_level]):   # b0 is significant
                return "The series doesn't have a unit root"
            else:
                return "The	series has a unit root and a deterministic trend"
        else:   # b1 is not significant
            critical_values = { '1%': -3.51, '5%': -2.89, '10%': -2.58 }
            adf_res = smt.adfuller(series.dropna(), regression='n', maxlag=12)
            if 