from pathlib import Path
import json
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
import pypdfium2 as pdfium
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/cleaned_data_analysis'
m=json.loads((OUT/'analysis_metrics.json').read_text());schema=json.loads((ROOT/'data/training_candidates/do_next_month_v1/feature_schema.json').read_text())
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyCustom',fontName='Helvetica',fontSize=10,leading=14,spaceAfter=8))
styles.add(ParagraphStyle(name='SmallCustom',fontName='Helvetica',fontSize=8.5,leading=11,spaceAfter=6))
styles.add(ParagraphStyle(name='TitleCustom',fontName='Helvetica-Bold',fontSize=19,leading=23,textColor=colors.black,spaceAfter=12))
styles.add(ParagraphStyle(name='HeadingCustom',fontName='Helvetica-Bold',fontSize=12,leading=15,spaceBefore=9,spaceAfter=7,textColor=colors.black))
story=[]
def p(t,style='BodyCustom'):story.append(Paragraph(t,styles[style]))
def heading(t):p(t,'HeadingCustom')
def chart(name,width=506):
 im=Image(str(OUT/'charts'/name));ratio=im.imageHeight/im.imageWidth;im.drawWidth=width;im.drawHeight=width*ratio;story.append(im);story.append(Spacer(1,7))
def table(data,widths):
 cells=[[Paragraph(str(v),styles['SmallCustom']) for v in row] for row in data]
 t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7edf3')),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#d9d9d9')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
 story.append(t);story.append(Spacer(1,7))
p('EcoFlow Optima cleaned lake data analysis','TitleCustom')
p('Lake BOD and dissolved oxygen | Prepared 2 November 2026','SmallCustom')
p('The cleaned release is suitable for descriptive analysis and a proposed retrospective monthly DO forecasting experiment. It does not establish fish-kill, carrying-capacity or gate-control labels. No model has been trained.')
heading('Reviewed data and exact value summaries')
p('The release covers 52 available quarterly reports from January 2013 to June 2026, with gaps. Its 3,555 reviewed parameter cells contain 3,384 exact numeric values, 24 censored values, 146 source-missing cells and one unreadable digit excluded from numeric analysis. There are 1,766 station-months with at least one exact value. These are not independent samples.')
stats={r['parameter']:r for r in m['stats']}
table([['Parameter','Exact n','Mean','Median','Range'],['DO (mg/L)',1765,f"{stats['dissolved_oxygen']['mean']:.2f}",'7.80','4.0 to 18.3'],['BOD (mg/L)',1619,f"{stats['bod']['mean']:.2f}",'2.00','0.5 to 10.0']],[128,70,85,85,138])
p('Summaries use exact available cells only. They weight observed cells and do not estimate a balanced lake-wide average. Censored BOD values are excluded, so exact-only BOD summaries can differ from summaries that explicitly model censoring.','SmallCustom')
chart('coverage.png')
p('Station codes identify reported monitoring locations. First appearance in these tables does not prove a commissioning date. Gray and pale cells distinguish source gaps from stations or parameters absent from the reviewed table.','SmallCustom')
story.append(PageBreak())
p('Distributions and South Bay history','TitleCustom')
chart('distributions.png')
p('DO has a median of 7.8 mg/L; BOD has a median of 2.0 mg/L. High source-reported DO values were retained after source review. Without temperature, saturation and sampling metadata, they cannot be explained or removed solely because they are high.')
chart('south_bay_history.png')
p('Lines break at unavailable values. Month-start plotting anchors do not represent actual sampling days. Monthly reported observations cannot reveal unobserved daily or hourly oxygen minima.','SmallCustom')
p('Only three exact reported DO cells are below 5 mg/L, all at San Pedro. This is a descriptive threshold count, not a fish-kill label. The monthly series is too limited to infer the frequency of short-lived low-oxygen episodes.')
story.append(PageBreak())
p('Reporting patterns and interpretation','TitleCustom')
chart('reporting_patterns.png')
heading('Avoid interpreting reporting changes as environmental trends')
p('Among the historical nine station identities, whole-number DO values account for about 7.4% of exact values in 2019, 86.9% in 2024 and 100% in 2025. This is an observed precision pattern, not proof of a specific instrument or laboratory change. Annual means are descriptive, some years have gaps, and 2026 covers January to June only. Method and instrument metadata are needed before attributing differences to environmental change.')
heading('BOD and DO association')
p(f"The pooled same-month Pearson correlation is {m['same_month_bod_do_pearson_r']:.3f} across {m['matched_bod_do_station_months']:,} matched station-months. This weak positive association is not a causal result or a measure of future predictive accuracy. Station, time and reporting effects are not adjusted. A fitted model must still be compared with simple persistence and seasonal baselines.")
heading('Missingness and representativeness')
p('Some gaps have documented causes, including equipment failure, shallow water and weather. Missingness should not be assumed random. Complete-case training excludes periods without the required exact values; report those exclusions and compare with the supplied DO-history-only alternative. Do not replace missing measurements with zero.')
heading('What this means for the thesis')
p('The reviewed data can support investigation of monthly water-quality behavior and a limited retrospective prediction component. The original platform outputs still require their own evidence: location-specific fish-kill outcomes and reliable negatives, sustainable capacity outcomes, or actual operation and hydraulic records. A DO forecast alone does not establish those outputs.')
story.append(PageBreak())
p('Candidate training data and methodology','TitleCustom')
p('Primary file: training_do_next_month.csv. It contains 1,430 complete examples. Each row predicts exact DO in month t+1 from information indexed at months t-2, t-1 and t. The separate DO-history-only candidate contains 1,558 examples.')
table([['Role','Columns or meaning'],['Predictors','station_id; do_t_mg_l; do_t_minus_1_mg_l; do_t_minus_2_mg_l; bod_t_mg_l; target_month_sin; target_month_cos'],['Target','target_do_next_month_mg_l in mg/L'],['Metadata only','Example ID, origin and target months, proposed split, source record IDs and station_seen_in_training. Exclude these columns from predictor selection.']],[100,406])
table([['Proposed split','Examples','Target period'],['Train',819,'April 2013 to December 2022, with gaps'],['Validation',176,'January to December 2023'],['Test',435,'January 2024 to June 2026']],[110,85,311])
p('Splits use target month and are shared across stations. No random row split was used. Required calendar months are checked explicitly; no lag jumps across missing months. No scaling, categorical encoding, imputation or model fitting has been performed.')
heading('Conditions before fitting a model')
p('Fit preprocessing and station encoders on the training set only. Station XXIV has no training-period observations and contributes '+str(schema['unseen_station_test_examples'])+' test examples. Handle its unseen category explicitly and report known-station and new-station results separately. Earlier observed values across split boundaries are allowed for rolling one-month prediction; future target labels are not predictors.')
p('Publication timing is unresolved. Current-month values in a quarterly report may only have become available after the next-month target. These files therefore describe a retrospective observational experiment until operational input availability is established. Full-period descriptive exploration has already occurred, so the proposed test period is not a blind research holdout.')
p('Before training, confirm that this target supports the thesis scope, document timing assumptions, review reporting shifts and missingness, and define evaluation. Then compare persistence and seasonal baselines with simple candidate models using MAE/RMSE and results by station and period.')
p('Analysis was executed in Python. R import/exploration scripts are supplied but have not been executed in this environment. Source: LLDA quarterly water-quality reports, https://llda.gov.ph/ldb-and-its-tributaries/. Every reviewed measurement retains a PDF locator.','SmallCustom')
def footer(canvas,doc):
 canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#555555'));canvas.drawString(44,25,'EcoFlow Optima');canvas.drawRightString(A4[0]-44,25,str(doc.page))
path=OUT/'EcoFlow_Cleaned_Data_Analysis.pdf'
doc=SimpleDocTemplate(str(path),pagesize=A4,leftMargin=44,rightMargin=44,topMargin=39,bottomMargin=42,title='EcoFlow Optima cleaned lake data analysis',author='EcoFlow Optima')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
qa=ROOT/'tmp/cleaned_analysis_pdf_qa';qa.mkdir(parents=True,exist_ok=True)
pdf=pdfium.PdfDocument(str(path))
for i in range(len(pdf)):pdf[i].render(scale=1.5).to_pil().save(qa/f'page-{i+1}.png')
print(json.dumps({'pdf':str(path),'pages':len(pdf)}))
