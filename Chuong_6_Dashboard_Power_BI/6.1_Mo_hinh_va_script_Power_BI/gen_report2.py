# -*- coding: utf-8 -*-
# Dashboard Coffee BI v2: D1 điều hành, D2 Menu Engineering + What-If, D3 hao hụt và thất thoát.
import os, json, shutil, hashlib
BASE = os.path.expanduser('~/mnt/BI_K24406H_Kỳ7-20261116T011316Z-1-001/BI_K24406H_Kỳ7/powerbi')
PROJ = os.path.join(BASE, 'coffee_bi_model')
RP = os.path.join(PROJ, 'coffee_bi_model.Report')
SCH = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/'

def wj(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f: json.dump(obj, f, ensure_ascii=False, indent=2)

def hid(s): return hashlib.md5(s.encode()).hexdigest()[:20]
def lit(v): return {"expr": {"Literal": {"Value": v}}}
def S(s): return lit("'" + s + "'")
def N(n): return lit(str(n) + 'D')
def B(b): return lit('true' if b else 'false')
def COLOR(c): return {"solid": {"color": S(c)}}

BROWN, ACC, TAN, GREEN, RED, BLUE, BG, CARD, LINE = '#503524', '#8C5A3C', '#C9A27A', '#3F8F7B', '#C0504D', '#5B7DB1', '#F7F4EF', '#F3E7DA', '#E4D6C6'
OKBG, BADBG, WARNBG, BLUEBG = '#DDEFEA', '#F6DDD9', '#FBEBC8', '#E3EAF6'

def col(t, c): return {"Column": {"Expression": {"SourceRef": {"Entity": t}}, "Property": c}}
def msr(m): return {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": m}}
def agg(t, c, fn): return {"Aggregation": {"Expression": col(t, c), "Function": fn}}
def P(field, ref, native, **kw):
    d = {"field": field, "queryRef": ref, "nativeQueryRef": native}; d.update(kw); return d
def pc(t, c): return P(col(t, c), f"{t}.{c}", c)
def pm(m): return P(msr(m), f"_Measures.{m}", m)
def pa(t, c, fn=0, disp=None):
    nm = {0: 'Sum', 1: 'Average', 4: 'Count'}[fn]
    kw = {"displayName": disp} if disp else {}
    return P(agg(t, c, fn), f"{nm}({t}.{c})", f"{nm} of {c}", **kw)

def vco(title=None, bg='#FFFFFF', border=True):
    o = {"background": [{"properties": {"show": B(True), "color": COLOR(bg), "transparency": N(0)}}]}
    if border: o["border"] = [{"properties": {"show": B(True), "color": COLOR(LINE), "radius": N(8)}}]
    o["subTitle"] = [{"properties": {"show": B(False)}}]
    if title: o["title"] = [{"properties": {"show": B(True), "text": S(title), "fontSize": N(11), "fontColor": COLOR(BROWN), "bold": B(True)}}]
    else: o["title"] = [{"properties": {"show": B(False)}}]
    return o

def vis(page, key, x, y, w, h, vtype, query=None, objects=None, container=None, filters=None, sort=None, sort_dir='Descending'):
    name = hid(page + key)
    v = {"$schema": SCH + "visualContainer/2.14.0/schema.json", "name": name,
         "position": {"x": x, "y": y, "z": 0, "height": h, "width": w, "tabOrder": 0},
         "visual": {"visualType": vtype}}
    if query:
        v["visual"]["query"] = {"queryState": query}
        if sort: v["visual"]["query"]["sortDefinition"] = {"sort": [{"field": msr(sort), "direction": sort_dir}]}
    if objects: v["visual"]["objects"] = objects
    if container: v["visual"]["visualContainerObjects"] = container
    v["visual"]["drillFilterOtherVisuals"] = True
    if filters: v["filterConfig"] = {"filters": filters}
    return name, v

def in_filter(tbl, c, values, negate=False, nm='f1'):
    cond = {"In": {"Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": c}}],
                   "Values": [[{"Literal": {"Value": "'" + v + "'"}}] for v in values]}}
    if negate: cond = {"Not": {"Expression": cond}}
    return {"name": nm, "field": col(tbl, c), "type": "Categorical",
            "filter": {"Version": 2, "From": [{"Name": "t", "Entity": tbl, "Type": 0}], "Where": [{"Condition": cond}]}}

def textbox(text, size, bold=True, color=BROWN, align='left'):
    return {"general": [{"properties": {"paragraphs": [{"textRuns": [{"value": text, "textStyle": {"fontWeight": "bold" if bold else "normal", "fontSize": f"{size}pt", "color": color}}], "horizontalTextAlignment": align}]}}]}

def card(page, key, x, y, w, h, m, fill=CARD, fs=22):
    return vis(page, key, x, y, w, h, 'cardVisual', {"Data": {"projections": [pm(m)]}},
               {"value": [{"properties": {"fontSize": N(fs), "labelDisplayUnits": N(1)}, "selector": {"id": "default"}}], "label": [{"properties": {"fontSize": N(10)}, "selector": {"id": "default"}}]},
               vco(None, fill))

def slicer(page, key, x, y, w, h, t, c, title, mode='Dropdown', single=False, filters=None):
    obj = {"data": [{"properties": {"mode": S(mode)}}], "header": [{"properties": {"show": B(False)}}]}
    if single: obj["selection"] = [{"properties": {"singleSelect": B(True), "selectAllCheckboxEnabled": B(False)}}]
    return vis(page, key, x, y, w, h, 'slicer', {"Values": {"projections": [pc(t, c)]}}, obj, vco(title, '#FFFFFF'), filters)

def nav(page, key, x, y, label, target, active):
    o = {"text": [{"properties": {"show": B(True), "text": S(label), "fontSize": N(11), "bold": B(True), "fontColor": COLOR('#FFFFFF' if active else BROWN)}, "selector": {"id": "default"}}, {"properties": {"show": B(True)}}],
         "fill": [{"properties": {"show": B(True), "fillColor": COLOR(ACC if active else CARD)}, "selector": {"id": "default"}}],
         "icon": [{"properties": {"shapeType": S('blank')}, "selector": {"id": "default"}}],
         "outline": [{"properties": {"show": B(False)}, "selector": {"id": "default"}}]}
    c = {"visualLink": [{"properties": {"show": B(True), "type": S('PageNavigation'), "navigationSection": S(target)}}],
         "title": [{"properties": {"show": B(False)}}]}
    return vis(page, key, x, y, 44, 30, 'actionButton', None, o, c)

def heat(measure, mx, fs=None):
    o = {"values": [{"properties": {"backColor": {"solid": {"color": {"expr": {"FillRule": {"Input": msr(measure),
        "FillRule": {"linearGradient2": {"min": {"color": {"Literal": {"Value": "'#FFFFFF'"}}}, "max": {"color": {"Literal": {"Value": f"'{mx}'"}}},
                     "nullColoringStrategy": {"strategy": {"Literal": {"Value": "'noColor'"}}}}}}}}}}},
        "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}], "metadata": f"_Measures.{measure}"}}]}
    if fs:
        o["values"].insert(0, {"properties": {"fontSize": N(fs)}})
        o["columnHeaders"] = [{"properties": {"fontSize": N(fs)}}]
        o["rowHeaders"] = [{"properties": {"fontSize": N(fs)}}]
    return o

def cases(left, rules, prop):
    """rules: [(kind, literal, color)] kind 0 '=',1 '>',2 '>=' ; trả về object định dạng có điều kiện."""
    cs = [{"Condition": {"Comparison": {"ComparisonKind": k, "Left": left, "Right": {"Literal": {"Value": lv}}}},
           "Value": {"Literal": {"Value": "'" + c + "'"}}} for (k, lv, c) in rules]
    return {prop: {"solid": {"color": {"expr": {"Conditional": {"Cases": cs}}}}}}

def cf(selector, left, rules, prop):
    return {"properties": cases(left, rules, prop), "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}], "metadata": selector}}

CLSRULES = [(0, "'Stars'", GREEN), (0, "'Plowhorses'", '#A9743F'), (0, "'Puzzles'", BLUE), (0, "'Dogs'", RED)]

PID = {k: hid('page' + k) for k in ('D1', 'D2', 'D3')}
TITLES = {'D1': 'D1 · Tổng quan điều hành', 'D2': 'D2 · Menu Engineering và What-If', 'D3': 'D3 · Hao hụt và thất thoát'}
SUBS = {'D1': '41 đồ uống · 3 cửa hàng · 01/01/2023 đến 30/06/2023. Giá vốn thực tế lấy từ kiểm kê tuần, nên so sánh với lý thuyết theo cửa hàng và theo tuần.',
        'D2': 'Popularity: Menu Mix % so với hệ số/n. Profitability: CM mỗi ly so với CM bình quân có trọng số. Khu What-If đổi giá bán, giá sữa, độ co giãn cầu.',
        'D3': 'Variance = (AU − TU) × giá mua. Unexplained = Variance − hao hụt ghi nhận. Cảnh báo từ Variance Rate 5%, ưu tiên từ 8%.'}

def header(p):
    v = [vis(p, 'title', 20, 6, 440, 40, 'textbox', None, textbox(TITLES[p], 20), None),
         vis(p, 'sub', 20, 44, 590, 34, 'textbox', None, textbox(SUBS[p], 8, False, ACC), None)]
    for i, k in enumerate(('D1', 'D2', 'D3')):
        v.append(nav(p, 'nav' + k, 468 + i * 50, 12, k, PID[k], k == p))
    return v

NO_DEC = lambda: [in_filter('Dim_Date', 'month_name', ['December'], negate=True, nm='fmonth')]
pages = []

# ===================== D1 =====================
p = 'D1'
v = header(p)
v.append(slicer(p, 's_store', 625, 6, 200, 66, 'Dim_Store', 'store_location', 'Cửa hàng'))
v.append(slicer(p, 's_shift', 835, 6, 200, 66, 'Dim_Shift', 'shift_name', 'Ca'))
v.append(slicer(p, 's_month', 1045, 6, 205, 66, 'Dim_Date', 'month_name', 'Tháng', filters=NO_DEC()))
D1C = [('Doanh thu', CARD), ('Số ly bán', CARD), ('Tổng CM', OKBG), ('Lợi nhuận gộp thực tế', OKBG), ('Food Cost % lý thuyết', CARD), ('Food Cost % thực tế', CARD), ('Cost Variance (điểm %)', BADBG), ('Waste Rate %', WARNBG)]
for i, (m, f) in enumerate(D1C):
    v.append(card(p, 'c%d' % i, 20 + i * 154, 84, 146, 88, m, f, 20))
v.append(vis(p, 'line', 20, 184, 400, 250, 'lineChart', {"Category": {"projections": [pc('Dim_Date', 'month_name')]}, "Y": {"projections": [pm('Doanh thu')]}, "Series": {"projections": [pc('Dim_Store', 'store_location')]}},
             None, vco('Doanh thu theo tháng × cửa hàng'), NO_DEC()))
v.append(vis(p, 'fcweek', 430, 184, 400, 250, 'lineChart', {"Category": {"projections": [pc('Dim_Date', 'week_no')]}, "Y": {"projections": [pm('Food Cost % thực tế'), pm('Food Cost % lý thuyết (phạm vi kiểm kê)')]}},
             {"legend": [{"properties": {"show": B(True), "position": S('Bottom')}}]}, vco('Food Cost % thực tế và lý thuyết theo tuần')))
v.append(vis(p, 'heat', 840, 184, 410, 250, 'pivotTable', {"Rows": {"projections": [pc('Fact_Sales', 'hour')]}, "Columns": {"projections": [pc('Dim_Date', 'day_name')]}, "Values": {"projections": [pm('Số dòng giao dịch')]}},
             heat('Số dòng giao dịch', ACC, 8), vco('Số dòng giao dịch theo giờ × thứ trong tuần')))
v.append(vis(p, 'cat', 20, 446, 290, 262, 'clusteredColumnChart', {"Category": {"projections": [pc('Dim_Menu_Item', 'product_category')]}, "Y": {"projections": [pm('Doanh thu')]}},
             None, vco('Doanh thu theo nhóm sản phẩm'), sort='Doanh thu'))
v.append(vis(p, 'tbl', 320, 446, 400, 262, 'tableEx', {"Values": {"projections": [pc('Dim_Store', 'store_location'), pm('Doanh thu'), pm('Tổng CM'), pm('Food Cost % lý thuyết'), pm('Food Cost % thực tế')]}},
             None, vco('So sánh cửa hàng'), sort='Doanh thu'))
v.append(vis(p, 'mtbl', 730, 446, 330, 262, 'tableEx', {"Values": {"projections": [pc('Dim_Date', 'month_name'), pm('Doanh thu'), pm('Doanh thu MoM %'), pm('Tổng CM')]}},
             None, vco('Theo tháng và tăng trưởng so tháng trước'), NO_DEC()))
v.append(vis(p, 'donut', 1070, 446, 180, 262, 'donutChart', {"Category": {"projections": [pc('Dim_Shift', 'shift_name')]}, "Y": {"projections": [pm('Doanh thu')]}},
             {"legend": [{"properties": {"position": S('Bottom')}}]}, vco('Theo ca')))
pages.append((p, 'D1 Tổng quan điều hành', v))

# ===================== D2 =====================
p = 'D2'
v = header(p)
v.append(slicer(p, 's_store', 625, 6, 150, 66, 'Dim_Store', 'store_location', 'Cửa hàng'))
v.append(slicer(p, 's_cat', 783, 6, 150, 66, 'Dim_Menu_Item', 'product_category', 'Nhóm món'))
v.append(slicer(p, 's_month', 941, 6, 150, 66, 'Dim_Date', 'month_name', 'Tháng', filters=NO_DEC()))
v.append(slicer(p, 's_thr', 1099, 6, 151, 66, 'Tham_so_Popularity', 'Nhan_nguong', 'Ngưỡng Popularity'))
D2C = [('Số món Stars', OKBG), ('Số món Plowhorses', WARNBG), ('Số món Puzzles', BLUEBG), ('Số món Dogs', BADBG), ('Ngưỡng Popularity', CARD), ('CM bình quân có trọng số', CARD), ('Tổng CM', CARD), ('Food Cost % lý thuyết', CARD)]
for i, (m, f) in enumerate(D2C):
    v.append(card(p, 'c%d' % i, 20 + i * 154, 84, 146, 88, m, f, 20))
ref = lambda mname, color, label: [{"properties": {"show": B(True), "value": {"expr": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": mname}}},
                                    "lineColor": COLOR(color), "style": S('dashed'), "transparency": N(0), "displayName": S(label), "dataLabelShow": B(True)}, "selector": {"id": "1"}}]
scatter_obj = {"dataPoint": [{"properties": {"fill": {"solid": {"color": {"expr": msr('Màu phân loại')}}}}, "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}}],
               "y1AxisReferenceLine": ref('CM bình quân có trọng số', ACC, 'CM bình quân'),
               "xAxisReferenceLine": ref('Ngưỡng Popularity (%)', ACC, 'Ngưỡng Popularity'),
               "categoryAxis": [{"properties": {"showAxisTitle": B(True), "titleText": S('Menu Mix (%)')}}],
               "valueAxis": [{"properties": {"showAxisTitle": B(True), "titleText": S('CM mỗi ly (USD)')}}]}
v.append(vis(p, 'scatter', 20, 184, 560, 290, 'scatterChart', {"Category": {"projections": [pc('Dim_Menu_Item', 'product_detail')]},
             "X": {"projections": [pm('Menu Mix (%)')]}, "Y": {"projections": [pm('CM mỗi ly')]}, "Size": {"projections": [pm('Tổng CM')]},
             "Tooltips": {"projections": [pm('Số ly bán'), pm('Giá bán TB (P)'), pm('CM mỗi ly'), pm('Tổng CM'), pm('Phân loại món')]}},
             scatter_obj, vco('Ma trận 4 góc: Menu Mix % × CM mỗi ly (màu theo nhóm: xanh Stars, nâu Plowhorses, xanh dương Puzzles, đỏ Dogs)'), NO_DEC()))
v.append(vis(p, 'bystore', 590, 184, 330, 290, 'clusteredColumnChart', {"Category": {"projections": [pc('Dim_Store', 'store_location')]},
             "Y": {"projections": [pm('Số món Stars'), pm('Số món Plowhorses'), pm('Số món Puzzles'), pm('Số món Dogs')]}},
             {"legend": [{"properties": {"show": B(True), "position": S('Bottom')}}], "dataPoint": []}, vco('Số món theo nhóm tại từng cửa hàng')))
# khu What-If
v.append(vis(p, 'wi_title', 932, 184, 318, 26, 'textbox', None, textbox('Khu What-If: giá bán và giá sữa', 11), vco(None, '#FFFFFF', False)))
v.append(slicer(p, 'wi_price', 932, 210, 318, 64, 'What_if_Gia_ban', 'Thay đổi giá bán', 'Thay đổi giá bán (%)', single=True))
v.append(slicer(p, 'wi_milk', 932, 274, 318, 64, 'What_if_Gia_sua', 'Thay đổi giá sữa', 'Thay đổi giá sữa tươi (%)', single=True))
v.append(slicer(p, 'wi_elas', 932, 338, 318, 64, 'What_if_Co_gian', 'Độ co giãn cầu', 'Độ co giãn cầu (0 = không đổi)', single=True))
for i, (m, f) in enumerate([('Tổng CM (What-If)', OKBG), ('Thay đổi Tổng CM (%)', WARNBG)]):
    v.append(card(p, 'wc%d' % i, 932 + i * 162, 406, 156, 68, m, f, 20))
mname = lambda m: {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": m}}
tbl_obj = {"values": [cf('_Measures.Phân loại món', mname('Phân loại món'), CLSRULES, 'fontColor'),
                      cf('_Measures.Phân loại món (What-If)', mname('Phân loại món (What-If)'), CLSRULES, 'fontColor')]}
v.append(vis(p, 'tbl', 20, 486, 1230, 222, 'tableEx', {"Values": {"projections": [pc('Dim_Menu_Item', 'product_detail'), pm('Số ly bán'), pm('Menu Mix %'), pm('CM mỗi ly'), pm('Tổng CM'), pm('Phân loại món'),
             pm('CM mỗi ly (What-If)'), pm('Tổng CM (What-If)'), pm('Thay đổi Tổng CM (USD)'), pm('Phân loại món (What-If)')]}},
             tbl_obj, vco('Bảng so sánh 41 món: hiện tại và What-If (đổi nhóm khi đổi giá bán, giá sữa)'), NO_DEC(), sort='Tổng CM'))
pages.append((p, 'D2 Menu Engineering', v))

# ===================== D3 =====================
p = 'D3'
v = header(p)
v.append(slicer(p, 's_store', 625, 6, 300, 66, 'Dim_Store', 'store_location', 'Cửa hàng'))
v.append(slicer(p, 's_ing', 940, 6, 310, 66, 'Dim_Ingredient', 'ingredient_name', 'Nguyên vật liệu'))
D3C = [('Tiêu hao lý thuyết (USD)', CARD), ('Tiêu hao thực tế (USD)', CARD), ('Variance Rate %', BADBG), ('Waste Rate %', WARNBG), ('Unexplained Shrinkage (USD)', BADBG),
       ('Tỷ lệ chênh lệch được giải thích', OKBG), ('Số cảnh báo (cửa hàng × NVL × tuần)', WARNBG), ('Days Inventory Outstanding (DIO)', CARD)]
for i, (m, f) in enumerate(D3C):
    v.append(card(p, 'c%d' % i, 20 + i * 154, 84, 146, 88, m, f, 20))
v.append(vis(p, 'heat', 20, 184, 600, 250, 'pivotTable', {"Rows": {"projections": [pc('Dim_Store', 'store_location')]}, "Columns": {"projections": [pc('Dim_Date', 'week_no')]}, "Values": {"projections": [pm('Variance Rate %')]}},
             heat('Variance Rate %', RED, 7), vco('Heatmap Variance Rate % theo cửa hàng × tuần')))
bullet_obj = {"lineStyles": [{"properties": {"strokeWidth": N(0), "showMarker": B(True), "markerShape": S('diamond'), "markerSize": N(9)}}],
              "legend": [{"properties": {"show": B(True), "position": S('Bottom')}}],
              "dataPoint": [{"properties": {"fill": {"solid": {"color": S(TAN)}}}, "selector": {"metadata": "_Measures.Tiêu hao thực tế (USD)"}}]}
v.append(vis(p, 'bar', 630, 184, 620, 250, 'lineClusteredColumnComboChart', {"Category": {"projections": [pc('Dim_Ingredient', 'ingredient_name')]},
             "Y": {"projections": [pm('Tiêu hao thực tế (USD)')]}, "Y2": {"projections": [pm('Tiêu hao lý thuyết (USD)')]},
             "Tooltips": {"projections": [pm('Variance Rate %'), pm('Waste Rate %'), pm('Inventory Turnover Ratio (ITR)'), pm('Days Inventory Outstanding (DIO)')]}},
             bullet_obj, vco('So sánh tiêu hao thực tế (cột) và lý thuyết (điểm kim cương) theo NVL'), sort='Tiêu hao thực tế (USD)'))
par_obj = {"lineStyles": [{"properties": {"showMarker": B(True), "markerShape": S('circle'), "markerSize": N(5)}}],
           "legend": [{"properties": {"show": B(True), "position": S('Bottom')}}],
           "y2Axis": [{"properties": {"show": B(True), "end": N(1), "start": N(0)}}]}
v.append(vis(p, 'pareto', 20, 446, 440, 262, 'lineClusteredColumnComboChart', {"Category": {"projections": [pc('Dim_Ingredient', 'ingredient_name')]},
             "Y": {"projections": [pm('Unexplained Shrinkage dương (USD)')]}, "Y2": {"projections": [pm('Pareto lũy kế %')]}},
             par_obj, vco('Pareto: Unexplained Shrinkage dương theo NVL và % lũy kế'), sort='Unexplained Shrinkage dương (USD)'))
VR = agg('Variance_Weekly', 'variance_rate_pct', 0)
UV = agg('Variance_Weekly', 'unexplained_shrinkage_value_usd', 0)
alert_obj = {"values": [cf('Sum(Variance_Weekly.variance_rate_pct)', VR, [(2, '8D', BADBG), (2, '5D', WARNBG)], 'backColor'),
                        cf('Sum(Variance_Weekly.unexplained_shrinkage_value_usd)', VR, [(2, '8D', BADBG), (2, '5D', WARNBG)], 'backColor'),
                        cf('Variance_Weekly.priority', col('Variance_Weekly', 'priority'), [(0, "'Ưu tiên kiểm tra'", BADBG), (0, "'Cảnh báo'", WARNBG)], 'backColor')]}
v.append(vis(p, 'tbl', 470, 446, 520, 262, 'tableEx', {"Values": {"projections": [pc('Variance_Weekly', 'store_location'), pc('Variance_Weekly', 'ingredient_name'), pc('Variance_Weekly', 'week_no'),
             pa('Variance_Weekly', 'variance_rate_pct', 0, 'Variance Rate (%)'), pa('Variance_Weekly', 'unexplained_shrinkage_value_usd', 0, 'Unexplained (USD)'), pc('Variance_Weekly', 'priority')]}},
             alert_obj, vco('Bảng cảnh báo: tô đỏ khi Variance Rate ≥ 8%, vàng khi ≥ 5%'), [in_filter('Variance_Weekly', 'priority', ['Bình thường'], negate=True, nm='fprio')]))
v.append(vis(p, 'donut', 1000, 446, 250, 262, 'donutChart', {"Category": {"projections": [pc('Fact_Waste_Log', 'reason')]}, "Y": {"projections": [pm('Giá trị hủy theo phiếu (USD)')]}},
             {"legend": [{"properties": {"position": S('Bottom')}}]}, vco('Giá trị hủy theo lý do ghi nhận')))
pages.append((p, 'D3 Hao hụt và thất thoát', v))

# ===================== write =====================
os.makedirs(RP + '/definition/pages', exist_ok=True)
wj(RP + '/definition.pbir', {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json", "version": "4.0",
                              "datasetReference": {"byPath": {"path": "../coffee_bi_model.SemanticModel"}}})
if os.path.exists('/tmp/report_theme.json'):   # report.json đã đăng ký theme Coffee BI
    shutil.copy('/tmp/report_theme.json', RP + '/definition/report.json')
    os.makedirs(RP + '/StaticResources/RegisteredResources', exist_ok=True)
    shutil.copy('/tmp/theme_reg.json', RP + '/StaticResources/RegisteredResources/Coffee_BI42464788934050846.json')
ids = []
for pid, disp, vs in pages:
    pn = PID[pid]; ids.append(pn)
    wj(f'{RP}/definition/pages/{pn}/page.json', {"$schema": SCH + "page/2.1.0/schema.json", "name": pn, "displayName": disp, "displayOption": "FitToPage", "height": 720, "width": 1280,
                                                 "objects": {"background": [{"properties": {"color": {"solid": {"color": S(BG)}}}}]}})
    for k, (name, obj) in enumerate(vs):
        obj['position']['z'] = k * 1000; obj['position']['tabOrder'] = k * 1000
        wj(f'{RP}/definition/pages/{pn}/visuals/{name}/visual.json', obj)
wj(RP + '/definition/pages/pages.json', {"$schema": SCH + "pagesMetadata/1.1.0/schema.json", "pageOrder": ids, "activePageName": ids[0]})
print('report written:', len(ids), 'pages;', sum(len(x[2]) for x in pages), 'visuals')
