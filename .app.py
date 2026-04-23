-- تحديد الأدوار بشكل صارم
CREATE TYPE user_role AS ENUM ('super_admin', 'back_office', 'accountant', 'sales_rep', 'merchant');

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    phone_number VARCHAR(15) UNIQUE NOT NULL, -- مفتاح الحساب
    full_name VARCHAR(100),
    role user_role NOT NULL,
    territory_id INT, -- ربط المندوب أو التاجر بمنطقته
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE territories (
    id SERIAL PRIMARY KEY,
    governorate VARCHAR(50), -- المحافظة
    city VARCHAR(50),        -- المركز
    zone_name VARCHAR(50),   -- منطقة التوزيع
    assigned_warehouse_id INT, -- المخزن المسؤول عن هذه المنطقة
    assigned_sales_rep_id INT  -- المندوب المسؤول عن هذه المنطقة
);
async function getProductPrice(merchantId, productId) {
    const merchant = await db.merchants.find(merchantId);
    const product = await db.products.find(productId);
    
    let finalPrice = product.base_price;

    // 1. تسعير حسب فئة التاجر (جملة، نصف جملة، تجزئة)
    if (merchant.type === 'WHOLESALE') finalPrice -= product.wholesale_discount;

    // 2. تسعير حسب المنطقة (مصاريف شحن أو دعم منطقة)
    const zonePremium = await db.zone_prices.find(merchant.zone_id, productId);
    if (zonePremium) finalPrice += zonePremium.adjustment;

    // 3. عروض مؤقتة
    const activePromo = await db.promotions.findActive(productId);
    if (activePromo) finalPrice -= activePromo.discount_value;

    return finalPrice;
}
async function validateOrder(orderRequest) {
    const merchant = await db.merchants.find(orderRequest.merchantId);

    // شرط 1: حالة الحساب
    if (!merchant.is_active) throw new Error("الحساب موقوف، يرجى التواصل مع الإدارة");

    // شرط 2: الحد الائتماني
    const currentDebt = merchant.balance;
    if ((currentDebt + orderRequest.total) > merchant.credit_limit) {
        throw new Error("عفواً، لقد تخطيت الحد الائتماني المسموح به");
    }

    // شرط 3: توفر المخزون في أقرب مخزن
    const stock = await db.inventory.check(merchant.territory.warehouse_id, orderRequest.items);
    if (!stock.available) throw new Error("بعض الأصناف غير متوفرة في مخزن منطقتك");
    
    return "Order Validated";
}
CREATE TABLE merchants (
    id SERIAL PRIMARY KEY,
    business_name VARCHAR(255) NOT NULL,
    owner_name VARCHAR(255),
    phone_key VARCHAR(15) UNIQUE NOT NULL, -- رقم الهاتف هو الهوية (Login)
    gps_lat DECIMAL(10, 8),
    gps_long DECIMAL(11, 8),
    territory_id INT REFERENCES territories(id),
    merchant_type ENUM('Wholesale', 'Retail', 'Supermarket'), -- أنواع التجار للتسعير
    credit_limit DECIMAL(12, 2) DEFAULT 0.00, -- الحد الائتماني
    payment_terms_days INT DEFAULT 30, -- فترة السداد (مثلاً 30 يوم)
    current_balance DECIMAL(12, 2) DEFAULT 0.00, -- الرصيد الحالي
    is_active BOOLEAN DEFAULT true -- حالة الحساب
);
CREATE TABLE products (
    sku_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255),
    barcode VARCHAR(50) UNIQUE,
    unit_type ENUM('Carton', 'Packet'), -- وحدة البيع
    pieces_per_unit INT, -- عدد القطع بالكرتونة
    weight DECIMAL(5, 2),
    expiry_date DATE,
    base_price DECIMAL(10, 2) -- السعر الأساسي قبل الخصومات
);

CREATE TABLE warehouse_stock (
    warehouse_id INT REFERENCES warehouses(id),
    product_id INT REFERENCES products(sku_id),
    quantity INT DEFAULT 0, -- الكمية المتوفرة في هذا المخزن تحديداً
    min_order_limit INT DEFAULT 1,
    PRIMARY KEY (warehouse_id, product_id)
);
// دالة حساب السعر للتاجر عند فتح التطبيق
function calculateMerchantPrice(product, merchant) {
    let finalPrice = product.base_price;

    // 1. خصم نوع التاجر (مثلاً الجملة خصم 5%)
    if (merchant.merchant_type === 'Wholesale') {
        finalPrice *= 0.95;
    }

    // 2. خصم شريحة الكمية (مثلاً أكثر من 10 كراتين)
    if (order.quantity >= 10) {
        finalPrice -= 5.00; // خصم 5 جنيه على كل كرتونة
    }

    // 3. العروض المؤقتة (Flash Sales)
    if (currentDate >= promo.start && currentDate <= promo.end) {
        finalPrice -= promo.discount;
    }

    return finalPrice;
}
