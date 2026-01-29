import pandas as pd
import numpy as np
from typing import Any, Dict, List, Union

def sanitize_data(data: Any) -> Any:
    """
    Recursively replace NaN/inf with None for JSON compliance.
    """
    if isinstance(data, dict):
        return {k: sanitize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_data(v) for v in data]
    elif isinstance(data, (float, np.float64, np.float32)):
        if pd.isna(data) or np.isinf(data):
            return None
        return float(data)
    elif isinstance(data, (int, np.int64, np.int32)):
        return int(data)
    return data
