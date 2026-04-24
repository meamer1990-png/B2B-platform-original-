import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="مجموعة أبو الفتوح للتجارة", layout="wide")

# الرابط الخاص بملفك
URL = "https://docs.google.com/spreadsheets/d/1Ey5M-J_O50wvYty00cgZvsyKq_LLcQBmMwKWf_Nl_rk/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    st.error("فشل الاتصال.. تأكد من صلاحية الرابط في جوجل شيت (Editor)")

if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 دخول نظام أبو الفتوح")
    u_in = st.text_input("الاسم")
    p_in = st.text_input("كلمة المرور", type="password")
    
    if st.button("دخول"):
        try:
            # قراءة صفحة Users
            df = conn.read(spreadsheet=URL, worksheet="Users")
            
            # معالجة ذكية للأعمدة: إزالة المسافات وتوحيد التنسيق
            df.columns = [str(c).strip() for c in df.columns]
            
            # البحث عن الصفوف المطابقة
            # نستخدم .astype(str) لضمان مقارنة النصوص بشكل صحيح
            user_found = df[
                (df['الاسم'].astype(str).str.strip() == u_in.strip()) & 
                (df['كلمة_المرور'].astype(str).str.strip() == p_in.strip())
            ]
            
            if not user_found.empty:
                st.session_state.auth = True
                st.session_state.role = user_found.iloc[0]['الصلاحية']
                st.session_state.u_name = u_in
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة")
                st.info("تأكد من كتابة البيانات في الشيت بنفس الطريقة (admin1 / 123)")
        except Exception as e:
            st.error(f"حدث خطأ في القراءة: {e}")
            st.warning("تأكد من تسمية الصفحة بالأسفل Users وأن الأعمدة هي: الاسم | كلمة_المرور | الصلاحية")
else:
    # واجهة النظام بعد الدخول
    st.sidebar.success(f"مرحباً: {st.session_state.u_name}")
    role = st.session_state.role
    
    if st.sidebar.button("خروج"):
        st.session_state.auth = False
        st.rerun()
        
    st.header(f"لوحة التحكم - بصلاحية: {role}")
    
    if role == "Control":
        st.subheader("📊 تقارير الإدارة العامة")
    elif role == "Sales":
        st.subheader("📑 تسجيل طلبيات المندوب")
