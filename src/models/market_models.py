"""Estimator factories.

Everything here produces an object with the sklearn ``fit`` / ``predict_proba``
interface so the walk-forward harness can treat them interchangeably. The panel
is deliberately broad (linear, tree, kernel, neural, generative) because Section
14 forbids assuming that complexity buys accuracy - the comparison has to be
made, not asserted.

Determinism: every stochastic estimator is seeded from the project seed, so a
re-run reproduces the same probabilities bit-for-bit.
"""

from __future__ import annotations

from typing import Any, Callable

import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import (
    ExtraTreesClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

SEED = 20250101
N_CLASSES = 10


def _scaled(estimator: Any) -> Pipeline:
    """Median-impute, then scale, then model - all fitted inside the training fold.

    The imputer is not cosmetic: the causal feature matrix legitimately contains
    NaN for the first observation of every lagged cross-market column. Dropping
    those rows would bias the evaluation window, and letting sklearn raise would
    silently turn a working model into a constant-uniform forecast (a failure mode
    this platform hit during development and now guards against).
    """
    return Pipeline([
        ("impute", SimpleImputer(strategy="median", keep_empty_features=True)),
        ("scale", StandardScaler()),
        ("model", estimator),
    ])


def _unscaled(estimator: Any) -> Pipeline:
    """Impute only - for estimators that do not need scaling."""
    return Pipeline([
        ("impute", SimpleImputer(strategy="median", keep_empty_features=True)),
        ("model", estimator),
    ])


def build(model_name: str, *, seed: int = SEED, n_classes: int = N_CLASSES) -> Any:
    """Construct a fresh, unfitted estimator."""
    if model_name == "logistic":
        return _scaled(LogisticRegression(
            C=0.1, max_iter=800, solver="lbfgs", random_state=seed,
        ))
    if model_name == "logistic_strong_reg":
        return _scaled(LogisticRegression(
            C=0.01, max_iter=800, solver="lbfgs", random_state=seed,
        ))
    if model_name == "random_forest":
        return _unscaled(RandomForestClassifier(
            n_estimators=40, max_depth=12, min_samples_leaf=15,
            max_features="sqrt", random_state=seed, n_jobs=1,
        ))
    if model_name == "extra_trees":
        return _unscaled(ExtraTreesClassifier(
            n_estimators=40, max_depth=12, min_samples_leaf=15,
            max_features="sqrt", random_state=seed, n_jobs=1,
        ))
    if model_name == "gradient_boosting":
        return HistGradientBoostingClassifier(
            max_iter=80, learning_rate=0.10, max_depth=4, min_samples_leaf=30,
            l2_regularization=1.0, early_stopping=False, random_state=seed,
        )
    if model_name == "knn":
        return _scaled(KNeighborsClassifier(n_neighbors=75, weights="distance"))
    if model_name == "naive_bayes":
        return Pipeline([
            ("impute", SimpleImputer(strategy="median", keep_empty_features=True)),
            ("model", GaussianNB(var_smoothing=1e-3)),
        ])
    if model_name == "lda":
        return _scaled(LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto"))
    if model_name == "mlp":
        return _scaled(MLPClassifier(
            hidden_layer_sizes=(32,), alpha=0.01, max_iter=150,
            early_stopping=False, random_state=seed,
        ))
    if model_name == "xgboost":
        from xgboost import XGBClassifier
        return XGBClassifier(
            n_estimators=80, max_depth=4, learning_rate=0.10, subsample=0.8,
            colsample_bytree=0.8, reg_lambda=1.0, objective="multi:softprob",
            num_class=n_classes, tree_method="hist", random_state=seed,
            n_jobs=1, verbosity=0, eval_metric="mlogloss",
        )
    if model_name == "lightgbm":
        from lightgbm import LGBMClassifier
        return LGBMClassifier(
            n_estimators=80, num_leaves=15, min_child_samples=40, learning_rate=0.10,
            subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0, random_state=seed,
            n_jobs=1, verbose=-1,
        )
    if model_name == "catboost":
        from catboost import CatBoostClassifier
        return CatBoostClassifier(
            iterations=80, depth=4, learning_rate=0.10, loss_function="MultiClass",
            random_seed=seed, verbose=0, allow_writing_files=False, thread_count=1,
        )
    if model_name == "svm":
        from sklearn.svm import SVC
        return _scaled(SVC(
            kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=seed,
        ))
    raise ValueError(f"unknown model '{model_name}'")


#: Methods 73-84 map onto these factories.
MODEL_FACTORIES: dict[str, Callable[[], Any]] = {
    "logistic": lambda: build("logistic"),
    "logistic_strong_reg": lambda: build("logistic_strong_reg"),
    "random_forest": lambda: build("random_forest"),
    "extra_trees": lambda: build("extra_trees"),
    "gradient_boosting": lambda: build("gradient_boosting"),
    "knn": lambda: build("knn"),
    "naive_bayes": lambda: build("naive_bayes"),
    "lda": lambda: build("lda"),
    "mlp": lambda: build("mlp"),
    "xgboost": lambda: build("xgboost"),
    "lightgbm": lambda: build("lightgbm"),
    "catboost": lambda: build("catboost"),
    "svm": lambda: build("svm"),
}

#: The subset used for the full 100-method sweep, chosen to bound runtime while
#: still covering every model family.
CORE_MODELS = [
    "logistic", "random_forest", "gradient_boosting", "knn", "naive_bayes", "mlp",
    "xgboost", "lightgbm", "catboost", "svm",
]

#: Refit cadence per model, in prediction steps. Slower estimators are refitted
#: less often; the schedule is fixed a priori and reported with every result, so
#: it cannot be tuned on the test set.
REFIT_SCHEDULE = {
    "logistic": 80, "logistic_strong_reg": 80, "random_forest": 80,
    "extra_trees": 80, "gradient_boosting": 80, "knn": 80, "naive_bayes": 80,
    "lda": 80, "mlp": 80, "xgboost": 100, "lightgbm": 100, "catboost": 120, "svm": 160,
}


def describe(model_name: str) -> dict[str, Any]:
    """Static description used in the model documentation and registry."""
    descriptions = {
        "logistic": ("Multinomial logistic regression", "linear", "none",
                     "C=0.1, lbfgs, standardised features"),
        "logistic_strong_reg": ("Multinomial logistic, heavy L2", "linear", "L2",
                                "C=0.01"),
        "random_forest": ("Random forest classifier", "bagged trees", "max_depth=12",
                          "40 trees, sqrt features, min_samples_leaf=15"),
        "extra_trees": ("Extremely randomised trees", "bagged trees", "max_depth=12",
                        "60 trees, random splits"),
        "gradient_boosting": ("Histogram gradient boosting", "boosted trees", "L2=1.0",
                              "80 iters, lr=0.10, depth 4"),
        "knn": ("K-nearest neighbours", "instance based", "k=75",
                "distance weights, standardised"),
        "naive_bayes": ("Gaussian naive Bayes", "generative", "var_smoothing=1e-3",
                        "conditional independence assumption"),
        "lda": ("Linear discriminant analysis", "linear generative", "shrinkage=auto",
                "Ledoit-Wolf shrinkage"),
        "mlp": ("Multi-layer perceptron", "neural network", "alpha=1e-3",
                "32 hidden units, alpha=0.01"),
        "xgboost": ("XGBoost", "boosted trees", "reg_lambda=1.0",
                    "80 rounds, depth 4, subsample 0.8"),
        "lightgbm": ("LightGBM", "boosted trees (leaf-wise)", "reg_lambda=1.0",
                     "80 rounds, 15 leaves, min_child_samples=40"),
        "catboost": ("CatBoost", "ordered boosting", "depth=4",
                     "80 iterations, MultiClass loss"),
        "svm": ("Support vector machine (RBF)", "kernel", "C=1.0",
                "Platt-scaled probabilities, standardised"),
    }
    name, family, regularisation, detail = descriptions.get(
        model_name, (model_name, "unknown", "unknown", ""))
    return {"name": name, "family": family, "regularisation": regularisation,
            "detail": detail, "deterministic": True, "seed": SEED}
