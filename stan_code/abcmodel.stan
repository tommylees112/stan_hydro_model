functions{
    // System state S is one dimensional storage
    // The evolution of S is determined by 2 parameters
    //  a: proportion of Precipitation (P) to Storage (S)
    //  c: Proportion of Storage (S) to Slow Flow (Qs)
    // And driven by the changes in
    //  P: precipitation inputs
    real[] ode_abcmodel_state(
        real t,
        real P,
        real[] S,
        real[] theta,
        real[] x_r,
        real[] x_i,
    ){
        real a;
        real b;
        real dSdt;

        a = theta[1];
        b = theta[2];

        dSdt = (a * P) - (c * S);

        return dSdt;
    }

    /**
    * ABC Hydrological Model
    * Compute total simulated flow from the system given
    *  parameters and times. This is done by simulating
    *  the system storage defined in ode_abcmodel_state
    *
    * Parameters:
    * ----------
    *  @param T : number of times
    *  @param t0: initial time
    *  @param ts: observation times
    *  @param P: observation for Precipitation
    *  @param a : proportion of Precipitation (P) to Storage (S)
    *  @param b : proportion of Precipitation (P) lost to evaporation
    *  @param c : Proportion of Storage (S) to Slow Flow (Qs)
    *  @return Q: evolved discharge for times ts
    */
    real[] abcmodel(
        int T;
        real t0;
        real[] ts;
        real[] P,
        real a;
        real b;
        real c;
        real[] x_r;
        real[] x_i;
    ){
        real S_t0;          // initial state
        real theta[3];      // ABCModel parameters
        real S_hat[T];      // predicted Storage content
        real Qsim[T];       // simulated flow

        // initialise parameters
        theta[1] = a;
        theta[2] = b;
        theta[3] = c;

        // integrate the system
        // HOW TO PASS IN P[t] ??
        S_hat = integrate_ode_rk45(
            ode_abcmodel_state,
            S_t0, t0, ts, theta
        );

        # calculate system evolution over time
        for (t in 1: T)
            S[t] = ((1 - c) * S_hat[t - 1]) + (a * P[t]);
            Qs[t] = c * S[t];
            // L[t] = b * P[t]
            Qf[t] = (1 - a - b) * P[t];
            Qsim[t] = Qf[t] + Qs[t];

        return Qsim;
    }

}

data{
    int<lower=0> T;
    real Q[T];      // measured flow
    real P[T];      // measured precipitation
    real S_t0;      // initial storage
}

transformed data{
    // Why are these here? Copied from example
    real x_r[0];    // no real data for ODE system
    int x_i[0];     // no integer data for ODE system
}

parameters{
    real<lower=0, upper=1> a;
    real<lower=0, upper=1> b;
    real<lower=0, upper=1> c;
    real<lower=0, upper=1> sigma;
}

transformed parameters{
    real Qsim[T];   // process model for flow (Q)

    Qsim = abcmodel(
        T, t0, ts, P, a, b, c, x_r, x_i
    );
}

model{
    // Priors
    // What priors to choose?
    a ~ normal(0.5, 1);
    b ~ normal(0.5, 1);
    c ~ normal(0.5, 1);
    sigma ~ normal(0, 1);

    # normal measurement error of Q
    for (t in 1: T)
        Q[t] ~ normal(sim_Q[t], sigma);
}
