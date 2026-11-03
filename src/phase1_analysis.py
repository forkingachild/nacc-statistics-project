







from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / 'figures'
TAB = ROOT / 'outputs' / 'tables'
LABELS = {1:'normal cognition', 2:'impaired, not mci', 3:'mci', 4:'dementia'}
COLORS = ['#222222', '#777777', '#aaaaaa', '#dddddd']
PRIMARY_MRI = ['LH_ENTORHINAL_GVOL','RH_ENTORHINAL_GVOL','LH_ENTORHINAL_AVGTH','RH_ENTORHINAL_AVGTH']
PRIMARY_UDS = ['NACCID','NACCUDSD','NACCAGE','SEX','EDUC','CDRSUM','CDRGLOB','MOCATOTS','NACCBMI']


def sha256(path:Path) -> str:
    with path.open('rb') as f:
        h=hashlib.sha256()
        for block in iter(lambda:f.read(1048576),b''):
            h.update(block)
    return h.hexdigest()


def sf(x,n=2):
    return None if pd.isna(x) else round(float(x),n)


def numeric_desc(s:pd.Series):
    x = pd.to_numeric(s, errors='coerce').dropna()
    if len(x)==0: return {'n':0}
    q1,q3=x.quantile([.25,.75]); low=q1-1.5*(q3-q1); hi=q3+1.5*(q3-q1)
    return {'n':int(len(x)),'missing':int(len(s)-len(x)),'mean':sf(x.mean()),'median':sf(x.median()),
            'sd':sf(x.std(ddof=1)),'min':sf(x.min()),'q1':sf(q1),'q3':sf(q3),
            'iqr':sf(q3-q1),'max':sf(x.max()), 'iqr_flags':int(((x<low)|(x>hi)).sum()),
            'lower_fence':sf(low), 'upper_fence':sf(hi)}


def write_csv(df,name):
    TAB.mkdir(parents=True,exist_ok=True)
    df=df.copy()
    for c in df.select_dtypes(include='object').columns:
        if c!='variable':
            df[c]=df[c].map(lambda x: x.lower() if isinstance(x,str) else x)
    df.to_csv(TAB/name,index=False, float_format='%.4f')


def style_figure():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10.2,'axes.spines.top':False,
                         'axes.spines.right':False,'axes.titleweight':'normal','figure.dpi':115,
                         'savefig.dpi':180,'axes.labelpad':6,'axes.titlesize':12.2,
                         'axes.edgecolor':'#444444','grid.alpha':0})

def save(fig,file):
    FIG.mkdir(parents=True,exist_ok=True)
    for ax in fig.axes:
        ax.set_title(ax.get_title().lower())
        ax.set_xlabel(ax.get_xlabel().lower())
        ax.set_ylabel(ax.get_ylabel().lower())
        for t in ax.texts:
            t.set_text(t.get_text().lower())
        leg=ax.get_legend()
        if leg is not None:
            for t in leg.get_texts():
                t.set_text(t.get_text().lower())
    fig.tight_layout(pad=2.2)
    fig.savefig(FIG/file,bbox_inches='tight',facecolor='white')
    plt.close(fig)


def draw_figures(d, missing):
    style_figure()
    fig,ax=plt.subplots(figsize=(8.3,4.0))
    vals=d.NACCUDSD.astype(int).value_counts().reindex([1,2,3,4],fill_value=0)
    bars=ax.bar([LABELS[x] for x in vals.index],vals.values,color=COLORS,width=.65)
    for b,v in zip(bars,vals.values): ax.text(b.get_x()+b.get_width()/2,v+10,f'{v} ({v/len(d):.1%})',ha='center',fontsize=9)
    ax.set_ylim(0,max(vals)*1.14);ax.set_ylabel('Participants (count)');ax.set_title('Clinical cognitive-status distribution')
    save(fig,'fig01_diagnosis_counts.png')

    fig,ax=plt.subplots(figsize=(8.3,4.0))
    ax.hist(d['CDRSUM'],bins=np.arange(-.25,15.751,.5),color=COLORS[0],edgecolor='white',linewidth=.6)
    ax.set_ylabel('Participants (count)');ax.set_xlabel('CDR Sum of Boxes (0-18, higher = worse)')
    ax.set_title('Clinical dementia severity is strongly right-skewed');ax.set_xlim(-.35,15.5)
    ax.text(.98,.94,f'Zero score: {(d.CDRSUM==0).sum()} ({(d.CDRSUM==0).mean():.1%})',transform=ax.transAxes,ha='right',va='top',bbox={'facecolor':'white','edgecolor':'#aaaaaa','boxstyle':'round,pad=0.4'})
    save(fig,'fig02_cdr_distribution.png')

    for field,color,name,title,unit in [
        ('entorhinal_volume',COLORS[2],'fig03_entorhinal_volume.png','Bilateral entorhinal gray-matter volume','Volume (mm³)'),
        ('entorhinal_thickness',COLORS[0],'fig04_entorhinal_thickness.png','Bilateral average entorhinal thickness','Thickness (mm)')]:
        fig,ax=plt.subplots(figsize=(8.3,4.0)); vals=d[field].dropna()
        ax.hist(vals,bins=38,color=color,edgecolor='white',linewidth=.7)
        ax.axvline(vals.median(),color='#000000',ls='--',lw=1.8,label=f'Median = {vals.median():,.1f}')
        ax.set(xlabel=unit,ylabel='Participants (count)',title=title);ax.legend(frameon=False)
        save(fig,name)

    groups=[d.loc[d.NACCUDSD==i,'entorhinal_thickness'].dropna() for i in LABELS]
    fig,ax=plt.subplots(figsize=(8.6,4.3))
    bp=ax.boxplot(groups,tick_labels=[f'{LABELS[i]}\n(n={len(groups[i-1])})' for i in LABELS],showfliers=True,patch_artist=True,
                  medianprops={'color':'#000000','linewidth':1.8},flierprops={'markersize':2.5,'alpha':.3})
    for patch,color in zip(bp['boxes'],COLORS):patch.set_facecolor(color);patch.set_alpha(.7)
    ax.set(ylabel='Bilateral mean thickness (mm)',title='Entorhinal thickness across cognitive-status groups');
    save(fig,'fig05_thickness_by_diagnosis.png')

    fig,ax=plt.subplots(figsize=(8.6,4.3))
    groups=[d.loc[d.NACCUDSD==i,'CDRSUM'] for i in LABELS]
    bp=ax.boxplot(groups,tick_labels=[f'{LABELS[i]}\n(n={len(groups[i-1])})' for i in LABELS],showfliers=True,patch_artist=True,
                  medianprops={'color':'#000000','linewidth':1.8},flierprops={'markersize':2.5,'alpha':.25})
    for patch,color in zip(bp['boxes'],COLORS):patch.set_facecolor(color);patch.set_alpha(.7)
    ax.set(ylabel='CDR Sum of Boxes (0-18)',title='Observed CDR severity by cognitive-status group');
    save(fig,'fig06_cdr_by_diagnosis.png')

    fig,ax=plt.subplots(figsize=(8.3,4.4))
                                                                             
    rng=np.random.default_rng(1405)
    for i,cat in LABELS.items():
        g=d.loc[d.NACCUDSD==i]
        ax.scatter(g['entorhinal_thickness'],g.CDRSUM+rng.uniform(-.115,.115,len(g)),s=11,alpha=.24,color=COLORS[i-1],label=f'{cat} (n={len(g)})')
    ax.set(xlabel='Bilateral entorhinal mean thickness (mm)',ylabel='CDR Sum of Boxes (jittered for visibility)',title='Participant-level MRI and clinical severity')
    ax.legend(fontsize=8,frameon=False,loc='upper right',ncol=2)
    save(fig,'fig07_thickness_vs_cdr.png')

    fig,ax=plt.subplots(figsize=(8.3,4.3))
    for i,cat in LABELS.items():
        g=d.loc[d.NACCUDSD==i].dropna(subset=['entorhinal_volume'])
        ax.scatter(g['entorhinal_volume'],g.CDRSUM,s=10,alpha=.25,color=COLORS[i-1],label=f'{cat} (n={len(g)})')
    ax.set(xlabel='Bilateral entorhinal gray volume (mm³)',ylabel='CDR Sum of Boxes (0-18)',title='Bilateral gray volume and clinical severity')
    ax.legend(frameon=False,fontsize=8,loc='upper right',ncol=2)
    save(fig,'fig08_volume_vs_cdr.png')

    fig,ax=plt.subplots(figsize=(8.5,4.1))
    items=['CDRSUM','Age','Education','MoCA','MRI volume L','MRI volume R','MRI thickness L','MRI thickness R']
    misskeys=['CDRSUM','NACCAGE','EDUC','MOCATOTS','LH_ENTORHINAL_GVOL','RH_ENTORHINAL_GVOL','LH_ENTORHINAL_AVGTH','RH_ENTORHINAL_AVGTH']
    counts=[int(missing[k]) for k in misskeys]
    bars=ax.barh(items,counts,color=['#444444' if v else '#bbbbbb' for v in counts],height=.6)
    ax.invert_yaxis();ax.set_xlabel('Unusable values after variable-specific rules (count)')
    ax.set_title('Selected-variable data quality (zero means usable for these rules)')
    ax.set_xlim(0,max(counts+[1])*1.13)
    for b,v in zip(bars,counts):ax.text(v+max(counts+[1])*.012,b.get_y()+b.get_height()/2,str(v),va='center')
    save(fig,'fig09_core_missingness.png')


def inspect(data_dir:Path):
    files={fn:data_dir/fn for fn in ('udslong_imputed.csv','mriscanclean.csv','combined_adjacency_matrix.csv')}
    absent=[str(p) for p in files.values() if not p.exists()]
    if absent:raise FileNotFoundError('Missing source files: '+', '.join(absent)+'; see data/README.md')
    u=pd.read_csv(files['udslong_imputed.csv'],low_memory=False)
    m=pd.read_csv(files['mriscanclean.csv'],low_memory=False)
    a=pd.read_csv(files['combined_adjacency_matrix.csv'],index_col=0)
    for name,df in [('UDS',u),('MRI',m)]:
        assert 'NACCID' in df, f'{name}: participant identifier absent'
        assert df.NACCID.notna().all(),f'{name}: missing participant IDs'
        assert df.NACCID.is_unique,f'{name}: repeated participant IDs: need visit-level join protocol'
    a_vals=a.to_numpy()
    assert a.shape==(62,62),'Unexpected adjacency dimensions'
    assert np.array_equal(a_vals,a_vals.T),'Adjacency matrix not symmetric'
    assert set(np.unique(a_vals)).issubset({0,1}),'Adjacency nonbinary'
    assert len(set(a.index))==62 and set(a.index)==set(a.columns)

    s1=set(u.NACCID);s2=set(m.NACCID)
    diag_match=(u.set_index('NACCID')['NACCUDSD'].sort_index()==m.set_index('NACCID')['NACCUDSD'].sort_index()).all()
    assert diag_match,'Conflicting diagnosis for same participant'
    d=u.merge(m.drop(columns='NACCUDSD'),on='NACCID',how='inner',validate='one_to_one')
    assert not d.NACCID.duplicated().any()
                                                                       
    for v in (c for c in m.columns if c.endswith('_GVOL')):
        d[v+'_clean']=d[v].where(d[v]>0,np.nan) if v in PRIMARY_MRI else d[v]
    for v in (c for c in PRIMARY_MRI if c.endswith('_AVGTH')):
        d[v+'_clean']=d[v].where(d[v]>0,np.nan)
    d['entorhinal_volume']=d.LH_ENTORHINAL_GVOL_clean+d.RH_ENTORHINAL_GVOL_clean
                                                         
    d['entorhinal_thickness']=(d.LH_ENTORHINAL_AVGTH_clean+d.RH_ENTORHINAL_AVGTH_clean)/2
    d['EDUC_clean']=d.EDUC.where((d.EDUC.between(0,30)) & (d.EDUC!=99),np.nan)
    d['MOCATOTS_clean']=d.MOCATOTS.where(d.MOCATOTS.between(0,30)&(np.mod(d.MOCATOTS,1)==0),np.nan)
    d['NACCBMI_clean']=d.NACCBMI.where((d.NACCBMI>0)&(d.NACCBMI<100),np.nan)
    d['CDRSUM_clean']=d.CDRSUM.where(d.CDRSUM.between(0,18),np.nan)
    d['NACCAGE_clean']=d.NACCAGE.where(d.NACCAGE.between(0,120),np.nan)
    d['SEX_clean']=d.SEX.where(d.SEX.isin([1,2]),np.nan)
    d['NACCUDSD_clean']=d.NACCUDSD.where(d.NACCUDSD.isin([1,2,3,4]),np.nan)
    missing={
        'CDRSUM':d.CDRSUM_clean.isna().sum(),'NACCAGE':d.NACCAGE_clean.isna().sum(),
        'SEX':d.SEX_clean.isna().sum(),'EDUC':d.EDUC_clean.isna().sum(),
        'MOCATOTS':d.MOCATOTS_clean.isna().sum(),'NACCBMI':d.NACCBMI_clean.isna().sum(),
        'NACCUDSD':d.NACCUDSD_clean.isna().sum(),
        **{v:d[v+'_clean'].isna().sum() for v in PRIMARY_MRI}
    }
    categories=[]
    for code in [1,2,3,4]:
        n=int((d.NACCUDSD==code).sum())
        categories.append({'code':code,'diagnosis':LABELS[code],'n':n,'percent':round(100*n/len(d),2)})
    diag=pd.DataFrame(categories)
    write_csv(diag,'diagnosis_frequency.csv')
    sexes=d.SEX.value_counts().reindex([1,2],fill_value=0)
    write_csv(pd.DataFrame({'code':sexes.index.astype(int),'label':['male','female'],'n':sexes.values,
                            'percent':(100*sexes.values/len(d)).round(2)}),'sex_frequency.csv')
    core=[('NACCAGE_clean','Age (years)','UDS'),('EDUC_clean','Education (years)','UDS'),
          ('CDRSUM_clean','CDR Sum of Boxes','UDS'),('MOCATOTS_clean','MoCA valid integer only (secondary audit)','UDS'),
          ('LH_ENTORHINAL_GVOL_clean','Left entorhinal volume (mm3)','MRI'),
          ('RH_ENTORHINAL_GVOL_clean','Right entorhinal volume (mm3)','MRI'),
          ('LH_ENTORHINAL_AVGTH_clean','Left entorhinal thickness (mm)','MRI'),
          ('RH_ENTORHINAL_AVGTH_clean','Right entorhinal thickness (mm)','MRI'),
          ('entorhinal_volume','Bilateral entorhinal volume (mm3)','MRI derived'),
          ('entorhinal_thickness','Bilateral entorhinal mean thickness (mm)','MRI derived')]
    summaries=[]
    for col,desc,mod in core:
        stats=numeric_desc(d[col]);summaries.append({'variable':col,'label':desc.lower(),'modality':mod.lower(),**stats})
    stats_df=pd.DataFrame(summaries)
    write_csv(stats_df,'core_descriptive_statistics.csv')

    grouped=[]
    for cat in [1,2,3,4]:
        df=d[d.NACCUDSD==cat]
        for col,desc in [('CDRSUM','CDR Sum of Boxes'),('NACCAGE','Age (years)'),
                         ('entorhinal_volume','Bilateral volume (mm3)'),('entorhinal_thickness','Bilateral thickness (mm)')]:
            grouped.append({'diagnosis_code':cat,'diagnosis':LABELS[cat],'variable':desc.lower(),**numeric_desc(df[col])})
    write_csv(pd.DataFrame(grouped),'by_diagnosis_descriptives.csv')
    write_csv(pd.DataFrame([{'variable':k,'unusable_n':int(v),'percent':round(100*v/len(d),3)} for k,v in missing.items()]),'missingness_selected.csv')

                                                                      
    demo=set('SEX HISPANIC HISPOR RACE PRIMLANG EDUC MARISTAT NACCLIVS INDEPEND RESIDENC NACCNIHR NACCAGE'.split())
    clinical=set('CDRSUM CDRGLOB MEMORY ORIENT JUDGMENT COMMUN HOMEHOBB PERSCARE NACCUDSD MOCATOTS DECSUB ANIMALS VEG TRAILA TRAILB'.split())
    physical=set('HEIGHT WEIGHT BPSYS BPDIAS HRATE NACCBMI VISION HEARING'.split())
    functional=set('BILLS TAXES SHOPPING GAMES STOVE MEALPREP EVENTS PAYATTN REMDATES TRAVEL'.split())
    mental=set('NACCGDS DEL HALL AGIT DEPD ANX ELAT APA DISN IRR MOT NITE APP'.split())
    inv=[]
    for mod,df in [('UDS',u),('MRI',m)]:
        for col in df.columns:
            if col=='NACCID': cat='Identifier';typ='ID (nominal)';unit='not applicable'
            elif mod=='MRI' and col.endswith('_GVOL'):cat='MRI regional gray volume';typ='Quantitative continuous (recorded discrete mm3)';unit='mm3'
            elif mod=='MRI' and col.endswith('_AVGTH'):cat='MRI average thickness';typ='Quantitative continuous';unit='mm'
            elif col=='NACCUDSD':cat='Clinical status';typ='Categorical nominal';unit='category'
            elif col in demo:cat='Demographic / participant characteristics';typ='Categorical or numerical - verify dictionary';unit='variable-specific'
            elif col in clinical:cat='Cognitive / clinical assessment';typ='Categorical or numerical - verify dictionary';unit='variable-specific'
            elif col in physical:cat='Physical assessment';typ='Categorical or numerical - verify dictionary';unit='variable-specific'
            elif col in functional:cat='Functional assessment';typ='Categorical or numerical - verify dictionary';unit='variable-specific'
            elif col in mental:cat='Neuropsychiatric / psychological';typ='Categorical or numerical - verify dictionary';unit='variable-specific'
            else:cat='Medical history / medications / other UDS';typ='Categorical or numerical - verify dictionary';unit='variable-specific'
            inv.append({'modality':mod.lower(),'variable':col,'domain':cat.lower(),'type_note':typ.lower(),'units':unit.lower(),
                'rows':len(df),'ordinary_na':int(df[col].isna().sum()),'distinct_values':int(df[col].nunique(dropna=True))})
    write_csv(pd.DataFrame(inv),'full_variable_inventory.csv')

                                                                           
    match=pd.DataFrame([
        {'step':'uds supplied','rows':len(u),'unique_NACCID':u.NACCID.nunique()},
        {'step':'mri supplied','rows':len(m),'unique_NACCID':m.NACCID.nunique()},
        {'step':'uds only','rows':len(s1-s2),'unique_NACCID':len(s1-s2)},
        {'step':'mri only','rows':len(s2-s1),'unique_NACCID':len(s2-s1)},
        {'step':'matched merged cohort','rows':len(d),'unique_NACCID':d.NACCID.nunique()},
        {'step':'bilateral volume usable','rows':int(d.entorhinal_volume.notna().sum()),'unique_NACCID':int(d.entorhinal_volume.notna().sum())},
        {'step':'Bilateral thickness usable','rows':int(d.entorhinal_thickness.notna().sum()),'unique_NACCID':int(d.entorhinal_thickness.notna().sum())}])
    write_csv(match,'linkage_flow.csv')

                                                                   
    qc=[
        {'issue':'UDS ordinary NaN (all 179 numeric variables)','count':int(u.drop(columns='NACCID').isna().sum().sum()),'decision':'Raw audit only; absence of NaN does not mean absence of missing codes'},
        {'issue':'MRI ordinary NaN (124 measurements + diagnosis)','count':int(m.drop(columns='NACCID').isna().sum().sum()),'decision':'No ordinary NaNs observed'},
        {'issue':'EDUC code 99 (unknown)','count':int((d.EDUC==99).sum()),'decision':'Mark missing in education summaries'},
        {'issue':'MOCATOTS code 88 or outside 0-30','count':int((~d.MOCATOTS.between(0,30)).sum()),'decision':'Not a valid total score; report separately'},
        {'issue':'MOCATOTS fractional values','count':int((np.mod(d.MOCATOTS,1)!=0).sum()),'decision':'Flag possible imputation/transformation; do not use as primary outcome'},
        {'issue':'NACCBMI >=100 (888.8 sentinel observed)','count':int((d.NACCBMI>=100).sum()),'decision':'Mark missing for BMI summaries; not a real BMI'},
        {'issue':'MRI gray volume <=0 in any region','count':int((m[[x for x in m if x.endswith('_GVOL')]]<=0).sum().sum()),'decision':'Flag; use nonpositive as missing for any preselected derived primary volume'},
        {'issue':'Left entorhinal gray volume <=0','count':int((d.LH_ENTORHINAL_GVOL<=0).sum()),'decision':'Missing for the bilateral-volume composite'},
        {'issue':'Right entorhinal gray volume <100mm3 (suspicious, not proven invalid)','count':int((d.RH_ENTORHINAL_GVOL<100).sum()),'decision':'Retain positive values; flag for original-scan QC review'},
        {'issue':'CDRSUM unequal to sum of six CDR boxes','count':int(((d[['MEMORY','ORIENT','JUDGMENT','COMMUN','HOMEHOBB','PERSCARE']].sum(axis=1)-d.CDRSUM).abs()>1e-8).sum()),'decision':'No discrepancy observed'},
        {'issue':'Diagnosis code disagreement across UDS/MRI','count':int((~(u.set_index('NACCID').NACCUDSD==m.set_index('NACCID').NACCUDSD)).sum()),'decision':'No disagreement observed'},
    ]
    write_csv(pd.DataFrame(qc),'quality_audit.csv')

    draw_figures(d,missing)
    summary={
        'source_archive_files':[{ 'name':fn, 'sha256':sha256(path),'bytes':path.stat().st_size} for fn,path in files.items()],
        'uds':{'rows':len(u),'columns':len(u.columns),'unique_ids':int(u.NACCID.nunique()), 'duplicate_ids':int(u.NACCID.duplicated().sum()),'na_cells':int(u.isna().sum().sum())},
        'mri':{'rows':len(m),'columns':len(m.columns),'unique_ids':int(m.NACCID.nunique()), 'duplicate_ids':int(m.NACCID.duplicated().sum()),'na_cells':int(m.isna().sum().sum()),
               'gray_volume_features':len([c for c in m if c.endswith('_GVOL')]),'average_thickness_features':len([c for c in m if c.endswith('_AVGTH')])},
        'linkage':{'shared_ids':len(s1&s2),'uds_only':len(s1-s2),'mri_only':len(s2-s1),'final_n':len(d),'diagnosis_agreement':bool(diag_match)},
        'adjacency':{'shape':list(a.shape),'binary':True,'symmetric':True,'self_loops':int(np.trace(a_vals)),
                     'undirected_edges_excluding_self_loops':int((a_vals.sum()-np.trace(a_vals))//2)},
        'cognitive_groups':categories,'core_missingness':{k:int(v) for k,v in missing.items()},
        'medians':{'cdr':sf(d.CDRSUM.median()),'volume':sf(d.entorhinal_volume.median()),'thickness':sf(d.entorhinal_thickness.median())},
        'averages':{'cdr':sf(d.CDRSUM.mean()),'volume':sf(d.entorhinal_volume.mean()),'thickness':sf(d.entorhinal_thickness.mean())},
        'zero_cdr':{'n':int((d.CDRSUM==0).sum()),'fraction':sf((d.CDRSUM==0).mean(),4)},
        'moca_fractional':int((np.mod(d.MOCATOTS,1)!=0).sum()),
        'raw_moca_over_30':int((d.MOCATOTS>30).sum()),
        'smallest_rh_entorhinal_volume':sf(d.RH_ENTORHINAL_GVOL.min()),
        'selected_age':numeric_desc(d.NACCAGE),'selected_cdr':numeric_desc(d.CDRSUM),
        'selected_volume':numeric_desc(d.entorhinal_volume),'selected_thickness':numeric_desc(d.entorhinal_thickness),
        'limitations':[ 'the original full uds cohort is unavailable so the scanned and unscanned groups cannot be compared.',
                        'source visit and mri dates are absent so the choice and timing of records cannot be verified.',
                        'the original missing values and imputation procedure are not available.',
                        'image quality flags and scanner details are unavailable.',
                        'the files do not include intracranial volume for volume adjustment.',
                        'Recruitment at Alzheimer\'s Disease Research Centers does not support population prevalence estimates.' ]}
    (ROOT/'outputs').mkdir(exist_ok=True)
    (ROOT/'outputs'/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    print('Phase 1 descriptive analysis complete:',len(d),'participant rows')
    print('Tables:',len(list(TAB.glob('*.csv'))),'figures:',len(list(FIG.glob('fig*.png'))))
    return summary


def main():
    p=argparse.ArgumentParser();p.add_argument('--data-dir',type=Path,default=ROOT/'data'/'raw')
    args=p.parse_args();inspect(args.data_dir)
if __name__=='__main__':main()
