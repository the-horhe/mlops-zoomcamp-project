# """
# Unit test for pipeline steeps.
# """

# mypy: disable-error-code="attr-defined"

import pandas.api.types as ptypes
import pytest
from pytest import fixture

from src.pipelines.train_linear_lag_model import (
    DriftDetectedError,
    PipelineConfig,
    clean_data,
    feature_rich_data,
    input_quality_report,
    raw_data,
)


@fixture
def pipeline_config() -> PipelineConfig:
    return PipelineConfig(
        data_path="tests/data/data_sample.csv",
    )


def test_raw_data(pipeline_config: PipelineConfig) -> None:
    data = raw_data(pipeline_config)

    assert data.shape == (3, 3)  # 3 rows, 3 cols
    assert ptypes.is_datetime64_any_dtype(data.DATE)


def test_clean_data(pipeline_config: PipelineConfig) -> None:
    raw = raw_data(pipeline_config)
    clean = clean_data(raw)

    assert clean.shape == (1, 3)  # rows under 1939 removed


def test_input_quality_report(pipeline_config: PipelineConfig) -> None:
    raw = raw_data(pipeline_config)
    clean = clean_data(raw)

    # No drift - no exception
    input_quality_report(raw, clean)

    # Add significant drift and expect exception
    clean.PRCP.iloc[0] = 1000000
    with pytest.raises(DriftDetectedError):
        input_quality_report(raw, clean)


def test_feature_rich_data(pipeline_config: PipelineConfig) -> None:
    raw = raw_data(pipeline_config)
    rich = feature_rich_data(raw)

    assert rich.shape == (0, 11)  # All rows will be dropped due to NA
