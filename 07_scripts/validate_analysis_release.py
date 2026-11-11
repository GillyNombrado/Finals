from pathlib import Path
import csv,json,hashlib,collections,zipfile
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/analysis_ready/llda_lake_bod_do_v1'
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
rows=read(OUT/'lake_measurements_reviewed_long.csv');good=read(OUT/'lake_numeric_analysis.csv');panel=read(OUT/'lake_station_month_calendar.csv');audit=read(OUT/'source_review_audit.csv');pairs=read(OUT/'candidate_adjacent_month_do_pairs.csv')
assert len(audit)==52 and len(rows)==3555 and len(good)==3384
assert len({r['record_id'] for r in rows})==len(rows)
assert len({(r['station_id'],r['observation_month'],r['parameter']) for r in rows})==len(rows)
assert all(r['numeric_value'] and r['qualifier']=='=' and r['review_status']=='source_visually_checked' for r in good)
assert all(not r['numeric_value'] for r in rows if r['value_status'] in ['censored','blank_as_reported','missing_as_reported','no_data_as_reported','unreadable_source'])
assert all(not r['available_at'] and not r['sample_datetime'] for r in rows)
assert len(panel)==16*162 and len({(r['station_id'],r['observation_month']) for r in panel})==len(panel)
def mid(s):y,m=map(int,s.split('-'));return y*12+m
assert all(mid(r['target_month'])-mid(r['input_month'])==1 for r in pairs)
assert not any(r['observation_month'] in ['2014-07','2014-08','2014-09','2020-04','2020-05','2020-06'] for r in rows)
assert all(int(r['source_page'])==2 for r in rows if r['source_file']=='2014q1.pdf')
assert sum(int(r['reviewed_parameter_cells']) for r in audit)==len(rows)
raw=ROOT/'data/raw/llda_reports_2026-11-02';originals=read(raw/'download_inventory.csv')
assert all(hashlib.sha256((raw/r['filename']).read_bytes()).hexdigest()==r['sha256'].lower() for r in originals)
moves=read(ROOT/'data/raw/download_archive_2026-11-02/move_manifest.csv')
assert len(moves)==67
assert all(Path(r['project_path']).exists() and not Path(r['original_path']).exists() for r in moves)
assert all(hashlib.sha256(Path(r['project_path']).read_bytes()).hexdigest()==r['sha256'].lower() for r in moves if r['item_type']=='file')
compiled=ROOT/'data/analysis_ready/compiled_reference_v1';inventory=read(compiled/'dataset_inventory.csv')
assert len(inventory)==11 and sum(int(r['rows']) for r in inventory)==186
assert all(len(read(compiled/(r['dataset']+'.csv')))==int(r['rows']) for r in inventory)
result={'checks_passed':['52 quarterly reports represented in reviewed lake scope','3555 reviewed cells reconcile with 3384 exact numeric cells and 171 non-exact cells','Unique record IDs and station-month-parameter keys','Missing, censored and unreadable values cannot enter exact numeric analysis','16-station 162-month calendar has unique keys','All candidate input-target pairs are truly adjacent months','Unavailable source quarters are not invented','Conflicting 2014 appendix excluded','Actual sample and release timestamps not invented','56 source PDF hashes unchanged','67 project items moved and destination file hashes verified','11 reference tables retain all 186 rows'],'numeric_scope':'Lake BOD/DO only','r_execution':'Not run: Rscript was not found in PATH or C:/Program Files/R','review_limitation':'One ambiguous source digit excluded; no independent second human transcription audit'}
(OUT/'validation_checks.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
