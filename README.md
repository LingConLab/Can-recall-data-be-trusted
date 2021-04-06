# Can recall data be trusted?
## Online supplement for paper
Authors:

- Michael Daniel
- Alexey Koshevoy
- Ilya Schurov
- Nina Dobrushina

The article was prepared within the framework of the HSE University Basic Research Program.

## Main supplement

[Here](https://lingconlab.github.io/Can-recall-data-be-trusted/) you can find the main supplement to the paper. It contains the following parts:

- Additional visualisations of the dataset
- Details of model tuning and selection process
- Alternative analysis of our data using propensity score matching

## Reproduction

You can also find all the code that is needed to reproduce results of the paper.

The initial data are stored in folder [data](https://github.com/LingConLab/Can-recall-data-be-trusted/tree/master/data). It is processed as follows:
    
- [preprocessing.py](https://github.com/LingConLab/Can-recall-data-be-trusted/blob/master/preprocessing.py) performs different changes on the data downloaded using the parser. It returns two datasets used in the further analysis.

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
- [plots.R](https://github.com/LingConLab/Can-recall-data-be-trusted/blob/master/plots.R) 
    draws the versions of the plots used in the paper.
- [propensity-score-matching.Rmd](https://htmlpreview.github.io/?https://github.com/LingConLab/Can-recall-data-be-trusted/blob/master/propensity-score-matching.html)
    uses different technique to test main conclusions of the paper.

Some auxiliary functions that are used by different ipynb files are moved to
[indirect-utils.py](https://github.com/LingConLab/Can-recall-data-be-trusted/blob/master/indirect_utils.py).

All the packages needed to reproduce our work are presented in
[requirements.txt](https://github.com/LingConLab/Can-recall-data-be-trusted/blob/master/requirements.txt). To guarantee reproducibility you have to install the particular versions of these
packages (`pip install -r requirements.txt`). To avoid conflict we recommend using
[virtualenv](https://virtualenv.pypa.io/en/latest/) or other Python environment managers.

