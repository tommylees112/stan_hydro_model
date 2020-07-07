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
bernoulli_data: Dict = { "N" : 10, "y" : [0,1,0,0,0,0,0,0,0,1] }
data = pd.DataFrame({"y": bernoulli_data["y"]}, index=np.arange(bernoulli_data["N"]))

# ---- model ---- #
bernoulli_stan = Path(cmdstan_path()) / "examples/bernoulli/bernoulli.stan"
bernoulli_model = CmdStanModel(stan_file=bernoulli_stan)
bernoulli_model.compile()

# ---- fitting ---- #
bern_fit: CmdStanMCMC = bernoulli_model.sample(
    data=bernoulli_data,
    chains=4,
    cores=1,
    seed=1111,
    show_progress=True,
)

# ---- results ---- #
"""samples = multi-dimensional array
    all draws from all chains arranged as dimensions:
    (draws, chains, columns).
"""
posterior = az.from_cmdstanpy(
    posterior=bern_fit,
    posterior_predictive="y",
    # observed_data={"y": np.array(bernoulli_data["y"])},
)





# POSTERIOR PREDICTIVE CHECKS

# bernoulli_path =
bernoulli_ppc = CmdStanModel(stan_file=model_dir / "bernoulli_ppc.stan")

# fit the model to the data
bern_fit = bernoulli_ppc.sample(data=bernoulli_data)


# PRIOR PREDICTIVE CHECKS
# https://cmdstanpy.readthedocs.io/en/latest/sample.html
# generate data - fixed_param=True
datagen_stan = model_dir / "bernoulli.stan"
datagen_model = CmdStanModel(stan_file=datagen_stan)
datagen_model.compile()

sim_data = datagen_model.sample(fixed_param=True)
sim_data.summary()

drawset_pd = sim_data.get_drawset()
drawset_pd.columns

# extract new series of outcomes of N Bernoulli trials
y_sims = drawset_pd.drop(columns=['lp__', 'accept_stat__'])

# plot total number of successes per draw
y_sums = y_sims.sum(axis=1)
y_sums.astype('int32').plot.hist(range(0,datagen_data['N']+1))
