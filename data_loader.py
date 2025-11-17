import pandas as pd
import streamlit as st

class DataLoader:
    """
    مسؤول عن تحميل البيانات من الملف المرفوع.
    """
    def __init__(self, uploaded_file):
        self.uploaded_file = uploaded_file

    def load_data(self):
        """
        تحميل البيانات من ملف Excel المرفوع.
        """
        try:
            # قراءة الملف مع محاولة استخدام محركات مختلفة
            try:
                df = pd.read_excel(self.uploaded_file, engine='openpyxl')
            except ImportError:
                df = pd.read_excel(self.uploaded_file, engine='xlrd')
            
            st.success("✅ تم تحميل البيانات بنجاح")
            st.info(f"📊 عدد الحركات: {len(df)}")
            return df
        except Exception as e:
            st.error(f"❌ خطأ في تحميل الملف: {e}")
            st.exception(e)
            return None
