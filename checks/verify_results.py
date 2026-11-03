
import json
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
s=json.loads((ROOT/'outputs/summary.json').read_text())
assert s['linkage']['final_n']==1237
assert s['linkage']['shared_ids']==1237
assert s['uds']['duplicate_ids']==0 and s['mri']['duplicate_ids']==0
assert sum(x['n'] for x in s['cognitive_groups'])==1237
assert s['selected_volume']['n']==1236
assert s['selected_thickness']['n']==1237
assert s['core_missingness']['EDUC']==2
assert s['zero_cdr']['n']==757
assert s['adjacency']['symmetric'] is True
assert len(list((ROOT/'figures').glob('fig*.png')))>=4
assert len(list((ROOT/'outputs'/'tables').glob('*.csv')))>=6
assert (ROOT/'reports'/'phase1.pdf').exists()
print('PASS: linkage, denominators, MRI QC, documentation outputs and report.')
