from dagster import (
    AssetSelection,
    Definitions,
    define_asset_job,
    load_assets_from_modules,
)

from src.pipelines import train_linear_lag_model

all_assets = load_assets_from_modules([train_linear_lag_model])

# Addition: define a job that will materialize the assets
train_linear_model_job = define_asset_job("train_linear_model", selection=AssetSelection.all())

defs = Definitions(
    assets=all_assets,
    jobs=[train_linear_model_job],  # Addition: add the job to Definitions object (see below)
)
