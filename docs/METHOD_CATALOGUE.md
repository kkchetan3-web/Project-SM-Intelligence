# Complete method catalogue

100 methods documented, 100 implemented, 0 missing. Generated from `src/mathematics/registry.py` by `scripts/export_catalogue.py` - do not edit by hand.

Status vocabulary used by every method: `computed`, `not_applicable`, `insufficient_data`, `dependency_unavailable`, `failed`. A method that cannot run says so; it never returns a placeholder number.

## Category A - Frequency and Probability (12 methods)

| ID | Method | Implementation | Formula |
|---|---|---|---|
| `M001` | Absolute Frequency Analysis | `src.mathematics.frequency::run_001` | `n_k = \sum_{t=1}^{N} \mathbf{1}[X_t = k]` |
| `M002` | Relative Frequency Analysis | `src.mathematics.frequency::run_002` | `\hat{p}_k = \frac{n_k}{N}, \qquad \sum_{k=1}^{K}\hat{p}_k = 1` |
| `M003` | Rolling Frequency Analysis | `src.mathematics.frequency::run_003` | `\hat{p}_{k,t} = \frac{1}{W}\sum_{i=t-W+1}^{t}\mathbf{1}[X_i=k]` |
| `M004` | Exponentially Weighted Frequency | `src.mathematics.frequency::run_004` | `w_k(t)=\sum_{i \le t}\lambda^{t-i}\mathbf{1}[X_i=k],\quad \hat{p}_k(t)=\frac{w_k(t)}{\sum_j w_j(t)}` |
| `M005` | Bayesian Frequency Estimation | `src.mathematics.frequency::run_005` | `P(\theta \mid D) \propto P(D \mid \theta)P(\theta)` |
| `M006` | Dirichlet-Multinomial Modelling | `src.mathematics.frequency::run_006` | `\theta \mid D \sim \mathrm{Dirichlet}(\alpha_1+n_1,\ldots,\alpha_K+n_K)` |
| `M007` | Laplace Smoothing | `src.mathematics.frequency::run_007` | `\hat{p}_k = \frac{n_k+\alpha}{N+\alpha K}` |
| `M008` | Entropy Analysis | `src.mathematics.frequency::run_008` | `H(X) = -\sum_{k=1}^{K} p_k \log_2 p_k \le \log_2 K` |
| `M009` | Chi-Square Goodness-of-Fit | `src.mathematics.frequency::run_009` | `\chi^2 = \sum_{k=1}^{K}\frac{(O_k-E_k)^2}{E_k},\quad df = K-1` |
| `M010` | Categorical Distribution Testing | `src.mathematics.frequency::run_010` | `\chi^2_{\text{indep}} = \sum_{i,j}\frac{(O_{ij}-E_{ij})^2}{E_{ij}}` |
| `M011` | Jeffreys Prior Estimation | `src.mathematics.frequency::run_011` | `\theta \sim \mathrm{Dirichlet}(\tfrac{1}{2},\ldots,\tfrac{1}{2})` |
| `M012` | Hierarchical Bayesian Probability Modelling | `src.mathematics.frequency::run_012` | `\theta_m \sim \mathrm{Dirichlet}(\alpha_0/K,\ldots),\quad \alpha_0 \sim p(\alpha_0)` |

## Category B - Recency and Occurrence (10 methods)

| ID | Method | Implementation | Formula |
|---|---|---|---|
| `M013` | Last Occurrence Analysis | `src.mathematics.recurrence::run_013` | `G_{k,t} = t - \max\{i < t : X_i = k\}` |
| `M014` | Inter-Occurrence Gap Analysis | `src.mathematics.recurrence::run_014` | `G_j = T_j - T_{j-1}` |
| `M015` | Average Recurrence Interval | `src.mathematics.recurrence::run_015` | `\bar{G} = \frac{1}{m}\sum_{j=1}^{m} G_j \approx \frac{1}{\hat{p}}` |
| `M016` | Median Recurrence Interval | `src.mathematics.recurrence::run_016` | `\tilde{G} = \mathrm{median}(G_1,\ldots,G_m)` |
| `M017` | Gap Distribution Modelling | `src.mathematics.recurrence::run_017` | `P(G=g) = (1-p)^{g-1}p \quad\text{(geometric)}` |
| `M018` | Survival Analysis | `src.mathematics.recurrence::run_018` | `\hat{S}(t)=\prod_{s \le t}\left(1-\frac{d_s}{n_s}\right)` |
| `M019` | Hazard Rate Estimation | `src.mathematics.recurrence::run_019` | `h(t) = P(T=t \mid T \ge t) = \frac{d_t}{n_t}` |
| `M020` | Hot and Cold Frequency Analysis | `src.mathematics.recurrence::run_020` | `z_k = \frac{n_k - N/K}{\sqrt{N \cdot \frac{1}{K}(1-\frac{1}{K})}}` |
| `M021` | Rolling Recency Weighting | `src.mathematics.recurrence::run_021` | `\hat{p}_k(t; W, \lambda)=\frac{\sum_{i=t-W+1}^{t}\lambda^{t-i}\mathbf{1}[X_i=k]}{\sum_j(\cdot)}` |
| `M022` | Change-Point Detection | `src.mathematics.recurrence::run_022` | `S_t = \max\left(0, S_{t-1} + (X_t - \mu_0)\right)` |

## Category C - Transitions and Dependencies (12 methods)

| ID | Method | Implementation | Formula |
|---|---|---|---|
| `M023` | First-Order Markov Chain | `src.mathematics.markov::run_023` | `P(X_{t+1}=j \mid X_t=i, X_{t-1},\ldots) = P(X_{t+1}=j \mid X_t=i) = P_{ij}` |
| `M024` | Second-Order Markov Chain | `src.mathematics.markov::run_024` | `P(X_{t+1}=k \mid X_t=j, X_{t-1}=i) = P_{ijk}` |
| `M025` | Higher-Order Markov Models | `src.mathematics.markov::run_025` | `P(X_{t+1}\mid X_{t-p+1},\ldots,X_t),\quad p=1,2,3` |
| `M026` | Conditional Probability Analysis | `src.mathematics.markov::run_026` | `P(A \mid B) = \frac{P(A \cap B)}{P(B)}` |
| `M027` | Open-to-Close Conditional Modelling | `src.mathematics.markov::run_027` | `P(C_t = c \mid O_t = o)` |
| `M028` | Cross-Correlation Analysis | `src.mathematics.markov::run_028` | `\rho(k) = \mathrm{corr}(X_t, Y_{t-k})` |
| `M029` | Autocorrelation Function | `src.mathematics.markov::run_029` | `\rho_k = \frac{\sum_t (x_t-\bar{x})(x_{t-k}-\bar{x})}{\sum_t (x_t-\bar{x})^2}` |
| `M030` | Partial Autocorrelation | `src.mathematics.markov::run_030` | `\phi_{kk} = \mathrm{corr}(x_t, x_{t-k} \mid x_{t-1},\ldots,x_{t-k+1})` |
| `M031` | Mutual Information | `src.mathematics.markov::run_031` | `I(X;Y)=\sum_{x,y}p(x,y)\log\frac{p(x,y)}{p(x)p(y)}` |
| `M032` | Conditional Mutual Information | `src.mathematics.markov::run_032` | `I(X;Y \mid Z)=\sum_{x,y,z}p(x,y,z)\log\frac{p(x,y\mid z)}{p(x\mid z)p(y\mid z)}` |
| `M033` | Transition Matrix Analysis | `src.mathematics.markov::run_033` | `\hat{P}_{ij} = \frac{n_{ij}+\alpha}{\sum_j (n_{ij}+\alpha)}` |
| `M034` | Variable-Length Markov Modelling | `src.mathematics.markov::run_034` | `\hat{P}(x_{t+1}\mid \text{ctx}) = \begin{cases}\text{order 3} & n_{\text{ctx}} \ge \tau_3\\ \text{order 2} & n_{\text{ctx}} \ge \tau_2\\ \text{order 1} & \te...` |

## Category D - Time Series (12 methods)

| ID | Method | Implementation | Formula |
|---|---|---|---|
| `M035` | Moving Average Analysis | `src.mathematics.time_series::run_035` | `\mathrm{MA}_t^{(W)} = \frac{1}{W}\sum_{i=0}^{W-1}x_{t-i}` |
| `M036` | Weighted Moving Average | `src.mathematics.time_series::run_036` | `\mathrm{WMA}_t = \frac{\sum_{i=0}^{W-1}w_i x_{t-i}}{\sum_i w_i}` |
| `M037` | Exponential Moving Average | `src.mathematics.time_series::run_037` | `\mathrm{EMA}_t = \alpha x_t + (1-\alpha)\mathrm{EMA}_{t-1}` |
| `M038` | Autoregressive Models | `src.mathematics.time_series::run_038` | `X_t = c + \sum_{i=1}^{p}\phi_i X_{t-i} + \varepsilon_t` |
| `M039` | ARMA Modelling | `src.mathematics.time_series::run_039` | `\phi(B)X_t = \theta(B)\varepsilon_t` |
| `M040` | ARIMA Modelling | `src.mathematics.time_series::run_040` | `\phi(B)(1-B)^d X_t = \theta(B)\varepsilon_t` |
| `M041` | Seasonal Decomposition | `src.mathematics.time_series::run_041` | `X_t = T_t + S_t + R_t` |
| `M042` | Seasonal ARIMA | `src.mathematics.time_series::run_042` | `\phi(B)\Phi(B^s)(1-B)^d(1-B^s)^D X_t = \theta(B)\Theta(B^s)\varepsilon_t` |
| `M043` | Calendar Effect Analysis | `src.mathematics.time_series::run_043` | `\chi^2_{\text{cal}} = \sum_{d}\sum_{k}\frac{(O_{dk}-E_{dk})^2}{E_{dk}}` |
| `M044` | Rolling Regime Analysis | `src.mathematics.time_series::run_044` | `\hat{p}^{(w)}_k = \frac{1}{\|W_w\|}\sum_{t \in W_w}\mathbf{1}[X_t=k]` |
| `M045` | State-Space Modelling | `src.mathematics.time_series::run_045` | `x_t = F x_{t-1} + w_t,\quad y_t = H x_t + v_t` |
| `M046` | Dynamic Generalized Linear Models | `src.mathematics.time_series::run_046` | `g(\mu_t) = x_t^\top\beta_t,\quad \beta_t = \beta_{t-1} + \eta_t` |

## Category E - Number Theory and Transformations (14 methods)

| ID | Method | Implementation | Formula |
|---|---|---|---|
| `M047` | Modular Arithmetic | `src.mathematics.number_theory::run_047` | `r = n \bmod m` |
| `M048` | Digital Root Analysis | `src.mathematics.number_theory::run_048` | `\mathrm{dr}(n) = 1 + ((n-1) \bmod 9)` |
| `M049` | Digit Sum Distribution | `src.mathematics.number_theory::run_049` | `S = d_1 + d_2 + d_3,\quad d_i \in \{0,\ldots,9\}` |
| `M050` | Digit Difference Analysis | `src.mathematics.number_theory::run_050` | `D = \|d_1 - d_2\|,\ldots` |
| `M051` | Complementary Digit Analysis | `src.mathematics.number_theory::run_051` | `d' = 9 - d` |
| `M052` | Reversal Relationship Analysis | `src.mathematics.number_theory::run_052` | `\mathrm{rev}(d_1d_2d_3) = d_3d_2d_1` |
| `M053` | Parity Analysis | `src.mathematics.number_theory::run_053` | `P(\text{even}) = \sum_{k \text{ even}} p_k` |
| `M054` | Prime and Composite Classification | `src.mathematics.number_theory::run_054` | `\mathbb{P} = \{2,3,5,7\},\quad n \in \mathbb{P}?` |
| `M055` | Combinatorial Probability Analysis | `src.mathematics.number_theory::run_055` | `\|\Omega\| = K,\quad P(A) = \frac{\|A\|}{\|\Omega\|}` |
| `M056` | Permutation and Combination Analysis | `src.mathematics.number_theory::run_056` | `{}^nP_r=\frac{n!}{(n-r)!},\qquad {}^nC_r=\frac{n!}{r!(n-r)!}` |
| `M057` | Numerical Distance Analysis | `src.mathematics.number_theory::run_057` | `d_t = \|x_t - x_{t-1}\|` |
| `M058` | Pairwise Digit Association | `src.mathematics.number_theory::run_058` | `\chi^2 = \sum_{i,j}\frac{(O_{ij}-E_{ij})^2}{E_{ij}}` |
| `M059` | Hamming Distance Analysis | `src.mathematics.number_theory::run_059` | `d_H(x,y)=\sum_{i}\mathbf{1}[x_i \neq y_i]` |
| `M060` | Residue Distribution Analysis | `src.mathematics.number_theory::run_060` | `c_k = \|\{t : x_t \equiv k \pmod m\}\|` |

## Category F - Randomness and Statistical Structure (12 methods)

| ID | Method | Implementation | Formula |
|---|---|---|---|
| `M061` | Runs Test | `src.mathematics.randomness::run_061` | `R = 1 + \sum_{t=2}^{N}\mathbf{1}[S_t \neq S_{t-1}]` |
| `M062` | Ljung-Box Test | `src.mathematics.randomness::run_062` | `Q=n(n+2)\sum_{k=1}^{h}\frac{\hat{\rho}_k^2}{n-k}` |
| `M063` | Permutation Testing | `src.mathematics.randomness::run_063` | `p = \frac{1+\sum_{b=1}^{B}\mathbf{1}[T_b \ge T_{\text{obs}}]}{B+1}` |
| `M064` | Bootstrap Analysis | `src.mathematics.randomness::run_064` | `\mathrm{CI}_{1-\alpha} = [q_{\alpha/2}(\hat{\theta}^*), q_{1-\alpha/2}(\hat{\theta}^*)]` |
| `M065` | Monte Carlo Simulation | `src.mathematics.randomness::run_065` | `\hat{P}(T \ge t) = \frac{1}{M}\sum_{m=1}^{M}\mathbf{1}[T_m \ge t]` |
| `M066` | Sample Entropy | `src.mathematics.randomness::run_066` | `SampEn(m,r)=-\ln\frac{A}{B}` |
| `M067` | Approximate Entropy | `src.mathematics.randomness::run_067` | `ApEn(m,r)=\Phi^m(r)-\Phi^{m+1}(r)` |
| `M068` | Hurst Exponent Analysis | `src.mathematics.randomness::run_068` | `\mathbb{E}\left[\frac{R(n)}{S(n)}\right] \sim n^{H}` |
| `M069` | Hidden Markov Models | `src.mathematics.randomness::run_069` | `P(X_{1:T},Z_{1:T}) = \pi_{z_1}b_{z_1}(x_1)\prod_{t=2}^{T}A_{z_{t-1},z_t}b_{z_t}(x_t)` |
| `M070` | Bayesian Change-Point Modelling | `src.mathematics.randomness::run_070` | `P(\tau \mid x_{1:T}) \propto P(x_{1:\tau})P(x_{\tau+1:T})P(\tau)` |
| `M071` | Wald-Wolfowitz Runs Analysis | `src.mathematics.randomness::run_071` | `E[R] = \frac{2n_1n_2}{n}+1,\quad \mathrm{Var}(R)=\frac{2n_1n_2(2n_1n_2-n)}{n^2(n-1)}` |
| `M072` | Block Bootstrap Analysis | `src.mathematics.randomness::run_072` | `\hat{\theta}^*_b \text{ from blocks } (x_{i},x_{i+1},\ldots,x_{i+\ell-1})` |

## Category G - Machine Learning (12 methods)

| ID | Method | Implementation | Formula |
|---|---|---|---|
| `M073` | Logistic Regression | `src.mathematics.machine_learning::run_073` | `P(Y=1\mid X)=\frac{1}{1+e^{-(\beta_0+\beta^{T}X)}}` |
| `M074` | Multinomial Logistic Regression | `src.mathematics.machine_learning::run_074` | `P(Y=k\mid X)=\frac{e^{\beta_k^{T}X}}{\sum_j e^{\beta_j^{T}X}}` |
| `M075` | Random Forest | `src.mathematics.machine_learning::run_075` | `\hat{P}(Y=k\mid x)=\frac{1}{B}\sum_{b=1}^{B}\hat{P}_b(Y=k\mid x)` |
| `M076` | Gradient Boosting | `src.mathematics.machine_learning::run_076` | `F_m(x)=F_{m-1}(x)+\nu h_m(x)` |
| `M077` | XGBoost | `src.mathematics.machine_learning::run_077` | `\mathcal{L}=\sum_i \ell(y_i,\hat{y}_i)+\sum_m\Omega(h_m)` |
| `M078` | LightGBM | `src.mathematics.machine_learning::run_078` | `\text{leaf-wise growth with histogram binning}` |
| `M079` | CatBoost | `src.mathematics.machine_learning::run_079` | `\text{ordered target statistics for categorical splits}` |
| `M080` | Support Vector Machines | `src.mathematics.machine_learning::run_080` | `\min_{w,b}\tfrac{1}{2}\\|w\\|^2 + C\sum_i \xi_i` |
| `M081` | K-Nearest Neighbours | `src.mathematics.machine_learning::run_081` | `\hat{P}(Y=k\mid x)=\frac{1}{K}\sum_{i \in N_K(x)}\mathbf{1}[y_i=k]` |
| `M082` | Naive Bayes | `src.mathematics.machine_learning::run_082` | `P(Y\mid X)\propto P(Y)\prod_i P(X_i\mid Y)` |
| `M083` | Neural Network Classification | `src.mathematics.machine_learning::run_083` | `h^{(l)}=\sigma(W^{(l)}h^{(l-1)}+b^{(l)})` |
| `M084` | Regularized Ensemble Learning | `src.mathematics.machine_learning::run_084` | `\hat{p} = \sum_m w_m \hat{p}_m,\quad w \in \Delta^{M-1}` |

## Category H - Advanced Probability, Ensembles and Validation (16 methods)

| ID | Method | Implementation | Formula |
|---|---|---|---|
| `M085` | Bayesian Model Averaging | `src.mathematics.advanced_statistics::run_085` | `P(Y\mid D)=\sum_m P(Y\mid M_m,D)P(M_m\mid D)` |
| `M086` | Regularized Stacking | `src.mathematics.advanced_statistics::run_086` | `w^{*}=\arg\min_{w \in \Delta^{M-1}}\\| \sum_m w_m \hat{p}_m - y \\|^2` |
| `M087` | Conformal Prediction | `src.mathematics.advanced_statistics::run_087` | `\mathcal{C}_\alpha(x)=\{y : s(x,y) \le \hat{q}_{1-\alpha}\}` |
| `M088` | Isotonic Probability Calibration | `src.mathematics.advanced_statistics::run_088` | `\hat{p}_{\text{iso}} = \arg\min_{g \text{ monotone}} \sum_i (g(\hat{p}_i)-y_i)^2` |
| `M089` | Platt Probability Calibration | `src.mathematics.advanced_statistics::run_089` | `P(y=1\mid s)=\frac{1}{1+e^{As+B}}` |
| `M090` | Dirichlet Probability Calibration | `src.mathematics.advanced_statistics::run_090` | `\hat{p}' = \mathrm{softmax}(W \log \hat{p} + b)` |
| `M091` | False Discovery Rate Analysis | `src.mathematics.advanced_statistics::run_091` | `\mathrm{FDR} = \mathbb{E}\left[\frac{V}{\max(R,1)}\right]` |
| `M092` | Multiple Hypothesis Correction | `src.mathematics.advanced_statistics::run_092` | `p_i^{\text{Holm}} = \max_{j \le i}\left((n-j+1)p_{(j)}\right)` |
| `M093` | Information-Theoretic Feature Selection | `src.mathematics.advanced_statistics::run_093` | `\mathrm{MI}(X_i;Y) = \sum p(x_i,y)\log\frac{p(x_i,y)}{p(x_i)p(y)}` |
| `M094` | SHAP-Based Feature Interpretation | `src.mathematics.advanced_statistics::run_094` | `\phi_i = \sum_{S \subseteq F \setminus \{i\}}\frac{\|S\|!(\|F\|-\|S\|-1)!}{\|F\|!}[f(S\cup\{i\})-f(S)]` |
| `M095` | Stability Selection | `src.mathematics.advanced_statistics::run_095` | `\hat{\Pi}_i = \frac{1}{B}\sum_{b=1}^{B}\mathbf{1}[i \in \hat{S}(D_b)]` |
| `M096` | Rolling Model Performance Weighting | `src.mathematics.advanced_statistics::run_096` | `w_{m,t} = \frac{\exp(-\gamma \bar{L}_{m,t-W:t})}{\sum_j \exp(-\gamma \bar{L}_{j,t-W:t})}` |
| `M097` | Regime-Conditional Probability Modelling | `src.mathematics.advanced_statistics::run_097` | `P(Y\mid \text{regime}=r) \perp \text{regime assignment uses only past data}` |
| `M098` | Ensemble Diversity Optimization | `src.mathematics.advanced_statistics::run_098` | `\rho_{ij} = \mathrm{corr}(\epsilon_i, \epsilon_j),\quad \sigma^2_{\text{ens}}=\sum_{i,j}w_iw_j\rho_{ij}\sigma_i\sigma_j` |
| `M099` | Online Bayesian Updating | `src.mathematics.advanced_statistics::run_099` | `P(\theta\mid x_{1:t}) \propto P(x_t\mid\theta)P(\theta\mid x_{1:t-1})` |
| `M100` | Sequential Probability Ratio Testing | `src.mathematics.advanced_statistics::run_100` | `\Lambda_n = \prod_{t=1}^{n}\frac{P_1(x_t)}{P_0(x_t)},\quad \text{stop when } \log\Lambda_n \notin (a,b)` |

