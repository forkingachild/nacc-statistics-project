# project card - path c

**study:** cognitive severity and entorhinal mri measurements in the supplied nacc cohort  
**phase:** 1 of 5  
**design:** observational and descriptive using one supplied record per participant

## 1. data

i am using the prepared `alzheimer(1).zip` files. `udslong_imputed.csv` has 1,237 rows and 180 columns. `mriscanclean.csv` has 1,237 rows and 126 columns. the third file `combined_adjacency_matrix.csv` describes 62 brain regions and is not a participant table.

this is an already-matched subset of nacc uds and mri data. it is not the full nacc database. its original extraction date and visit-selection method are not in the zip. the population i can describe is the 1,237 supplied participants rather than all people with cognitive impairment.

## 2. research question

how are bilateral entorhinal gray-matter volume and average cortical thickness related to clinical cognitive severity measured with cdr sum of boxes among the matched nacc participants?

in later phases i will also compare what uds and mri explain separately with what they explain together. the models will use the same participant-level sample so their results are comparable.

## 3. variables

| role | file and variable | measurement and treatment |
|---|---|---|
| outcome | uds `CDRSUM` | numeric score from 0 to 18. higher scores indicate greater severity |
| mri measure | `LH_ENTORHINAL_GVOL` and `RH_ENTORHINAL_GVOL` | sum of left and right gray volume in mm³. nonpositive measurements are treated as missing |
| mri measure | `LH_ENTORHINAL_AVGTH` and `RH_ENTORHINAL_AVGTH` | equal-weight mean of left and right thickness in mm |
| clinical group | uds `NACCUDSD` | categorical codes 1 normal cognition 2 impaired not mci 3 mci and 4 dementia |
| possible adjustment | uds `NACCAGE` | numeric age in years |
| possible adjustment | uds `SEX` | binary recorded sex code 1 male and 2 female |
| possible adjustment | uds `EDUC` | years of education with 99 marked unknown |
| secondary quality check | uds `MOCATOTS` | usually an integer score from 0 to 30. this prepared file has unexpected values so it is not our main outcome |

i chose cdrsum rather than moca as the main score because cdrsum matches its component scores in all supplied rows while the moca totals show signs of earlier processing. bilateral volume is a sum because volume is additive. bilateral thickness is an average because the two sides measure the same quantity in millimeters. the thickness average is not weighted by region size.

## 4. observation unit and sampling

both supplied main files have 1,237 distinct `NACCID` values with no repeats. the sets of identifiers match exactly. i merge on that id instead of assuming the rows are in the same order.

i use one supplied row per participant. this avoids treating the same person as several independent observations within these files. however the original uds can have repeated visits. we have no visit number or scan date here so we cannot determine which assessment was chosen or how close it was to imaging.

nacc draws on assessments at alzheimer's disease research centers. the prepared records are observational and are not a random sample of the general population. i will not interpret sample percentages as national prevalence or make causal claims.

## 5. question type and initial expectation

this is a descriptive and associational question with a group-comparison component. my initial expectation is that lower entorhinal volume or thickness may accompany higher cdr scores. the data could show otherwise and that result would still be worth reporting. statistical tests are planned for phase 3 and regression for phase 4.

## 6. phase 1 results

- normal cognition: 847 participants
- impaired but not mci: 7 participants
- mci: 252 participants
- dementia: 131 participants
- cdr sum of boxes: mean 0.82 and median 0.00. there are 757 zero scores or 61.2% of the sample
- bilateral entorhinal volume: 1,236 usable observations after excluding one invalid zero left volume. mean 3,081.88 mm³ and median 3,073.5 mm³
- bilateral mean entorhinal thickness: 1,237 usable observations. mean 3.01 mm and median 3.06 mm

the zero left volume was not replaced with another measurement. i excluded that bilateral sum because treating an invalid zero as real volume would make it artificially small. i kept positive outliers pending mri quality-control information.

## 7. limitations

the main limitation is that both csv files already contain only people with matched imaging. there is no uds-only comparison group so we cannot measure how the selection of mri participants changed the sample. the original visit dates and scan dates are missing too. this prevents verification of temporal matching and previous repeated visits.

the source imputation method is also unknown. some moca totals are fractional and the bmi column includes special values. scanner details and intracranial volume are unavailable. the group coded as impaired but not mci has only seven participants so its averages should be treated cautiously.

these gaps are reported openly in the phase 1 pdf. they cannot be fixed by statistical calculation on the supplied files alone.

## 8. later phases

- phase 2 will describe conditional probabilities and the joint distribution of selected clinical and mri events
- phase 3 will estimate uncertainty and compare groups with suitable tests and bootstrap methods
- phase 4 will compare uds-only and mri-only linear models with a combined model. it will check the heavily zero-concentrated cdr score and possible collinearity. the cdr components will not be used to predict their own sum
- phase 5 will review how sample selection and unusual measurements affect the findings. any visit-selection sensitivity will require original visit records

## 9. reproduction

place the original three csv files locally in `data/raw/` and run `python src/phase1_analysis.py` followed by `python src/build_report.py`. participant-level data are not included in this submission. see `data/README.md` for source details.
