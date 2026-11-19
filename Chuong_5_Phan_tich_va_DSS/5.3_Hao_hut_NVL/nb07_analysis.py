from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
IN=ROOT/'input'; OUT=ROOT/'processed'; CHART=ROOT/'charts'
for d in [IN,OUT,CHART]: d.mkdir(exist_ok=True)

def pareto(df, name, value, label, title, out):
    a=df.sort_values(value,ascending=False).copy()
    a['cumulative_pct']=100*a[value].cumsum()/a[value].sum()
    prev=a['cumulative_pct']-100*a[value]/a[value].sum()
    a['abc_class']=np.select([prev<80,prev<95],['A','B'],default='C')
    a.to_csv(OUT/out,index=False,encoding='utf-8-sig')
    fig,ax=plt.subplots(figsize=(12,5)); xs=np.arange(len(a))
    ax.bar(xs,a[value]);ax.set_ylabel(value);ax.set_xlabel(label)
    ax.set_xticks(xs[::max(1,len(a)//16)]);ax.set_xticklabels(a[label].astype(str).iloc[::max(1,len(a)//16)],rotation=65,ha='right',fontsize=7)
    ay=ax.twinx();ay.plot(xs,a['cumulative_pct'],color='darkorange',linewidth=2);ay.axhline(80,color='gray',linestyle='--');ay.axhline(95,color='gray',linestyle=':');ay.set_ylim(0,105);ay.set_ylabel('Doanh thu/hao hụt lũy kế (%)')
    ax.set_title(title);fig.tight_layout();fig.savefig(CHART/(out.replace('.csv','.png')),dpi=170);plt.close(fig)
    return a

sales_path=IN/'sales_clean.csv'
if not sales_path.exists(): raise FileNotFoundError('Thiếu input/sales_clean.csv')
sales=pd.read_csv(sales_path)
needed={'product_id','product_detail','revenue','transaction_qty'}
assert needed.issubset(sales.columns),needed-set(sales.columns)
agg=sales.groupby(['product_id','product_detail'],as_index=False).agg(revenue_usd=('revenue','sum'),quantity_sold=('transaction_qty','sum'))
abc=pareto(agg,'revenue','revenue_usd','product_detail','Pareto doanh thu – toàn bộ POS (80 sản phẩm)','abc_revenue.csv')
print('ABC doanh thu:',len(abc),'sản phẩm,',round(abc.revenue_usd.sum(),2),'USD');print(abc.groupby('abc_class').agg(items=('product_id','size'),revenue=('revenue_usd','sum')).to_string())

# Chỉ tính variance khi có số kiểm kê thực tế, nhập kho và waste log; tuyệt đối không giả lập.
inv_path=IN/'inventory_audit.csv'; waste_path=IN/'waste_log.csv'; bom_path=IN/'bom.csv'; ing_path=IN/'ingredient.csv'
if not (inv_path.exists() and waste_path.exists() and bom_path.exists() and ing_path.exists()):
    print('CHƯA CÓ các nguồn bắt buộc:', [x.name for x in [inv_path,waste_path,bom_path,ing_path] if not x.exists()], '— chưa tạo variance_weekly.csv.')
else:
    inv=pd.read_csv(inv_path);waste=pd.read_csv(waste_path);bom=pd.read_csv(bom_path);ing=pd.read_csv(ing_path)
    invcols={'store_id','ingredient_id','week_start','opening_qty','received_qty','closing_qty'}
    wastecols={'store_id','ingredient_id','event_date','waste_qty'}
    assert invcols.issubset(inv.columns),f'Inventory thiếu {invcols-set(inv.columns)}'
    assert wastecols.issubset(waste.columns),f'Waste thiếu {wastecols-set(waste.columns)}'
    assert {'product_id','ingredient_id','quantity_ep'}.issubset(bom.columns)
    assert {'ingredient_id','yield_pct','unit_cost_usd'}.issubset(ing.columns)
    for x in [inv,waste,bom,ing]: x['ingredient_id']=x['ingredient_id'].astype(str)
    inv['week_start']=pd.to_datetime(inv['week_start']).dt.normalize()
    waste['week_start']=pd.to_datetime(waste['event_date']).dt.to_period('W-SUN').dt.start_time
    sales['week_start']=pd.to_datetime(sales['transaction_date']).dt.to_period('W-SUN').dt.start_time
    bom=bom.merge(ing[['ingredient_id','yield_pct','unit_cost_usd','ingredient_name','unit']],on='ingredient_id',validate='many_to_one')
    assert bom['yield_pct'].between(0.01,100).all()
    bom['quantity_ap']=bom['quantity_ep']/(bom['yield_pct']/100)
    # Có thể lọc thêm theo BOM version nếu dữ liệu nguồn có nhiều phiên bản.
    usage=sales.groupby(['store_id','week_start','product_id'],as_index=False)['transaction_qty'].sum().merge(bom[['product_id','ingredient_id','quantity_ap']],on='product_id',how='inner')
    usage['theoretical_qty']=usage.transaction_qty*usage.quantity_ap
    theoretical=usage.groupby(['store_id','ingredient_id','week_start'],as_index=False)['theoretical_qty'].sum()
    waste_agg=waste.groupby(['store_id','ingredient_id','week_start'],as_index=False)['waste_qty'].sum()
    key=['store_id','ingredient_id','week_start']
    assert not inv.duplicated(key).any(),'Kiểm kê bị trùng store × NVL × tuần'
    result=inv.merge(theoretical,on=key,how='left').merge(waste_agg,on=key,how='left').merge(ing[['ingredient_id','ingredient_name','unit','unit_cost_usd']],on='ingredient_id',how='left',validate='many_to_one')
    if result.theoretical_qty.isna().any(): print('CẢNH BÁO: có dòng kiểm kê không khớp định mức BOM/sales; giữ NaN để kiểm tra, không tự điền 0')
    result['actual_usage_qty']=result.opening_qty+result.received_qty-result.closing_qty
    result['variance_qty']=result.actual_usage_qty-result.theoretical_qty
    result['variance_rate_pct']=np.where(result.theoretical_qty>0,100*result.variance_qty/result.theoretical_qty,np.nan)
    result['waste_rate_pct']=np.where(result.actual_usage_qty>0,100*result.waste_qty/result.actual_usage_qty,np.nan)
    result['unexplained_shrinkage_qty']=result.variance_qty-result.waste_qty
    result['unexplained_shrinkage_value_usd']=result.unexplained_shrinkage_qty.clip(lower=0)*result.unit_cost_usd
    result['variance_value_usd']=result.variance_qty*result.unit_cost_usd
    result['waste_value_usd']=result.waste_qty*result.unit_cost_usd
    result.to_csv(OUT/'variance_weekly.csv',index=False,encoding='utf-8-sig')
    # Pareto theo giá trị thất thoát không giải trình dương; không gộp các khoản tiết kiệm âm.
    shrink=result.groupby(['ingredient_id','ingredient_name'],as_index=False)['unexplained_shrinkage_value_usd'].sum()
    shrink=shrink[shrink.unexplained_shrinkage_value_usd>0]
    if len(shrink):
        pareto(shrink,'shrink','unexplained_shrinkage_value_usd','ingredient_name','Pareto giá trị thất thoát chưa giải trình (USD)','abc_shrinkage.csv')
        shrink.sort_values('unexplained_shrinkage_value_usd',ascending=False).head(10).to_csv(OUT/'top_10_ingredient_shrinkage.csv',index=False,encoding='utf-8-sig')
    print('Đã xuất variance_weekly.csv:',len(result),'dòng; thiếu theoretical:',result.theoretical_qty.isna().sum())
