# nacc statistics project - phase 1

this project looks at cdr cognitive severity and entorhinal brain measurements in the supplied nacc uds and mri files. it is a descriptive course project using 1,237 matched participants.

## how to run it

1. install python 3.10 or newer and the packages in `requirements.txt`.
2. extract the original `alzheimer(1).zip` on your own computer.
3. put `udslong_imputed.csv` and `mriscanclean.csv` and `combined_adjacency_matrix.csv` in `data/raw/`.
4. run the commands below from the project root.

```bash
pip install -r requirements.txt
python src/phase1_analysis.py
python src/build_report.py
python checks/verify_results.py
```

the first script checks the source files and creates the tables and figures. the second builds `reports/phase1.pdf` from those results. the last command checks important counts and confirms the expected output files exist.

if the original csv files are kept elsewhere run `python src/phase1_analysis.py --data-dir /path/to/files`.

## what is in the folder

| path | purpose |
|---|---|
| `PROJECT_CARD.md` | the question and the decisions made in phase 1 |
| `src/phase1_analysis.py` | input checks and descriptive analysis |
| `src/build_report.py` | rebuilds the pdf report |
| `notebooks/` | a short walkthrough of the same work |
| `outputs/tables/` | aggregate numerical tables and data checks |
| `outputs/summary.json` | aggregate results and original input hashes |
| `figures/` | nine statistical figures |
| `reports/phase1.pdf` | the phase 1 report |
| `data/README.md` | where the data came from and what is missing |
| `checks/verify_results.py` | basic reproducibility checks |

## main decisions

i used `NACCID` to match the files and checked that each participant occurs once in each supplied table. i kept only one copy of the diagnosis variable because the values agree. i did not merge the adjacency matrix with the participant records because it is a graph of brain regions.

i used cdr sum of boxes as the main outcome. the orignal imputation procedure for moca is not available and several totals look processed. an education code of 99 is unknown. a nonpositive gray volume is treated as missing when the bilateral volume is calculated. positive mri outliers remain in the descriptive statistics because they are not proven errors.

the cdr distribution has many zeros. the report therefore shows its median and quartiles as well as its mean. it describes group differences but does not claim that those differences are statistically significant. hypothesis testing and regression belong to later phases.

## limitations

the files do not include the original visits or mri acquisition dates. they also do not contain participants from the parent uds cohort who lack mri. these missing source details limit the visit and selection analyses required by path c. there are no raw missingness records or scanner quality-control details either.

these are limits of the supplied data. they are listed in the report instead of being replaced with estimates that cannot be checked.

## submission and data handling

the package excludes the original participant-level csv files and their ids. keep them locally in `data/raw/` and do not upload raw records to a public repository without permission. the pdf and aggregate tables can be regenerated from the files as instructed above.

the course requires a github repository with the `phase-1` tag and a separate submission to cw. no remote upload or tag has been created here. this is an individual course project so read through the methods and make sure you can explain the calculations and decisions.

## source information

- nacc researcher's guide: https://www.naccdata.org/the-nacc-researchers-guide/
- nacc data request guide: https://www.naccdata.org/requesting-data/data-request-process/
- nacc data file faq: https://www.naccdata.org/data-file-faq
- nacc scan mri dictionary: https://files.alz.washington.edu/documentation/SCAN-MRI-Imaging-RDD.pdf
- nacc uds derived variable guide: https://files.alz.washington.edu/documentation/uds2-dervar.pdf
- university course instructions: supplied `project.pdf`
