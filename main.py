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
discharge_data: Dict = { "T" : len(Q), "Q" : Q , "P":  precip}

# ---- model ---- # 
stan_file = model_dir / "abcmodel.stan"
stan_model = CmdStanModel(stan_file=stan_file)
stan_model.compile()

# ---- fit parameters ---- # 
abcmodel_fit: CmdStanMCMC = stan_model.sample(
    data=discharge_data,
    chains=4,
    cores=1,
    seed=1111,
    show_progress=True,
)

# ---- get simulations ---- #
posterior = az.from_cmdstanpy(
    posterior=bern_fit,
    posterior_predictive="y",
)
