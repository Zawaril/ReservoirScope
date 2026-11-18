import numpy as np
import pandas as pd

from river import linear_model
from river import preprocessing


def train_forecast_model(
    series,
    history_weeks=260,
    lags=8,
    exogenous_data=None,
    use_temperature=False,
    use_precipitation=False,
    use_eur=False,
    use_usd=False
):
    """
    Train a River linear regression forecasting model
    using lag features, annual seasonality, and optional
    exogenous variables.
    """

    series = (
        series
        .dropna()
        .sort_index()
        .tail(history_weeks)
    )

    data = pd.DataFrame(
        {
            "fill_level": series
        }
    )

    # Lag features
    for lag in range(
        1,
        lags + 1
    ):

        data[
            f"lag_{lag}"
        ] = (
            data[
                "fill_level"
            ]
            .shift(lag)
        )


    
    # Join optional historical exogenous data
    if exogenous_data is not None:

        exogenous_data = (
            exogenous_data
            .copy()
            .sort_index()
        )


        if (
            use_temperature
            and "temperature_mean"
            in exogenous_data.columns
        ):

            data[
                "temperature_mean"
            ] = exogenous_data[
                "temperature_mean"
            ]


        if (
            use_precipitation
            and "precipitation_sum"
            in exogenous_data.columns
        ):

            data[
                "precipitation_sum"
            ] = exogenous_data[
                "precipitation_sum"
            ]


        if (
            use_eur
            and "eur_nok"
            in exogenous_data.columns
        ):

            data[
                "eur_nok"
            ] = exogenous_data[
                "eur_nok"
            ]


        if (
            use_usd
            and "usd_nok"
            in exogenous_data.columns
        ):

            data[
                "usd_nok"
            ] = exogenous_data[
                "usd_nok"
            ]


    data = (
        data
        .dropna()
    )


    model = (
        preprocessing.StandardScaler()
        | linear_model.LinearRegression()
    )


    
    # Train River model
    for timestamp, row in data.iterrows():

        x = {
            f"lag_{lag}":
                row[
                    f"lag_{lag}"
                ]
            for lag in range(
                1,
                lags + 1
            )
        }


        # Annual seasonality
        week = (
            timestamp
            .isocalendar()
            .week
        )


        x[
            "week_sin"
        ] = np.sin(
            2 * np.pi * week / 52
        )

        x[
            "week_cos"
        ] = np.cos(
            2 * np.pi * week / 52
        )


        # Optional exogenous variables
        if (
            use_temperature
            and "temperature_mean"
            in row.index
        ):

            x[
                "temperature_mean"
            ] = row[
                "temperature_mean"
            ]


        if (
            use_precipitation
            and "precipitation_sum"
            in row.index
        ):

            x[
                "precipitation_sum"
            ] = row[
                "precipitation_sum"
            ]


        if (
            use_eur
            and "eur_nok"
            in row.index
        ):

            x[
                "eur_nok"
            ] = row[
                "eur_nok"
            ]


        if (
            use_usd
            and "usd_nok"
            in row.index
        ):

            x[
                "usd_nok"
            ] = row[
                "usd_nok"
            ]


        model.learn_one(
            x,
            row[
                "fill_level"
            ]
        )


    return (
        model,
        series
    )


def forecast_future(
    model,
    history,
    lags=8,
    horizon=12,
    future_temperature=None,
    future_precipitation=None,
    future_eur=None,
    future_usd=None
):
    """
    Generate a recursive future reservoir forecast.
    """

    history = (
        history
        .dropna()
        .sort_index()
    )


    history_values = list(
        history.values
    )


    future_dates = pd.date_range(
        start=(
            history.index.max()
            + pd.Timedelta(
                weeks=1
            )
        ),
        periods=horizon,
        freq="W-SUN"
    )


    predictions = []


    for future_date in future_dates:

        x = {
            f"lag_{lag}":
                history_values[
                    -lag
                ]
            for lag in range(
                1,
                lags + 1
            )
        }


        # Annual seasonality
        week = (
            future_date
            .isocalendar()
            .week
        )


        x[
            "week_sin"
        ] = np.sin(
            2 * np.pi * week / 52
        )

        x[
            "week_cos"
        ] = np.cos(
            2 * np.pi * week / 52
        )


        # Future exogenous assumptions
        if future_temperature is not None:

            x[
                "temperature_mean"
            ] = float(
                future_temperature
            )


        if future_precipitation is not None:

            x[
                "precipitation_sum"
            ] = float(
                future_precipitation
            )


        if future_eur is not None:

            x[
                "eur_nok"
            ] = float(
                future_eur
            )


        if future_usd is not None:

            x[
                "usd_nok"
            ] = float(
                future_usd
            )


        prediction = (
            model.predict_one(
                x
            )
        )


        prediction = max(
            0,
            min(
                1,
                prediction
            )
        )


        predictions.append(
            prediction
        )


        history_values.append(
            prediction
        )


    return pd.Series(
        predictions,
        index=future_dates,
        name="forecast"
    )


def train_final_seasonal_model(
    series,
    history_weeks=260,
    lags=8
):
    """
    Backwards-compatible default model.
    """

    return train_forecast_model(
        series=series,
        history_weeks=history_weeks,
        lags=lags
    )