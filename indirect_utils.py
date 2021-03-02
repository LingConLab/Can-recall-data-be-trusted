from sklearn.base import BaseEstimator
import pandas as pd
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from itertools import product
import numpy as np

def generate_x_y(data, real_col, cat_col, y):
    data_real = data[real_col]
    data_cat = data[cat_col]
    data_cat = pd.get_dummies(data_cat)
    X = pd.concat([data_real, data_cat], axis=1)
    if y in X.columns:
        X = X.drop(y, axis=1)
    return X, data[y].rename('y') 

class DispatchEstimator(BaseEstimator):
    """
    We assume that data type is first column and takes values 0 and 1
    """
    def __init__(self, base_estimator, **kwargs):
        if isinstance(base_estimator, tuple) or isinstance(base_estimator, list):
            self.base_estimator = list(base_estimator)
        elif isinstance(base_estimator, BaseEstimator):
            self.base_estimator = [base_estimator(**kwargs),
                                   base_estimator(**kwargs)]
        else:
            raise TypeError("Unknown base_estimator")
            
    def fit(self, X, y):
        if hasattr(X, 'todense'):
            X = X.todense()
        X, y = check_X_y(X, y, accept_sparse=False)
        assert set(np.unique(X[:, 0])) == {0, 1}
        for datatype in [0, 1]:
            mask = X[:, 0] == datatype
            self.base_estimator[datatype].fit(X[mask][:, 1:],
                                              y[mask])
        self.is_fitted_ = True
        return self
    
    def _predict(self, X, method="predict"):
        """
        This is a helper function that invokes either 
        `self.base_estimator[d].predict` or `self.base_estimator[d].predict_proba`
        depending on the value of `method` argument.
        
        Uses some `getattr` magic to avoid code duplication. 
        (Probably, it will be much simpler just to add a couple of if's but 
        the temptation to use fancy features of Python to avoid code duplication 
        is too strong.)
        """
        if method not in ("predict", "predict_proba"):
            raise NotImplementedError(
              "method should be in ('predict', 'predict_proba')")
        if hasattr(X, 'todense'):
            X = X.todense()
            
        assert set(np.unique(X[:, 0])) == {0, 1}
        
        X = check_array(X, accept_sparse=True)
        check_is_fitted(self, 'is_fitted_')
        
        # we need to know the shape of the output
        # let's probe appropriate method of self.base_estimator[0]
        result_shape = getattr(self.base_estimator[0], 
                               method)(X[:1, 1:]).shape
        
        # we replace first element in shape with the number of samples
        y = np.zeros((X.shape[0],) + result_shape[1:])
        
        for datatype in [0, 1]:
            mask = X[:, 0] == datatype
            X_ = X[mask]
            y[mask] = getattr(self.base_estimator[datatype],
                              method)(X_[:, 1:])
        return y

    def predict(self, X):
        return self._predict(X, method="predict")
    
    def predict_proba(self, X):
        return self._predict(X, method="predict_proba")
    
def fullspace(data, variables):
    """
    Makes a dataframe like presented in `data`
    but with all possible combinations of values of variables `variables`
    """
    
    values = {var: data[var].unique() for var in variables}
    return pd.DataFrame.from_records(product(*values.values()), columns=variables)


def stratified_permute(column, strats=5):
    """
    Splits the column into `strats` parts, then permute each part separately
    To use this function meaningfully you have to make sure
    that the variable you want to stratify by is sorted
    """
    newcolumn_parts = []
    step = (len(column)) // (strats)
    for i in range(strats):
        newcolumn_parts.append(
            column[i * len(column) // strats: 
                   (i + 1) * len(column) // strats]
            .sample(frac=1))
    return pd.concat(newcolumn_parts).reset_index(drop=True)

def logodds(x, nan_policy='raise'):
    if nan_policy == 'raise':
        if (x <= 0).any() or (x >= 1).any():
            raise ValueError("Cannot find log odds for values 0 or 1")
    return np.log(x / (1 - x))

def trimmed(f, x, margin=1):
    """
    Apply function `f` to all values of array_like `x` where `0 < x < 1`.
    For values of `x` that are 0 or 1, we return minimum / maximum of all values 
    of f for internal points, minus / plus margin.
    
    Useful in combination with logodds for future visualization 
    (i.e. values minimum - margin and maximum + margin correspond to -∞ and +∞)
    """
   
    x = x.copy()
    
    assert ((x >= 0) & (x <= 1)).all()
    
    internal_points = (x != 0) & (x != 1)
    x[internal_points] = f(x[internal_points])
    f_max = x[internal_points].max()
    f_min = x[internal_points].min()
    x[x == 1] = f_max + margin
    x[x == 0] = f_min - margin
    return x
    
def tologodds(df, y):
    """
    Converts column `y` of dataframe `df` to its trimmed logodds.
    Name is preserved.
    """
    return df.assign(**{y: df[y].pipe(lambda x: trimmed(logodds, x))})

def get_delta(data, use_logodds=False):
    """
    Finds delta: data.query("type == 0")['pred'] - data.query("type == 1")['pred'],
    adds to dataframe (one half of it) under name `"delta"`
    
    If `use_logodds` is `True`, apply `logodds` finds difference between logodds.
    
    Assumes that data.query("type == 0") and data.query("type == 1") are identical with respect
    all variables except `pred`
    """
    
    data_type0 = data.query("type == 0").reset_index(drop=True)
    data_type1 = data.query("type == 1").reset_index(drop=True)
    assert (data_type0.drop(columns=['type', 'pred']) == 
            data_type1.drop(columns=['type', 'pred'])).all().all()
    
    if not use_logodds:
        delta = data_type0['pred'] - data_type1['pred']
    else:
        delta = logodds(data_type0['pred']) - logodds(data_type1['pred'])

    delta_df = data_type0.drop(columns=['type', 'pred']).assign(delta=delta)
    return delta_df

def identity(x):
    return x

residence_info = pd.read_csv("data/residence_info.csv")

def read_data(filename):
    return (pd.read_csv(filename)
    #        .merge(residence_info[['residence', 'elevation']], on='residence', how='left')
            .sort_values(['year_of_birth', 'type', 'sex'])
            .reset_index(drop=True))

russian_to_target = {True: 'russian',
                     False: 'number of lang'}

def ci(series, beta=0.95):
    """
    Finds an interval that takes proprotion of beta of the distribution in series
    """
    alpha = 1 - beta
    return (series.quantile(alpha / 2), series.quantile(1 - alpha / 2))

def confint_df(delta_df, beta=0.95):
    """
    This function is used to construct confidence band for null distribution
    For each year_of_birth it finds corresponding confidence interval
    Adds columns low, mean and high.
    """
    return (
        (
            delta_df.groupby("year_of_birth").agg(
                dict(
                    delta=(
                        ("low", lambda x: x.quantile((1 - beta) / 2)),
                        "mean",
                        ("high", lambda x: x.quantile(1 - (1 - beta) / 2)),
                    )
                )
            )
        )
        .droplevel(axis=1, level=0)
        .reset_index()
    )
