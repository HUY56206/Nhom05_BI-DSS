# Nhóm 05 – Hệ thống DSS & BI quản trị Menu Engineering và kiểm soát hao hụt NVL – chuỗi cà phê Maven Roasters

Môn: Trí tuệ doanh nghiệp. Code được xếp theo mục lục báo cáo.

**Thứ tự chạy:** NB01 → NB03 → NB04_ddl → NB04_dwh_etl → NB5 → NB05_eda / NB05_DQ → NB06 → NB07 → NB08 → Power BI.
Dữ liệu gốc: Coffee Shop Sales – Maven Analytics (149.116 dòng POS, 01–06/2023). Dữ liệu kho và phiếu hủy là dữ liệu mô phỏng (seed 42).

## Chương 3 – Dữ liệu và xử lý dữ liệu
| Mục | File | Nội dung |
|---|---|---|
| 3.4 | `NB01_clean.ipynb` | Làm sạch POS, trường dẫn xuất, gắn cờ ngoại lai, chọn 41 đồ uống |
| 3.5 | `NB03_generate.ipynb` | Sinh `inventory_weekly` (1.755 dòng) và `waste_log` (5.042 phiếu), 2 kịch bản cài sẵn |
| 3.6 | `NB05_DQ.ipynb` | 23 phép kiểm chất lượng dữ liệu theo 5 tiêu chí |

## Chương 4 – Kho dữ liệu và ETL
| Mục | File | Nội dung |
|---|---|---|
| 4.1 | `schema_dbdiagram.dbml`, `ddl_coffee_bi_thiet_ke.sql` | Mô hình chòm sao (3 Fact, 5 Dim, Bridge_BOM) |
| 4.2 | `NB04_ddl.ipynb`, `01_ddl.sql` | Cài `coffee_bi` trên MySQL 8.0.46, thử ràng buộc toàn vẹn |
| 4.3 | `NB04_dwh_etl.ipynb` | ETL nạp Dim/Bridge/Fact vào SQLite `coffee_bi.db` |
| 4.4 | `NB5_Kiem_thu_ETL.ipynb`, `02_test.sql` | Kiểm thử source-to-target |

## Chương 5 – Phân tích dữ liệu và DSS
| Mục | File | Nội dung |
|---|---|---|
| 5.1 | `NB05_eda.ipynb` | Phân tích mô tả |
| 5.2 | `NB06_Menu_Engineering.ipynb` | MM%, CM, ngưỡng 70%/n và 100%/n, phân loại 41 món |
| 5.3 | `NB07_FINAL.ipynb`, `nb07_analysis.py`, `complete_nb07.py` | Variance, Waste Rate, Pareto, kiểm chứng kịch bản |
| 5.4 | `NB07_5_4_FULL.ipynb` | Tương quan Spearman theo ca, Z-score tuần bất thường |
| 5.5 | `NB08_whatif.ipynb` | 3 kịch bản What-If và độ nhạy |

## Chương 6 – Dashboard Power BI
| Mục | File | Nội dung |
|---|---|---|
| 6.1 | `gen_model.py`, `patch_model.py`, `gen_report.py`, `gen_report2.py`, `coffee_theme.json` | Script sinh mô hình/report, theme màu |
| 6.2–6.4 | `coffee_bi_model.pbix`, `D1_Tong_quan_dieu_hanh.pbix`, `Dashboard_D3_HaoHut.pbix` | Dashboard D1, D2, D3 |
