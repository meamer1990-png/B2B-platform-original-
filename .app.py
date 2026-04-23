import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# --- 1. إعدادات النظام المتقدمة ---
st.set_page_config(page_title="B2B Enterprise System", layout="wide")

# --- 2. محاكاة قاعدة البيانات الشاملة (RBAC & Logic) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        'users': [
            {'name': 'Admin', 'role': 'Super Admin', 'phone': '2010'},
            {'name': 'Hossam', 'role': 'Accountant', 'phone': '2011'},
            {'name': 'Maged', 'role': 'Sales Rep', 'phone': '2012'}
        ],
        'merchants': [
            {'name': 'محل الأمانة', 'phone': '201012345678', 'credit_limit': 10000.0, 'balance': 2000.0, 'zone': 'كفر الشيخ', 'status': 'نشط'},
            {'name': 'سوبر ماركت النور', 'phone': '201212345678', 'credit_limit': 5000.0, 'balance': 4800.0, 'zone': 'سيدي سالم', 'status': 'نشط'}
        ],
        'warehouses': {
            'كفر الشيخ': {'شاي': 100, 'ملح': 200},
            'سيدي سالم': {'شاي': 50, 'ملح': 30},
            'المخزن الرئيسي': {'شاي': 1000, 'ملح': 1000}
        },
        'orders': []
    }

# --- 3. بوابة الدخول بنظام الأدوار (RBAC) ---
st.sidebar.title("🔐 نظام الصلاحيات الموحد")
user_role = st.sidebar.selectbox("الدخول بصلاحية:", 
    ["Super Admin", "Back Office", "Accountant", "Sales Rep", "Merchant"])

# ---------------------------------------------------------
# 1. Super Admin: الإدارة العليا والنتائج النهائية
# ---------------------------------------------------------
if user_role == "Super Admin":
    st.header("📊 لوحة القيادة - الرقم النهائي")
    col1, col2, col3 = st.columns(3)
    total_sales = sum(o['total'] for o in st.session_state.db['orders'] if o['status'] == 'Delivered')
    col1.metric("إجمالي الأرباح المحققة", f"{total_sales} ج.م")
    col2.metric("التجار النشطين", len(st.session_state.db['merchants']))
    col3.metric("المخازن المفعلة", len(st.session_state.db['warehouses']))
    
    st.subheader("📦 حالة المخازن والمناطق")
    st.write(st.session_state.db['warehouses'])

# ---------------------------------------------------------
# 2. Accountant: الرقابة المالية والائتمان
# ---------------------------------------------------------
elif user_role == "Accountant":
    st.header("💰 الإدارة المالية والائتمان")
    
    tab1, tab2 = st.tabs(["مراجعة الطلبات", "إدارة الائتمان"])
    
    with tab1:
        pending = [o for o in st.session_state.db['orders'] if o['status'] == 'Awaiting Payment']
        if not pending: st.write("لا توجد فواتير بانتظار الاعتماد.")
        for i, order in enumerate(pending):
            if st.button(f"اعتماد تحويل {order['merchant']} بمبلغ {order['total']}"):
                order['status'] = 'Approved'
                st.success("تم الاعتماد وتوجيه الطلب للمخزن")
    
    with tab2:
        st.subheader("تعديل حدود الائتمان")
        df_m = pd.DataFrame(st.session_state.db['merchants'])
        edited_m = st.data_editor(df_m)
        if st.button("حفظ تحديثات الائتمان"):
            st.session_state.db['merchants'] = edited_m.to_dict('records')

# ---------------------------------------------------------
# 3. Sales Rep: العمل الميداني و GPS Geofencing
# ---------------------------------------------------------
elif user_role == "Sales Rep":
    st.header("🚚 تطبيق المندوب - العمل الميداني")
    st.info("نظام Geofencing: يتم التحقق من وجودك في نطاق 50 متر من التاجر.")
    
    selected_m = st.selectbox("اختر التاجر للزيارة", [m['name'] for m in st.session_state.db['merchants']])
    location_check = st.checkbox("محاكاة الوصول لموقع التاجر (GPS)")
    
    if location_check:
        st.success("✅ تم التحقق من الموقع. يمكنك البدء.")
        action = st.radio("الإجراء:", ["زيارة سلبية", "تحصيل كاش", "إنشاء طلب بالنيابة"])
        if st.button("تسجيل العملية"):
            st.info("تم المزامنة مع السيرفر الرئيسي.")
    else:
        st.error("❌ لا يمكنك تسجيل عملية. أنت خارج نطاق التاجر.")

# ---------------------------------------------------------
# 4. Merchant: الطلب المباشر والائتمان
# ---------------------------------------------------------
elif user_role == "Merchant":
    st.header("🛒 طلب مباشر (خدمة ذاتية)")
    m_name = st.selectbox("اختر اسم محلك:", [m['name'] for m in st.session_state.db['merchants']])
    m_info = next(m for m in st.session_state.db['merchants'] if m['name'] == m_name)
    
    st.info(f"المنطقة: {m_info['zone']} | مديونيتك: {m_info['balance']} | حد الائتمان: {m_info['credit_limit']}")
    
    item = st.selectbox("المنتج", ["شاي", "ملح"])
    qty = st.number_input("الكمية", min_value=1)
    price = 100 # سعر أساسي محاكي
    total = qty * price
    
    if st.button("تأكيد الطلب الآجل"):
        # محرك الائتمان (Logic)
        if (m_info['balance'] + total) > m_info['credit_limit']:
            st.error("❌ الطلب مرفوض: تجاوزت الحد الائتماني المسموح.")
        else:
            # التوجيه الذكي (Smart Routing)
            warehouse = st.session_state.db['warehouses'].get(m_info['zone'], 'المخزن الرئيسي')
            if warehouse[item] >= qty:
                new_order = {'id': len(st.session_state.db['orders'])+1, 'merchant': m_name, 'total': total, 'status': 'Approved', 'wh': m_info['zone']}
                st.session_state.db['orders'].append(new_order)
                st.success(f"✅ تم التوجيه لمخزن {m_info['zone']} بنجاح")
            else:
                st.warning("⚠️ الصنف غير كافٍ في مخزن المنطقة. يتم التحويل للمخزن الرئيسي...")
                new_order = {'id': len(st.session_state.db['orders'])+1, 'merchant': m_name, 'total': total, 'status': 'Approved', 'wh': 'المخزن الرئيسي'}
                st.session_state.db['orders'].append(new_order)

# ---------------------------------------------------------
# 5. Back Office: العمليات اليومية
# ---------------------------------------------------------
elif user_role == "Back Office":
    st.header("⚙️ إدارة العمليات اليومية")
    st.subheader("متابعة دورة حياة الطلبات")
    df_orders = pd.DataFrame(st.session_state.db['orders'])
    st.table(df_orders)
        
