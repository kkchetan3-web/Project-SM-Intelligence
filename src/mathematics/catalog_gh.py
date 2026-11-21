"""Documentation records for Methods 73-100 (Categories G and H)."""

from __future__ import annotations

from src.mathematics.catalog_ab import M

G = "G - Machine Learning"
H = "H - Advanced Probability, Ensembles and Validation"

METHODS_GH = [
    M("M073", "Logistic Regression", G,
      r"P(Y=1\mid X)=\frac{1}{1+e^{-(\beta_0+\beta^{T}X)}}",
      "Binary logistic regression models log-odds as a linear function of features. Here the binary "
      "task is deliberately the coarsest useful one - predicting parity - because a linear model "
      "cannot represent a cyclic dependence over ten categories but can handle a two-class split "
      "honestly.",
      "Fit a binary logistic model and evaluate its probabilities chronologically.",
      ["Log-odds are linear in the features", "Observations are conditionally independent"],
      [("beta", "coefficient vector"), ("X", "feature vector"), ("p", "event probability")],
      ["Assemble causal features",
       "Fit on an expanding window with L2 regularisation",
       "Score out of sample against the parity-frequency baseline"],
      "Linear log-odds capture only monotone effects; the cyclic structure of digit sequences is "
      "invisible to it.",
      "Several hundred observations per fold.",
      "src.mathematics.machine_learning::run_073"),

    M("M074", "Multinomial Logistic Regression", G,
      r"P(Y=k\mid X)=\frac{e^{\beta_k^{T}X}}{\sum_j e^{\beta_j^{T}X}}",
      "Multinomial logistic regression produces a full probability distribution over ten outcomes "
      "with a shared linear structure. It is the honest baseline for 'can a learned model beat simple "
      "frequencies', and the coefficient count (K x d) makes its data appetite clear.",
      "Produce a complete 10-way distribution and compare it with frequency baselines.",
      ["The log-odds are linear in the features", "The outcome space is complete"],
      [("beta_k", "coefficient vector for class k"), ("K", "number of classes")],
      ["Assemble causal features",
       "Fit with multinomial loss and L2 penalty",
       "Evaluate log loss, Brier score and calibration out of sample"],
      "With 60+ features and 10 classes the parameter count is large relative to the sample; "
      "regularisation strength is the binding constraint.",
      "Several thousand observations for a stable fit.",
      "src.mathematics.machine_learning::run_074"),

    M("M075", "Random Forest", G,
      r"\hat{P}(Y=k\mid x)=\frac{1}{B}\sum_{b=1}^{B}\hat{P}_b(Y=k\mid x)",
      "A random forest averages many decorrelated trees, each grown on a bootstrap sample with a "
      "random feature subset at every split. The averaging reduces variance without much bias, and it "
      "captures interactions and threshold effects that a linear model cannot.",
      "Test whether a bagged tree ensemble extracts more from the feature set than a linear model.",
      ["Trees are grown on exchangeable training samples", "Averaging reduces variance"],
      [("B", "number of trees"), ("P_b", "probability from tree b")],
      ["Grow trees on bootstrap samples with random feature subsets",
       "Average their class probabilities",
       "Evaluate chronologically and inspect feature importance"],
      "Tree ensembles are stable but cannot extrapolate, and with limited signal they mostly "
      "reproduce the marginal distribution.",
      "Several thousand observations.",
      "src.mathematics.machine_learning::run_075", "Breiman (2001)"),

    M("M076", "Gradient Boosting", G,
      r"F_m(x)=F_{m-1}(x)+\nu h_m(x)",
      "Gradient boosting fits successive weak learners to the negative gradient of the loss, with a "
      "shrinkage factor controlling each step. Its strength is bias reduction on structured data; its "
      "weakness is that it will happily fit noise if the loss curve is not monitored out of sample.",
      "Evaluate boosted trees and check for the overfitting that this family invites.",
      ["The loss is differentiable", "Weak learners can be fitted to pseudo-residuals"],
      [("h_m", "weak learner at step m"), ("nu", "learning rate"), ("M", "number of boosting rounds")],
      ["Initialise with the base rate",
       "Iteratively fit to pseudo-residuals with a small learning rate",
       "Evaluate out of sample and compare with the simpler models"],
      "Boosting is prone to overfitting on noisy features; the configuration here uses shallow trees "
      "and explicit L2 regularisation for that reason.",
      "Several thousand observations.",
      "src.mathematics.machine_learning::run_076", "Friedman (2001)"),

    M("M077", "XGBoost", G,
      r"\mathcal{L}=\sum_i \ell(y_i,\hat{y}_i)+\sum_m\Omega(h_m)",
      "XGBoost adds explicit regularisation and second-order loss approximations to gradient "
      "boosting. The objective exposes the complexity penalty directly, which makes the bias-variance "
      "trade-off a tunable quantity rather than an emergent property.",
      "Evaluate a regularised boosted-tree implementation.",
      ["The regularised objective is correctly specified", "Training is strictly chronological"],
      [("Omega", "tree complexity penalty"), ("lambda", "L2 leaf penalty"), ("eta", "shrinkage")],
      ["Configure the regularised objective",
       "Train on the expanding window",
       "Evaluate the full probability distribution out of sample"],
      "Implementation differences between boosting libraries are second-order compared with the "
      "effect of the data having no signal.",
      "Several thousand observations.",
      "src.mathematics.machine_learning::run_077", "Chen & Guestrin (2016)"),

    M("M078", "LightGBM", G,
      r"\text{leaf-wise growth with histogram binning}",
      "LightGBM grows trees leaf-wise and bins continuous features into histograms, which makes it "
      "fast and able to find deep interactions in large data. On modest samples the leaf-wise growth "
      "can overfit unless leaf size is constrained.",
      "Evaluate histogram-based boosting with explicit leaf-size control.",
      ["Histogram binning preserves the relevant feature information", "Leaf constraints prevent overfitting"],
      [("num_leaves", "maximum leaves per tree"), ("min_data_in_leaf", "minimum observations per leaf")],
      ["Configure leaf-wise growth with a leaf-size floor",
       "Train chronologically",
       "Evaluate out of sample against the other boosted model"],
      "Speed is not accuracy: the same lack of signal caps every boosted implementation.",
      "Several thousand observations.",
      "src.mathematics.machine_learning::run_078", "Ke et al. (2017)"),

    M("M079", "CatBoost", G,
      r"\text{ordered target statistics for categorical splits}",
      "CatBoost targets categorical features with ordered target statistics, designed to avoid the "
      "target leakage that naive encoding introduces. Even where features are numeric, its ordered "
      "boosting scheme is a useful robustness check on the other boosted models.",
      "Evaluate ordered boosting and target-statistic handling.",
      ["Ordered boosting reduces target leakage", "Categorical handling is consistent"],
      [("ordered statistics", "leak-free categorical encoding"), ("depth", "tree depth")],
      ["Configure ordered boosting",
       "Train chronologically",
       "Evaluate out of sample and compare with XGBoost and LightGBM"],
      "The library's advantages concentrate on categorical feature engineering, which is only "
      "indirectly relevant here.",
      "Several thousand observations.",
      "src.mathematics.machine_learning::run_079", "Prokhorenkova et al. (2018)"),

    M("M080", "Support Vector Machines", G,
      r"\min_{w,b}\tfrac{1}{2}\|w\|^2 + C\sum_i \xi_i",
      "An SVM finds the maximum-margin separating boundary, optionally in a kernel-induced space. "
      "Probabilities require an extra calibration step (Platt scaling), which is fitted internally "
      "and is therefore a source of additional variance worth reporting.",
      "Evaluate a maximum-margin classifier with calibrated probabilities.",
      ["Classes are separable to some degree in feature space", "The kernel bandwidth is appropriate"],
      [("C", "regularisation strength"), ("xi", "slack variables"), ("gamma", "RBF kernel width")],
      ["Standardise features inside each fold",
       "Fit the kernel SVM on the expanding window",
       "Convert decision values to probabilities and evaluate"],
      "SVM probability calibration is itself a fitted model, adding a layer of variance; and kernel "
      "SVMs scale poorly beyond a few thousand observations.",
      "Several thousand observations.",
      "src.mathematics.machine_learning::run_080", "Cortes & Vapnik (1995)"),

    M("M081", "K-Nearest Neighbours", G,
      r"\hat{P}(Y=k\mid x)=\frac{1}{K}\sum_{i \in N_K(x)}\mathbf{1}[y_i=k]",
      "KNN predicts from the outcomes of the most similar historical feature vectors. It makes no "
      "global parametric assumption, so it can capture local structure - but in a high-dimensional "
      "feature space distances concentrate and neighbourhoods stop being meaningful.",
      "Test whether local similarity in feature space predicts the next outcome.",
      ["Similar feature vectors imply similar outcome distributions", "The distance metric is meaningful"],
      [("N_K(x)", "the K nearest neighbours"), ("K", "neighbourhood size")],
      ["Standardise features inside each fold",
       "Find the K nearest historical rows",
       "Average their outcomes into a probability vector"],
      "With 60+ dimensions the curse of dimensionality dominates, which is itself the finding.",
      "Several thousand observations.",
      "src.mathematics.machine_learning::run_081"),

    M("M082", "Naive Bayes", G,
      r"P(Y\mid X)\propto P(Y)\prod_i P(X_i\mid Y)",
      "Naive Bayes assumes conditional independence of features given the class. That assumption is "
      "violated spectacularly by a feature set containing cumulative frequencies, so its failure here "
      "is expected and instructive rather than surprising.",
      "Demonstrate the cost of the conditional-independence assumption.",
      ["Features are conditionally independent given the class"],
      [("P(X_i|Y)", "class-conditional feature likelihood"), ("P(Y)", "class prior")],
      ["Estimate class priors",
       "Estimate per-feature class-conditional densities",
       "Multiply and normalise, then evaluate out of sample"],
      "The independence assumption produces wild overconfidence when features are correlated, which "
      "manifests as catastrophically high log loss.",
      "Several hundred observations per class.",
      "src.mathematics.machine_learning::run_082"),

    M("M083", "Neural Network Classification", G,
      r"h^{(l)}=\sigma(W^{(l)}h^{(l-1)}+b^{(l)})",
      "A small multilayer perceptron learns nonlinear feature combinations through hidden layers. On a "
      "few thousand noisy observations the parameter count is large relative to the signal, so the "
      "regularisation and early-stopping configuration dominates the result.",
      "Evaluate a nonlinear learned representation under strict chronological validation.",
      ["The architecture is adequate", "Regularisation prevents memorisation"],
      [("W", "weight matrices"), ("sigma", "activation function"), ("alpha", "L2 penalty")],
      ["Standardise features inside each fold",
       "Fit a small MLP with L2 regularisation",
       "Evaluate against the linear model and the baselines"],
      "Neural networks need far more data than these markets provide; the result is a data-requirement "
      "finding as much as a modelling one.",
      "Tens of thousands of observations for this architecture to be well determined.",
      "src.mathematics.machine_learning::run_083"),

    M("M084", "Regularized Ensemble Learning", G,
      r"\hat{p} = \sum_m w_m \hat{p}_m,\quad w \in \Delta^{M-1}",
      "Combining predictors with non-negative weights summing to one constrains the ensemble to the "
      "convex hull of its members, which bounds its worst case by its best member. The weights are "
      "fitted on validation predictions only.",
      "Test whether a regularised combination beats the best single model.",
      ["Base predictions are out of sample", "Weights are fitted on a separate slice"],
      [("w_m", "ensemble weight"), ("Delta", "the probability simplex")],
      ["Collect out-of-sample predictions from the base models",
       "Fit simplex-constrained weights on an earlier slice",
       "Evaluate the combination on a later slice"],
      "A convex combination cannot exceed the best member's expected performance except through "
      "variance reduction, which is small when the members are highly correlated.",
      "Out-of-fold predictions from at least three models.",
      "src.mathematics.machine_learning::run_084"),

    M("M085", "Bayesian Model Averaging", H,
      r"P(Y\mid D)=\sum_m P(Y\mid M_m,D)P(M_m\mid D)",
      "BMA weights models by their posterior probability, which penalises complexity through the "
      "evidence term. It is the principled alternative to picking a single winner, and it degrades "
      "gracefully when no model is clearly best.",
      "Combine models by posterior model probability.",
      ["The model space is enumerable", "Posterior probabilities are estimable"],
      [("M_m", "model m"), ("P(M_m|D)", "posterior model probability")],
      ["Compute each model's marginal likelihood approximation",
       "Normalise to posterior weights",
       "Average the predictive distributions"],
      "The BIC approximation to the evidence is crude for non-nested models, so the weights are an "
      "approximation and are labelled as one.",
      "Several candidate models with out-of-sample predictions.",
      "src.mathematics.advanced_statistics::run_085"),

    M("M086", "Regularized Stacking", H,
      r"w^{*}=\arg\min_{w \in \Delta^{M-1}}\| \sum_m w_m \hat{p}_m - y \|^2",
      "Stacking learns a second-level combiner from out-of-fold predictions. The simplex constraint is "
      "the regularisation: it prevents negative weights and extrapolation, which are the main ways "
      "stacking overfits.",
      "Fit a constrained meta-learner on out-of-fold predictions.",
      ["Base predictions are genuinely out of fold", "The meta-sample is disjoint from the test"],
      [("w", "meta-weights"), ("p_m", "base probability matrix")],
      ["Generate strictly out-of-fold base predictions",
       "Fit simplex-constrained weights",
       "Evaluate the stack on untouched later data"],
      "The meta-sample is small relative to the number of base models, and any leakage in the base "
      "predictions is amplified at this level.",
      "Out-of-fold predictions from at least three models.",
      "src.mathematics.advanced_statistics::run_086"),

    M("M087", "Conformal Prediction", H,
      r"\mathcal{C}_\alpha(x)=\{y : s(x,y) \le \hat{q}_{1-\alpha}\}",
      "Conformal prediction builds prediction sets with a distribution-free marginal coverage "
      "guarantee, provided calibration and test points are exchangeable. Time series violate "
      "exchangeability, so the guarantee is nominal rather than actual - and measuring the gap between "
      "nominal and empirical coverage is the useful part here.",
      "Construct prediction sets and measure realised coverage against the nominal level.",
      ["Exchangeability between calibration and test points"],
      [("s(x,y)", "nonconformity score"), ("q", "calibration quantile"), ("coverage", "1-alpha")],
      ["Score the calibration set",
       "Take the appropriate empirical quantile",
       "Build test sets and measure realised coverage"],
      "Exchangeability fails for dependent sequences, so nominal coverage will not be achieved; the "
      "method reports the discrepancy rather than assuming it away.",
      "A calibration set of at least a few hundred observations.",
      "src.mathematics.advanced_statistics::run_087", "Vovk et al. (2005)"),

    M("M088", "Isotonic Probability Calibration", H,
      r"\hat{p}_{\text{iso}} = \arg\min_{g \text{ monotone}} \sum_i (g(\hat{p}_i)-y_i)^2",
      "Isotonic regression fits the best monotone mapping from raw scores to observed frequencies. It "
      "is nonparametric and flexible, which is both its strength and its overfitting risk on small "
      "calibration samples.",
      "Recalibrate probabilities with a monotone mapping fitted on a separate slice.",
      ["The calibration relation is monotone", "The calibration sample is large enough"],
      [("g", "monotone mapping"), ("y_i", "binary outcome of class membership")],
      ["Fit one-vs-rest isotonic models on the calibration slice",
       "Apply to later predictions and renormalise",
       "Evaluate log loss and the calibration slope"],
      "Isotonic maps can be non-monotone in the multiclass setting after renormalisation, and they "
      "cannot extrapolate beyond the calibration range.",
      "Several hundred calibration observations.",
      "src.mathematics.advanced_statistics::run_088"),

    M("M089", "Platt Probability Calibration", H,
      r"P(y=1\mid s)=\frac{1}{1+e^{As+B}}",
      "Platt scaling fits a two-parameter logistic transformation to raw scores. It is far more "
      "constrained than isotonic regression, which makes it safer on small calibration samples and "
      "unable to correct non-monotone miscalibration.",
      "Recalibrate with a parametric sigmoid fitted on a separate slice.",
      ["The miscalibration is approximately sigmoidal", "The calibration sample is representative"],
      [("A", "slope parameter"), ("B", "intercept parameter"), ("s", "raw score")],
      ["Fit the logistic transformation per class on the calibration slice",
       "Apply and renormalise",
       "Compare calibrated and uncalibrated log loss"],
      "Two parameters cannot fix arbitrary miscalibration, and the renormalisation step distorts the "
      "fitted per-class maps.",
      "Several hundred calibration observations.",
      "src.mathematics.advanced_statistics::run_089", "Platt (1999)"),

    M("M090", "Dirichlet Probability Calibration", H,
      r"\hat{p}' = \mathrm{softmax}(W \log \hat{p} + b)",
      "Dirichlet calibration applies a full linear map in log-probability space, which can correct "
      "multi-class miscalibration that per-class methods cannot. With K=10 it has 110 parameters, "
      "which is dangerous on small samples - hence the L2 shrinkage toward the identity.",
      "Recalibrate the full probability vector and evaluate on later data.",
      ["The miscalibration is approximately log-linear", "The calibration sample supports K x K parameters"],
      [("W", "calibration matrix"), ("b", "bias vector"), ("l2", "shrinkage toward identity")],
      ["Fit W and b on the calibration slice by gradient descent",
       "Apply to later predictions",
       "Evaluate log loss, ECE and the calibration slope"],
      "The parameter count is large relative to typical calibration samples; shrinkage toward the "
      "identity is essential and is part of the specification rather than a tuning detail.",
      "At least a few thousand calibration observations for the full map.",
      "src.mathematics.advanced_statistics::run_090"),

    M("M091", "False Discovery Rate Analysis", H,
      r"\mathrm{FDR} = \mathbb{E}\left[\frac{V}{\max(R,1)}\right]",
      "Testing 100 methods produces many p-values, and at alpha=0.05 roughly five spurious rejections "
      "are expected by construction. The Benjamini-Hochberg procedure controls the expected proportion "
      "of false discoveries and is far less conservative than family-wise correction when many tests "
      "are genuinely null.",
      "Control the false discovery rate across all method p-values.",
      ["Tests are independent or positively dependent", "P-values are valid under the null"],
      [("V", "false discoveries"), ("R", "total rejections"), ("q", "target FDR")],
      ["Collect every p-value produced by the method suite",
       "Sort and apply the Benjamini-Hochberg step-up procedure",
       "Report which findings survive"],
      "BH assumes independence or positive dependence; the tests here are heavily correlated, which "
      "makes it conservative rather than invalid.",
      "A collected set of valid p-values.",
      "src.mathematics.advanced_statistics::run_091", "Benjamini & Hochberg (1995)"),

    M("M092", "Multiple Hypothesis Correction", H,
      r"p_i^{\text{Holm}} = \max_{j \le i}\left((n-j+1)p_{(j)}\right)",
      "Family-wise error control bounds the probability of *any* false rejection. Holm's step-down "
      "procedure is uniformly more powerful than Bonferroni while retaining that guarantee, which "
      "makes it the sensible default when a single false claim is costly.",
      "Apply family-wise error control and compare it with FDR control.",
      ["Tests are valid marginally", "The family of tests is defined in advance"],
      [("p_(j)", "j-th ordered p-value"), ("n", "number of tests")],
      ["Order the p-values",
       "Apply the Holm step-down adjustment",
       "Compare surviving findings with the BH set"],
      "FWER control is very strict with 100 correlated tests; it is reported alongside FDR rather "
      "than instead of it.",
      "A defined family of tests.",
      "src.mathematics.advanced_statistics::run_092", "Holm (1979)"),

    M("M093", "Information-Theoretic Feature Selection", H,
      r"\mathrm{MI}(X_i;Y) = \sum p(x_i,y)\log\frac{p(x_i,y)}{p(x_i)p(y)}",
      "Ranking features by mutual information with the target selects on relevance rather than on "
      "linear correlation. Redundancy between selected features is then removed with conditional "
      "mutual information, which is the principled way to avoid 40 collinear frequency features.",
      "Rank features by information content and remove redundancy.",
      ["Features are estimable", "Relevance implies potential usefulness"],
      [("MI", "mutual information with the target"), ("redundancy", "MI between features")],
      ["Compute MI between each feature and the target",
       "Remove features that are redundant with a stronger one",
       "Evaluate the retained set chronologically"],
      "MI is biased upward for continuous features with many effective bins; the ranking is therefore "
      "computed on discretised features with a permutation reference.",
      "Several hundred observations.",
      "src.mathematics.advanced_statistics::run_093"),

    M("M094", "SHAP-Based Feature Interpretation", H,
      r"\phi_i = \sum_{S \subseteq F \setminus \{i\}}\frac{|S|!(|F|-|S|-1)!}{|F|!}[f(S\cup\{i\})-f(S)]",
      "SHAP values attribute a prediction to its features using cooperative-game Shapley values. They "
      "are locally accurate and consistent, which makes them the best available tool for asking "
      "whether a model is relying on anything sensible - or on a spurious artefact.",
      "Explain model predictions and check for spurious reliance.",
      ["Features are treated as players in a cooperative game", "The model is deterministic"],
      [("phi_i", "attribution to feature i"), ("F", "feature set"), ("S", "coalition")],
      ["Fit the model on the training window",
       "Compute Shapley attributions for a sample of predictions",
       "Rank features by mean absolute attribution"],
      "Attributions explain the model, not the world; a large attribution to a meaningless feature is "
      "a warning about the model rather than a discovery.",
      "A fitted tree or linear model.",
      "src.mathematics.advanced_statistics::run_094", "Lundberg & Lee (2017)"),

    M("M095", "Stability Selection", H,
      r"\hat{\Pi}_i = \frac{1}{B}\sum_{b=1}^{B}\mathbf{1}[i \in \hat{S}(D_b)]",
      "Stability selection refits a selection procedure on many subsamples and keeps features chosen "
      "frequently. It converts a fragile, sample-specific selection into a reproducible one and "
      "provides a principled threshold on the selection frequency.",
      "Identify features that are selected reproducibly.",
      ["Subsamples are drawn from the same distribution", "The base selector is sparse"],
      [("Pi_i", "selection probability of feature i"), ("S(D_b)", "selected set on subsample b")],
      ["Draw B subsamples",
       "Run the selector on each",
       "Report selection frequencies and retain features above the threshold"],
      "Frequent selection can reflect a strong but spurious association that is stable within the "
      "sample, so stability is necessary but not sufficient.",
      "Enough observations for subsampling to be informative.",
      "src.mathematics.advanced_statistics::run_095", "Meinshausen & Buhlmann (2010)"),

    M("M096", "Rolling Model Performance Weighting", H,
      r"w_{m,t} = \frac{\exp(-\gamma \bar{L}_{m,t-W:t})}{\sum_j \exp(-\gamma \bar{L}_{j,t-W:t})}",
      "Adaptive weighting shifts ensemble mass toward models that have recently performed well. It "
      "helps when relative performance is persistent and hurts when it is noise - which is precisely "
      "the regime these markets inhabit.",
      "Test whether adaptive weighting improves on fixed weights.",
      ["Recent performance predicts near-future performance", "Weights are computed causally"],
      [("w_m,t", "weight for model m at time t"), ("gamma", "sharpness"),
       ("W", "lookback window")],
      ["Compute rolling per-model log loss using only past steps",
       "Convert to weights with a softmax",
       "Apply to the next step and evaluate the resulting ensemble"],
      "In a world where all models perform equally, adaptive weighting adds pure noise to the "
      "combination.",
      "A long out-of-sample window.",
      "src.mathematics.advanced_statistics::run_096"),

    M("M097", "Regime-Conditional Probability Modelling", H,
      r"P(Y\mid \text{regime}=r) \perp \text{regime assignment uses only past data}",
      "Regime-conditional modelling estimates a separate distribution per regime. The critical "
      "discipline is that regime assignment must use only information available at prediction time; "
      "assigning regimes with full-sample knowledge and then 'predicting' within them is one of the "
      "most common and most fatal leakage patterns.",
      "Estimate regime-specific distributions with causal regime assignment.",
      ["Regimes are identifiable from past data only", "Regimes are persistent enough to matter"],
      [("r", "regime label"), ("P(Y|r)", "regime-conditional distribution")],
      ["Define a causal regime rule from past statistics",
       "Estimate the conditional distribution within each regime",
       "Compare predictive loss with the unconditional model"],
      "Regime definitions are themselves a researcher degree of freedom; with many candidate rules, "
      "some will appear to help by chance.",
      "Several hundred observations per regime.",
      "src.mathematics.advanced_statistics::run_097"),

    M("M098", "Ensemble Diversity Optimization", H,
      r"\rho_{ij} = \mathrm{corr}(\epsilon_i, \epsilon_j),\quad \sigma^2_{\text{ens}}=\sum_{i,j}w_iw_j\rho_{ij}\sigma_i\sigma_j",
      "Ensemble variance depends on the correlation between member errors. Two models with identical "
      "accuracy but independent errors combine better than two correlated ones, so diversity is a "
      "quantity worth measuring rather than assuming.",
      "Measure error diversity and test whether it produces a better combination.",
      ["Base models are individually reasonable", "Error correlation is estimable"],
      [("rho_ij", "error correlation"), ("sigma", "error standard deviation")],
      ["Compute per-observation losses for each model",
       "Correlate them across models",
       "Compare the diversity-weighted combination with a simple average"],
      "Diversity among models that are all equally uninformative produces no gain, only a different "
      "way of averaging noise.",
      "At least three base models.",
      "src.mathematics.advanced_statistics::run_098"),

    M("M099", "Online Bayesian Updating", H,
      r"P(\theta\mid x_{1:t}) \propto P(x_t\mid\theta)P(\theta\mid x_{1:t-1})",
      "Online Bayesian updating maintains the posterior sequentially, so each new draw refines the "
      "estimate without reprocessing history. For a Dirichlet-categorical model this is exact and "
      "cheap, and the posterior at time t is the natural 'state of knowledge' at that moment.",
      "Verify that sequential updating reproduces the batch posterior and improves calibration.",
      ["The model is correctly specified", "The prior is fixed a priori"],
      [("theta", "probability vector"), ("posterior", "state of knowledge after t draws")],
      ["Start from the prior",
       "Update the Dirichlet parameters with each draw",
       "Compare sequential forecasts against batch re-estimation"],
      "Sequential updating compounds model misspecification: if the process is non-stationary the "
      "posterior becomes steadily more wrong.",
      "Any non-empty sequence.",
      "src.mathematics.advanced_statistics::run_099"),

    M("M100", "Sequential Probability Ratio Testing", H,
      r"\Lambda_n = \prod_{t=1}^{n}\frac{P_1(x_t)}{P_0(x_t)},\quad \text{stop when } \log\Lambda_n \notin (a,b)",
      "SPRT tests two simple hypotheses as data arrive, with Wald's optimality result guaranteeing the "
      "smallest expected sample size for given error rates. It is the natural framework for asking "
      "'how much evidence would it take to convince me that this market is biased?'",
      "Quantify how much data would be needed to detect a specified bias.",
      ["Two simple hypotheses are specified", "Observations are independent under each"],
      [("Lambda_n", "likelihood ratio"), ("a, b", "decision boundaries"),
       ("alpha, beta", "error rates")],
      ["Specify a null and an alternative probability vector",
       "Accumulate the log likelihood ratio as draws arrive",
       "Report the stopping time and the implied sample-size requirement"],
      "SPRT assumes i.i.d. observations; under dependence the error rates are not honoured, which is "
      "reported as a caveat rather than ignored.",
      "A specified alternative hypothesis.",
      "src.mathematics.advanced_statistics::run_100", "Wald (1945)"),
]
