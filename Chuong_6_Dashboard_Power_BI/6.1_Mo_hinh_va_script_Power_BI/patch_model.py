# -*- coding: utf-8 -*-
# Bổ sung vào mô hình đã có: bảng What-If, cột chi phí sữa, measure mới. Chạy nhiều lần vẫn an toàn.
import os, re, uuid
BASE = os.path.expanduser('~/mnt/BI_K24406H_Kỳ7-20261116T011316Z-1-001/BI_K24406H_Kỳ7/powerbi')
D = BASE + '/coffee_bi_model/coffee_bi_model.SemanticModel/definition'
NS = uuid.UUID('6f1f0a52-0c0d-4c34-9a55-6b1d7a0e2f11')
def g(x): return str(uuid.uuid5(NS, x))
T = '\t'
def rd(p): return open(p, encoding='utf-8').read()
def wr(p, s):
    with open(p, 'w', encoding='utf-8', newline='\n') as f: f.write(s)

# 1) cột chi phí sữa trên Dim_Menu_Item
p = D + '/tables/Dim_Menu_Item.tmdl'
s = rd(p)
if 'milk_cost_unit' not in s:
    col = ('\tcolumn milk_cost_unit =\n'
           '\t\t\tCALCULATE(SUMX(Bridge_BOM, IF(RELATED(Dim_Ingredient[ingredient_name]) = "Fresh Milk", Bridge_BOM[line_cost_usd], 0)))\n'
           '\t\tdataType: double\n\t\tisHidden\n\t\tformatString: 0.0000\n\t\tlineageTag: ' + g('col_milk_cost_unit') + '\n\t\tsummarizeBy: none\n\n'
           '\t\tannotation SummarizationSetBy = Automatic\n\n')
    s = s.replace('\tpartition Dim_Menu_Item', col + '\tpartition Dim_Menu_Item', 1)
    wr(p, s)

# 2) bảng tham số What-If
def param_table(tname, colname, rng, fmt):
    return '\n'.join([
        'table ' + tname, T + 'lineageTag: ' + g('t' + tname), '',
        T + 'column ' + colname, T * 2 + 'dataType: double', T * 2 + 'formatString: ' + fmt, T * 2 + 'lineageTag: ' + g(tname + colname),
        T * 2 + 'summarizeBy: none', T * 2 + 'sourceColumn: [Value]', '',
        T * 2 + 'annotation SummarizationSetBy = Automatic', '',
        T + 'partition ' + tname + ' = calculated', T * 2 + 'mode: import', T * 2 + 'source = GENERATESERIES(' + rng + ')', '',
        T + 'annotation PBI_Id = ' + g('id' + tname).replace('-', ''), ''])
PT = [('What_if_Gia_ban', 'Thay đổi giá bán', '-0.2, 0.2, 0.01', '0%'),
      ('What_if_Gia_sua', 'Thay đổi giá sữa', '-0.2, 0.5, 0.05', '0%'),
      ('What_if_Co_gian', 'Độ co giãn cầu', '-2, 0, 0.25', '0.00')]
for (tn, cn, rng, fmt) in PT:
    wr(D + '/tables/' + tn + '.tmdl', param_table(tn, "'" + cn + "'", rng, fmt))

# 3) khai báo bảng trong model.tmdl
p = D + '/model.tmdl'
s = rd(p)
for (tn, *_r) in PT:
    if 'ref table ' + tn not in s:
        s = s.replace('ref cultureInfo en-US', 'ref table ' + tn + '\n\nref cultureInfo en-US', 1)
wr(p, re.sub(r'\n\n(ref table What_if)', r'\n\1', s))

# 4) measure mới
F1, F2, F3, F4 = '1. Bán hàng và giá vốn', '2. Tồn kho và hao hụt', '3. Menu Engineering', '4. What-If giá bán và giá sữa'
USD0, USD2, PCT, INT = r'\$#,0', r'\$#,0.00', '0.00%', '#,0'
IA = 'Fact_Inventory_Audit'
CLS = lambda mix, cm, thr, wcm: ('IF(\n\tISBLANK([Số ly bán]),\n\tBLANK(),\n\tVAR _pop = %s >= [Ngưỡng Popularity]\n\tVAR _prof = %s >= %s\n'
                                 '\tRETURN SWITCH(TRUE(), _pop && _prof, "Stars", _pop, "Plowhorses", _prof, "Puzzles", "Dogs")\n)' % (mix, cm, wcm))
NEW = [
 # D1
 ('Doanh thu tháng trước', 'CALCULATE([Doanh thu], DATEADD(Dim_Date[full_date], -1, MONTH))', USD0, F1),
 ('Doanh thu MoM %', 'DIVIDE([Doanh thu] - [Doanh thu tháng trước], [Doanh thu tháng trước])', '+0.0%;-0.0%;0.0%', F1),
 ('Biên lợi nhuận gộp thực tế %', 'DIVIDE([Lợi nhuận gộp thực tế], [Doanh thu])', PCT, F1),
 # D2
 ('Menu Mix (%)', '[Menu Mix %] * 100', '0.00', F3),
 ('Ngưỡng Popularity (%)', '[Ngưỡng Popularity] * 100', '0.00', F3),
 ('Giá bán TB (P)', 'DIVIDE([Doanh thu], [Số ly bán])', USD2, F3),
 ('Màu phân loại', 'SWITCH([Phân loại món], "Stars", "#3F8F7B", "Plowhorses", "#C9A27A", "Puzzles", "#5B7DB1", "Dogs", "#C0504D", BLANK())', None, F3),
 # What-If
 ('WI Δ giá bán', "SELECTEDVALUE(What_if_Gia_ban[Thay đổi giá bán], 0)", '0%', F4),
 ('WI Δ giá sữa', "SELECTEDVALUE(What_if_Gia_sua[Thay đổi giá sữa], 0)", '0%', F4),
 ('WI Độ co giãn cầu', "SELECTEDVALUE(What_if_Co_gian[Độ co giãn cầu], 0)", '0.00', F4),
 ('WI Hệ số sản lượng', 'MAX(0, 1 + [WI Độ co giãn cầu] * [WI Δ giá bán])', '0.000', F4),
 ('Giá vốn sữa (định mức)', 'SUMX(Fact_Sales, Fact_Sales[transaction_qty] * RELATED(Dim_Menu_Item[milk_cost_unit]))', USD0, F4),
 ('Số ly bán (What-If)', '[Số ly bán] * [WI Hệ số sản lượng]', INT, F4),
 ('Doanh thu (What-If)', '[Doanh thu] * (1 + [WI Δ giá bán]) * [WI Hệ số sản lượng]', USD0, F4),
 ('Giá vốn định mức (What-If)', '([Tổng giá vốn định mức] + [Giá vốn sữa (định mức)] * [WI Δ giá sữa]) * [WI Hệ số sản lượng]', USD0, F4),
 ('Tổng CM (What-If)', '[Doanh thu (What-If)] - [Giá vốn định mức (What-If)]', USD0, F4),
 ('Thay đổi Tổng CM (USD)', '[Tổng CM (What-If)] - [Tổng CM]', '+\\$#,0;-\\$#,0;\\$0', F4),
 ('Thay đổi Tổng CM (%)', 'DIVIDE([Tổng CM (What-If)] - [Tổng CM], [Tổng CM])', '+0.00%;-0.00%;0.00%', F4),
 ('Food Cost % (What-If)', 'DIVIDE([Giá vốn định mức (What-If)], [Doanh thu (What-If)])', PCT, F4),
 ('CM mỗi ly (What-If)', 'DIVIDE([Tổng CM (What-If)], [Số ly bán (What-If)])', USD2, F4),
 ('Menu Mix % (What-If)', 'DIVIDE([Số ly bán (What-If)], CALCULATE([Số ly bán (What-If)], ALLSELECTED(Dim_Menu_Item)))', PCT, F4),
 ('CM bình quân có trọng số (What-If)', 'DIVIDE(CALCULATE([Tổng CM (What-If)], ALLSELECTED(Dim_Menu_Item)), CALCULATE([Số ly bán (What-If)], ALLSELECTED(Dim_Menu_Item)))', USD2, F4),
 ('Phân loại món (What-If)', CLS('[Menu Mix % (What-If)]', '[CM mỗi ly (What-If)]', '', '[CM bình quân có trọng số (What-If)]'), None, F4),
 # D3
 ('Ngưỡng VR cảnh báo', '0.05', '0%', F2),
 ('Ngưỡng VR ưu tiên', '0.08', '0%', F2),
 ('Ngưỡng Waste Rate', '0.04', '0%', F2),
 ('Mức cảnh báo', 'IF([Unexplained Shrinkage (USD)] <= 0 || ISBLANK([Variance Rate %]), "Bình thường", IF([Variance Rate %] >= [Ngưỡng VR ưu tiên], "Ưu tiên kiểm tra", IF([Variance Rate %] >= [Ngưỡng VR cảnh báo], "Cảnh báo", "Bình thường")))', None, F2),
 ('Số cảnh báo (cửa hàng × NVL × tuần)', f'COUNTROWS(FILTER(SUMMARIZE({IA}, Dim_Store[store_location], Dim_Ingredient[ingredient_name], Dim_Date[week_no]), [Mức cảnh báo] <> "Bình thường"))', INT, F2),
 ('Pareto lũy kế %', 'VAR _cur = [Unexplained Shrinkage dương (USD)]\nVAR _all = ALLSELECTED(Dim_Ingredient[ingredient_name])\nVAR _tot = SUMX(_all, [Unexplained Shrinkage dương (USD)])\nRETURN IF(ISBLANK(_cur) || _cur = 0, BLANK(), DIVIDE(SUMX(FILTER(_all, [Unexplained Shrinkage dương (USD)] >= _cur), [Unexplained Shrinkage dương (USD)]), _tot))', '0%', F2),
 ('Tồn kho bình quân (USD)', f'SUMX(SUMMARIZE({IA}, {IA}[store_key], {IA}[ingredient_key]), CALCULATE(AVERAGEX({IA}, ({IA}[opening_value_usd] + {IA}[closing_value_usd]) / 2)))', USD0, F2),
 ('Inventory Turnover Ratio (ITR)', 'DIVIDE([Giá vốn thực tế (Actual COGS)], [Tồn kho bình quân (USD)])', '0.00', F2),
 ('Số ngày quan sát', f'DIVIDE(SUM({IA}[days_observed]), COUNTROWS(SUMMARIZE({IA}, {IA}[store_key], {IA}[ingredient_key])))', '0', F2),
 ('Days Inventory Outstanding (DIO)', 'DIVIDE([Số ngày quan sát], [Inventory Turnover Ratio (ITR)])', '0.0', F2),
]

def meas(n, dax, fmt, folder):
    q = n if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', n) else "'" + n.replace("'", "''") + "'"
    L = []
    if '\n' in dax:
        L.append(T + 'measure ' + q + ' =')
        L += [T * 3 + ln for ln in dax.split('\n')]
    else: L.append(T + 'measure ' + q + ' = ' + dax)
    if fmt: L.append(T * 2 + 'formatString: ' + fmt)
    L += [T * 2 + 'displayFolder: ' + folder, T * 2 + 'lineageTag: ' + g('m' + n), '']
    return '\n'.join(L) + '\n'

p = D + '/tables/_Measures.tmdl'
s = rd(p)
add = ''
for (n, dax, fmt, folder) in NEW:
    key = "measure '" + n + "'"
    key2 = 'measure ' + n + ' ='
    if key in s or key2 in s: continue
    add += meas(n, dax, fmt, folder)
if add:
    s = s.replace('\tcolumn Ghi_chu', add + '\tcolumn Ghi_chu', 1)
    wr(p, s)
print('ok; measures added:', add.count('\tmeasure '))
