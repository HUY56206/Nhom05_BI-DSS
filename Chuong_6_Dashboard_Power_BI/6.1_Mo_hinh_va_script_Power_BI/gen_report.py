# -*- coding: utf-8 -*-
import os, json, shutil, hashlib
BASE = os.path.expanduser('~/mnt/BI_K24406H_Kỳ7-20261116T011316Z-1-001/BI_K24406H_Kỳ7/powerbi')
PROJ = os.path.join(BASE, 'coffee_bi_model')
RP = os.path.join(PROJ, 'coffee_bi_model.Report')
D1 = '/tmp/d1'
shutil.rmtree(RP, ignore_errors=True)
os.makedirs(RP + '/definition/pages', exist_ok=True)
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

BROWN, ACC, TAN, GREEN, RED, BG, CARD, LINE = '#503524', '#8C5A3C', '#C9A27A', '#3F8F7B', '#C0504D', '#F7F4EF', '#F3E7DA', '#E4D6C6'

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
    if title: o["title"] = [{"properties": {"show": B(True), "text": S(title), "fontSize": N(12), "fontColor": COLOR(BROWN), "bold": B(True)}}]
    else: o["title"] = [{"properties": {"show": B(False)}}]
    return o

def vis(page, key, x, y, w, h, vtype, query=None, objects=None, container=None, filters=None, sort=None):
    name = hid(page + key)
    v = {"$schema": SCH + "visualContainer/2.14.0/schema.json", "name": name,
         "position": {"x": x, "y": y, "z": 0, "height": h, "width": w, "tabOrder": 0},
         "visual": {"visualType": vtype}}
    if query:
        v["visual"]["query"] = {"queryState": query}
        if sort: v["visual"]["query"]["sortDefinition"] = {"sort": [{"field": msr(sort), "direction": "Descending"}]}
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

def card(page, key, x, y, w, h, m, fill=CARD):
    return vis(page, key, x, y, w, h, 'cardVisual', {"Data": {"projections": [pm(m)]}},
               {"value": [{"properties": {"fontSize": N(24), "labelDisplayUnits": N(1)}, "selector": {"id": "default"}}], "label": [{"properties": {"fontSize": N(11)}, "selector": {"id": "default"}}]},
               vco(None, fill))

def slicer(page, key, x, y, w, h, t, c, title, mode='Dropdown'):
    return vis(page, key, x, y, w, h, 'slicer', {"Values": {"projections": [pc(t, c)]}},
               {"data": [{"properties": {"mode": S(mode)}}], "header": [{"properties": {"show": B(False)}}]}, vco(title, '#FFFFFF'))

def heat(measure, mx, fs=None):
    o = heat0(measure, mx)
    if fs:
        o["values"].insert(0, {"properties": {"fontSize": N(fs)}})
        o["columnHeaders"] = [{"properties": {"fontSize": N(fs)}}]
        o["rowHeaders"] = [{"properties": {"fontSize": N(fs)}}]
    return o

def heat0(measure, mx):
    return {"values": [{"properties": {"backColor": {"solid": {"color": {"expr": {"FillRule": {"Input": msr(measure),
        "FillRule": {"linearGradient2": {"min": {"color": {"Literal": {"Value": "'#FFFFFF'"}}}, "max": {"color": {"Literal": {"Value": f"'{mx}'"}}},
                     "nullColoringStrategy": {"strategy": {"Literal": {"Value": "'noColor'"}}}}}}}}}}},
        "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}], "metadata": f"_Measures.{measure}"}}]}

pages = []  # (id, display, [visuals])

# ===================== D1 =====================
p = 'D1'
v = []
v.append(vis(p, 'title', 20, 8, 900, 54, 'textbox', None, textbox('D1 · Tổng quan điều hành', 24), None))
v.append(vis(p, 'sub', 20, 44, 900, 26, 'textbox', None, textbox('41 đồ uống · 3 cửa hàng · 01/01/2023–30/06/2023 · nguồn: coffee_bi (Fact_Sales, Fact_Inventory_Audit)', 10, False, ACC), None))
v.append(slicer(p, 's_store', 940, 12, 150, 52, 'Dim_Store', 'store_location', 'Cửa hàng'))
v.append(slicer(p, 's_shift', 1100, 12, 150, 52, 'Dim_Shift', 'shift_name', 'Ca'))
for i, m in enumerate(['Doanh thu', 'Số ly bán', 'Tổng CM', 'Food Cost % lý thuyết', 'Food Cost % thực tế', 'Cost Variance (điểm %)']):
    v.append(card(p, 'c%d' % i, 20 + i * 207, 80, 195, 92, m, [CARD, CARD, '#DDEFEA', CARD, CARD, '#F6DDD9'][i]))
v.append(vis(p, 'line', 20, 184, 620, 250, 'lineChart', {"Category": {"projections": [pc('Dim_Date', 'month_name')]}, "Y": {"projections": [pm('Doanh thu')]}, "Series": {"projections": [pc('Dim_Store', 'store_location')]}},
             None, vco('Doanh thu theo tháng × cửa hàng')))
v.append(vis(p, 'heat', 652, 184, 598, 250, 'pivotTable', {"Rows": {"projections": [pc('Fact_Sales', 'hour')]}, "Columns": {"projections": [pc('Dim_Date', 'day_name')]}, "Values": {"projections": [pm('Số dòng giao dịch')]}},
             heat('Số dòng giao dịch', ACC), vco('Số dòng giao dịch theo giờ × thứ trong tuần')))
v.append(vis(p, 'cat', 20, 446, 420, 262, 'clusteredColumnChart', {"Category": {"projections": [pc('Dim_Menu_Item', 'product_category')]}, "Y": {"projections": [pm('Doanh thu')]}},
             None, vco('Doanh thu theo nhóm sản phẩm'), sort='Doanh thu'))
v.append(vis(p, 'tbl', 452, 446, 400, 262, 'tableEx', {"Values": {"projections": [pc('Dim_Store', 'store_location'), pm('Doanh thu'), pm('Tổng CM'), pm('Food Cost % lý thuyết'), pm('Food Cost % thực tế')]}},
             None, vco('So sánh cửa hàng'), sort='Doanh thu'))
v.append(vis(p, 'donut', 864, 446, 386, 262, 'donutChart', {"Category": {"projections": [pc('Dim_Shift', 'shift_name')]}, "Y": {"projections": [pm('Doanh thu')]}},
             None, vco('Doanh thu theo ca')))
pages.append(('D1', 'D1 Tổng quan điều hành', v))

# ===================== D2 =====================
p = 'D2'
v = []
v.append(vis(p, 'title', 20, 8, 900, 54, 'textbox', None, textbox('D2 · Menu Engineering', 24), None))
v.append(vis(p, 'sub', 20, 44, 900, 26, 'textbox', None, textbox('Stars · Plowhorses · Puzzles · Dogs của 41 đồ uống; ngưỡng Popularity = hệ số / n, ngưỡng Profitability = CM bình quân có trọng số Q', 10, False, ACC), None))
v.append(slicer(p, 's_store', 940, 12, 150, 52, 'Dim_Store', 'store_location', 'Cửa hàng'))
v.append(slicer(p, 's_thr', 1100, 12, 150, 52, 'Tham_so_Popularity', 'Nhan_nguong', 'Ngưỡng Popularity'))
for i, (m, f) in enumerate([('Số món Stars', '#DDEFEA'), ('Số món Plowhorses', CARD), ('Số món Puzzles', '#E3EAF6'), ('Số món Dogs', '#F6DDD9'), ('Ngưỡng Popularity', CARD), ('CM bình quân có trọng số', CARD)]):
    v.append(card(p, 'c%d' % i, 20 + i * 207, 80, 195, 92, m, f))
v.append(vis(p, 'scatter', 20, 184, 620, 300, 'scatterChart', {"Category": {"projections": [pc('Menu_Matrix', 'product_detail')]}, "Series": {"projections": [pc('Menu_Matrix', 'class_100')]},
             "X": {"projections": [pa('Menu_Matrix', 'mm_pct', 1)]}, "Y": {"projections": [pa('Menu_Matrix', 'CM', 1)]}},
             None, vco('Ma trận Popularity × Profitability (toàn chuỗi, ngưỡng 100%/n, NB06)'), [in_filter('Menu_Matrix', 'scope_type', ['chain'], nm='fscope')]))
v.append(vis(p, 'bystore', 652, 184, 598, 300, 'clusteredColumnChart', {"Category": {"projections": [pc('Menu_Matrix', 'store_location')]}, "Series": {"projections": [pc('Menu_Matrix', 'class_100')]},
             "Y": {"projections": [pa('Menu_Matrix', 'product_id', 4)]}},
             None, vco('Số món theo nhóm tại từng cửa hàng (NB06)'), [in_filter('Menu_Matrix', 'scope_type', ['store'], nm='fscope')]))
v.append(vis(p, 'tbl', 20, 496, 1230, 212, 'tableEx', {"Values": {"projections": [pc('Dim_Menu_Item', 'product_detail'), pm('Số ly bán'), pm('Menu Mix %'), pm('CM mỗi ly'), pm('Tổng CM'), pm('Phân loại món')]}},
             None, vco('Phân loại 41 món tính trực tiếp bằng DAX (đối chiếu với NB06)'), sort='Tổng CM'))
pages.append(('D2', 'D2 Menu Engineering', v))

# ===================== D3 =====================
p = 'D3'
v = []
v.append(vis(p, 'title', 20, 8, 900, 54, 'textbox', None, textbox('D3 · Hao hụt và thất thoát', 24), None))
v.append(vis(p, 'sub', 20, 44, 900, 26, 'textbox', None, textbox('Variance = (AU − TU) × giá mua; Unexplained Shrinkage = Variance − hao hụt ghi nhận · 22 NVL kiểm kê × 3 cửa hàng × 27 tuần', 10, False, ACC), None))
v.append(slicer(p, 's_store', 940, 12, 150, 52, 'Dim_Store', 'store_location', 'Cửa hàng'))
v.append(slicer(p, 's_ing', 1100, 12, 150, 52, 'Dim_Ingredient', 'ingredient_name', 'Nguyên vật liệu'))
for i, (m, f) in enumerate([('Tiêu hao lý thuyết (USD)', CARD), ('Tiêu hao thực tế (USD)', CARD), ('Variance Rate %', '#F6DDD9'), ('Waste Rate %', CARD), ('Unexplained Shrinkage (USD)', '#F6DDD9'), ('Tỷ lệ chênh lệch được giải thích', '#DDEFEA')]):
    v.append(card(p, 'c%d' % i, 20 + i * 207, 80, 195, 92, m, f))
v.append(vis(p, 'heat', 20, 184, 770, 250, 'pivotTable', {"Rows": {"projections": [pc('Dim_Store', 'store_location')]}, "Columns": {"projections": [pc('Dim_Date', 'week_no')]}, "Values": {"projections": [pm('Variance Rate %')]}},
             heat('Variance Rate %', RED, 8), vco('Variance Rate % theo cửa hàng × tuần')))
v.append(vis(p, 'bar', 802, 184, 448, 250, 'clusteredBarChart', {"Category": {"projections": [pc('Dim_Ingredient', 'ingredient_name')]}, "Y": {"projections": [pm('Variance (USD)')]}},
             None, vco('Variance (USD) theo nguyên vật liệu'), sort='Variance (USD)'))
v.append(vis(p, 'tbl', 20, 446, 770, 262, 'tableEx', {"Values": {"projections": [pc('Variance_Weekly', 'store_location'), pc('Variance_Weekly', 'ingredient_name'), pc('Variance_Weekly', 'week_no'),
             pa('Variance_Weekly', 'variance_rate_pct', 0, 'Variance Rate (%)'), pa('Variance_Weekly', 'unexplained_shrinkage_value_usd', 0, 'Unexplained (USD)'), pc('Variance_Weekly', 'priority')]}},
             None, vco('Cảnh báo: dòng cửa hàng × NVL × tuần ở mức Cảnh báo hoặc Ưu tiên kiểm tra'), [in_filter('Variance_Weekly', 'priority', ['Bình thường'], negate=True, nm='fprio')]))
v.append(vis(p, 'donut', 802, 446, 448, 262, 'donutChart', {"Category": {"projections": [pc('Fact_Waste_Log', 'reason')]}, "Y": {"projections": [pm('Giá trị hủy theo phiếu (USD)')]}},
             None, vco('Giá trị hủy theo lý do ghi nhận')))
pages.append(('D3', 'D3 Hao hụt và thất thoát', v))

# ===================== write =====================
wj(RP + '/definition.pbir', {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json", "version": "4.0",
                              "datasetReference": {"byPath": {"path": "../coffee_bi_model.SemanticModel"}}})
shutil.copy(D1 + '/Report/definition/version.json', RP + '/definition/version.json')
shutil.copy(D1 + '/Report/definition/report.json', RP + '/definition/report.json')
os.makedirs(RP + '/StaticResources', exist_ok=True)
shutil.copytree(D1 + '/Report/StaticResources/SharedResources', RP + '/StaticResources/SharedResources', dirs_exist_ok=True)
ids = []
for pid, disp, vs in pages:
    pn = hid('page' + pid); ids.append(pn)
    wj(f'{RP}/definition/pages/{pn}/page.json', {"$schema": SCH + "page/2.1.0/schema.json", "name": pn, "displayName": disp, "displayOption": "FitToPage", "height": 720, "width": 1280,
                                                 "objects": {"background": [{"properties": {"color": {"solid": {"color": S(BG)}}}}]}})
    for k, (name, obj) in enumerate(vs):
        obj['position']['z'] = k * 1000; obj['position']['tabOrder'] = k * 1000
        wj(f'{RP}/definition/pages/{pn}/visuals/{name}/visual.json', obj)
wj(RP + '/definition/pages/pages.json', {"$schema": SCH + "pagesMetadata/1.1.0/schema.json", "pageOrder": ids, "activePageName": ids[0]})
print('report written:', len(ids), 'pages;', sum(len(x[2]) for x in pages), 'visuals')
