data{
    int<lower=0> T;
    real Q[T];      // measured flow
    real P[T];      // measured precipitation
    real S_t0;      // initial storage
}

parameters{
    real<lower=0, upper=1> a;
    real<lower=0, upper=1> b;
    real<lower=0, upper=1> c;
    real<lower=0, upper=1> sigma;
}

transformed parameters{
    real Qsim[T];
    real Qs[T];
    real Qf[T];
    real S[T];

    // process model for flow (Q)
    S[1] = S_t0;     // Set the initial estimate of the storage
    for (t in 2:T){
        S[t] = ((1 - c) * S[t - 1]) + (a * P[t]);
        Qs[t] = c * S[t];
        Qf[t] = (1 - a - b) * P[t];
        Qsim[t] = Qf[t] + Qs[t];
    }
}

model{
    // Priors
    a ~ normal(0.5, 1);
    b ~ normal(0.5, 1);
    c ~ normal(0.5, 1);
    sigma ~ normal(0, 1);


    // normal measurement error of Q
    for (t in 1: T)
        Q[t] ~ normal(Qsim[t], sigma);
}
