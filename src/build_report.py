
from pathlib import Path
import re
from xml.sax.saxutils import escape
import json
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable

ROOT=Path(__file__).resolve().parents[1]
RPT=ROOT/'reports'/'phase1.pdf'
BASE=Path('/usr/share/fonts/truetype/dejavu')
pdfmetrics.registerFont(TTFont('DejaVu',str(BASE/'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DejaVu-Bold',str(BASE/'DejaVuSans-Bold.ttf')))
pdfmetrics.registerFontFamily('DejaVu',normal='DejaVu',bold='DejaVu-Bold')
BLACK=colors.black
LIGHTGRAY=colors.HexColor('#dddddd')
W=A4[0]-37*mm
styles={
 'cover_tag':ParagraphStyle('cover_tag',fontName='DejaVu',fontSize=9,leading=14,spaceAfter=7,textColor=BLACK),
 'cover':ParagraphStyle('cover',fontName='DejaVu-Bold',fontSize=13,leading=19,spaceAfter=9,textColor=BLACK),
 'subtitle':ParagraphStyle('subtitle',fontName='DejaVu',fontSize=9,leading=14,spaceAfter=9,textColor=BLACK),
 'h1':ParagraphStyle('h1',fontName='DejaVu-Bold',fontSize=10.5,leading=16,spaceBefore=11,spaceAfter=7,textColor=BLACK,keepWithNext=True),
 'h2':ParagraphStyle('h2',fontName='DejaVu-Bold',fontSize=9.6,leading=14,spaceBefore=7,spaceAfter=5,textColor=BLACK,keepWithNext=True),
 'body':ParagraphStyle('body',fontName='DejaVu',fontSize=8.8,leading=14.1,spaceAfter=7,textColor=BLACK),
 'small':ParagraphStyle('small',fontName='DejaVu',fontSize=8.1,leading=12.3,spaceAfter=5,textColor=BLACK),
 'tiny':ParagraphStyle('tiny',fontName='DejaVu',fontSize=7.0,leading=10.5,spaceAfter=4,textColor=BLACK),
 'table_head':ParagraphStyle('table_head',fontName='DejaVu-Bold',fontSize=7.2,leading=11,textColor=BLACK),
 'table':ParagraphStyle('table',fontName='DejaVu',fontSize=7.2,leading=10.9,textColor=BLACK),
 'table_bold':ParagraphStyle('table_bold',fontName='DejaVu',fontSize=7.2,leading=10.9,textColor=BLACK),
 'caption':ParagraphStyle('caption',fontName='DejaVu',fontSize=7.8,leading=11.6,spaceAfter=10,textColor=BLACK),
 'alert':ParagraphStyle('alert',fontName='DejaVu',fontSize=8.8,leading=14,spaceAfter=7,textColor=BLACK),
}

def p(s,style='body'):
    source=str(s)
    display=source.lower()
    for u in re.findall(r'https?://[^\s<)]+',source):
        display=display.replace(u.lower(),'<link href="'+escape(u)+'" color="black">'+u.lower()+'</link>',1)
    return Paragraph(display,styles[style])

def rich_table(head,rows,widths,fs=None):
    h=[p(v,'table_head') for v in head]
    data=[h]+[[p(v,'table_bold' if j==0 else 'table') for j,v in enumerate(row)] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LINEBELOW',(0,0),(-1,0),.6,BLACK),
        ('LINEBELOW',(0,1),(-1,-1),.18,LIGHTGRAY),
        ('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),4),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
    ]))
    return t

def png(name,maxwidth=W, maxheight=83*mm):
    im=Image(str(ROOT/'figures'/name))
    scale=min(maxwidth/im.imageWidth,maxheight/im.imageHeight)
    im.drawWidth=im.imageWidth*scale; im.drawHeight=im.imageHeight*scale
    return im


def running(canvas,doc):
    canvas.saveState()
    canvas.setFont('DejaVu',8)
    canvas.setFillColor(colors.black)
    canvas.drawCentredString(A4[0]/2,13*mm,str(doc.page))
    canvas.restoreState()

summary=json.loads((ROOT/'outputs'/'summary.json').read_text())
core=pd.read_csv(ROOT/'outputs/tables/core_descriptive_statistics.csv')
grp=pd.read_csv(ROOT/'outputs/tables/by_diagnosis_descriptives.csv')
qc=pd.read_csv(ROOT/'outputs/tables/quality_audit.csv')
miss=pd.read_csv(ROOT/'outputs/tables/missingness_selected.csv')
link=pd.read_csv(ROOT/'outputs/tables/linkage_flow.csv')
RPT.parent.mkdir(parents=True,exist_ok=True)
doc=SimpleDocTemplate(str(RPT),pagesize=A4,rightMargin=18.5*mm,leftMargin=18.5*mm,
                      topMargin=25*mm,bottomMargin=23*mm,title='nacc uds + mri statistics project - phase 1',author='course project')
S=[]

       
S.append(p('phase 1: data and descriptive statistics','cover'))
S.append(p('cognitive severity and entorhinal mri measurements in the supplied nacc cohort','subtitle'))
S.append(p('statistics course / path c / 03 november 2026','small'))
S.append(Spacer(1,5*mm))
S.append(p('summary','h1'))
S.append(p('i looked at whether entorhinal brain measurements vary with clinical cognitive severity in the prepared nacc data. severity is measured with cdr sum of boxes. the question is about an observed relationship rather than the cause of cognitive decline.','body'))
S.append(p('the supplied uds and mri files each have 1,237 participant records. the files match on naccid with no unmatched identifiers. each file has one row per person. however the original visits and dates of the scans are not included. this limits what we can say about how the records were chosen. [1]','body'))
S.append(p('there are 847 participants with normal cognition and 252 with mci. another 131 have dementia and 7 are classified as impaired but not mci. the median cdr score is 0 and 757 participants score exactly zero. the median bilateral entorhinal volume is 3,073.5 mm³ among 1,236 usable records. the median thickness is 3.06 mm among all 1,237 records.','body'))
S.append(p('mean entorhinal thickness is 3.09 mm for normal cognition and 2.91 mm for mci. it is 2.72 mm for dementia. higher-severity groups also have higher median cdr scores. the pattern is worth studying but it is an unadjusted description of this particular sample.','body'))
S.append(p('the csv files contain no ordinary nan cells. they still have special missing-value codes and unusual values. i treated two education codes of 99 as missing and excluded one zero left entorhinal volume from the bilateral sum. the moca and bmi fields also contain values that should not be used without checking the original processing.','body'))
S.append(p('two questions cannot be settled with these files. we cannot identify the original visit chosen for each participant or compare participants with mri against the wider uds group without mri. i have left these points open rather than making assumptions.','body'))
S.append(p('what this phase covers','h2'))
S.append(p('this phase describes the data and its limitations. it does not include hypothesis tests or regression models. those come in later phases.','body'))
S.append(PageBreak())

S.append(p('1. question and study design','h1'))
S.append(p('<b>working title:</b> cognitive severity and entorhinal mri measurements in nacc participants.','body'))
S.append(p('<b>question:</b> how do bilateral entorhinal gray-matter volume and mean cortical thickness vary with cdr sum of boxes in the linked uds and mri sample?','body'))
S.append(p('<b>initial expectation:</b> lower entorhinal volume and thickness may be seen alongside higher cdr scores. this is a proposed relationship to examine later. phase 1 does not test it.','body'))
S.append(p('<b>unit of analysis:</b> one supplied record for each naccid. i treat this as a participant-level cross-sectional sample. the original rule used to pair a clinical visit with an mri scan is not available so this description has a qualification.','body'))
S.append(p('2. where the data came from','h1'))
S.append(p("nacc brings together clinical assessments from alzheimer's disease research centers. the uds records cover personal characteristics and medical history as well as clinical and cognitive assessments. the imaging data provide brain measurements for selected participants. recruitment is not a random sample of the us population. these data should not be used to estimate national disease prevalence. [1, 2]",'body'))
S.append(p('the exact selection process for our prepared subset is unknown. for example scan availability or imaging quality may have affected who appears in the files. the results in this report therefore describe the 1,237 supplied participants. they cannot automatically be extended to everyone in nacc.','body'))
S.append(p('the zip contains file timestamps but not the clinical collection period or nacc release date. file creation dates are not visit dates. the source release and data-use terms need confirmation.','body'))
S.append(p('3. the three files','h1'))
S.append(rich_table(['FILE','ROWS × COLS','ROLE'],[
 ('udslong_imputed.csv','1,237 × 180','clinical uds records with demographics and medical history plus cognitive and functional scores and diagnosis.'),
 ('mriscanclean.csv','1,237 × 126','124 mri measurements covering gray volume and cortical thickness across 62 regions. also includes id and diagnosis.'),
 ('combined_adjacency_matrix.csv','62 × 63 raw','62 region labels and a 62 × 62 binary symmetric matrix with 62 diagonal ones and 232 off-diagonal undirected links. not participant data.')],[165,94,W-259]))
S.append(p('the adjacency matrix describes links between brain regions rather than measurements from participants. i kept it separate instead of joining it to the clinical records by row number. how that graph was created is not documented.','small'))

S.append(p('4. variables used','h1'))
S.append(rich_table(['VARIABLE / SOURCE','ROLE AND TYPE','VALIDITY / UNITS'],[
 ('CDRSUM / UDS','numeric severity score from 0 to 18','0 to 18 points. higher scores mean more impairment. many scores are zero.'),
 ('Left + right entorhinal GVOL / MRI','Main continuous MRI measure','sum of left and right volume in mm³. both sides must be positive.'),
 ('Left + right entorhinal AVGTH / MRI','Main continuous MRI measure','average of left and right thickness in mm.'),
 ('NACCUDSD / UDS','Categorical grouping / clinical status','1 normal, 2 impaired not MCI, 3 MCI, 4 dementia. Diagnose group, not MRI-derived.'),
 ('NACCAGE / UDS','Numerical covariate (age at chosen visit)','age in years. observed range 41 to 91.'),
 ('SEX / UDS','Binary categorical covariate','In these UDS records 1=male, 2=female.'),
 ('EDUC / UDS','Numerical covariate','years of education. code 99 is unknown. 1,235 usable values.'),
 ('MOCATOTS / UDS','Secondary quality-control variable','moca is usually 0 to 30. fractional and out-of-range entries prevent primary use.')],[156,154,W-310]))
S.append(Spacer(1,4*mm))
S.append(p('why these measures','h2'))
S.append(p('i added left and right entorhinal volumes because their units are cubic millimeters and the two volumes describe separate regions. for thickness i took the simple average of the left and right measurements. this is not an area-weighted measure. the mri units follow the scan data dictionary. [3]','body'))
S.append(p('counts and percentages make sense for diagnosis groups. a mean of the numeric diagnosis codes would have no useful meaning. for the measured scores and brain features i use means and standard deviations alongside medians and quartiles. cdr scores are mostly zero so a median and the full distribution tell us more than a mean alone. possible outliers are flagged rather than deleted automatically.','body'))
S.append(p('the full variable list','h2'))
S.append(p('the script also saves a list of all 306 columns across the two original tables. this includes the identifier and diagnosis columns present in both files. the list groups variables by general type but it is not a replacement for the original version-specific codebook.','body'))

S.append(p('5. matching participants and visits','h1'))
S.append(p('i matched the records using naccid. before merging i checked that neither file has a repeated identifier and that the diagnosis code agrees for every person. the repeated diagnosis column from the mri table was then dropped. using row order would be unsafe even when two files happen to have the same size.','body'))
S.append(rich_table(['LINKAGE STEP','ROWS / PARTICIPANTS'],[(r['step'],str(int(r['unique_NACCID']))) for _,r in link.iterrows()],[W*.66,W*.34]))
S.append(Spacer(1,4*mm))
S.append(p('what the perfect match means','h2'))
S.append(p('all 1,237 ids in the prepared uds file also appear in the prepared mri file. this shows that our two supplied tables line up. it does not show that every participant in the original nacc cohort received an mri scan.','body'))
S.append(p('what we know about visits','h2'))
S.append(p('each naccid appears once in each supplied table. so the observed distribution is exactly one supplied record per participant. we cannot count the original uds visits or determine which visit was selected. there is also no scan date to check how close the mri was to the clinical assessment. [1]','body'))
S.append(p('i kept one row per participant throughout the analysis. if the original repeated visits become available we will need a documented rule for choosing a clinical visit and matching its mri scan. using the first or closest visit now would be a guess.','body'))

S.append(p('6. checking the data','h1'))
S.append(p('the files have zero ordinary nan cells. that does not mean every value is usable. nacc records can use different numeric codes for missing or skipped answers. those codes must be checked separately for each variable. otherwise a real category coded as 8 or 9 could be lost. [1, 2]','body'))
S.append(rich_table(['AUDIT FLAG','N','TREATMENT / IMPLICATION'],[
 ('UDS/MRI ordinary NaN','0 / 0','review special codes and prior imputation seperately.'),
 ('Education = 99', '2','Exclude from education mean/SD.'),
 ('MoCA >30 / code 88', '9','outside the expected scale. excluded from valid moca summaries.'),
 ('MoCA noninteger', '249','likely upstream processing. not used as the primary measure.'),
 ('MoCA unavailable for strict integer valid-score summaries', '253','9 out-of-range and 249 fractional observations overlap in five cases.'),
 ('BMI ≥ 100', '131','126 use code 888.8. five more are implausibly high. bmi is secondary.'),
 ('MRI nonpositive regional gray volumes', '2','Includes one left entorhinal zero and one other cortical region zero.'),
 ('Left entorhinal GVOL = 0', '1','set left and bilateral volume to missing. 1,236 usable sums remain.'),
 ('Right entorhinal GVOL < 100 mm³', '3','unusual but still positive. retained while awaiting mri quality checks.'),
 ('CDRSUM differs from six box-score sum', '0','Every computed CDRSUM matches its six component box scores.'),
 ('Disagreement on NACCUDSD across files','0','All 1,237 values match.')],[170,40,W-210]))
S.append(Spacer(1,4*mm))
S.append(p('what was excluded and why','h2'))
S.append(p('the main cdr and thickness measures have no unusable entries under the checks applied here. one left entorhinal volume is zero. i set that measurement to missing before adding the two hemispheric volumes because zero is not a valid measured gray-matter volume in this context. the bilateral volume therefore has 1,236 usable records. i kept other positive extreme values because an unusual measurement is not necessarily an error.','body'))
S.append(p('moca includes fractional totals and values outside its usual scale. bmi has sentinel and implausibly large values. the supplied data appear to have been processed already but we cannot recover the original missingness. for this reason neither variable is central to this phase.','body'))

S.append(p('7. what the variables look like','h1'))
S.append(p('the table uses valid records for each measure. standard deviation is calculated with n minus 1 in the denominator. sample sizes may differ when a measurement fails a documented quality check.','body'))
rows=[]
for k in ('NACCAGE_clean','EDUC_clean','CDRSUM_clean','entorhinal_volume','entorhinal_thickness'):
    x=core[core.variable==k].iloc[0]
    rows.append((x['label'],str(int(x['n'])),f"{x['mean']:,.2f}",f"{x['median']:,.2f}",f"{x['sd']:,.2f}",f"{x['q1']:,.2f}–{x['q3']:,.2f}",f"{x['min']:,.2f}–{x['max']:,.2f}"))
S.append(rich_table(['MEASURE','N','MEAN','MEDIAN','SD','Q1–Q3','RANGE'],rows,[126,36,54,57,49,86,W-408]))
S.append(Spacer(1,4*mm))
S.append(p('reading the numbers','h2'))
S.append(p('cdr sum of boxes has a mean of 0.82 but a median of 0. this happens because most people have very low scores while a smaller number have much higher scores. the average entorhinal thickness is 3.01 mm and the median is 3.06 mm. i kept the units visible because volumes and thicknesses are different measurements and their raw spread cannot be compared directly.','body'))
S.append(p('diagnosis and sex counts','h2'))
diagnosis=summary['cognitive_groups']
S.append(rich_table(['CLINICAL CATEGORY','N','SHARE IN MATCHED COHORT'],[(x['diagnosis'],str(x['n']),f"{x['percent']:.2f}%") for x in diagnosis],[W*.48,W*.18,W*.34]))
S.append(Spacer(1,4*mm))
S.append(p('the data record 497 males and 740 females. two education entries use the unknown code 99 so the education summary uses 1,235 records. only 7 participants are in the impaired but not mci group. i kept the group in the tables to show the full sample but its small size makes comparisons uncertain.','body'))
S.append(p("the categories record clinical status. they do not establish that every dementia case is caused by alzheimer's disease.",'body'))

S.append(p('8. comparing clinical groups','h1'))
S.append(p('i compared cdr scores and the two entorhinal measures across the four recorded diagnostic groups. this is a descriptive comparison only.','body'))
rows=[]
for cat in [1,2,3,4]:
    g=grp[grp.diagnosis_code==cat]
    def row(v):return g[g.variable.str.lower()==v.lower()].iloc[0]
    c=row('CDR Sum of Boxes'); v=row('Bilateral volume (mm3)'); t=row('Bilateral thickness (mm)')
    rows.append((summary['cognitive_groups'][cat-1]['diagnosis'], str(summary['cognitive_groups'][cat-1]['n']),
                  f"{c['median']:.2f}", f"{v['mean']:,.0f}",f"{v['median']:,.0f}",f"{t['mean']:.2f}",f"{t['median']:.2f}"))
S.append(rich_table(['GROUP','N','CDR MED.','VOL MEAN','VOL MED.','THICK MEAN','THICK MED.'],rows,[103,37,61,68,68,83,W-420]))
S.append(Spacer(1,4*mm))
S.append(p('participants with normal cognition have mean entorhinal volume of 3,165 mm³ and mean thickness of 3.09 mm. for mci the values are 3,014 mm³ and 2.91 mm. for dementia they are 2,669 mm³ and 2.72 mm. the pattern shows smaller average measures in the more impaired groups. we have not adjusted these comparisons for age or education. scanner differences and head size may also matter.','body'))
S.append(p('the impaired but not mci group does not follow a simple trend on every measure. with only seven participants it would be misleading to merge or remove this group just to produce a smoother pattern. i left it visible instead.','body'))
S.append(p('checking unusual values','h2'))
vol=summary['selected_volume'];th=summary['selected_thickness'];cdr=summary['selected_cdr']
S.append(rich_table(['MEASURE','1.5 × IQR FLAGS','INTERPRETATION'],[
 ('CDR Sum of Boxes',str(cdr['iqr_flags']),'scores above 2.5 are flagged by the iqr rule. higher clinical severity is not itself a data error.'),
 ('Bilateral entorhinal volume',str(vol['iqr_flags']),'positive extremes were retained. original scan qc would help decide if they are errors.'),
 ('Bilateral mean thickness',str(th['iqr_flags']),'unusual values were kept because we cannot separate measurement issues from real variation.')],[162,84,W-246]))
S.append(p('how to read the plots','h2'))
S.append(p('histograms show where values are concentrated. boxplots make group medians and unusually high or low values easier to see. scatterplots display individual relationships without a fitted line. one plot uses slight vertical jitter so repeated cdr scores do not sit directly on top of each other. the jitter is only visual and does not change any calculation.','body'))
S.append(PageBreak())

plots=[
 ('fig01_diagnosis_counts.png','figure 1. number of participants in each cognitive-status group in the matched cohort.'),
 ('fig02_cdr_distribution.png','figure 2. cdr sum of boxes has many zero scores and a long right tail.'),
 ('fig03_entorhinal_volume.png','figure 3. bilateral entorhinal volume for the 1,236 participants with valid measurements on both sides.'),
 ('fig04_entorhinal_thickness.png','figure 4. average thickness of the left and right entorhinal regions for 1,237 participants.'),
 ('fig05_thickness_by_diagnosis.png','figure 5. entorhinal thickness by diagnosis. the group with seven people needs cautious interpretation.'),
 ('fig06_cdr_by_diagnosis.png','figure 6. cdr score distributions within clinical-status groups. both use clinical assessments.'),
 ('fig07_thickness_vs_cdr.png','figure 7. thickness and cdr score. slight vertical jitter makes overlapping scores visible.'),
 ('fig08_volume_vs_cdr.png','figure 8. entorhinal volume and cdr score before adjustment for other variables.'),
 ('fig09_core_missingness.png','figure 9. unusable values in the selected variables after checking their valid ranges and codes.')
]
for j in range(0,len(plots),2):
    S.append(p(f'9. plots {j+1} to {min(j+2,len(plots))}','h1'))
    for fn,caption in plots[j:j+2]:
        S.append(png(fn,maxheight=87*mm if j<8 else 125*mm))
        S.append(p(caption,'caption'))
        S.append(Spacer(1,2*mm))
    S.append(PageBreak())

S.append(p('10. phase 1 checklist','h1'))
S.append(p('the table distinguishes checks that can be completed from these files from questions that need the original nacc preparation records.','body'))
requirements=[
 ('Common 1: origin and collection','limited','the nacc study design is known but the exact release and processing are not.'),
 ('Common 2: observation unit','limited','1,237 unique supplied rows. the original visits are not included.'),
 ('Common 3: sampling/generalization','limited','the broad recruitment setting is known but the subset selection is not.'),
 ('Common 4: variable types','done','Core variable dictionary, units, and full 306-column inventory.'),
 ('Common 5: data quality','complete with current files','Unusable values, special codes, unusual MRI values and retention rules documented.'),
 ('Common 6: frequency/distributions','done','Diagnosis and sex frequency, outcome and MRI distributions.'),
 ('Common 7: center/spread','done','N, means, medians, SD, quartiles, IQR, min/max and IQR flags.'),
 ('Common 8: four graphs','done','Nine meaningfully labeled, reproducible figures.'),
 ('Common 9: group comparison','done','Unadjusted descriptive MRI and severity by NACCUDSD.'),
 ('Common 10: final question','done','Specific multi-modal question and justified scope.'),
 ('C1: map modalities','complete with current files','UDS domain map, MRI 124 features, auxiliary adjacency separation.'),
 ('C2: participants and visits','limited','ids were counted but the source visits and scan dates are missing.'),
 ('C3: link UDS + MRI','complete with current files','1,237 ids matched exactly and diagnosis codes agreed.'),
 ('C4: missingness / MRI selection','limited','important variables were checked. there is no uds-only comparison group.'),
 ('C5: cognitive + MRI summary','done','CDRSUM, gray volume and thickness with tables and figures.')]
S.append(rich_table(['REQUIREMENT','STATUS','EVIDENCE / LIMIT'],requirements,[151,93,W-244]))
S.append(Spacer(1,5*mm))
S.append(p('phase 1 is worth 12.5 base points. path c offers up to 10 extra points across the project when the multimodal requirements are done correctly. the unresolved source-data questions cannot be marked complete simply because the supplied tables already match.','small'))

S.append(p('11. limits of the supplied data','h1'))
S.append(rich_table(['REQUIRED INFORMATION','WHY IT MATTERS / HOW TO COMPLETE'],[
 ('Parent/full UDS cohort or MRI availability flag','the original uds cohort is needed to compare people with and without mri.'),
 ('Visit numbers and dates, MRI dates','visit and scan dates are needed to assess repeated visits and clinical-to-scan timing.'),
 ('Subset-generation code and data freeze','the extraction rules and release date would explain who entered the matched sample.'),
 ('Raw missing-value map and imputation log','an imputation log would show which original responses were missing and how values were filled.'),
 ('MRI QC, scanner/site, brain-size covariates','scan qc and head-size measures would help interpret unusual volumes and measurement differences.')],[151,W-151]))
S.append(Spacer(1,5*mm))
S.append(p('why the mri selection comparison is missing','h2'))
S.append(p('we can only compare people who appear in the files. both supplied files already contain the same 1,237 participants and neither contains a participant without mri. to compare scanned and unscanned people we would need the earlier uds cohort before this subset was assembled. inventing a comparison group would give a false answer.','body'))
S.append(p('12. what the findings mean','h1'))
S.append(p('the unadjusted data show lower average entorhinal measurements in the groups with greater recorded cognitive impairment. there could be other reasons for these differences. age and head size are obvious examples. the scanner and visit selection may also play a role. this phase cannot tell us whether these factors explain the pattern or whether brain changes caused the clinical differences.','body'))
S.append(p('the same question can continue through the course. phase 2 can examine conditional probabilities using stated mri thresholds. phase 3 can add confidence intervals and group comparisons. phase 4 can compare uds-only and mri-only models with a combined model using the same participants. that phase must also check whether a linear model is appropriate for a score with so many zeros. phase 5 can revisit sensitive decisions if the original records become available.','body'))

S.append(p('13. how to reproduce this work','h1'))
S.append(p('reproducing the analysis','h2'))
S.append(p('the repository contains the scripts and notebooks along with aggregate tables and nine figures. it also includes the project card and data instructions. to reproduce the results place the three original csv files in data/raw/ and run <b>python src/phase1_analysis.py</b> then <b>python src/build_report.py</b>. the analysis checks unique keys and matching diagnoses before calculating anything. it also records file hashes so the original inputs can be checked later. raw records and participant ids are not included in the submission.','body'))
S.append(p('how the summaries were calculated','h2'))
S.append(p('means are sums divided by the number of usable observations. sample standard deviations use n minus 1. q1 and q3 are the 25th and 75th percentiles. iqr is q3 minus q1. values farther than 1.5 times the iqr below q1 or above q3 are flagged for review. percentages divide each group count by 1,237. diagnosis codes are categories so they are summarized as counts instead of averages.','body'))
S.append(p('sources','h2'))
refs=[
 '[1] National Alzheimer’s Coordinating Center. NACC Researcher’s Guide. https://www.naccdata.org/the-nacc-researchers-guide/ (accessed 2026-11-03).',
 '[2] NACC. Data Request Process / Data File FAQ. https://www.naccdata.org/requesting-data/data-request-process/ and https://www.naccdata.org/data-file-faq (accessed 2026-11-03).',
 '[3] NACC. Researchers Data Dictionary — SCAN MRI Data, April 2024. https://files.alz.washington.edu/documentation/SCAN-MRI-Imaging-RDD.pdf (accessed 2026-11-03).',
 '[4] NACC. Description of derived variables (including NACCUDSD coding). https://files.alz.washington.edu/documentation/uds2-dervar.pdf (historical definition. confirm version-specific dictionary with course staff).',
 '[5] University statistics course, “Project instructions, Fall 1405” (uploaded project.pdf), pp. 3–8 and 18–19. Local course-provided document.'
]
for r in refs:S.append(p(r,'small'))
S.append(p('final note','h2'))
S.append(p('this is a descriptive study of the prepared files rather than an original national nacc estimate. the numerical results can be reproduced from the supplied data. full verification of participant selection and mri timing still needs the upstream records. the author should read the analysis and be able to explain each decision before submitting the individual course project.','body'))

       
try:
    doc.build(S,onFirstPage=running,onLaterPages=running)
except Exception:
    import traceback;traceback.print_exc();raise
print('PDF created:',RPT)
