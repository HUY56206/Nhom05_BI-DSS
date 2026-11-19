-- SQLite. Use run_audit.py to load independent CSV references into TEMP tables.
-- All seven statements read the existing target without changing it.

-- T01
WITH checks AS (
SELECT 'POS toàn bộ' AS scope, (SELECT COUNT(*) FROM src_sales) AS expected, (SELECT COUNT(*) FROM Fact_Sales) AS actual
UNION ALL
SELECT 'NB04: 41 đồ uống' AS scope, (SELECT COUNT(*) FROM src_sales WHERE is_drink = 1) AS expected, (SELECT COUNT(*) FROM Fact_Sales) AS actual
UNION ALL
SELECT 'Fact_Inventory_Audit', (SELECT COUNT(*) FROM src_inventory), (SELECT COUNT(*) FROM Fact_Inventory_Audit)
UNION ALL
SELECT 'Fact_Waste_Log', (SELECT COUNT(*) FROM src_waste), (SELECT COUNT(*) FROM Fact_Waste_Log)
UNION ALL
SELECT 'Bridge_BOM', (SELECT COUNT(*) FROM src_bom), (SELECT COUNT(*) FROM Bridge_BOM)
)
SELECT 'T01' AS test, scope, expected, actual, CASE WHEN expected = actual THEN 'PASS' ELSE 'FAIL' END AS status FROM checks;

-- T02 (money in integer cents)
WITH checks AS (
SELECT 'POS toàn bộ' AS scope, (SELECT SUM(revenue_cents) FROM src_sales) AS expected, (SELECT SUM(CAST(ROUND(revenue * 100) AS INTEGER)) FROM Fact_Sales) AS actual
UNION ALL
SELECT 'NB04: 41 đồ uống' AS scope, (SELECT SUM(revenue_cents) FROM src_sales WHERE is_drink = 1) AS expected, (SELECT SUM(CAST(ROUND(revenue * 100) AS INTEGER)) FROM Fact_Sales) AS actual
)
SELECT 'T02' AS test, scope, expected, actual, CASE WHEN expected = actual THEN 'PASS' ELSE 'FAIL' END AS status FROM checks;

-- T03
WITH checks AS (
SELECT 'POS toàn bộ' AS scope, (SELECT SUM(transaction_qty) FROM src_sales) AS expected, (SELECT SUM(transaction_qty) FROM Fact_Sales) AS actual
UNION ALL
SELECT 'NB04: 41 đồ uống' AS scope, (SELECT SUM(transaction_qty) FROM src_sales WHERE is_drink = 1) AS expected, (SELECT SUM(transaction_qty) FROM Fact_Sales) AS actual
)
SELECT 'T03' AS test, scope, expected, actual, CASE WHEN expected = actual THEN 'PASS' ELSE 'FAIL' END AS status FROM checks;

-- T04
WITH checks AS (
SELECT 'Fact_Sales.date_key' AS scope, COUNT(*) AS actual FROM Fact_Sales f WHERE f.date_key IS NULL
UNION ALL
SELECT 'Fact_Sales.store_key' AS scope, COUNT(*) AS actual FROM Fact_Sales f WHERE f.store_key IS NULL
UNION ALL
SELECT 'Fact_Sales.shift_key' AS scope, COUNT(*) AS actual FROM Fact_Sales f WHERE f.shift_key IS NULL
UNION ALL
SELECT 'Fact_Sales.menu_item_key' AS scope, COUNT(*) AS actual FROM Fact_Sales f WHERE f.menu_item_key IS NULL
UNION ALL
SELECT 'Fact_Inventory_Audit.week_start_date_key' AS scope, COUNT(*) AS actual FROM Fact_Inventory_Audit f WHERE f.week_start_date_key IS NULL
UNION ALL
SELECT 'Fact_Inventory_Audit.store_key' AS scope, COUNT(*) AS actual FROM Fact_Inventory_Audit f WHERE f.store_key IS NULL
UNION ALL
SELECT 'Fact_Inventory_Audit.ingredient_key' AS scope, COUNT(*) AS actual FROM Fact_Inventory_Audit f WHERE f.ingredient_key IS NULL
UNION ALL
SELECT 'Fact_Waste_Log.date_key' AS scope, COUNT(*) AS actual FROM Fact_Waste_Log f WHERE f.date_key IS NULL
UNION ALL
SELECT 'Fact_Waste_Log.store_key' AS scope, COUNT(*) AS actual FROM Fact_Waste_Log f WHERE f.store_key IS NULL
UNION ALL
SELECT 'Fact_Waste_Log.shift_key' AS scope, COUNT(*) AS actual FROM Fact_Waste_Log f WHERE f.shift_key IS NULL
UNION ALL
SELECT 'Fact_Waste_Log.ingredient_key' AS scope, COUNT(*) AS actual FROM Fact_Waste_Log f WHERE f.ingredient_key IS NULL
UNION ALL
SELECT 'Bridge_BOM.menu_item_key' AS scope, COUNT(*) AS actual FROM Bridge_BOM f WHERE f.menu_item_key IS NULL
UNION ALL
SELECT 'Bridge_BOM.ingredient_key' AS scope, COUNT(*) AS actual FROM Bridge_BOM f WHERE f.ingredient_key IS NULL
)
SELECT 'T04' AS test, scope, 0 AS expected, actual, CASE WHEN actual = 0 THEN 'PASS' ELSE 'FAIL' END AS status FROM checks;

-- T05
WITH checks AS (
SELECT 'Fact_Sales.date_key' AS scope, COUNT(*) AS actual FROM Fact_Sales f LEFT JOIN Dim_Date d ON f.date_key = d.date_key WHERE f.date_key IS NOT NULL AND d.date_key IS NULL
UNION ALL
SELECT 'Fact_Sales.store_key' AS scope, COUNT(*) AS actual FROM Fact_Sales f LEFT JOIN Dim_Store d ON f.store_key = d.store_key WHERE f.store_key IS NOT NULL AND d.store_key IS NULL
UNION ALL
SELECT 'Fact_Sales.shift_key' AS scope, COUNT(*) AS actual FROM Fact_Sales f LEFT JOIN Dim_Shift d ON f.shift_key = d.shift_key WHERE f.shift_key IS NOT NULL AND d.shift_key IS NULL
UNION ALL
SELECT 'Fact_Sales.menu_item_key' AS scope, COUNT(*) AS actual FROM Fact_Sales f LEFT JOIN Dim_Menu_Item d ON f.menu_item_key = d.menu_item_key WHERE f.menu_item_key IS NOT NULL AND d.menu_item_key IS NULL
UNION ALL
SELECT 'Fact_Inventory_Audit.week_start_date_key' AS scope, COUNT(*) AS actual FROM Fact_Inventory_Audit f LEFT JOIN Dim_Date d ON f.week_start_date_key = d.date_key WHERE f.week_start_date_key IS NOT NULL AND d.date_key IS NULL
UNION ALL
SELECT 'Fact_Inventory_Audit.store_key' AS scope, COUNT(*) AS actual FROM Fact_Inventory_Audit f LEFT JOIN Dim_Store d ON f.store_key = d.store_key WHERE f.store_key IS NOT NULL AND d.store_key IS NULL
UNION ALL
SELECT 'Fact_Inventory_Audit.ingredient_key' AS scope, COUNT(*) AS actual FROM Fact_Inventory_Audit f LEFT JOIN Dim_Ingredient d ON f.ingredient_key = d.ingredient_key WHERE f.ingredient_key IS NOT NULL AND d.ingredient_key IS NULL
UNION ALL
SELECT 'Fact_Waste_Log.date_key' AS scope, COUNT(*) AS actual FROM Fact_Waste_Log f LEFT JOIN Dim_Date d ON f.date_key = d.date_key WHERE f.date_key IS NOT NULL AND d.date_key IS NULL
UNION ALL
SELECT 'Fact_Waste_Log.store_key' AS scope, COUNT(*) AS actual FROM Fact_Waste_Log f LEFT JOIN Dim_Store d ON f.store_key = d.store_key WHERE f.store_key IS NOT NULL AND d.store_key IS NULL
UNION ALL
SELECT 'Fact_Waste_Log.shift_key' AS scope, COUNT(*) AS actual FROM Fact_Waste_Log f LEFT JOIN Dim_Shift d ON f.shift_key = d.shift_key WHERE f.shift_key IS NOT NULL AND d.shift_key IS NULL
UNION ALL
SELECT 'Fact_Waste_Log.ingredient_key' AS scope, COUNT(*) AS actual FROM Fact_Waste_Log f LEFT JOIN Dim_Ingredient d ON f.ingredient_key = d.ingredient_key WHERE f.ingredient_key IS NOT NULL AND d.ingredient_key IS NULL
UNION ALL
SELECT 'Bridge_BOM.menu_item_key' AS scope, COUNT(*) AS actual FROM Bridge_BOM f LEFT JOIN Dim_Menu_Item d ON f.menu_item_key = d.menu_item_key WHERE f.menu_item_key IS NOT NULL AND d.menu_item_key IS NULL
UNION ALL
SELECT 'Bridge_BOM.ingredient_key' AS scope, COUNT(*) AS actual FROM Bridge_BOM f LEFT JOIN Dim_Ingredient d ON f.ingredient_key = d.ingredient_key WHERE f.ingredient_key IS NOT NULL AND d.ingredient_key IS NULL
)
SELECT 'T05' AS test, scope, 0 AS expected, actual, CASE WHEN actual = 0 THEN 'PASS' ELSE 'FAIL' END AS status FROM checks;

-- T06
WITH checks AS (
SELECT 'Dim_Date (date_key)' AS scope, COUNT(*) AS actual FROM (SELECT date_key FROM Dim_Date GROUP BY date_key HAVING COUNT(*) > 1 OR date_key IS NULL)
UNION ALL
SELECT 'Dim_Store (store_key)' AS scope, COUNT(*) AS actual FROM (SELECT store_key FROM Dim_Store GROUP BY store_key HAVING COUNT(*) > 1 OR store_key IS NULL)
UNION ALL
SELECT 'Dim_Shift (shift_key)' AS scope, COUNT(*) AS actual FROM (SELECT shift_key FROM Dim_Shift GROUP BY shift_key HAVING COUNT(*) > 1 OR shift_key IS NULL)
UNION ALL
SELECT 'Dim_Menu_Item (menu_item_key)' AS scope, COUNT(*) AS actual FROM (SELECT menu_item_key FROM Dim_Menu_Item GROUP BY menu_item_key HAVING COUNT(*) > 1 OR menu_item_key IS NULL)
UNION ALL
SELECT 'Dim_Ingredient (ingredient_key)' AS scope, COUNT(*) AS actual FROM (SELECT ingredient_key FROM Dim_Ingredient GROUP BY ingredient_key HAVING COUNT(*) > 1 OR ingredient_key IS NULL)
UNION ALL
SELECT 'Bridge_BOM (bom_key)' AS scope, COUNT(*) AS actual FROM (SELECT bom_key FROM Bridge_BOM GROUP BY bom_key HAVING COUNT(*) > 1 OR bom_key IS NULL)
UNION ALL
SELECT 'Fact_Sales (sales_key)' AS scope, COUNT(*) AS actual FROM (SELECT sales_key FROM Fact_Sales GROUP BY sales_key HAVING COUNT(*) > 1 OR sales_key IS NULL)
UNION ALL
SELECT 'Fact_Inventory_Audit (inventory_key)' AS scope, COUNT(*) AS actual FROM (SELECT inventory_key FROM Fact_Inventory_Audit GROUP BY inventory_key HAVING COUNT(*) > 1 OR inventory_key IS NULL)
UNION ALL
SELECT 'Fact_Waste_Log (waste_key)' AS scope, COUNT(*) AS actual FROM (SELECT waste_key FROM Fact_Waste_Log GROUP BY waste_key HAVING COUNT(*) > 1 OR waste_key IS NULL)
UNION ALL
SELECT 'Fact_Sales (transaction_id)' AS scope, COUNT(*) AS actual FROM (SELECT transaction_id FROM Fact_Sales GROUP BY transaction_id HAVING COUNT(*) > 1 OR transaction_id IS NULL)
UNION ALL
SELECT 'Fact_Waste_Log (waste_id)' AS scope, COUNT(*) AS actual FROM (SELECT waste_id FROM Fact_Waste_Log GROUP BY waste_id HAVING COUNT(*) > 1 OR waste_id IS NULL)
UNION ALL
SELECT 'Fact_Inventory_Audit (store_key, ingredient_key, week_start_date_key)' AS scope, COUNT(*) AS actual FROM (SELECT store_key, ingredient_key, week_start_date_key FROM Fact_Inventory_Audit GROUP BY store_key, ingredient_key, week_start_date_key HAVING COUNT(*) > 1 OR store_key IS NULL OR ingredient_key IS NULL OR week_start_date_key IS NULL)
UNION ALL
SELECT 'Bridge_BOM (menu_item_key, ingredient_key, bom_version)' AS scope, COUNT(*) AS actual FROM (SELECT menu_item_key, ingredient_key, bom_version FROM Bridge_BOM GROUP BY menu_item_key, ingredient_key, bom_version HAVING COUNT(*) > 1 OR menu_item_key IS NULL OR ingredient_key IS NULL OR bom_version IS NULL)
)
SELECT 'T06' AS test, scope, 0 AS expected, actual, CASE WHEN actual = 0 THEN 'PASS' ELSE 'FAIL' END AS status FROM checks;

-- T07. Compare every source/target grain and totals separately by ingredient.
WITH target_rows AS (
 SELECT s.store_id, i.ingredient_id, d.full_date AS week_start,
        f.theoretical_usage AS tu
 FROM Fact_Inventory_Audit f
 LEFT JOIN Dim_Store s ON s.store_key = f.store_key
 LEFT JOIN Dim_Ingredient i ON i.ingredient_key = f.ingredient_key
 LEFT JOIN Dim_Date d ON d.date_key = f.week_start_date_key
), source_groups AS (
 SELECT store_id, ingredient_id, week_start, COUNT(*) AS n, SUM(theoretical_usage) AS tu
 FROM src_inventory GROUP BY store_id, ingredient_id, week_start
), target_groups AS (
 SELECT store_id, ingredient_id, week_start, COUNT(*) AS n, SUM(tu) AS tu
 FROM target_rows GROUP BY store_id, ingredient_id, week_start
), keys AS (
 SELECT store_id, ingredient_id, week_start FROM source_groups
 UNION SELECT store_id, ingredient_id, week_start FROM target_groups
), compared AS (
 SELECT k.ingredient_id, s.tu AS source_tu, t.tu AS target_tu,
        CASE WHEN k.store_id IS NULL OR k.ingredient_id IS NULL OR k.week_start IS NULL
          OR s.n IS NULL OR t.n IS NULL OR s.n <> 1 OR t.n <> 1
          OR s.tu IS NULL OR t.tu IS NULL OR ABS(s.tu - t.tu) > 0.000001
          THEN 1 ELSE 0 END AS bad
 FROM keys k
 LEFT JOIN source_groups s USING (store_id, ingredient_id, week_start)
 LEFT JOIN target_groups t USING (store_id, ingredient_id, week_start)
), totals AS (
 SELECT ingredient_id, SUM(source_tu) AS expected, SUM(target_tu) AS actual, SUM(bad) AS bad_grains
 FROM compared GROUP BY ingredient_id
)
SELECT 'T07' AS test, COALESCE(ingredient_id, 'UNMAPPED') AS scope,
       ROUND(expected, 6) AS expected, ROUND(actual, 6) AS actual,
       CASE WHEN bad_grains = 0 AND ABS(expected - actual) <= 0.000001 THEN 'PASS' ELSE 'FAIL' END AS status,
       bad_grains
FROM totals ORDER BY scope;

