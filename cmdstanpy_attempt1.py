from pathlib import Path
import cmdstanpy
from cmdstanpy import cmdstan_path, CmdStanModel, CmdStanMCMC
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict
import arviz as az
import os

cmdstanpy.CMDSTAN_PATH = "/Users/tommylees/.cmdstanpy/cmdstan-2.21.0"
print(cmdstan_path())

def clear_pre_existing_files():
    os.system(
        """
        pchs=`find . -name "*.gch"`;
        for f in $pchs; do rm $f; done;
        """
    )
    os.system(
        """
        hpps=`find . -name "*.hpp"`;
        for f in $hpps; do rm $f; done;
        """
    )
    print("Deleted *.hpp and *.gch files")


if __name__ == "__main__":
    clear_pre_existing_files()

    # set the directories
    model_dir = Path("stan_code")
    data_dir = Path("data")

    data = pd.read_csv(data_dir / "cherwell_station.csv")

    # ---- data ---- #
    Q: np.ndarray = data["discharge_spec"].values
    precip: np.ndarray = data["precipitation"].values
    initial_state: float = 0.0

    discharge_data: Dict = { "T" : len(Q), "Q" : Q , "P":  precip, "S_t0": initial_state}

    # ---- model ---- # 
    stan_file = model_dir / "bernoulli.stan"
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