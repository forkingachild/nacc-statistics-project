# the data files

the source is the supplied `alzheimer(1).zip`. it contains a prepared nacc subset. the zip timestamps are not clinical visit dates and do not establish when the original nacc data were collected.

| file | observed shape | what it contains |
|---|---|---|
| `udslong_imputed.csv` | 1,237 x 180 | clinical uds variables including cognitive scores and diagnosis |
| `mriscanclean.csv` | 1,237 x 126 | structural mri volume and thickness plus the participant id |
| `combined_adjacency_matrix.csv` | 62 x 63 in the csv | a 62 x 62 brain-region adjacency matrix with a label column |

put these files in `data/raw/` on your computer. the scripts use them to reproduce the tables and report. the original zip is not part of the submission.

## what is missing

the prepared subset has one row per participant but no original visit number or assessment date. there are no mri scan dates. so we cannot tell which uds visit was selected or how much time passed between assessment and scan. we also have no wider uds group without imaging. that prevents the scanned-versus-unscanned comparison requested for path c.

the file called `udslong_imputed.csv` suggests earlier processing. we do not have its original missing-value map or imputation script. the mri preparation method and scanner qc flags are missing as well. these gaps are discussed in the report and project card.

## reproducibility and privacy

the analysis records sha256 hashes of the three source csvs in `outputs/summary.json`. it exports descriptive tables and figures but not participant identifiers. the `.gitignore` file keeps `data/raw/` and identifiable source files out of a normal git commit. check the original nacc data-use terms before sharing any data.
