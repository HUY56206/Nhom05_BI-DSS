# -*- coding: utf-8 -*-
import os, json, uuid, shutil, re
BASE = os.path.expanduser('~/mnt/BI_K24406H_Kỳ7-20261116T011316Z-1-001/BI_K24406H_Kỳ7/powerbi')
WIN_DATA = r'D:\HK7_Năm 3\Trí tuệ doanh nghiệp\BI_K24406H_Kỳ7-20261116T011316Z-1-001\BI_K24406H_Kỳ7\powerbi\data'
PROJ = os.path.join(BASE, 'coffee_bi_model')
SM = os.path.join(PROJ, 'coffee_bi_model.SemanticModel')
RP = os.path.join(PROJ, 'coffee_bi_model.Report')
shutil.rmtree(SM, ignore_errors=True)
for d in (SM+'/definition/tables', SM+'/definition/cultures', RP):
    os.makedirs(d, exist_ok=True)
NS = uuid.UUID('6f1f0a52-0c0d-4c34-9a55-6b1d7a0e2f11')
def g(x): return str(uuid.uuid5(NS, x))
def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f: f.write(text)
T = '\t'

MT = {'int':'Int64.Type','num':'type number','text':'type text','date':'type date','datetime':'type datetime','time':'type time','bool':'type logical'}
DT = {'int':'int64','num':'double','text':'string','date':'dateTime','datetime':'dateTime','time':'dateTime','bool':'boolean'}

def C(_n,_t,**o): return (_n,_t,o)
tables = {}
tables['Dim_Date'] = ('dim_date.csv', [
 C('date_key','int',h=1,n=1,f='0'), C('full_date','date',k=1,f='dd/MM/yyyy'), C('year','int',n=1,f='0'), C('quarter','int',n=1,f='0'),
 C('month','int',n=1,f='0'), C('month_name','text',s='month'), C('day_of_week','int',n=1,f='0'), C('day_name','text',s='day_of_week'),
 C('is_weekend','int',n=1,f='0'), C('week_start','date',f='dd/MM/yyyy'), C('week_no','int',n=1,f='0'), C('in_data_period','int',n=1,f='0')], dict(cat='Time'))
tables['Dim_Store'] = ('dim_store.csv', [C('store_key','int',h=1,n=1,f='0'), C('store_id','int',n=1,f='0'), C('store_location','text')], {})
tables['Dim_Shift'] = ('dim_shift.csv', [C('shift_key','int',h=1,n=1,f='0'), C('shift_name','text',s='shift_key'), C('start_hour','int',n=1,f='0'), C('end_hour','int',n=1,f='0')], {})
tables['Dim_Menu_Item'] = ('dim_menu_item.csv', [C('menu_item_key','int',h=1,n=1,f='0'), C('product_id','int',n=1,f='0'), C('product_category','text'), C('product_type','text'),
 C('product_detail','text'), C('base_item','text'), C('size','text')], {})
tables['Dim_Ingredient'] = ('dim_ingredient.csv', [C('ingredient_key','int',h=1,n=1,f='0'), C('ingredient_id','text'), C('ingredient_name','text'), C('unit','text'),
 C('unit_cost_usd','num',n=1,f='0.0000'), C('yield_pct','num',n=1,f='0.0'), C('shelf_life_days','int',n=1,f='0')], {})
tables['Bridge_BOM'] = ('bridge_bom.csv', [C('bom_key','int',h=1,n=1,f='0'), C('menu_item_key','int',h=1,n=1,f='0'), C('ingredient_key','int',h=1,n=1,f='0'),
 C('bom_version','int',n=1,f='0'), C('quantity_ep','num',f='#,0.000'), C('quantity_basis','text'), C('yield_pct','num',n=1,f='0.0'), C('quantity_ap','num',f='#,0.000'),
 C('unit','text'), C('unit_cost_usd','num',n=1,f='0.0000'), C('line_cost_usd','num',f='0.0000')], {})
tables['Fact_Sales'] = ('fact_sales.csv', [C('sales_key','int',h=1,n=1,f='0'), C('transaction_id','int',n=1,f='0'), C('date_key','int',h=1,n=1,f='0'), C('store_key','int',h=1,n=1,f='0'),
 C('shift_key','int',h=1,n=1,f='0'), C('menu_item_key','int',h=1,n=1,f='0'), C('transaction_time','time',f='hh:mm:ss'), C('hour','int',n=1,f='0'), C('transaction_qty','int',f='#,0'),
 C('unit_price','num',n=1,f='0.00'), C('revenue','num',f='#,0.00'), C('outlier_flag','int',n=1,f='0'), C('std_cost','num',n=1,f='0.0000'), C('cm','num',n=1,f='0.0000'),
 C('total_std_cost','num',f='#,0.0000'), C('total_cm','num',f='#,0.0000')], {})
tables['Fact_Inventory_Audit'] = ('fact_inventory_audit.csv', [C('inventory_key','int',h=1,n=1,f='0'), C('store_key','int',h=1,n=1,f='0'), C('ingredient_key','int',h=1,n=1,f='0'),
 C('week_start_date_key','int',h=1,n=1,f='0'), C('week_no','int',n=1,f='0'), C('days_observed','int',n=1,f='0'), C('opening_qty','num',f='#,0.000'), C('receipt_qty','num',f='#,0.000'),
 C('actual_usage','num',f='#,0.000'), C('closing_qty','num',f='#,0.000'), C('theoretical_usage','num',f='#,0.000'), C('theoretical_usage_etl','num',f='#,0.000000'),
 C('recorded_waste','num',f='#,0.000'), C('unit_cost_usd','num',n=1,f='0.0000'), C('opening_value_usd','num',f='#,0.0000'), C('receipt_value_usd','num',f='#,0.0000'),
 C('closing_value_usd','num',f='#,0.0000'), C('actual_cogs_usd','num',f='#,0.0000')], {})
tables['Fact_Waste_Log'] = ('fact_waste_log.csv', [C('waste_key','int',h=1,n=1,f='0'), C('waste_id','text'), C('date_key','int',h=1,n=1,f='0'), C('store_key','int',h=1,n=1,f='0'),
 C('shift_key','int',h=1,n=1,f='0'), C('ingredient_key','int',h=1,n=1,f='0'), C('waste_datetime','datetime',f='dd/MM/yyyy hh:mm'), C('week_no','int',n=1,f='0'), C('reason','text'),
 C('waste_qty','num',f='#,0.000'), C('unit_cost_usd','num',n=1,f='0.0000'), C('waste_value_usd','num',f='#,0.0000')], {})
tables['Menu_Matrix'] = ('menu_matrix.csv', [C('scope_type','text'), C('store_id','num',n=1,f='0'), C('store_location','text'), C('product_id','int',n=1,f='0'), C('product_detail','text'),
 C('product_category','text'), C('Q','int',f='#,0'), C('revenue','num',f='#,0.00'), C('mm_pct','num',n=1,f='0.000'), C('P','num',n=1,f='0.00'), C('std_cost','num',n=1,f='0.0000'),
 C('CM','num',n=1,f='0.0000'), C('total_std_cost','num',f='#,0.00'), C('total_cm','num',f='#,0.00'), C('mm_threshold_70_pct','num',n=1,f='0.000'), C('mm_threshold_100_pct','num',n=1,f='0.000'),
 C('cm_threshold','num',n=1,f='0.0000'), C('class_70','text'), C('class_100','text'), C('whatif_selected','bool')], {})
tables['Variance_Weekly'] = ('variance_weekly.csv', [C('store_id','int',n=1,f='0'), C('store_location','text'), C('ingredient_id','text'), C('ingredient_name','text'), C('unit','text'),
 C('week_no','int',n=1,f='0'), C('week_start','date',f='dd/MM/yyyy'), C('days_observed','int',n=1,f='0'), C('opening_qty','num',f='#,0.000'), C('receipt_qty','num',f='#,0.000'),
 C('actual_usage','num',f='#,0.000'), C('closing_qty','num',f='#,0.000'), C('theoretical_usage','num',f='#,0.000'), C('recorded_waste','num',f='#,0.000'), C('unit_cost_usd','num',n=1,f='0.0000'),
 C('opening_value_usd','num',f='#,0.0000'), C('receipt_value_usd','num',f='#,0.0000'), C('closing_value_usd','num',f='#,0.0000'), C('actual_cogs_usd','num',f='#,0.0000'),
 C('waste_qty','num',f='#,0.000'), C('waste_log_value_usd','num',f='#,0.0000'), C('variance_qty','num',f='#,0.000'), C('variance_rate_pct','num',n=1,f='0.00'), C('waste_rate_pct','num',n=1,f='0.00'),
 C('unexplained_shrinkage_qty','num',f='#,0.000'), C('variance_value_usd','num',f='#,0.0000'), C('waste_value_usd','num',f='#,0.0000'), C('unexplained_shrinkage_value_usd','num',f='#,0.0000'),
 C('positive_shrinkage_value_usd','num',f='#,0.0000'), C('priority','text')], {})
tables['WhatIf_Dogs'] = ('whatif_dogs.csv', [C('product_id','int',n=1,f='0'), C('product_detail','text'), C('Q','int',f='#,0'), C('mm_pct','num',n=1,f='0.000'), C('P','num',n=1,f='0.00'),
 C('std_cost','num',n=1,f='0.0000'), C('CM','num',n=1,f='0.0000'), C('total_cm','num',f='#,0.00'), C('class_type','text')], {})

def q(n):
    return n if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', n) else "'" + n.replace("'", "''") + "'"

def table_tmdl(name, csv, cols, opt):
    L = ['table ' + q(name), T+'lineageTag: '+g('t'+name)]
    if opt.get('cat'): L.append(T+'dataCategory: '+opt['cat'])
    L.append('')
    for (n, t, o) in cols:
        L += [T+'column '+q(n), T*2+'dataType: '+DT[t]]
        if o.get('f'): L.append(T*2+'formatString: '+o['f'])
        if o.get('h'): L.append(T*2+'isHidden')
        if o.get('k'): L.append(T*2+'isKey')
        L.append(T*2+'lineageTag: '+g(name+n))
        if o.get('n') or t in ('text','date','datetime','time','bool'): L.append(T*2+'summarizeBy: none')
        L.append(T*2+'sourceColumn: '+n)
        if o.get('s'): L.append(T*2+'sortByColumn: '+o['s'])
        L.append('')
    types = ', '.join('{"%s", %s}' % (n, MT[t]) for (n, t, o) in cols)
    L += [T+'partition '+q(name)+' = m', T*2+'mode: import', T*2+'source =', T*4+'let',
          T*5+'Source = Csv.Document(File.Contents(DataFolder & "\\%s"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),' % csv,
          T*5+'Encabezados = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
          T*5+'Tipos = Table.TransformColumnTypes(Encabezados, {%s}, "en-US")' % types,
          T*4+'in', T*5+'Tipos', '']
    L.append(T+'annotation PBI_ResultType = Table'); L.append('')
    return '\n'.join(L)

def tham_so():
    return '\n'.join([
        'table Tham_so_Popularity', T+'lineageTag: '+g('tTham_so_Popularity'), '',
        T+'column Nhan_nguong', T*2+'dataType: string', T*2+'lineageTag: '+g('tpNhan'), T*2+'summarizeBy: none', T*2+'sourceColumn: Nhan_nguong', T*2+'sortByColumn: He_so', '',
        T+'column He_so', T*2+'dataType: double', T*2+'formatString: 0%', T*2+'isHidden', T*2+'lineageTag: '+g('tpHe'), T*2+'summarizeBy: none', T*2+'sourceColumn: He_so', '',
        T+'partition Tham_so_Popularity = m', T*2+'mode: import', T*2+'source =', T*4+'let',
        T*5+'Source = #table(type table [Nhan_nguong = text, He_so = number], {{"70% / n (ngưỡng chính)", 0.7}, {"100% / n (độ nhạy)", 1}})',
        T*4+'in', T*5+'Source', '', T+'annotation PBI_ResultType = Table', ''])

F1, F2, F3 = '1. Bán hàng và giá vốn', '2. Tồn kho và hao hụt', '3. Menu Engineering'
USD0, USD2, PCT, INT = r'\$#,0', r'\$#,0.00', '0.00%', '#,0'
IA = 'Fact_Inventory_Audit'
M = [
 ('Doanh thu', 'SUM(Fact_Sales[revenue])', USD0, F1),
 ('Số ly bán', 'SUM(Fact_Sales[transaction_qty])', INT, F1),
 ('Số dòng giao dịch', 'COUNTROWS(Fact_Sales)', INT, F1),
 ('Tổng giá vốn định mức', 'SUM(Fact_Sales[total_std_cost])', USD0, F1),
 ('Tổng CM', 'SUM(Fact_Sales[total_cm])', USD0, F1),
 ('CM mỗi ly', 'DIVIDE([Tổng CM], [Số ly bán])', USD2, F1),
 ('Food Cost % lý thuyết', 'DIVIDE([Tổng giá vốn định mức], [Doanh thu])', PCT, F1),
 ('Giá vốn thực tế (Actual COGS)', f'SUM({IA}[actual_cogs_usd])', USD0, F1),
 ('Food Cost % thực tế', 'DIVIDE([Giá vốn thực tế (Actual COGS)], [Doanh thu])', PCT, F1),
 ('Lợi nhuận gộp thực tế', '[Doanh thu] - [Giá vốn thực tế (Actual COGS)]', USD0, F1),
 ('Food Cost % lý thuyết (phạm vi kiểm kê)', 'DIVIDE([Tiêu hao lý thuyết (USD)], [Doanh thu])', PCT, F1),
 ('Cost Variance (điểm %)', '([Food Cost % thực tế] - [Food Cost % lý thuyết (phạm vi kiểm kê)]) * 100', '0.00', F1),
 ('Tỷ trọng doanh thu', 'DIVIDE([Doanh thu], CALCULATE([Doanh thu], ALLSELECTED()))', PCT, F1),
 ('Tiêu hao lý thuyết (USD)', f'SUMX({IA}, {IA}[theoretical_usage] * {IA}[unit_cost_usd])', USD0, F2),
 ('Tiêu hao thực tế (USD)', f'SUMX({IA}, {IA}[actual_usage] * {IA}[unit_cost_usd])', USD0, F2),
 ('Variance (USD)', '[Tiêu hao thực tế (USD)] - [Tiêu hao lý thuyết (USD)]', USD0, F2),
 ('Variance Rate %', 'DIVIDE([Variance (USD)], [Tiêu hao lý thuyết (USD)])', PCT, F2),
 ('Hao hụt ghi nhận (USD)', f'SUMX({IA}, {IA}[recorded_waste] * {IA}[unit_cost_usd])', USD0, F2),
 ('Waste Rate %', 'DIVIDE([Hao hụt ghi nhận (USD)], [Tiêu hao thực tế (USD)])', PCT, F2),
 ('Unexplained Shrinkage (USD)', '[Variance (USD)] - [Hao hụt ghi nhận (USD)]', USD0, F2),
 ('Unexplained Shrinkage dương (USD)', f'SUMX({IA}, MAX(0, ({IA}[actual_usage] - {IA}[theoretical_usage] - {IA}[recorded_waste]) * {IA}[unit_cost_usd]))', USD0, F2),
 ('Tỷ lệ chênh lệch được giải thích', 'DIVIDE([Hao hụt ghi nhận (USD)], [Variance (USD)])', PCT, F2),
 ('Tiêu hao lý thuyết (lượng)', f'SUM({IA}[theoretical_usage])', '#,0.0', F2),
 ('Tiêu hao thực tế (lượng)', f'SUM({IA}[actual_usage])', '#,0.0', F2),
 ('Giá trị hủy theo phiếu (USD)', 'SUM(Fact_Waste_Log[waste_value_usd])', USD0, F2),
 ('Số phiếu hủy', 'COUNTROWS(Fact_Waste_Log)', INT, F2),
 ('Hệ số ngưỡng Popularity', 'SELECTEDVALUE(Tham_so_Popularity[He_so], 1)', '0%', F3),
 ('Số món (n)', 'CALCULATE(COUNTROWS(Dim_Menu_Item), ALLSELECTED(Dim_Menu_Item))', INT, F3),
 ('Menu Mix %', 'DIVIDE([Số ly bán], CALCULATE([Số ly bán], ALLSELECTED(Dim_Menu_Item)))', PCT, F3),
 ('Ngưỡng Popularity', 'DIVIDE([Hệ số ngưỡng Popularity], [Số món (n)])', PCT, F3),
 ('CM bình quân có trọng số', 'DIVIDE(CALCULATE([Tổng CM], ALLSELECTED(Dim_Menu_Item)), CALCULATE([Số ly bán], ALLSELECTED(Dim_Menu_Item)))', USD2, F3),
 ('Phân loại món', 'IF(\n\tISBLANK([Số ly bán]),\n\tBLANK(),\n\tVAR _pop = [Menu Mix %] >= [Ngưỡng Popularity]\n\tVAR _prof = [CM mỗi ly] >= [CM bình quân có trọng số]\n\tRETURN SWITCH(TRUE(), _pop && _prof, "Stars", _pop, "Plowhorses", _prof, "Puzzles", "Dogs")\n)', None, F3),
]
for cls in ('Stars', 'Plowhorses', 'Puzzles', 'Dogs'):
    M.append((f'Số món {cls}', f'COUNTROWS(FILTER(VALUES(Dim_Menu_Item[product_detail]), [Phân loại món] = "{cls}"))', INT, F3))

def measures_tmdl():
    L = ['table _Measures', T+'lineageTag: '+g('t_Measures'), '']
    for (n, dax, fmt, folder) in M:
        if '\n' in dax:
            L.append(T+'measure '+q(n)+' =')
            L += [T*3+ln for ln in dax.split('\n')]
        else: L.append(T+'measure '+q(n)+' = '+dax)
        if fmt: L.append(T*2+'formatString: '+fmt)
        L.append(T*2+'displayFolder: '+folder); L.append(T*2+'lineageTag: '+g('m'+n)); L.append('')
    L += [T+'column Ghi_chu', T*2+'dataType: string', T*2+'isHidden', T*2+'lineageTag: '+g('mGhi'), T*2+'summarizeBy: none', T*2+'sourceColumn: Ghi_chu', '',
          T+'partition _Measures = m', T*2+'mode: import', T*2+'source =', T*4+'let', T*5+'Source = #table(type table [Ghi_chu = text], {})', T*4+'in', T*5+'Source', '',
          T+'annotation PBI_ResultType = Table', '']
    return '\n'.join(L)

R = [('Fact_Sales','date_key','Dim_Date','date_key'), ('Fact_Sales','store_key','Dim_Store','store_key'), ('Fact_Sales','shift_key','Dim_Shift','shift_key'),
     ('Fact_Sales','menu_item_key','Dim_Menu_Item','menu_item_key'),
     ('Fact_Inventory_Audit','store_key','Dim_Store','store_key'), ('Fact_Inventory_Audit','ingredient_key','Dim_Ingredient','ingredient_key'),
     ('Fact_Inventory_Audit','week_start_date_key','Dim_Date','date_key'),
     ('Fact_Waste_Log','date_key','Dim_Date','date_key'), ('Fact_Waste_Log','store_key','Dim_Store','store_key'), ('Fact_Waste_Log','shift_key','Dim_Shift','shift_key'),
     ('Fact_Waste_Log','ingredient_key','Dim_Ingredient','ingredient_key'),
     ('Bridge_BOM','menu_item_key','Dim_Menu_Item','menu_item_key'), ('Bridge_BOM','ingredient_key','Dim_Ingredient','ingredient_key'),
     ('Menu_Matrix','product_id','Dim_Menu_Item','product_id'),
     ('Variance_Weekly','store_id','Dim_Store','store_id'), ('Variance_Weekly','ingredient_id','Dim_Ingredient','ingredient_id'),
     ('WhatIf_Dogs','product_id','Dim_Menu_Item','product_id')]
rel = []
for (a, ac, b, bc) in R:
    rel += ['relationship '+g('r'+a+ac+b+bc), T+'fromColumn: '+a+'.'+ac, T+'toColumn: '+b+'.'+bc, '']

if __name__ == '__main__':
    w(PROJ+'/coffee_bi_model.pbip', json.dumps({"version":"1.0","artifacts":[{"report":{"path":"coffee_bi_model.Report"}}],"settings":{"enableAutoRecovery":True}}, indent=2))
    w(SM+'/definition.pbism', json.dumps({"version":"4.2","settings":{}}, indent=2))
    w(SM+'/definition/database.tmdl', 'database\n\tcompatibilityLevel: 1601\n')
    names = list(tables) + ['Tham_so_Popularity', '_Measures']
    mdl = ['model Model', T+'culture: en-US', T+'defaultPowerBIDataSourceVersion: powerBI_V3', T+'sourceQueryCulture: en-US', T+'dataAccessOptions', T*2+'legacyRedirects', T*2+'returnErrorValuesAsNull', '']
    mdl += ['ref table '+q(n) for n in names] + ['ref expression DataFolder', 'ref cultureInfo en-US', '']
    w(SM+'/definition/model.tmdl', '\n'.join(mdl))
    w(SM+'/definition/expressions.tmdl', 'expression DataFolder = "%s" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n\tlineageTag: %s\n\n\tannotation PBI_ResultType = Text\n' % (WIN_DATA, g('DataFolder')))
    w(SM+'/definition/cultures/en-US.tmdl', 'cultureInfo en-US\n')
    for n, (csv, cols, opt) in tables.items(): w(SM+'/definition/tables/'+n+'.tmdl', table_tmdl(n, csv, cols, opt))
    w(SM+'/definition/tables/Tham_so_Popularity.tmdl', tham_so())
    w(SM+'/definition/tables/_Measures.tmdl', measures_tmdl())
    w(SM+'/definition/relationships.tmdl', '\n'.join(rel))
    print('semantic model written;', len(M), 'measures;', len(R), 'relationships')
