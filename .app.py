import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import urllib.parse

# --- إعدادات النظام ---
st.set_page_config(page_title="مجموعة أبو الفتوح للتجارة", layout="wide")

# الرابط الخاص بملفك
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1Ey5M-J_O50wvYty00cgZvsyKq_LLcQBmMwKWf_Nl_rk/edit?usp=sharing"

# --- الاتصال بجوجل شيت ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    st.error("فشل الاتصال بجدول البيانات. تأكد من تفعيل المشاركة (Anyone with the link can edit).")

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
            
            # تطابق البيانات مع العناوين العربية في الشيت
            # تأكد أن العناوين في الشيت هي: اسم المستخدم | كلمة المرور | الصلاحية
            user_match = df_users[(df_users['اسم المستخدم'].astype(str) == user_input) & 
                                  (df_users['كلمة المرور'].astype(str) == pw_input)]
            
            if not user_match.empty:
                st.session_state.logged_in = True
                st.session_state.role = user_match.iloc[0]['الصلاحية']
                st.session_state.user_name = user_input
                st.rerun()
            else:
                st.error("بيانات الدخول غير صحيحة (تحقق من اسم المستخدم أو الباسورد)")
        except Exception as e:
            st.warning("تأكد أن أسماء الأعمدة في صفحة Users هي: 'اسم المستخدم' و 'كلمة المرور' و 'الصلاحية'")
else:
    # الواجهة بعد الدخول الناجح
    role = st.session_state.role
    st.sidebar.success(f"مرحباً: {st.session_state.user_name}")
    st.sidebar.write(f"الصلاحية: {role}")
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.rerun()

    # استكمال باقي النوافذ (الكنترول، المحاسب، إلخ) بناءً على الصلاحية
    if role == "الكنترول":
        st.header("🖥️ لوحة تحكم الإدارة")
        st.info("أهلاً بك يا دكتور محمد في لوحة التحكم الرئيسية.")
    elif role == "المحاسب":
        st.header("💰 نافذة المحاسبة")
    elif role == "مندوب":
        st.header("🚚 تطبيق الميدان")
    elif role == "تاجر":
        st.header("🏪 نافذة التاجر")
