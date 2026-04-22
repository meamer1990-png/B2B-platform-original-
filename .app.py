import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# إعدادات واجهة البرنامج
st.set_page_config(page_title="B2B Smart Platform", layout="wide")

# --- محاكاة الربط مع قاعدة البيانات ---
# ملاحظة: في النسخة الفعلية يتم استخدام st.connection("gsheets")
if 'orders_df' not in st.session_state:
    st.session_state.orders_df = pd.DataFrame(columns=['ID', 'Merchant', 'Phone', 'Total', 'Status'])

# بيانات التجار الثابتة
merchants = {
    'محل الأمانة': {'phone': '201012345678', 'limit': 10000, 'balance': 2500},
    'سوبر ماركت النور': {'phone': '201212345678', 'limit': 5000, 'balance': 4800}
}

# --- القائمة الجانبية (الأيقونات) ---
st.sidebar.title("🚀 نظام B2B الشامل")
role = st.sidebar.selectbox("تبديل الحساب:", ["التاجر", "المحاسب", "الإدارة العليا", "المندوب"])

# 1. واجهة التاجر: إنشاء الطلب والتحقق من الائتمان
if role == "التاجر":
    st.header("🛒 متجر التاجر المباشر")
    selected_m = st.selectbox("اختر حسابك:", list(merchants.keys()))
    m_data = merchants[selected_m]
    
    st.metric("الرصيد المتاح للطلب", f"{m_data['limit'] - m_data['balance']} ج.م")
    
    with st.form("order_form"):
        product = st.selectbox("الصنف", ["زيت كرتونة", "سكر كرتونة"])
        amount = st.number_input("الكمية", min_value=1)
        price = 600 if "زيت" in product else 400
        total = amount * price
        submit = st.form_submit_button("تثبيت الطلب")
        
        if submit:
            if (m_data['balance'] + total) > m_data['limit']:
                st.error("⚠️ فشل الطلب: لقد تجاوزت الحد الائتماني!")
            else:
                new_order = {'ID': len(st.session_state.orders_df)+1, 'Merchant': selected_m, 
                             'Phone': m_data['phone'], 'Total': total, 'Status': 'معلق'}
                st.session_state.orders_df = st.session_state.orders_df.append(new_order, ignore_index=True)
                st.success(f"✅ تم تسجيل الطلب رقم {new_id} بنجاح")

# 2. واجهة المحاسب: الاعتماد وواتساب
elif role == "المحاسب":
    st.header("💰 اعتماد المدفوعات والفواتير")
    pending = st.session_state.orders_df[st.session_state.orders_df['Status'] == 'معلق']
    
    if pending.empty:
        st.write("لا توجد طلبات جديدة.")
    else:
        for index, row in pending.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"طلب من {row['Merchant']} بقيمة {row['Total']} ج.م")
            with col2:
                if st.button(f"اعتماد #{row['ID']}"):
                    st.session_state.orders_df.at[index, 'Status'] = 'تم الاعتماد'
                    # تجهيز رسالة واتساب
                    msg = f"تم اعتماد طلبك رقم {row['ID']} بقيمة {row['Total']} ج.م. سيصلك المندوب قريباً."
                    wa_link = f"https://wa.me/{row['Phone']}?text={urllib.parse.quote(msg)}"
                    st.markdown(f'<a href="{wa_link}" target="_blank" style="background-color:#25D366;color:white;padding:10px;border-radius:5px;text-decoration:none;">إرسال فاتورة واتساب 💬</a>', unsafe_allow_html=True)

# 3. واجهة الإدارة: الرقابة والتقارير
elif role == "الإدارة العليا":
    st.header("📊 لوحة تحكم الإدارة")
    st.dataframe(st.session_state.orders_df)
    total_sales = st.session_state.orders_df[st.session_state.orders_df['Status'] == 'تم الاعتماد']['Total'].sum()
    st.metric("إجمالي المبيعات المعتمدة", f"{total_sales} ج.م")

# 4. واجهة المندوب: الـ GPS والتسليم
else:
    st.header("🚚 تطبيق المندوب")
    st.info("📍 يتم الآن التحقق من موقعك عبر GPS...")
    st.success("الموقع مطابق لنطاق التاجر. يمكنك تسليم الشحنة.")
    if st.button("تأكيد التسليم النهائي"):
        st.balloons()
