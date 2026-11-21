"""Documentation records for Methods 23-46 (Categories C and D)."""

from __future__ import annotations

from src.mathematics.catalog_ab import M

C = "C - Transitions and Dependencies"
D = "D - Time Series"

METHODS_CD = [
    M("M023", "First-Order Markov Chain", C,
      r"P(X_{t+1}=j \mid X_t=i, X_{t-1},\ldots) = P(X_{t+1}=j \mid X_t=i) = P_{ij}",
      "A first-order Markov chain is the minimal model of serial dependence: the next state depends "
      "on the current one and on nothing earlier. Its transition matrix P is estimated by row "
      "normalisation of the transition counts, and the Markov property itself is testable by "
      "comparing higher-order conditional distributions.",
      "Estimate the transition matrix and test whether it beats the marginal distribution out of sample.",
      ["The process is time-homogeneous", "The state space is the observed outcome space"],
      [("P_ij", "probability of moving from i to j"), ("n_ij", "transition count"),
       ("row sum", "total transitions out of state i")],
      ["Tabulate transitions between consecutive draws",
       "Row-normalise with smoothing",
       "Score causally and compare against the marginal-frequency baseline"],
      "With K=10 each row has 10 cells; at N=3000 that is ~30 transitions per cell, enough for the "
      "diagonal but thin for distant off-diagonals.",
      "At least ~10 transitions out of every state.",
      "src.mathematics.markov::run_023"),

    M("M024", "Second-Order Markov Chain", C,
      r"P(X_{t+1}=k \mid X_t=j, X_{t-1}=i) = P_{ijk}",
      "Conditioning on two previous states captures patterns a first-order chain cannot express, at "
      "the cost of K^2 = 100 contexts. Each context then holds only ~N/100 observations, so the "
      "estimates are severely data-limited and smoothing or pooling is mandatory.",
      "Test whether two-step history adds predictive information.",
      ["The process is second-order Markov", "Contexts are adequately populated"],
      [("P_ijk", "transition probability given two states"), ("context", "the pair (i, j)"),
       ("sparsity", "fraction of empty contexts")],
      ["Tabulate transitions conditioned on the previous two outcomes",
       "Smooth sparse rows toward the first-order estimate",
       "Score causally against the first-order model"],
      "The parameter count grows as K^2(K-1) = 900, which for these sample sizes generally loses to "
      "the simpler model - a genuine bias-variance trade-off, measured rather than assumed.",
      "N >> K^2 for reliable estimation.",
      "src.mathematics.markov::run_024"),

    M("M025", "Higher-Order Markov Models", C,
      r"P(X_{t+1}\mid X_{t-p+1},\ldots,X_t),\quad p=1,2,3",
      "Varying the Markov order traces the bias-variance trade-off explicitly. A useful summary is "
      "the conditional mutual information at each order: if conditioning on one more past state adds "
      "no information, the higher order is not earning its parameter count.",
      "Select the Markov order by out-of-sample performance, not by in-sample fit.",
      ["Orders are nested", "The evaluation window is identical across orders"],
      [("p", "Markov order"), ("order selection", "chosen by out-of-sample log loss")],
      ["Fit orders 1 through the configured maximum",
       "Score each on the same causal evaluation window",
       "Report the loss curve and the selected order"],
      "In-sample likelihood always increases with order; only the out-of-sample comparison is "
      "informative.",
      "N decreasing sharply in usefulness beyond p=2.",
      "src.mathematics.markov::run_025"),

    M("M026", "Conditional Probability Analysis", C,
      r"P(A \mid B) = \frac{P(A \cap B)}{P(B)}",
      "Conditional probability is the primitive that every dependence-based predictor ultimately "
      "rests on. Estimating P(next outcome | current outcome) reproduces the Markov matrix, but the "
      "general form also covers events rather than states - for example 'next draw is even given "
      "that the previous draw was prime'.",
      "Build conditional frequency tables and test whether conditioning changes anything.",
      ["The conditioning event has non-trivial probability",
       "Event definitions are fixed before looking at the data"],
      [("A", "target event"), ("B", "conditioning event"),
       ("P(B)", "marginal probability of the condition")],
      ["Define the events",
       "Tabulate joint and marginal counts",
       "Compute the conditional distribution and the lift over the unconditional one"],
      "Conditioning on rare events yields unstable estimates; and with many candidate events, "
      "apparent lift is easy to find by chance.",
      "Enough observations in the conditioning cell (say >= 50).",
      "src.mathematics.markov::run_026"),

    M("M027", "Open-to-Close Conditional Modelling", C,
      r"P(C_t = c \mid O_t = o)",
      "In these markets the same day's Open is announced before the Close, so it is the one "
      "same-day variable that is legitimately available to a Close forecast. The joint distribution "
      "of (Open, Close) on the same day either factorises or it does not; if it does, the Open "
      "carries exactly zero information about the Close.",
      "Test whether the same-day Open predicts the Close, and quantify any gain out of sample.",
      ["Publication order really does put Open before Close",
       "Same-day pairing is exact (no date shifting)"],
      [("O_t", "same-day open outcome"), ("C_t", "same-day close outcome"),
       ("mutual information", "dependence in bits")],
      ["Join each date's Open and Close",
       "Build the 10x10 contingency table",
       "Test independence and compare a Close model with and without the Open feature"],
      "If publication times are unavailable the pairing may be wrong; the platform records that "
      "assumption explicitly.",
      "Several hundred paired observations.",
      "src.mathematics.markov::run_027"),

    M("M028", "Cross-Correlation Analysis", C,
      r"\rho(k) = \mathrm{corr}(X_t, Y_{t-k})",
      "Pearson correlation is meaningless for nominal categories, so this implementation uses "
      "Cramer's V on the lagged contingency table, which is the categorical analogue. Testing many "
      "lags across many market pairs creates a large multiple-testing problem that must be "
      "corrected.",
      "Measure lagged association between markets with a categorical-appropriate statistic.",
      ["Lagged pairs are correctly time-aligned", "Observations are independent across pairs"],
      [("rho(k)", "association at lag k"), ("V", "Cramer's V"), ("k", "lag in observations")],
      ["Align the two markets on shared dates",
       "For each lag build the contingency table",
       "Compute V and a chi-square p-value, then correct across lags"],
      "Association at any lag does not establish causation, and with enough lags some association "
      "appears by construction.",
      "Adequate overlap of calendars between the two markets.",
      "src.mathematics.markov::run_028"),

    M("M029", "Autocorrelation Function", C,
      r"\rho_k = \frac{\sum_t (x_t-\bar{x})(x_{t-k}-\bar{x})}{\sum_t (x_t-\bar{x})^2}",
      "Autocorrelation measures linear serial dependence. Applied to the numeric encoding of an ank "
      "it asks whether large values follow large values; applied to indicator series it asks "
      "whether a category's presence predicts its own presence. Bands from a permutation null "
      "replace the inappropriate i.i.d. Gaussian bands.",
      "Detect linear serial dependence at multiple lags.",
      ["The numeric encoding has a defensible ordering",
       "The series is stationary over the window"],
      [("rho_k", "lag-k autocorrelation"), ("band", "permutation-based significance band")],
      ["Choose the representation (indicator or numeric)",
       "Compute autocorrelations up to the configured maximum lag",
       "Compare against a permutation null band"],
      "A flat ACF does not imply independence - nonlinear dependence is invisible to it, which is "
      "why M031 is also required.",
      "A few hundred observations for stable estimates.",
      "src.mathematics.markov::run_029"),

    M("M030", "Partial Autocorrelation", C,
      r"\phi_{kk} = \mathrm{corr}(x_t, x_{t-k} \mid x_{t-1},\ldots,x_{t-k+1})",
      "The PACF isolates the direct contribution of lag k by removing the intermediate lags. For a "
      "first-order Markov process the theoretical PACF is zero beyond lag 1; a non-zero value at lag "
      "2 is therefore evidence of genuine second-order structure rather than inherited dependence.",
      "Identify lags that carry direct rather than mediated information.",
      ["The series is stationary", "The AR representation is adequate"],
      [("phi_kk", "partial autocorrelation at lag k"), ("k", "lag")],
      ["Compute the ACF",
       "Solve the Yule-Walker recursion to obtain partial autocorrelations",
       "Compare with a permutation band"],
      "PACF assumes a linear autoregressive structure; categorical dependence may be entirely "
      "invisible to it.",
      "A few hundred observations.",
      "src.mathematics.markov::run_030"),

    M("M031", "Mutual Information", C,
      r"I(X;Y)=\sum_{x,y}p(x,y)\log\frac{p(x,y)}{p(x)p(y)}",
      "Mutual information measures any statistical dependence, linear or not, in bits. Unlike "
      "correlation it detects the cyclic, modular relationships that digit games are full of. Its "
      "finite-sample bias is upward and must be corrected by comparison with a permutation null "
      "rather than against a theoretical chi-square.",
      "Detect and quantify arbitrary dependence between consecutive draws.",
      ["The joint distribution is estimable from the sample",
       "The permutation null preserves the marginals"],
      [("I(X;Y)", "mutual information in bits"), ("p(x,y)", "joint probability"),
       ("null", "permutation distribution of I")],
      ["Estimate joint and marginal probabilities with smoothing",
       "Compute I",
       "Compare against the distribution of I under random pairing"],
      "MI is biased upward for sparse tables; the permutation comparison is the remedy, not an "
      "afterthought.",
      "N >> K^2 for the joint table to be estimable.",
      "src.mathematics.markov::run_031", "Shannon (1948)"),

    M("M032", "Conditional Mutual Information", C,
      r"I(X;Y \mid Z)=\sum_{x,y,z}p(x,y,z)\log\frac{p(x,y\mid z)}{p(x\mid z)p(y\mid z)}",
      "Conditional MI asks whether a candidate predictor still contributes once a competing "
      "predictor is known. It is the principled filter for feature selection in Method 93, because "
      "it screens out variables that are merely redundant with ones already in the model.",
      "Test whether a predictor adds information beyond an existing one.",
      ["Conditioning variable is observed for all rows", "Cell counts are adequate"],
      [("I(X;Y|Z)", "conditional mutual information"), ("Z", "conditioning variable")],
      ["Fit the conditional distributions",
       "Compute the conditional MI",
       "Compare against a permutation null that preserves the conditioning"],
      "Estimation noise grows quickly with the number of cells; conditioning on a 10-state variable "
      "already multiplies the table by 10.",
      "Large N relative to the joint state space.",
      "src.mathematics.markov::run_032"),

    M("M033", "Transition Matrix Analysis", C,
      r"\hat{P}_{ij} = \frac{n_{ij}+\alpha}{\sum_j (n_{ij}+\alpha)}",
      "The transition matrix is a complete description of a first-order chain, so its structural "
      "properties are diagnostic: the stationary distribution tells where the chain settles, the "
      "second eigenvalue governs the rate of mixing, and a near-uniform matrix indicates no "
      "dependence at all.",
      "Characterise the transition structure and its predictive content.",
      ["The chain is homogeneous", "The matrix is estimated from adequate counts"],
      [("P", "transition matrix"), ("stationary distribution", "left eigenvector for eigenvalue 1"),
       ("mixing time", "governed by the second eigenvalue modulus")],
      ["Estimate the matrix",
       "Compute the stationary distribution and spectral gap",
       "Compare selective rows against the marginal distribution"],
      "A non-uniform matrix may reflect sampling noise; the chi-square test in M023 and the "
      "out-of-sample comparison are what decide usability.",
      "Sufficient counts per row.",
      "src.mathematics.markov::run_033"),

    M("M034", "Variable-Length Markov Modelling", C,
      r"\hat{P}(x_{t+1}\mid \text{ctx}) = \begin{cases}\text{order 3} & n_{\text{ctx}} \ge \tau_3\\ \text{order 2} & n_{\text{ctx}} \ge \tau_2\\ \text{order 1} & \text{otherwise}\end{cases}",
      "A variable-length Markov model uses a long context where the data are dense enough and falls "
      "back to a shorter one where they are not. The support thresholds make the choice of order "
      "data-dependent rather than global, which controls context-tree growth and lets the method "
      "test whether selective long contexts help.",
      "Test whether a data-driven context length beats a fixed-order Markov model.",
      ["Contexts can be ranked by support", "Backoff preserves calibration"],
      [("ctx", "the recent outcome sequence"), ("tau", "minimum support to use a context")],
      ["Build the context tree to the maximum order",
       "Apply support thresholds with backoff to shorter contexts",
       "Score causally against the fixed-order models"],
      "Backoff introduces discontinuities; a context just above threshold is estimated from a "
      "handful of cases.",
      "Large N: the tree grows exponentially in the order.",
      "src.mathematics.markov::run_034"),

    M("M035", "Moving Average Analysis", D,
      r"\mathrm{MA}_t^{(W)} = \frac{1}{W}\sum_{i=0}^{W-1}x_{t-i}",
      "A moving average is a low-pass filter: it removes high-frequency variation to expose trend. "
      "For a numeric encoding of a categorical outcome it is a legitimate descriptive tool, but the "
      "smoothed value is not a probability and must not be read as one.",
      "Smooth the outcome series and test whether the smoothed level predicts the next draw.",
      ["The numeric encoding has meaning", "The window is chosen a priori"],
      [("MA_t", "moving average at t"), ("W", "window length"), ("x_t", "numeric outcome")],
      ["Compute the trailing average excluding the current draw",
       "Correlate it with the next outcome",
       "Score it as a regression predictor out of sample"],
      "Averaging arbitrary labels produces a meaningless number; the method is implemented with an "
      "explicit meaningfulness check.",
      "A few hundred observations.",
      "src.mathematics.time_series::run_035"),

    M("M036", "Weighted Moving Average", D,
      r"\mathrm{WMA}_t = \frac{\sum_{i=0}^{W-1}w_i x_{t-i}}{\sum_i w_i}",
      "Descending weights inside the window let the filter favour recent values without abandoning "
      "the rest. It interpolates between the simple moving average and an exponential filter and is "
      "useful mainly as a robustness check on the latter.",
      "Compare a linearly weighted filter with the simple and exponential alternatives.",
      ["Weights are fixed a priori", "The window is fixed a priori"],
      [("w_i", "weight for lag i"), ("WMA_t", "weighted average")],
      ["Choose linear descending weights",
       "Compute the trailing weighted average",
       "Compare predictive loss with MA and EMA"],
      "Adds a tuning dimension for little theoretical gain.",
      "A few hundred observations.",
      "src.mathematics.time_series::run_036"),

    M("M037", "Exponential Moving Average", D,
      r"\mathrm{EMA}_t = \alpha x_t + (1-\alpha)\mathrm{EMA}_{t-1}",
      "The EMA is a one-parameter recursive filter whose memory decays geometrically. It is the "
      "numeric counterpart of the exponentially weighted frequency in M004 and shares its property "
      "that the effective memory is 1/alpha observations.",
      "Test smoothing rates as predictors of the next outcome.",
      ["The encoding is numeric and meaningful", "Alpha is constant"],
      [("alpha", "smoothing constant in (0,1]"), ("EMA_t", "smoothed level")],
      ["Initialise the EMA on an initial window",
       "Update recursively with each new draw",
       "Score the smoothed level as a predictor out of sample"],
      "Like every smoother here, it can create apparent trend from pure noise.",
      "A few hundred observations.",
      "src.mathematics.time_series::run_037"),

    M("M038", "Autoregressive Models", D,
      r"X_t = c + \sum_{i=1}^{p}\phi_i X_{t-i} + \varepsilon_t",
      "An AR(p) model represents the series as a linear function of its own past plus noise. "
      "Applying it to a categorical outcome requires a numeric encoding, which is defensible for "
      "anks on a circle but not for jodis; the method therefore declares its applicability instead "
      "of forcing a fit.",
      "Fit autoregressive models and diagnose whether any lag structure survives.",
      ["The numeric encoding is meaningful", "Residuals are approximately white"],
      [("phi_i", "autoregressive coefficients"), ("p", "order"),
       ("epsilon", "innovation term")],
      ["Test the encoding's meaningfulness",
       "Fit orders up to the configured maximum",
       "Diagnose residuals with Ljung-Box and score out of sample"],
      "Linear AR structure cannot represent modular relationships, and a discrete bounded outcome "
      "violates the Gaussian innovation assumption.",
      "Meaningful numeric encoding; several hundred observations.",
      "src.mathematics.time_series::run_038"),

    M("M039", "ARMA Modelling", D,
      r"\phi(B)X_t = \theta(B)\varepsilon_t",
      "ARMA adds a moving-average term, capturing transient shocks on top of persistent "
      "autoregression. For a bounded discrete outcome its usefulness is limited, and it is included "
      "for completeness of the classical toolkit rather than expectation of success.",
      "Fit ARMA structures and compare against AR alone.",
      ["The series is stationary after any differencing", "Shocks are transient"],
      [("phi", "autoregressive polynomial"), ("theta", "moving-average polynomial"), ("B", "lag operator")],
      ["Test stationarity",
       "Fit candidate orders and compare by information criterion",
       "Check residual autocorrelation"],
      "Model selection on a few thousand discrete observations is fragile, and ARMA assumes a "
      "continuous unbounded innovation.",
      "Several hundred observations.",
      "src.mathematics.time_series::run_039"),

    M("M040", "ARIMA Modelling", D,
      r"\phi(B)(1-B)^d X_t = \theta(B)\varepsilon_t",
      "Differencing removes integrated behaviour, which matters because a non-stationary level will "
      "otherwise produce spurious persistence. The order of differencing is chosen by unit-root "
      "testing rather than by guesswork.",
      "Determine the integration order and fit a differenced model.",
      ["Differencing achieves stationarity", "The differenced series is invertible"],
      [("d", "differencing order"), ("ADF", "unit-root test statistic")],
      ["Run an ADF test on the level and on differences",
       "Select d accordingly",
       "Fit and evaluate out of sample"],
      "Ank sequences are bounded and discrete; differencing them is arithmetically possible but "
      "conceptually weak.",
      "Meaningful numeric encoding.",
      "src.mathematics.time_series::run_040"),

    M("M041", "Seasonal Decomposition", D,
      r"X_t = T_t + S_t + R_t",
      "Classical decomposition splits a series into trend, seasonal and residual components. It is "
      "a diagnostic that makes an anticipated seasonality visible - and, crucially, lets the "
      "residual be tested for the dependence that seasonality cannot explain.",
      "Test for periodic structure and isolate the residual.",
      ["The seasonal period is known a priori",
       "Seasonal amplitude is stable across periods"],
      [("T_t", "trend"), ("S_t", "seasonal"), ("R_t", "residual")],
      ["Detect the dominant period from the autocorrelation",
       "Decompose the series",
       "Test the residual for remaining dependence"],
      "With a weekly cycle and only ~3100 daily observations there are ~520 cycles, but the draw "
      "calendar omits Sundays, which distorts naive periodicity.",
      "At least two full cycles.",
      "src.mathematics.time_series::run_041"),

    M("M042", "Seasonal ARIMA", D,
      r"\phi(B)\Phi(B^s)(1-B)^d(1-B^s)^D X_t = \theta(B)\Theta(B^s)\varepsilon_t",
      "SARIMA adds seasonal autoregressive and moving-average polynomials. Its parameter count grows "
      "quickly, so a defensible seasonal period and strong prior evidence are prerequisites rather "
      "than niceties.",
      "Fit a seasonal model only where a seasonal period is empirically justified.",
      ["A genuine seasonal cycle exists", "Enough cycles to estimate seasonal parameters"],
      [("s", "seasonal period"), ("Phi", "seasonal AR polynomial"), ("Theta", "seasonal MA polynomial")],
      ["Establish the seasonal period from decomposition",
       "Fit a small seasonal model",
       "Evaluate out of sample and against the non-seasonal model"],
      "Fitting a seasonal model to noise will always appear to fit better in-sample and will "
      "generally fail out of sample.",
      "Numerous complete cycles.",
      "src.mathematics.time_series::run_042"),

    M("M043", "Calendar Effect Analysis", D,
      r"\chi^2_{\text{cal}} = \sum_{d}\sum_{k}\frac{(O_{dk}-E_{dk})^2}{E_{dk}}",
      "Calendar effects assert that the day of week, day of month or month changes the distribution. "
      "Such features are known in advance, which makes them attractive predictors, and the many "
      "possible calendar partitions guarantee that some will look significant by chance unless the "
      "tests are corrected.",
      "Test calendar features for distributional effects with multiple-testing control.",
      ["Calendar features are known before the draw", "Observations in each cell are exchangeable"],
      [("O_dk", "count of outcome k on calendar state d"), ("df", "degrees of freedom"),
       ("adjusted p", "FDR-controlled p-value")],
      ["Partition dates by weekday, month and day-of-month band",
       "Build contingency tables and test homogeneity",
       "Apply Benjamini-Hochberg across the calendar features tested"],
      "These markets draw most days, so calendar partitions have small cells and multiple testing is "
      "severe.",
      "Enough full cycles to populate each calendar cell.",
      "src.mathematics.time_series::run_043"),

    M("M044", "Rolling Regime Analysis", D,
      r"\hat{p}^{(w)}_k = \frac{1}{|W_w|}\sum_{t \in W_w}\mathbf{1}[X_t=k]",
      "A regime is a stretch of time over which the distribution is approximately constant. Dividing "
      "history into windows and comparing window-wise distributions exposes whether the process is "
      "stable enough for any pooled estimate to mean anything.",
      "Quantify regime instability and its effect on predictive performance.",
      ["The process is piecewise homogeneous", "Windows are comparable in length"],
      [("W_w", "window w"), ("p_k^(w)", "window-wise probability"),
       ("drift", "dispersion of window-wise estimates")],
      ["Slice history into equal windows",
       "Estimate the distribution in each",
       "Measure dispersion and compare with the multinomial expectation"],
      "Windows are an arbitrary partition; results depend on the chosen length.",
      "Several hundred observations per window.",
      "src.mathematics.time_series::run_044"),

    M("M045", "State-Space Modelling", D,
      r"x_t = F x_{t-1} + w_t,\quad y_t = H x_t + v_t",
      "A state-space model separates an unobserved latent level from observation noise. The "
      "Kalman filter gives the optimal linear estimate of the state, and the innovation sequence "
      "provides a direct test of the model's adequacy.",
      "Estimate a latent level and inspect the innovations for unexplained structure.",
      ["Linear Gaussian dynamics", "Innovations are white if the model is adequate"],
      [("x_t", "latent state"), ("y_t", "observation"), ("F, H", "transition and observation matrices"),
       ("w_t, v_t", "process and observation noise")],
      ["Specify the state and observation equations",
       "Run the Kalman recursion",
       "Test the standardised innovations for serial correlation"],
      "A Gaussian latent-level model is a poor fit for a bounded 10-category outcome; the method is "
      "applied to the numeric encoding and its conclusions are qualified accordingly.",
      "A meaningful numeric encoding.",
      "src.mathematics.time_series::run_045"),

    M("M046", "Dynamic Generalized Linear Models", D,
      r"g(\mu_t) = x_t^\top\beta_t,\quad \beta_t = \beta_{t-1} + \eta_t",
      "A dynamic GLM lets coefficients evolve over time, so a model can adapt to regime change "
      "without a discrete break detection. Tracking the coefficient path also answers a diagnostic "
      "question: if the coefficients wander randomly, there is no stable relationship to learn.",
      "Estimate time-varying coefficients and assess coefficient stability.",
      ["Coefficients evolve slowly", "The link function is appropriate"],
      [("beta_t", "time-varying coefficient vector"), ("g", "link function"), ("eta_t", "state noise")],
      ["Refit the GLM on expanding windows",
       "Track coefficient paths over time",
       "Measure path variance relative to the coefficient magnitude"],
      "Expanding-window refitting is only an approximation to a true dynamic GLM; the "
      "implementation notes that explicitly.",
      "Several hundred observations per refit.",
      "src.mathematics.time_series::run_046"),
]
