import pandas as pd
import streamlit as st

class DataCleaner:
    """
    مسؤول عن تنظيف ومعالجة البيانات الأولية.
    """
    def __init__(self, df):
        self.df = df

    def clean_data(self):
        """
        تنظيف البيانات ومعالجتها لتكون جاهزة للتحليل المحاسبي.
        """
        if self.df is None:
            return None
            
        # التأكد من وجود الأعمدة الأساسية (قد تحتاج إلى تعديل أسماء الأعمدة حسب ملف البنك الفعلي)
        required_columns = ['[SA]Processing Date', 'مدين', 'دائن', 'الرصيد', 'التفاصيل']
        for col in required_columns:
            if col not in self.df.columns:
                st.warning(f"⚠️ العمود '{col}' غير موجود في الملف. قد تحدث أخطاء.")
        
        # 1. تحويل التواريخ
        date_col = '[SA]Processing Date'
        if date_col in self.df.columns:
            self.df[date_col] = pd.to_datetime(self.df[date_col], errors='coerce')
            self.df = self.df.dropna(subset=[date_col]) # إزالة الصفوف التي لا تحتوي على تاريخ صالح
        
        # 2. تنظيف الأعمدة النقدية
        numeric_columns = ['مدين', 'دائن', 'الرصيد']
        for col in numeric_columns:
            if col in self.df.columns:
                # تحويل إلى رقمي وإزالة أي فواصل أو رموز غير ضرورية
                self.df[col] = self.df[col].astype(str).str.replace(r'[^\d\.\-]', '', regex=True)
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)
                # **التصحيح:** التأكد من أن قيم المدين والدائن موجبة (المطلق)
                if col in ['مدين', 'دائن']:
                    self.df[col] = self.df[col].abs()
        
        # 3. إضافة أعمدة مساعدة
        if date_col in self.df.columns:
            self.df['الشهر'] = self.df[date_col].dt.month
            self.df['السنة'] = self.df[date_col].dt.year
            self.df['التاريخ'] = self.df[date_col].dt.date # عمود تاريخ بسيط
        
        st.success("✅ تم تنظيف البيانات ومعالجتها بنجاح")
        return self.df
