Thanks @xiehw really appreciate the help!

**1) Stiff system?**
If I'm honest I am not certain what a stiff system is. From my brief glance at Wikipedia I don't think it's a particularly sensitive system and so I would say it's not stiff.

**2) Univariate / Bivariate Model**

So $P_t$ is the input / forcing data for the process model. I don't think i want to fit a bivariate model. My understanding is that I am currently observing the discharge. Eventually, in a more complex model, we also observe (very noisily) the soil moisture / storage ($S_t$).

**3) Stan Case Study**

I had not seen that case study, thanks so much for sharing! I hadn't checked the case studies before 2016. I am just writing the system below in the same format as the case study.

The system dynamics are modelled through:
$Q_t = Qf_t + Qs_t$
$Qf_t = (1-a-b) P_t$
$Qs_t = c S_t$
$S_t = (1-c) S_{t-1} + aP_t$
$L_t = bP_t$

Where:
$Q_t $ = River Flow
$Qf_t$ = Fast Flow
$Qs_t$ = Slow Flow
$S_t $ = Storage
$L_t $ = Losses

I want to solve the equations for $Q_{t}$ at measurement times $t = {1, ..., T}$

My updated stan code is here:

```stan
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
        real[] theta;
        real[] x_r;
        real[] x_i;
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
    a ~ beta(0.5, 1);
    b ~ beta(0.5, 1);
    c ~ beta(0.5, 1);
    sigma ~ normal(0, 1);

    # normal measurement error of Q
    for (t in 1: T)
        Q[t] ~ normal(sim_Q[t], sigma);
}
```

**Some questions:**
- What are `x_r` and `x_i`, vectors passed to the `ode_abcmodel_state` function (and the `two_pool_feedback` function in the example)?
- How do I pass the Precipitation vector (P[t]) into the `ode_abcmodel_state` function?
- How should I think about the difference between `ode_abcmodel_state` and `abcmodel`. Are these implemented correctly?
- What priors would be sensible starting points, the only real information I have is the bounds between 0-1 given that this is a highly idealised system. Although c is likely much smaller than a, b.
