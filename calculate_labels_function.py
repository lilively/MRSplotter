from status import update_status
from numpy import asarray
from scipy.stats import pearsonr


def calculate_labels(dataTable, soucreTable, th, sbar):
    ppm_columns_data = sorted(
        [c for c in dataTable.columns if c.startswith('PPM_')],
        key=lambda x: float(x.split('_')[1])
    )
    ppm_columns_src = sorted(
        [c for c in soucreTable.columns if c.startswith('PPM_')],
        key=lambda x: float(x.split('_')[1])
    )
    update_status(sbar, f"Found {len(ppm_columns_data)} PPM columns in data, "
                        f"{len(ppm_columns_src)} in sources")

    min_len = min(len(ppm_columns_data), len(ppm_columns_src))
    ppm_columns_data = ppm_columns_data[:min_len]
    ppm_columns_src = ppm_columns_src[:min_len]

    sources = {}
    for _, srow in soucreTable.iterrows():
        sname = str(srow['ID'])
        sources[sname] = asarray(srow[ppm_columns_src].values, dtype=float)

    # Insert new columns BEFORE the PPM block so they appear next to metadata.
    new_cols = [f'Corr_{sname}' for sname in sources] + ['winning corr']
    first_ppm_idx = next(
        (i for i, c in enumerate(dataTable.columns) if str(c).startswith('PPM_')),
        len(dataTable.columns)
    )
    for offset, col in enumerate(new_cols):
        if col in dataTable.columns:
            dataTable.drop(columns=[col], inplace=True)
        dataTable.insert(first_ppm_idx + offset, col, 0.0)

    replaced = 0
    for idx, row in dataTable.iterrows():
        voxel = asarray(row[ppm_columns_data].values, dtype=float)

        correlations = {}
        for sname, s in sources.items():
            r = pearsonr(voxel, s)[0]
            correlations[sname] = r
            dataTable.at[idx, f'Corr_{sname}'] = round(float(r), 4)

        winner = max(correlations, key=correlations.get)
        winner_corr = correlations[winner]
        dataTable.at[idx, 'winning corr'] = round(float(winner_corr), 4)

        if winner_corr >= th:
            dataTable.at[idx, 'TissueType'] = str(winner)
            replaced += 1

    if 'TissueType' in dataTable.columns:
        dataTable['TissueType'] = dataTable['TissueType'].astype(str)

    update_status(sbar, f"Relabeled {replaced}/{len(dataTable)} voxels "
                        f"(threshold={th})")
    return dataTable
