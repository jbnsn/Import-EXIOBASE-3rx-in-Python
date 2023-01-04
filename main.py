"""
Import the Exiobase database from a *.mat-file.

EXIOBASE 3rx

- 214 Regions
- 200 Categories/Products
- 12 Value added categories
- 7 Final demand categories (7*214 = 1498)

- Basic pricing
- Monetary unit: Million Euros (current prices)



| Value                 | Size            | Field | Description              |
|-----------------------|-----------------|-------|--------------------------|
| sparse.csc.csc_matrix | (452, 42800)    | S     | Stressor matrix          |
|                       |                 |       | per monetary unit        |
|-----------------------|-----------------|-------|--------------------------|
| sparse.csc.csc_matrix | (42800, 42800)  | A     | The coefficient matrix   |
|                       |                 |       | (inputs required         |
|                       |                 |       | per unit of output)      |
|-----------------------|-----------------|-------|--------------------------|
| sparse.csc.csc_matrix | (12, 42800)     | V     | Value added matrix       |
|-----------------------|-----------------|-------|--------------------------|
| sparse.csc.csc_matrix | (42800, 1498)   | Y     | Final demand matrix      |
|-----------------------|-----------------|-------|--------------------------|
| sparse.csc.csc_matrix | (42800, 1)      | x     | Vector of total output   |
|-----------------------|-----------------|-------|--------------------------|
| Array of float64      | (200, 214, 214) | TC    | Trade cube               |
|                       |                 |       | (product x exporter      |
|                       |                 |       | x importer)              |
|-----------------------|-----------------|-------|--------------------------|
| sparse.csc.csc_matrix | (452, 42800)    | F     | Total stressor matrix    |
|-----------------------|-----------------|-------|--------------------------|
| sparse.csc.csc_matrix | (452, 1498)     | F_hh  | Total household          |
|                       |                 |       | stressor matrix          |
|-----------------------|-----------------|-------|--------------------------|
| Array of void256      | (1,)            | pop   | Population per country   |
|-----------------------|-----------------|-------|--------------------------|
| Array of void256      | (1,)            | gdp   | GDP per country          |
|-----------------------|-----------------|-------|--------------------------|
| sparse.csc.csc_matrix | (12, 1498)      | VY    | Value added final demand |
|-----------------------|-----------------|-------|--------------------------|

"""

import pandas as pd
import scipy.io

# %% Import labels
exio_labs_f = pd.read_csv('./data/exiobase-3rx/labs/f.csv')  # 421
exio_labs_v = pd.read_csv('./data/exiobase-3rx/labs/v.csv')  # 7*214 = 1498
exio_labs_y = pd.read_csv('./data/exiobase-3rx/labs/y.csv')  # 7*214 = 1498
exio_labs_z = pd.read_csv('./data/exiobase-3rx/labs/z.csv')  # 200*214 = 42800

# %% Import matrices

exiobase = scipy.io.loadmat(
    './data/exiobase-3rx/EXIOBASE_3rx_aggLandUseExtensions_2010_pxp.mat'
    )

exio_db_sparse = {}

exio_db_sparse['header'] = exiobase['__header__']
exio_db_sparse['version'] = exiobase['__version__']

for key, item in zip(
        ['S', 'A', 'V', 'Y', 'x', 'TC', 'F', 'F_hh', 'pop', 'gdp', 'VY'],
        exiobase['IO'].item()
        ):

    exio_db_sparse[key] = item

del key, item
del exiobase

# %% To dense

exio_db_dense = {}

exio_db_dense['header'] = exio_db_sparse['header']
exio_db_dense['version'] = exio_db_sparse['version']

exio_db_dense['regions'] = exio_labs_z['Exiobase - Region'].unique()
exio_db_dense['categories'] = exio_labs_z['Exiobase - Category'].unique()

# %%% A - The coefficient matrix (inputs required per unit of outputs)

exio_db_dense['A'] = pd.DataFrame(
    exio_db_sparse['A'].todense(),
    index=pd.MultiIndex.from_frame(exio_labs_z),
    columns=pd.MultiIndex.from_frame(exio_labs_z)
    )

# %%% F - Total stressor matrix (452, 42800)

exio_db_dense['F'] = pd.DataFrame(
    exio_db_sparse['F'].todense(),
    index=pd.MultiIndex.from_frame(exio_labs_f),
    columns=pd.MultiIndex.from_frame(exio_labs_z)
    )

# %%% F_hh - Total household stressor matrix (452, 1498)

exio_db_dense['F_hh'] = pd.DataFrame(
    exio_db_sparse['F_hh'].todense(),
    index=pd.MultiIndex.from_frame(exio_labs_f),
    columns=pd.MultiIndex.from_frame(exio_labs_y)
    )

# %%% S - Stressor matrix per monetary unit (452, 42800)

exio_db_dense['S'] = pd.DataFrame(
    exio_db_sparse['S'].todense(),
    index=pd.MultiIndex.from_frame(exio_labs_f),
    columns=pd.MultiIndex.from_frame(exio_labs_z)
    )

# %%% V - Value added matrix (12, 42800)

exio_db_dense['V'] = pd.DataFrame(
    exio_db_sparse['V'].todense(),
    index=pd.MultiIndex.from_frame(exio_labs_v),
    columns=pd.MultiIndex.from_frame(exio_labs_z)
    )

# %%% VY - Value added final demand (12, 1498)

exio_db_dense['VY'] = pd.DataFrame(
    exio_db_sparse['VY'].todense(),
    index=pd.MultiIndex.from_frame(exio_labs_v),
    columns=pd.MultiIndex.from_frame(exio_labs_y)
    )

# %%% x - Vector of total output (42800, 1)

exio_db_dense['x'] = pd.DataFrame(
    exio_db_sparse['x'].todense(),
    index=pd.MultiIndex.from_frame(exio_labs_z),
    columns=['Exiobase - Total output']
    )

# %%% Y Final demand matrix (42800, 1498)

exio_db_dense['Y'] = pd.DataFrame(
    exio_db_sparse['Y'].todense(),
    index=pd.MultiIndex.from_frame(exio_labs_z),
    columns=pd.MultiIndex.from_frame(exio_labs_y)
    )
