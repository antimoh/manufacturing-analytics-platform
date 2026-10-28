"""
Raw Data Quality Tests
Validates the integrity and quality of the raw dataset.

Tests check:
- Expected row count
- Required columns present
- No missing values
- No duplicate rows
- Binary failure indicators (0 or 1 only)
"""

import json
from pathlib import Path

import pandas as pd
import pytest

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
DATA_FILE = RAW_DATA_DIR / "ai4i2020.csv"
MANIFEST_FILE = RAW_DATA_DIR / "manifest.json"

# Expected dataset properties
EXPECTED_ROW_COUNT = 10000
REQUIRED_COLUMNS = [
    "Type",
    "Air temperature",
    "Process temperature",
    "Rotational speed",
    "Torque",
    "Tool wear",
    "Machine failure",
    "TWF",
    "HDF",
    "PWF",
    "OSF",
    "RNF",
]
BINARY_COLUMNS = ["Machine failure", "TWF", "HDF", "PWF", "OSF", "RNF"]


@pytest.fixture
def raw_data():
    """Load the raw dataset."""
    if not DATA_FILE.exists():
        pytest.skip(f"Data file not found: {DATA_FILE}")
    return pd.read_csv(DATA_FILE)


@pytest.fixture
def manifest():
    """Load the manifest file."""
    if not MANIFEST_FILE.exists():
        pytest.skip(f"Manifest file not found: {MANIFEST_FILE}")
    with open(MANIFEST_FILE) as f:
        return json.load(f)


class TestRowCount:
    """Tests for expected row count."""

    def test_expected_row_count(self, raw_data):
        """Dataset should have exactly 10,000 rows."""
        assert len(raw_data) == EXPECTED_ROW_COUNT, (
            f"Expected {EXPECTED_ROW_COUNT} rows, found {len(raw_data)}"
        )

    def test_manifest_row_count_matches(self, raw_data, manifest):
        """Manifest row count should match actual data."""
        assert manifest["row_count"] == len(raw_data), (
            f"Manifest reports {manifest['row_count']} rows, "
            f"actual data has {len(raw_data)} rows"
        )


class TestRequiredColumns:
    """Tests for required columns."""

    def test_all_required_columns_present(self, raw_data):
        """All required columns should be present."""
        missing = set(REQUIRED_COLUMNS) - set(raw_data.columns)
        assert not missing, f"Missing required columns: {missing}"

    def test_manifest_columns_match(self, raw_data, manifest):
        """Manifest columns should match actual columns."""
        assert set(manifest["columns"]) == set(raw_data.columns), (
            "Manifest columns do not match actual data columns"
        )


class TestMissingValues:
    """Tests for missing values."""

    def test_no_missing_values(self, raw_data):
        """Dataset should have no missing values."""
        missing_count = raw_data.isnull().sum().sum()
        assert missing_count == 0, f"Found {missing_count} missing values"

    def test_manifest_missing_count(self, manifest):
        """Manifest should report zero missing values."""
        assert manifest["missing_value_count"] == 0, (
            f"Manifest reports {manifest['missing_value_count']} missing values"
        )


class TestDuplicates:
    """Tests for duplicate rows."""

    def test_no_exact_duplicates(self, raw_data):
        """Dataset should have no exact duplicate rows."""
        duplicates = raw_data.duplicated().sum()
        assert duplicates == 0, f"Found {duplicates} duplicate rows"


class TestBinaryColumns:
    """Tests for binary indicator columns."""

    @pytest.mark.parametrize("column", BINARY_COLUMNS)
    def test_binary_values_only(self, raw_data, column):
        """Binary columns should contain only 0 and 1."""
        unique_values = set(raw_data[column].unique())
        expected = {0, 1}
        assert unique_values.issubset(expected), (
            f"Column '{column}' contains non-binary values: "
            f"{unique_values - expected}"
        )


class TestFailureConsistency:
    """Tests for failure indicator consistency."""

    def test_deterministic_failure_modes_imply_machine_failure(self, raw_data):
        """
        When deterministic failure modes (TWF, HDF, PWF, OSF) are 1,
        Machine failure should also be 1.
        
        Note: RNF (Random Failure) is excluded because in this dataset,
        RNF=1 indicates random failure potential, not actual failure.
        There are 18 rows where RNF=1 but Machine failure=0, which is
        expected dataset behavior.
        """
        # Deterministic failure modes (excluding RNF)
        deterministic_modes = ["TWF", "HDF", "PWF", "OSF"]
        for mode in deterministic_modes:
            # Find rows where the specific mode is 1 but Machine failure is 0
            inconsistent = raw_data[
                (raw_data[mode] == 1) & (raw_data["Machine failure"] == 0)
            ]
            assert len(inconsistent) == 0, (
                f"Found {len(inconsistent)} rows where {mode}=1 but "
                "Machine failure=0"
            )

    def test_rnf_behavior_documented(self, raw_data):
        """
        Document RNF (Random Failure) behavior in the dataset.
        RNF=1 does not always imply Machine failure=1.
        This test documents and validates the expected count.
        """
        rnf_without_failure = raw_data[
            (raw_data["RNF"] == 1) & (raw_data["Machine failure"] == 0)
        ]
        # Documented: 18 rows have RNF=1 but Machine failure=0
        assert len(rnf_without_failure) == 18, (
            f"Expected 18 rows with RNF=1 and Machine failure=0, "
            f"found {len(rnf_without_failure)}"
        )
