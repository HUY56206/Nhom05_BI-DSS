-- =====================================================================
-- HỆ THỐNG KHO DỮ LIỆU COFFEE BI (DATA WAREHOUSE DDL)
-- Hệ quản trị cơ sở dữ liệu: MySQL 8.0+
-- Thiết kế Star Schema / Fact Constellation Schema (Mục 4.1)
-- Bản cập nhật đồng bộ các phản biện kỹ thuật
-- =====================================================================

CREATE DATABASE IF NOT EXISTS `coffee_bi` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `coffee_bi`;

-- --------------------------------------------------
-- 1. CÁC BẢNG DIMENSION (CHIỀU DỮ LIỆU)
-- --------------------------------------------------

DROP TABLE IF EXISTS `Fact_Sales`;
DROP TABLE IF EXISTS `Fact_Waste_Log`;
DROP TABLE IF EXISTS `Fact_Inventory_Audit`;
DROP TABLE IF EXISTS `Bridge_BOM`;
DROP TABLE IF EXISTS `Dim_Shift`;
DROP TABLE IF EXISTS `Dim_Store`;
DROP TABLE IF EXISTS `Dim_Ingredient`;
DROP TABLE IF EXISTS `Dim_Menu_Item`;
DROP TABLE IF EXISTS `Dim_Date`;

-- 1.1. Chiều thời gian Dim_Date (Bao gồm từ 2022-12-26 đến 2023-06-30)
CREATE TABLE `Dim_Date` (
  `date_key` INT NOT NULL COMMENT 'Khóa ngày dạng số nguyên YYYYMMDD (20221226 - 20230630)',
  `full_date` DATE NOT NULL COMMENT 'Ngày chuẩn YYYY-MM-DD',
  `day_of_week` TINYINT NOT NULL COMMENT 'ISO: 1=Thứ Hai, 2=Thứ Ba,..., 7=Chủ Nhật',
  `day_name` VARCHAR(15) NOT NULL COMMENT 'Monday, Tuesday,...',
  `day_of_month` TINYINT NOT NULL,
  `day_of_year` SMALLINT NOT NULL,
  `week_no` TINYINT NOT NULL COMMENT 'Tuần trong chu kỳ quan sát (1 - 27)',
  `week_start_date` DATE NOT NULL COMMENT 'Ngày đầu tuần (Thứ Hai, tuần 1 là 2022-12-26)',
  `week_end_date` DATE NOT NULL COMMENT 'Ngày cuối tuần (Chủ Nhật)',
  `month_no` TINYINT NOT NULL,
  `month_name` VARCHAR(15) NOT NULL,
  `quarter_no` TINYINT NOT NULL,
  `year_no` SMALLINT NOT NULL,
  `is_weekend` TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`date_key`),
  UNIQUE KEY `uk_full_date` (`full_date`),
  KEY `idx_week_no` (`week_no`),
  KEY `idx_month_year` (`year_no`, `month_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Chiều thời gian chuẩn hóa';

-- 1.2. Chiều cửa hàng Dim_Store
CREATE TABLE `Dim_Store` (
  `store_id` INT NOT NULL COMMENT 'Mã định danh cửa hàng (POS store_id: 3, 5, 8)',
  `store_location` VARCHAR(100) NOT NULL COMMENT 'Tên chi nhánh: Astoria, Lower Manhattan, Hell''s Kitchen',
  `neighborhood` VARCHAR(100) NULL,
  `city` VARCHAR(50) NOT NULL DEFAULT 'New York',
  `state` VARCHAR(10) NOT NULL DEFAULT 'NY',
  `status` VARCHAR(20) NOT NULL DEFAULT 'Active',
  PRIMARY KEY (`store_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Chiều thông tin chi nhánh cửa hàng';

-- 1.3. Chiều ca làm việc Dim_Shift
CREATE TABLE `Dim_Shift` (
  `shift_id` INT NOT NULL,
  `shift_name` VARCHAR(20) NOT NULL COMMENT 'Sáng, Chiều, Tối',
  `start_hour` TINYINT NOT NULL COMMENT '6, 11, 16',
  `end_hour` TINYINT NOT NULL COMMENT '10, 15, 20',
  `time_range_desc` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`shift_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Chiều phân loại ca làm việc';

-- 1.4. Chiều thực đơn Dim_Menu_Item
CREATE TABLE `Dim_Menu_Item` (
  `product_id` INT NOT NULL COMMENT 'Mã món POS gốc (1-87)',
  `product_name` VARCHAR(150) NOT NULL COMMENT 'Tên món POS đầy đủ (product_detail)',
  `base_item` VARCHAR(100) NOT NULL COMMENT 'Tên gốc sau tách size',
  `size` VARCHAR(10) NULL COMMENT 'Sm, Rg, Lg, Shot, NA',
  `product_category` VARCHAR(50) NOT NULL COMMENT 'Coffee, Tea, Drinking Chocolate, Bakery,...',
  `product_type` VARCHAR(50) NOT NULL,
  `is_drink` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '1: 41 món đồ uống pha chế, 0: 39 hàng khác',
  `unit_of_measure` VARCHAR(20) NOT NULL DEFAULT 'Ly/Cốc',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`product_id`),
  KEY `idx_is_drink` (`is_drink`),
  KEY `idx_category` (`product_category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Chiều danh mục thực đơn';

-- 1.5. Chiều nguyên vật liệu Dim_Ingredient
CREATE TABLE `Dim_Ingredient` (
  `ingredient_id` VARCHAR(20) NOT NULL COMMENT 'Mã NVL: I001 - I025',
  `ingredient_name` VARCHAR(150) NOT NULL,
  `ingredient_group` VARCHAR(50) NOT NULL COMMENT 'Cà phê, Sữa, Trà, Bao bì, Phụ liệu',
  `unit` VARCHAR(20) NOT NULL COMMENT 'Đơn vị mua/kho: g, ml, cái',
  `unit_cost_usd` DECIMAL(10,4) NOT NULL COMMENT 'Đơn giá mua AP chuẩn',
  `yield_pct` DECIMAL(5,2) NOT NULL DEFAULT 100.00 COMMENT 'Tỷ lệ thu hồi Yield %',
  `shelf_life_days` INT NULL COMMENT 'Hạn sử dụng tiêu chuẩn',
  `is_stocked` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '1: 22 NVL kiểm kê lưu kho, 0: I020 nước lọc lấy tại vòi',
  PRIMARY KEY (`ingredient_id`),
  KEY `idx_group` (`ingredient_group`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Chiều nguyên vật liệu lưu kho và pha chế';

-- --------------------------------------------------
-- 2. BẢNG CẦU (BRIDGE TABLE): Bridge_BOM
-- --------------------------------------------------

CREATE TABLE `Bridge_BOM` (
  `bom_id` INT NOT NULL AUTO_INCREMENT,
  `product_id` INT NOT NULL,
  `ingredient_id` VARCHAR(20) NOT NULL,
  `bom_version` VARCHAR(20) NOT NULL DEFAULT 'v1.0' COMMENT 'Phiên bản định mức',
  `quantity_ep` DECIMAL(10,4) NOT NULL COMMENT 'Định mức thành phẩm EP',
  `quantity_basis` VARCHAR(10) NOT NULL DEFAULT 'EP',
  `quantity_ap` DECIMAL(10,4) NOT NULL COMMENT 'Định mức nguyên liệu thô AP = EP / (Yield / 100)',
  `effective_start_date` DATE NOT NULL DEFAULT '2023-01-01',
  `effective_end_date` DATE NOT NULL DEFAULT '9999-12-31',
  `source_note` TEXT NULL,
  PRIMARY KEY (`bom_id`),
  UNIQUE KEY `uk_prod_ing_ver` (`product_id`, `ingredient_id`, `bom_version`),
  KEY `fk_bom_prod` (`product_id`),
  KEY `fk_bom_ing` (`ingredient_id`),
  CONSTRAINT `fk_bom_prod` FOREIGN KEY (`product_id`) REFERENCES `Dim_Menu_Item` (`product_id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_bom_ing` FOREIGN KEY (`ingredient_id`) REFERENCES `Dim_Ingredient` (`ingredient_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Bảng cầu liên kết N-N giữa Món đồ uống và Nguyên vật liệu';

-- --------------------------------------------------
-- 3. CÁC BẢNG SỰ KIỆN (FACT TABLES)
-- --------------------------------------------------

-- 3.1. Fact_Sales (Grain: 1 dòng POS)
CREATE TABLE `Fact_Sales` (
  `sales_fact_id` BIGINT NOT NULL AUTO_INCREMENT,
  `transaction_id` BIGINT NOT NULL COMMENT 'Mã dòng POS gốc (Degenerate Dimension, 149.116 mã đơn lẻ)',
  `date_key` INT NOT NULL,
  `store_id` INT NOT NULL,
  `product_id` INT NOT NULL,
  `shift_id` INT NOT NULL,
  `transaction_time` TIME NOT NULL,
  `transaction_datetime` DATETIME NOT NULL,
  `transaction_qty` INT NOT NULL,
  `unit_price` DECIMAL(10,2) NOT NULL COMMENT 'Đơn giá thực bán (Lưu giá ngữ cảnh / giá ưu đãi)',
  `revenue` DECIMAL(12,2) NOT NULL COMMENT 'Doanh thu = transaction_qty * unit_price',
  `std_cost_unit_usd` DECIMAL(10,4) NULL COMMENT 'Giá vốn định mức 1 đơn vị',
  `total_std_cogs_usd` DECIMAL(12,4) NULL COMMENT 'Tổng giá vốn định mức = qty * std_cost_unit',
  `contribution_margin_usd` DECIMAL(12,4) NULL COMMENT 'Lợi nhuận đóng góp CM',
  `outlier_flag` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '1 nếu là dòng ngoại lai theo IQR',
  PRIMARY KEY (`sales_fact_id`),
  KEY `fk_sales_date` (`date_key`),
  KEY `fk_sales_store` (`store_id`),
  KEY `fk_sales_product` (`product_id`),
  KEY `fk_sales_shift` (`shift_id`),
  KEY `idx_sales_trans_id` (`transaction_id`),
  KEY `idx_sales_composite` (`store_id`, `date_key`, `product_id`),
  CONSTRAINT `fk_sales_date` FOREIGN KEY (`date_key`) REFERENCES `Dim_Date` (`date_key`) ON UPDATE CASCADE,
  CONSTRAINT `fk_sales_store` FOREIGN KEY (`store_id`) REFERENCES `Dim_Store` (`store_id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_sales_product` FOREIGN KEY (`product_id`) REFERENCES `Dim_Menu_Item` (`product_id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_sales_shift` FOREIGN KEY (`shift_id`) REFERENCES `Dim_Shift` (`shift_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Bảng Fact bán hàng mức dòng giao dịch';

-- 3.2. Fact_Inventory_Audit (Grain: Cửa hàng × NVL × Tuần)
CREATE TABLE `Fact_Inventory_Audit` (
  `audit_fact_id` BIGINT NOT NULL AUTO_INCREMENT,
  `store_id` INT NOT NULL,
  `ingredient_id` VARCHAR(20) NOT NULL,
  `week_start_date_key` INT NOT NULL COMMENT 'FK tới Dim_Date ngày đầu tuần kiểm kê (Thứ Hai)',
  `week_no` TINYINT NOT NULL,
  `days_observed` TINYINT NOT NULL DEFAULT 7,
  `opening_qty` DECIMAL(12,3) NOT NULL DEFAULT 0.000 COMMENT 'Tồn đầu tuần',
  `receipt_qty` DECIMAL(12,3) NOT NULL DEFAULT 0.000 COMMENT 'Nhập kho trong tuần',
  `actual_usage` DECIMAL(12,3) NOT NULL DEFAULT 0.000 COMMENT 'Tiêu hao thực tế AU = Tồn đầu + Nhập - Tồn cuối',
  `closing_qty` DECIMAL(12,3) NOT NULL DEFAULT 0.000 COMMENT 'Tồn cuối tuần kiểm kê',
  `theoretical_usage` DECIMAL(12,3) NOT NULL DEFAULT 0.000 COMMENT 'Tiêu hao lý thuyết TU = SUM(Sales * BOM)',
  `variance_qty` DECIMAL(12,3) NOT NULL DEFAULT 0.000 COMMENT 'Chênh lệch = AU - TU',
  `recorded_waste_qty` DECIMAL(12,3) NOT NULL DEFAULT 0.000 COMMENT 'Lượng hủy ghi nhận (SUM phiếu hủy)',
  `unexplained_shrinkage_qty` DECIMAL(12,3) NOT NULL DEFAULT 0.000 COMMENT 'Hao hụt chưa giải thích U = Variance - Recorded Waste',
  `unit_cost_usd` DECIMAL(10,4) NOT NULL COMMENT 'Đơn giá mua AP chuẩn',
  `actual_cogs_usd` DECIMAL(12,4) NOT NULL COMMENT 'Giá vốn thực tế = AU * unit_cost',
  `opening_value_usd` DECIMAL(12,4) NOT NULL,
  `closing_value_usd` DECIMAL(12,4) NOT NULL,
  `variance_value_usd` DECIMAL(12,4) NOT NULL,
  `unexplained_value_usd` DECIMAL(12,4) NOT NULL,
  `variance_rate_pct` DECIMAL(8,4) NULL COMMENT 'Tỷ lệ % chênh lệch (AU - TU)/TU',
  `waste_rate_pct` DECIMAL(8,4) NULL COMMENT 'Tỷ lệ % hủy Recorded Waste / AU',
  PRIMARY KEY (`audit_fact_id`),
  UNIQUE KEY `uk_store_ing_week_key` (`store_id`, `ingredient_id`, `week_start_date_key`),
  KEY `fk_audit_store` (`store_id`),
  KEY `fk_audit_ing` (`ingredient_id`),
  KEY `fk_audit_date` (`week_start_date_key`),
  CONSTRAINT `fk_audit_store` FOREIGN KEY (`store_id`) REFERENCES `Dim_Store` (`store_id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_audit_ing` FOREIGN KEY (`ingredient_id`) REFERENCES `Dim_Ingredient` (`ingredient_id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_audit_date` FOREIGN KEY (`week_start_date_key`) REFERENCES `Dim_Date` (`date_key`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Bảng Fact kiểm kê chốt sổ tồn kho chu kỳ tuần';

-- 3.3. Fact_Waste_Log (Grain: 1 sự kiện lập phiếu hủy NVL)
CREATE TABLE `Fact_Waste_Log` (
  `waste_fact_id` BIGINT NOT NULL AUTO_INCREMENT,
  `date_key` INT NOT NULL,
  `store_id` INT NOT NULL,
  `ingredient_id` VARCHAR(20) NOT NULL,
  `shift_id` INT NOT NULL,
  `waste_datetime` DATETIME NOT NULL,
  `week_no` TINYINT NOT NULL,
  `reason` VARCHAR(100) NOT NULL COMMENT 'Lý do hủy: Pha lỗi, Rơi vãi, Hỏng/rách, Hết hạn,...',
  `waste_qty` DECIMAL(10,3) NOT NULL,
  `unit_cost_usd` DECIMAL(10,4) NOT NULL,
  `waste_value_usd` DECIMAL(12,4) NOT NULL COMMENT 'Thiệt hại = waste_qty * unit_cost',
  PRIMARY KEY (`waste_fact_id`),
  KEY `fk_waste_date` (`date_key`),
  KEY `fk_waste_store` (`store_id`),
  KEY `fk_waste_ing` (`ingredient_id`),
  KEY `fk_waste_shift` (`shift_id`),
  KEY `idx_waste_composite` (`store_id`, `ingredient_id`, `week_no`),
  CONSTRAINT `fk_waste_date` FOREIGN KEY (`date_key`) REFERENCES `Dim_Date` (`date_key`) ON UPDATE CASCADE,
  CONSTRAINT `fk_waste_store` FOREIGN KEY (`store_id`) REFERENCES `Dim_Store` (`store_id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_waste_ing` FOREIGN KEY (`ingredient_id`) REFERENCES `Dim_Ingredient` (`ingredient_id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_waste_shift` FOREIGN KEY (`shift_id`) REFERENCES `Dim_Shift` (`shift_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Bảng Fact ghi nhận chi tiết các sự kiện hủy/hao hụt nguyên vật liệu';
