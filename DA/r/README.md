# R

Quarto/R Markdown (`.qmd`/`.Rmd`) for same analytical tasks as Python.
Rendered HTML goes to `reports/`.

## Load engagement into warehouse

From project root in R:

```r
source("r/load_engagement_to_warehouse.R")
```

Or: `Rscript r/load_engagement_to_warehouse.R`

Requires: `DBI`, `RSQLite`, `jsonlite`. Same inputs/outputs as the Python script.
