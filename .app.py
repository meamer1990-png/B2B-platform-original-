import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# إعداد الصفحة
st.set_page_config(page_title="نظام أبو الفتوح للتجارة", layout="wide")

# رابط الشيت الخاص بك
URL = "https://docs.google.com/spreadsheets/d/1Ey5M-J_O50wvYty00cgZvsyKq_LLcQBmMwKWf_Nl_rk/edit?usp=sharing"

# الاتصال بجوجل شيت
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    st.error("خطأ في الاتصال بالقاعدة")

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# شاشة الدخول
if not st.session_state.authenticated:
    st.title("🔐 تسجيل دخول - مجموعة أبو الفتوح")
    u_input = st.text_input("الاسم")
    p_input = st.text_input("كلمة المرور", type="password")
    
    if st.button("دخول"):
        try:
            # قراءة صفحة Users
            df = conn.read(spreadsheet=URL, worksheet="Users")
            # تنظيف أي مسافات زائدة في أسماء الأعمدة أو البيانات
            df.columns = df.columns.str.strip()
            
            # مطابقة البيانات بناءً على العناوين التي حددتها: الاسم | كلمة_المرور | الصلاحية
            user_row = df[(df['الاسم'].astype(str).str.strip() == u_input.strip()) & 
                          (df['كلمة_المرور'].astype(str).str.strip() == p_input.strip())]
            
            if not user_row.empty:
                st.session_state.authenticated = True
                st.session_state.user_role = user_row.iloc[0]['الصلاحية']
                st.session_state.user_name = u_input
                st.rerun()
            else:
                st.error("بيانات الدخول غير صحيحة")
        except Exception as e:
            st.error("تأكد من تسمية الصفحة 'Users' والعناوين: الاسم، كلمة_المرور، الصلاحية")
else:
    # الواجهة الرئيسية بعد الدخول
    role = st.session_state.user_role
    st.sidebar.success(f"مرحباً: {st.session_state.user_name}")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.authenticated = False
        st.rerun()
    
    st.header(f"لوحة تحكم: {role}")
    
    # توزيع المهام حسب الصلاحية (Control أو غيرها)
    if role == "Control":
        st.subheader("إحصائيات الإدارة")
        # هنا سيتم لاحقاً سحب بيانات من صفحة Orders و Merchants
    elif role == "Sales":
        st.subheader("تسجيل طلبات المناديب")
