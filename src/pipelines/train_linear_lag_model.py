import mlflow
import pandas as pd
from dagster import AssetExecutionContext, asset
from sklearn.linear_model import LinearRegression
from sklearn.metrics import root_mean_squared_error
from sklearn.model_selection import train_test_split


@asset
def raw_data() -> pd.DataFrame:
    # TODO: parameter
    data_url = "https://www.ncei.noaa.gov/data/daily-summaries/access/SP000008181.csv"
    df = pd.read_csv(data_url, low_memory=False)

    retuired_columns = ["DATE", "NAME", "PRCP"]
    if not set(retuired_columns).issubset(list(df.columns)):
        raise ValueError(f"Unexpected source dataframe structure: {list(df.columns)}.")

    df = df[["NAME", "DATE", "PRCP"]]
    df["DATE"] = pd.to_datetime(df["DATE"])

    return df


@asset
def clean_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """
    This step is very specific to Barcelona airport station data.
    """
    df = raw_data
    # There is big gap in data in 1939-1938 year
    df = df[(df["DATE"] > "1939-01-01")].copy()
    df.dropna(inplace=True)

    return df


@asset
def feature_rich_data(clean_data: pd.DataFrame) -> pd.DataFrame:
    df = clean_data
    df["lag_1"] = df["PRCP"].shift(1)
    df["lag_7"] = df["PRCP"].shift(7)
    df["lag_30"] = df["PRCP"].shift(30)
    df["lag_365"] = df["PRCP"].shift(365)
    df["rolling_mean_7"] = df["PRCP"].rolling(window=7).mean()
    df["rolling_std_7"] = df["PRCP"].rolling(window=7).std()
    df["rolling_mean_30"] = df["PRCP"].rolling(window=30).mean()
    df["rolling_std_30"] = df["PRCP"].rolling(window=30).std()

    # drop rows with na in lags
    df.dropna(inplace=True)

    return df


@asset
def ml_model(context: AssetExecutionContext, feature_rich_data: pd.DataFrame) -> None:
    # TODO: parameter
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    features = ["lag_365"]

    df = feature_rich_data

    X = df[features]
    y = df["PRCP"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=False
    )

    mlflow.set_experiment("weather-prediction-exp")
    with mlflow.start_run():
        data_tags = {"location_names": list(df.NAME.unique())}
        mlflow.set_tags(data_tags)

        model = LinearRegression()
        mlflow.log_params({"features": features})

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        rmse = root_mean_squared_error(y_test, y_pred)
        mlflow.log_metric("RMSE", rmse)
        mlflow.sklearn.log_model(model, artifact_path="models")

        context.log.info(f"RMSE: {rmse}")
