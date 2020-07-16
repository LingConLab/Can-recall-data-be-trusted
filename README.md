# Can recall data be trusted?
## Online supplement for paper
Authors:

- Michael Daniel
- Alexey Koshevoy
- Ilya Schurov
- Nina Dobrushina

The article was prepared within the framework of the HSE University Basic Research Program
and funded by the Russian Academic Excellence Project ’5-100’.

## Description
The initial data are stored in folder [data](https://github.com/LingConLab/Can-recall-data-be-trusted/tree/master/data). It is processed as follows:

- [mkresidence.ipynb](https://github.com/LingConLab/Can-recall-data-be-trusted/blob/master/mkresidence.ipynb)
    creates file that contains information about each residence. You just need to run it once.

- [tuning-final.ipynb](https://github.com/LingConLab/Can-recall-data-be-trusted/blob/master/tuning-final.ipynb)
    contains all code for model selection and tuning. Here we try
    different ML models (gradient boosting, random forest, logistic and linear
    regression) and pick the best one with cross validation. We also find best
    hyperparameters that are used later.
- [do-simulations.ipynb](https://github.com/LingConLab/Can-recall-data-be-trusted/blob/master/do-simulations.ipynb) contains calculations of *imputed true difference* and corresponding distributions.
- [make-pics.ipynb](https://github.com/LingConLab/Can-recall-data-be-trusted/blob/master/make-pics.ipynb)
    contains the final results: pictures, confidence intervals and p-values.

Some auxiliary functions that are used by different ipynb files are moved to
[indirect-utils.py](https://github.com/LingConLab/Can-recall-data-be-trusted/blob/master/indirect_utils.py).

All the packages needed to reproduce our work are presented in
[requirements.txt](https://github.com/LingConLab/Can-recall-data-be-trusted/blob/master/requirements.txt).
To guarantee reproducibility you have to install the particular versions of these
packages (`pip install -r requirements.txt`). To avoid conflict we recommend using
[virtualenv](https://virtualenv.pypa.io/en/latest/) or other Python environment managers.

Note that currently submitted paper contains numerically different results due to usage of slighly different hyperparameters. All the qualitative conclusions are the same, and we will update the paper to match current reproducible results in the final version.
