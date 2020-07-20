import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from indirect_utils import get_delta, identity, tologodds, confint_df

@st.cache
def read_everything(target, postfix):
    target = target.lower()
    assert target in ("russian", "itm")

    if target == "russian":
        data = pd.read_csv("data/russian.csv")
        delta_perm = pd.read_csv(f"delta_russian_perm_gbr_{postfix}.csv")
        delta_bootstrap = pd.read_csv(f"delta_russian_bootstrap_gbr_{postfix}.csv")
        pred_full = pd.read_csv(f"pred_russian_full_gbr_{postfix}.csv")
        delta_full = get_delta(pred_full, use_logodds=True)
    else:
        data = pd.read_csv("data/ITM.csv")
        delta_perm = pd.read_csv(f"delta_itm_perm_gbr_{postfix}.csv")
        delta_bootstrap = pd.read_csv(f"delta_itm_bootstrap_gbr_{postfix}.csv")
        pred_full = pd.read_csv(f"pred_itm_full_gbr_{postfix}.csv")
        delta_full = get_delta(pred_full, use_logodds=False)

    return (data, delta_perm, delta_bootstrap, pred_full, delta_full)


st.title("Predictions explorer")

features_cat = ["sex", "mother tongue"]
features_real = ["village population", "elevation"]

target = st.sidebar.selectbox("target variable", ["Russian", "ITM"])
(data, delta_perm, delta_bootstrap, pred_full, delta_full) = read_everything(
    target, "no_residence"
)


def filter_df(df, selection):

    cat_mask = [
        df[feature] == sel
        for feature in features_cat
        if (sel := selection.get(feature)) is not None and sel != "all"
    ]

    real_mask = [
        (sel[0] <= df[feature]) & (df[feature] <= sel[1])
        for feature in features_real
        if (sel := selection.get(feature)) is not None
    ]
    masks = cat_mask + real_mask
    if not masks:
        return df

    mask = pd.concat(cat_mask + real_mask, axis=1).all(axis=1)
    return df[mask]


selection = {}

for feature in features_cat:
    selection[feature] = st.sidebar.selectbox(
        feature, ["all"] + list(pred_full[feature].unique())
    )

for feature in features_real:

    min_ = float((pred_full)[feature].min())
    max_ = float((pred_full)[feature].max())
    selection[feature] = st.sidebar.slider(feature, min_, max_, (min_, max_))


def typelabel(df, label="type"):
    """
    Helper function for plotting
    """
    return df.assign(
        type=lambda x: x["type"].replace({0: "indirect", 1: "direct"})
    ).rename(columns={"type": label})


def plot_pred_data(data, full, target, ylabel, ylim, ylogodds=False, showlegend=True):
    """
    Plots predictions along with data
    (averaged by all other variable except year_of_birth)
    """
    legend = "brief" if showlegend else False
    fig = plt.figure(figsize=(8, 4))

    def postprocess(df, y, hue):
        df = typelabel(df, hue)
        if ylogodds:
            df = tologodds(df, y)
        return df

    sns.scatterplot(
        x="year_of_birth",
        y="mean",
        size="count",
        hue="collected data",
        ci=None,
        data=(
            data.groupby(["year_of_birth", "type"])[target]
            .agg(("mean", "count"))
            .reset_index()
            .pipe(lambda x: postprocess(x, "mean", "collected data"))
        ),
        legend=legend,
    )

    sns.lineplot(
        x="year_of_birth",
        y="pred",
        hue="model prediction",
        style="model prediction",
        style_order=["direct", "indirect"],
        data=full.pipe(lambda x: postprocess(x, "pred", "model prediction")),
        ci=None,
        legend=legend,
    )

    plt.xlabel("Year of birth")
    plt.ylabel(ylabel)

    if ylim:
        plt.ylim(ylim)

    return fig


def plot_delta(delta_df, delta_full, data, title):
    """
    Plots imputed true difference and confidence band
    """
    ci = confint_df(delta_df)
    minyear = min(delta_full["year_of_birth"])

    fig, (ax1, ax2) = plt.subplots(
        nrows=2, sharex=True, figsize=(10, 6), gridspec_kw=dict(height_ratios=[3, 1])
    )

    ax1.plot(
        ci["year_of_birth"] - minyear, np.zeros_like(ci["year_of_birth"]), color="grey"
    )
    ax1.fill_between(
        ci["year_of_birth"] - minyear, ci["low"], ci["high"], alpha=0.2, color="grey"
    )
    delta_full.groupby("year_of_birth")["delta"].mean().reset_index(drop=True).plot(
        color="red", ax=ax1
    )
    # for i in range(5):
    #     ax1.plot(
    #         ci["year_of_birth"] - minyear,
    #         delta_df[lambda x: x["iter"] == i].groupby("year_of_birth")["delta"].mean(),
    #         color="grey",
    #         alpha=0.5,
    #     )
    ax1.set_ylabel("$indirect - direct$")

    sns.countplot(
        x="year_of_birth_int",
        hue="evidence type",
        data=typelabel(
            data.assign(year_of_birth_int=lambda x: x["year_of_birth"].astype(int)),
            "evidence type",
        ),
        ax=ax2,
    )

    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90)
    ax2.set_ylabel("number of observations")
    ax2.set_xlabel("year of birth")
    ax1.set_title(title)
    return fig


showlegend = st.checkbox("Show legend")

st.write(
    plot_pred_data(
        filter_df(data, selection),
        filter_df(pred_full, selection),
        "русский" if target == "Russian" else "number of lang",
        ylabel=target,
        ylim=(0.3, 1.1) if target == "Russian" else (0, 2.1),
        showlegend=showlegend,
    )
)

st.write(
    plot_delta(
        delta_perm,
        filter_df(delta_full, selection),
        filter_df(data, selection),
        "imputed true difference (Russian, log odds)",
    )
)
