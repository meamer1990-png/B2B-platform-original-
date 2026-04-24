import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import urllib.parse

# --- إعدادات النظام ---
st.set_page_config(page_title="مجموعة أبو الفتوح للتجارة", layout="wide")

# الرابط الخاص بملفك (تأكد أنه متاح للجميع Editor)
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1Ey5M-J_O50wvYty00cgZvsyKq_LLcQBmMwKWf_Nl_rk/edit?usp=sharing"

# --- الاتصال بجوجل شيت ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    st.error("فشل الاتصال بجدول البيانات. تأكد من تفعيل المشاركة.")

# --- نظام تسجيل الدخول ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 بوابة الدخول الموحدة - نظام أبو الفتوح")
    user_input = st.text_input("اسم المستخدم")
    pw_input = st.text_input("كلمة المرور", type="password")
    
    if st.button("دخول"):
        try:
            # قراءة صفحة المستخدمين
            df_users = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Users")
            
            # تنظيف البيانات من أي مسافات زائدة لضمان المطابقة
            df_users['اسم المستخدم'] = df_users['اسم المستخدم'].astype(str).str.strip()
            df_users['كلمة المرور'] = df_users['كلمة المرور'].astype(str).str.strip()
            
            # مطابقة البيانات
            user_match = df_users[(df_users['اسم المستخدم'] == user_input.strip()) & 
                                  (df_users['كلمة المرور'] == pw_input.strip())]
            
            if not user_match.empty:
                st.session_state.logged_in = True
                st.session_state.role = user_match.iloc[0]['الصلاحية']
                st.session_state.user_name = user_input
                st.rerun()
            else:
                st.error("بيانات الدخول غير صحيحة")
        except Exception as e:
            st.error(f"تأكد من وجود صفحة 'Users' والعناوين: اسم المستخدم، كلمة المرور، الصلاحية")
else:
    # --- الواجهة بعد الدخول الناجح ---
    role = st.session_state.role
    st.sidebar.success(f"مرحباً: {st.session_state.user_name}")
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.rerun()

    # توزيع النوافذ حسب الصلاحية المكتوبة في الشيت
    if role == "الكنترول":
        st.header("🖥️ لوحة تحكم الإدارة العليا")
        st.write("أهلاً بك يا دكتور محمد.")
    elif role == "المحاسب":
        st.header("💰 نافذة المحاسبة والمخازن")
    elif role == "مندوب":
        st.header("🚚 تطبيق الميدان للمناديب")
    elif role == "تاجر":
        st.header("🏪 نافذة التاجر والطلبات")
