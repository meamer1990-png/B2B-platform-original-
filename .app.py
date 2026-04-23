import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# --- 1. إعداد النظام ---
st.set_page_config(page_title="B2B-Platform", layout="wide")

# --- 2. إدارة البيانات في الذاكرة ---
if 'merchants_db' not in st.session_state:
    st.session_state.merchants_db = pd.DataFrame([
        {'Merchant': 'محل الأمانة', 'Phone': '201012345678', 'Limit': 10000.0, 'Balance': 0.0, 'Status': 'Active'},
        {'Merchant': 'سوبر ماركت النور', 'Phone': '201212345678', 'Limit': 5000.0, 'Balance': 0.0, 'Status': 'Active'}
    ])

if 'orders_db' not in st.session_state:
    st.session_state.orders_db = pd.DataFrame(columns=['ID', 'Merchant', 'Total', 'Status'])

# --- 3. القائمة الجانبية ---
st.sidebar.title("إدارة المنصة")
role = st.sidebar.radio("تبديل المستخدم:", ["الإدارة (التحكم الكامل)", "المحاسب", "التاجر"])

# --- 4. واجهة الإدارة (إضافة التجار والائتمان) ---
if role == "الإدارة (التحكم الكامل)":
    st.header("إدارة التجار والائتمان")
    
    with st.expander("تسجيل تاجر جديد"):
        name = st.text_input("اسم المحل")
        phone = st.text_input("رقم الواتساب (مثال: 201012345678)")
        credit = st.number_input("الحد الائتماني", min_value=0.0)
        if st.button("حفظ"):
            new_m = pd.DataFrame([{'Merchant': name, 'Phone': phone, 'Limit': credit, 'Balance': 0.0, 'Status': 'Active'}])
            st.session_state.merchants_db = pd.concat([st.session_state.merchants_db, new_m], ignore_index=True)
            st.success("تم الحفظ")

    st.subheader("تعديل الائتمان والإيقاف")
    st.session_state.merchants_db = st.data_editor(st.session_state.merchants_db)

# --- 5. واجهة التاجر (إنشاء طلب) ---
elif role == "التاجر":
    st.header("طلب بضاعة")
    active_m = st.session_state.merchants_db[st.session_state.merchants_db['Status'] == 'Active']
    m_name = st.selectbox("اختر اسمك:", active_m['Merchant'])
    m_info = active_m[active_m['Merchant'] == m_name].iloc[0]
    
    st.info(f"حدك الائتماني: {m_info['Limit']} | مديونيتك: {m_info['Balance']}")
    amount = st.number_input("قيمة الطلب", min_value=1.0)
    
    if st.button("تثبيت الطلب"):
        if (m_info['Balance'] + amount) > m_info['Limit']:
            st.error("عذراً، تخطيت حد الائتمان")
        else:
            new_order = pd.DataFrame([{'ID': len(st.session_state.orders_db)+1, 'Merchant': m_name, 'Total': amount, 'Status': 'Pending'}])
            st.session_state.orders_db = pd.concat([st.session_state.orders_db, new_order], ignore_index=True)
            st.success("تم إرسال الطلب للمحاسب")

# --- 6. واجهة المحاسب (الاعتماد وواتساب) ---
elif role == "المحاسب":
    st.header("اعتماد الفواتير")
    pending = st.session_state.orders_db[st.session_state.orders_db['Status'] == 'Pending']
    
    for idx, row in pending.iterrows():
        st.write(f"طلب من {row['Merchant']} بمبلغ {row['Total']}")
        if st.button(f"اعتماد طلب رقم {row['ID']}"):
            st.session_state.orders_db.at[idx, 'Status'] = 'Approved'
            
            # جلب الهاتف وإرسال واتساب
            phone = st.session_state.merchants_db[st.session_state.merchants_db['Merchant'] == row['Merchant']]['Phone'].values[0]
            msg = f"تم قبول طلبك رقم {row['ID']} بمبلغ {row['Total']}"
            wa_link = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{wa_link}" target="_blank" style="background-color:#25D366;color:white;padding:10px;border-radius:5px;text-decoration:none;">إرسال واتساب 💬</a>', unsafe_allow_html=True)
