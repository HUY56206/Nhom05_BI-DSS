-- =====================================================================
-- coffee_bi — DDL Data Mart (Phụ lục C)
-- Mô hình chòm sao theo mục 4.1: 5 Dimension + 1 Bridge + 3 Fact = 9 bảng,
-- 13 khóa ngoại. Viết cho MySQL 8.0 (InnoDB, utf8mb4).
-- Chạy lại an toàn: xóa bảng theo thứ tự ngược quan hệ phụ thuộc rồi tạo lại.
-- Bản SQLite (dự phòng) được NB04 sinh tự động từ file này: bỏ AUTO_INCREMENT,
-- ENGINE/CHARSET và COMMENT; giữ nguyên PK, FK, UNIQUE, CHECK và INDEX.
-- =====================================================================

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS fact_waste_log;
DROP TABLE IF EXISTS fact_inventory_audit;
DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS bridge_bom;
DROP TABLE IF EXISTS dim_ingredient;
DROP TABLE IF EXISTS dim_menu_item;
DROP TABLE IF EXISTS dim_shift;
DROP TABLE IF EXISTS dim_store;
DROP TABLE IF EXISTS dim_date;
SET FOREIGN_KEY_CHECKS = 1;

-- ---------------------------------------------------------------------
-- 1. DIMENSION
-- ---------------------------------------------------------------------

-- 187 ngày: 26/12/2022 (thứ Hai đầu tuần 1) đến 30/06/2023
CREATE TABLE dim_date (
    date_key         INT          NOT NULL,              -- YYYYMMDD
    full_date        DATE         NOT NULL,
    day_of_week      TINYINT      NOT NULL,              -- 1 = Thứ Hai ... 7 = Chủ nhật
    day_name         VARCHAR(10)  NOT NULL,
    is_weekend       TINYINT(1)   NOT NULL DEFAULT 0,
    week_no          TINYINT      NOT NULL,              -- tuần 1 bắt đầu 26/12/2022
    week_start_date  DATE         NOT NULL,
    month            TINYINT      NOT NULL,
    month_name       VARCHAR(10)  NOT NULL,
    quarter          TINYINT      NOT NULL,
    year             SMALLINT     NOT NULL,
    in_sales_period  TINYINT(1)   NOT NULL DEFAULT 1,    -- 0 cho 26–31/12/2022 (chỉ để neo tuần 1)
    CONSTRAINT pk_dim_date PRIMARY KEY (date_key),
    CONSTRAINT uq_dim_date_full_date UNIQUE (full_date),
    CONSTRAINT ck_dim_date_dow   CHECK (day_of_week BETWEEN 1 AND 7),
    CONSTRAINT ck_dim_date_month CHECK (month BETWEEN 1 AND 12),
    CONSTRAINT ck_dim_date_qtr   CHECK (quarter BETWEEN 1 AND 4)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

-- 3 cửa hàng, giữ mã POS gốc 3, 5, 8
CREATE TABLE dim_store (
    store_id         INT          NOT NULL,
    store_location   VARCHAR(50)  NOT NULL,
    district         VARCHAR(50)  NULL,
    city             VARCHAR(50)  NOT NULL DEFAULT 'New York',
    state            VARCHAR(20)  NOT NULL DEFAULT 'NY',
    status           VARCHAR(20)  NOT NULL DEFAULT 'Active',
    CONSTRAINT pk_dim_store PRIMARY KEY (store_id),
    CONSTRAINT uq_dim_store_location UNIQUE (store_location)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

-- 3 ca: Sáng 06:00–10:59, Chiều 11:00–15:59, Tối 16:00–20:59
CREATE TABLE dim_shift (
    shift_id         INT          NOT NULL,
    shift_name       VARCHAR(20)  NOT NULL,
    start_time       TIME         NOT NULL,
    end_time         TIME         NOT NULL,
    CONSTRAINT pk_dim_shift PRIMARY KEY (shift_id),
    CONSTRAINT uq_dim_shift_name UNIQUE (shift_name),
    CONSTRAINT ck_dim_shift_time CHECK (start_time < end_time)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

-- Danh mục sản phẩm, giữ mã POS gốc product_id (1–87); is_drink = 1 cho 41 đồ uống
CREATE TABLE dim_menu_item (
    product_id       INT          NOT NULL,
    product_detail   VARCHAR(100) NOT NULL,
    base_item        VARCHAR(100) NOT NULL,
    size             VARCHAR(10)  NULL,                  -- Sm / Rg / Lg / Shot; NULL với hàng không pha chế
    product_category VARCHAR(50)  NOT NULL,
    product_type     VARCHAR(50)  NOT NULL,
    unit             VARCHAR(20)  NOT NULL DEFAULT 'ly',
    is_drink         TINYINT(1)   NOT NULL DEFAULT 0,
    status           VARCHAR(20)  NOT NULL DEFAULT 'Active',
    CONSTRAINT pk_dim_menu_item PRIMARY KEY (product_id),
    CONSTRAINT ck_dim_menu_item_size CHECK (size IS NULL OR size IN ('Sm', 'Rg', 'Lg', 'Shot')),
    CONSTRAINT ck_dim_menu_item_drink CHECK (is_drink IN (0, 1))
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

-- 25 NVL; is_stocked = 1 cho 22 NVL thuộc phạm vi kiểm kê
CREATE TABLE dim_ingredient (
    ingredient_id    VARCHAR(20)  NOT NULL,
    ingredient_name  VARCHAR(100) NOT NULL,
    unit             VARCHAR(10)  NOT NULL,              -- g / ml / cai
    unit_cost_usd    DECIMAL(10,4) NOT NULL,             -- đơn giá mua (AP) theo đơn vị kho
    yield_pct        DECIMAL(5,2) NOT NULL,              -- tỷ lệ thu hồi, đơn vị %
    shelf_life_days  INT          NULL,
    is_stocked       TINYINT(1)   NOT NULL DEFAULT 1,
    CONSTRAINT pk_dim_ingredient PRIMARY KEY (ingredient_id),
    CONSTRAINT ck_dim_ingredient_unit  CHECK (unit IN ('g', 'ml', 'cai')),
    CONSTRAINT ck_dim_ingredient_cost  CHECK (unit_cost_usd >= 0),
    CONSTRAINT ck_dim_ingredient_yield CHECK (yield_pct > 0 AND yield_pct <= 100)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

-- ---------------------------------------------------------------------
-- 2. BRIDGE
-- ---------------------------------------------------------------------

-- 178 dòng định mức: một đồ uống × một NVL × một phiên bản công thức
CREATE TABLE bridge_bom (
    bom_id           INT          NOT NULL AUTO_INCREMENT,
    product_id       INT          NOT NULL,
    ingredient_id    VARCHAR(20)  NOT NULL,
    bom_version      SMALLINT     NOT NULL DEFAULT 1,
    quantity_ep      DECIMAL(10,3) NOT NULL,             -- lượng sau sơ chế / 1 đơn vị đồ uống
    quantity_ap      DECIMAL(12,5) NOT NULL,             -- = quantity_ep / (yield_pct / 100)
    valid_from       DATE         NOT NULL,
    valid_to         DATE         NULL,                  -- NULL = còn hiệu lực
    CONSTRAINT pk_bridge_bom PRIMARY KEY (bom_id),
    CONSTRAINT uq_bridge_bom UNIQUE (product_id, ingredient_id, bom_version),
    CONSTRAINT fk_bom_product    FOREIGN KEY (product_id)    REFERENCES dim_menu_item (product_id),
    CONSTRAINT fk_bom_ingredient FOREIGN KEY (ingredient_id) REFERENCES dim_ingredient (ingredient_id),
    CONSTRAINT ck_bom_qty   CHECK (quantity_ep > 0 AND quantity_ap >= quantity_ep),
    CONSTRAINT ck_bom_valid CHECK (valid_to IS NULL OR valid_to >= valid_from)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

-- ---------------------------------------------------------------------
-- 3. FACT
-- ---------------------------------------------------------------------

-- Grain: một dòng bán hàng POS
CREATE TABLE fact_sales (
    sales_fact_id          BIGINT        NOT NULL AUTO_INCREMENT,
    transaction_id         BIGINT        NOT NULL,       -- mã dòng POS gốc
    date_key               INT           NOT NULL,
    store_id               INT           NOT NULL,
    product_id             INT           NOT NULL,
    shift_id               INT           NOT NULL,
    transaction_time       TIME          NOT NULL,
    transaction_datetime   DATETIME      NOT NULL,
    transaction_qty        INT           NOT NULL,
    unit_price             DECIMAL(10,2) NOT NULL,
    revenue                DECIMAL(12,2) NOT NULL,       -- transaction_qty × unit_price
    std_cost_unit_usd      DECIMAL(10,4) NULL,           -- NULL khi thiếu BOM
    total_std_cogs_usd     DECIMAL(12,4) NULL,
    contribution_margin_usd DECIMAL(12,4) NULL,          -- revenue − total_std_cogs_usd
    outlier_flag           TINYINT(1)    NOT NULL DEFAULT 0,
    CONSTRAINT pk_fact_sales PRIMARY KEY (sales_fact_id),
    CONSTRAINT uq_fact_sales_txn UNIQUE (transaction_id),
    CONSTRAINT fk_sales_date    FOREIGN KEY (date_key)   REFERENCES dim_date (date_key),
    CONSTRAINT fk_sales_store   FOREIGN KEY (store_id)   REFERENCES dim_store (store_id),
    CONSTRAINT fk_sales_product FOREIGN KEY (product_id) REFERENCES dim_menu_item (product_id),
    CONSTRAINT fk_sales_shift   FOREIGN KEY (shift_id)   REFERENCES dim_shift (shift_id),
    CONSTRAINT ck_sales_qty     CHECK (transaction_qty > 0),
    CONSTRAINT ck_sales_price   CHECK (unit_price >= 0),
    CONSTRAINT ck_sales_revenue CHECK (ABS(revenue - transaction_qty * unit_price) < 0.005),
    CONSTRAINT ck_sales_outlier CHECK (outlier_flag IN (0, 1))
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

-- Grain: một cửa hàng × một NVL thuộc phạm vi kiểm kê × một tuần (periodic snapshot)
CREATE TABLE fact_inventory_audit (
    audit_fact_id          BIGINT        NOT NULL AUTO_INCREMENT,
    store_id               INT           NOT NULL,
    ingredient_id          VARCHAR(20)   NOT NULL,
    week_start_date_key    INT           NOT NULL,       -- ngày thứ Hai đầu tuần
    week_no                TINYINT       NOT NULL,
    days_observed          TINYINT       NOT NULL,
    opening_qty            DECIMAL(12,3) NOT NULL,
    receipt_qty            DECIMAL(12,3) NOT NULL,
    actual_usage           DECIMAL(12,3) NOT NULL,       -- AU = tồn đầu + nhập − tồn cuối
    closing_qty            DECIMAL(12,3) NOT NULL,
    theoretical_usage      DECIMAL(12,3) NOT NULL,       -- TU
    variance_qty           DECIMAL(12,3) NOT NULL,       -- AU − TU
    recorded_waste_qty     DECIMAL(12,3) NOT NULL,       -- W
    unexplained_shrinkage_qty DECIMAL(12,3) NOT NULL,    -- AU − TU − W
    unit_cost_usd          DECIMAL(10,4) NOT NULL,
    actual_cogs_usd        DECIMAL(12,4) NOT NULL,
    opening_value_usd      DECIMAL(12,4) NOT NULL,
    closing_value_usd      DECIMAL(12,4) NOT NULL,
    variance_value_usd     DECIMAL(12,4) NOT NULL,
    unexplained_value_usd  DECIMAL(12,4) NOT NULL,
    variance_rate_pct      DECIMAL(8,4)  NULL,           -- NULL khi TU = 0
    waste_rate_pct         DECIMAL(8,4)  NULL,           -- NULL khi AU = 0
    CONSTRAINT pk_fact_inventory_audit PRIMARY KEY (audit_fact_id),
    CONSTRAINT uq_inventory_store_ing_week UNIQUE (store_id, ingredient_id, week_start_date_key),
    CONSTRAINT fk_inv_store      FOREIGN KEY (store_id)            REFERENCES dim_store (store_id),
    CONSTRAINT fk_inv_ingredient FOREIGN KEY (ingredient_id)       REFERENCES dim_ingredient (ingredient_id),
    CONSTRAINT fk_inv_week       FOREIGN KEY (week_start_date_key) REFERENCES dim_date (date_key),
    CONSTRAINT ck_inv_nonneg  CHECK (opening_qty >= 0 AND receipt_qty >= 0 AND closing_qty >= 0
                                     AND actual_usage >= 0 AND theoretical_usage >= 0 AND recorded_waste_qty >= 0),
    CONSTRAINT ck_inv_balance CHECK (ABS(opening_qty + receipt_qty - actual_usage - closing_qty) < 0.0005),
    CONSTRAINT ck_inv_days    CHECK (days_observed BETWEEN 1 AND 7)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

-- Grain: một NVL trong một sự kiện hủy
CREATE TABLE fact_waste_log (
    waste_fact_id          BIGINT        NOT NULL AUTO_INCREMENT,
    waste_id               VARCHAR(20)   NOT NULL,       -- mã phiếu hủy nguồn (W000001...)
    date_key               INT           NOT NULL,
    store_id               INT           NOT NULL,
    ingredient_id          VARCHAR(20)   NOT NULL,
    shift_id               INT           NOT NULL,
    waste_datetime         DATETIME      NOT NULL,
    week_no                TINYINT       NOT NULL,
    reason                 VARCHAR(100)  NOT NULL,
    waste_qty              DECIMAL(10,3) NOT NULL,
    unit_cost_usd          DECIMAL(10,4) NOT NULL,
    waste_value_usd        DECIMAL(12,4) NOT NULL,       -- waste_qty × unit_cost_usd
    CONSTRAINT pk_fact_waste_log PRIMARY KEY (waste_fact_id),
    CONSTRAINT uq_fact_waste_id UNIQUE (waste_id),
    CONSTRAINT fk_waste_date       FOREIGN KEY (date_key)      REFERENCES dim_date (date_key),
    CONSTRAINT fk_waste_store      FOREIGN KEY (store_id)      REFERENCES dim_store (store_id),
    CONSTRAINT fk_waste_ingredient FOREIGN KEY (ingredient_id) REFERENCES dim_ingredient (ingredient_id),
    CONSTRAINT fk_waste_shift      FOREIGN KEY (shift_id)      REFERENCES dim_shift (shift_id),
    CONSTRAINT ck_waste_qty CHECK (waste_qty > 0 AND waste_value_usd >= 0)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

-- ---------------------------------------------------------------------
-- 4. INDEX
-- (a) Mỗi cột khóa ngoại phải đứng đầu ít nhất một index. Bỏ qua khi đã có sẵn:
--     bridge_bom.product_id và fact_inventory_audit.store_id đứng đầu khóa UNIQUE;
--     fact_sales.store_id và fact_waste_log.store_id đứng đầu index ghép ở (b).
-- (b) Index ghép cho các truy vấn chính của Dashboard D1–D3.
-- ---------------------------------------------------------------------

-- (a) Khóa ngoại
CREATE INDEX ix_bom_ingredient      ON bridge_bom (ingredient_id);
CREATE INDEX ix_sales_date          ON fact_sales (date_key);
CREATE INDEX ix_sales_product       ON fact_sales (product_id);
CREATE INDEX ix_sales_shift         ON fact_sales (shift_id);
CREATE INDEX ix_inv_ingredient      ON fact_inventory_audit (ingredient_id);
CREATE INDEX ix_inv_week            ON fact_inventory_audit (week_start_date_key);
CREATE INDEX ix_waste_date          ON fact_waste_log (date_key);
CREATE INDEX ix_waste_ingredient    ON fact_waste_log (ingredient_id);
CREATE INDEX ix_waste_shift         ON fact_waste_log (shift_id);

-- (b) Truy vấn phân tích
CREATE INDEX ix_sales_store_date_product ON fact_sales (store_id, date_key, product_id);   -- D1/D2: doanh thu, Menu Mix theo cửa hàng × kỳ
CREATE INDEX ix_waste_store_ing_week     ON fact_waste_log (store_id, ingredient_id, week_no); -- D3: đối chiếu W với kiểm kê tuần
CREATE INDEX ix_date_week                ON dim_date (week_no);                                 -- gom ngày về tuần kiểm kê
