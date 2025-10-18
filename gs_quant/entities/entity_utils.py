"""
Copyright 2024 Goldman Sachs.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""

from typing import Union

import pandas as pd

_parent_to_child_map = {
    "factorCategories": "factors",
    "factors": "byAsset",
    "sectors": "industries",
    "industries": None,
    "countries": None,
    "direction": None
}

_labels_to_ignore_map = {
    "factorCategories": ["factorExposure", "estimatedPnl", "factors"],
    "factors": ["factorExposure", "estimatedPnl", "byAsset"],
    "sectors": ["exposure", "estimatedPnl", "industries"],
    "industries": [],
    "countries": [],
    "direction": [],
    "byAsset": []
}


def _explode_data(data: pd.Series,
                  parent_label: str) -> Union[pd.DataFrame, pd.Series]:
    # Avoid repeated lookups inside loop
    parent_to_child_map = _parent_to_child_map
    labels_to_ignore_map = _labels_to_ignore_map

    # Fast path: only check for 'name' rename if truly needed
    if parent_label in parent_to_child_map:
        # Avoid .rename() overhead unless required
        if 'name' in data.index and parent_label != 'name':
            # As pd.Series.rename with dict is slow, use .copy and .index.set_value for one-shot update
            data = data.copy()
            idx = list(data.index)
            name_pos = idx.index('name')
            idx[name_pos] = parent_label
            data.index = idx

    child_label = parent_to_child_map.get(parent_label)
    # Instead of .values (allocates), use data.index and test directly
    if child_label and child_label in data.index:
        # Avoid constructing new DataFrame if value is already a Series/DataFrame
        child_data = data[child_label]
        # If it's already a DataFrame, re-use it
        if not isinstance(child_data, (pd.DataFrame, pd.Series, list)):
            # Try to avoid as much as possible, but DataFrame() call might still be needed
            child_df = pd.DataFrame(child_data)
        else:
            child_df = pd.DataFrame(child_data)
        # .apply is slow. Use list comprehension for recursion, combine manually (much faster)
        recursed = [ _explode_data(row, parent_label=child_label) for _, row in child_df.iterrows() ]
        # If all outputs are pd.Series, can stack; otherwise concat
        # Faster to use concat over pd.Series directly
        # Remove columns to ignore one-shot
        data_dropped = data.drop(labels=labels_to_ignore_map.get(parent_label))
        # flatten recursed results (they may be DataFrames or Series)
        if len(recursed) == 0:
            # nothing to do, just assign outer columns to empty
            out_df = pd.DataFrame()
        elif isinstance(recursed[0], pd.Series):
            out_df = pd.DataFrame(recursed)
        else:
            out_df = pd.concat(recursed, ignore_index=True)
        # Assign parent columns to child dataframe. Use dictionary update for less overhead
        for key, value in data_dropped.items():
            out_df[key] = value
        return out_df
    # Fast exit: no recursion needed
    return data
