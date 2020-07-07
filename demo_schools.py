from pathlib import Path
from cmdstanpy import cmdstan_path, CmdStanModel, CmdStanMCMC
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict
import arviz as az


model_dir = Path("stan_code")
data_dir = Path("data")

# ---- data ---- #
eight_school_data = {
    "J": 8,
    "y": np.array([28.0, 8.0, -3.0, 7.0, -1.0, 1.0, 18.0, 12.0]),
    "sigma": np.array([15.0, 10.0, 16.0, 11.0, 9.0, 11.0, 10.0, 18.0]),
}

# ---- model ---- #
stan_file = model_dir / "schools.stan"
stan_model = CmdStanModel(stan_file=stan_file)
stan_model.compile()

# ---- fitting ---- #
stan_fit = stan_model.sample(data=eight_school_data)

# ---- results ---- #
cmdstanpy_data = az.from_cmdstanpy(
    posterior=stan_fit,
    posterior_predictive="y_hat",
    observed_data={"y": eight_school_data["y"]},
    log_likelihood="log_lik",
    coords={"school": np.arange(eight_school_data["J"])},
    dims={
        "theta": ["school"],
        "y": ["school"],
        "log_lik": ["school"],
        "y_hat": ["school"],
        "theta_tilde": ["school"],
    },

