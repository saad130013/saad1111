import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF

def format_currency(value):
    """تنسيق القيمة كعملة بالريال السعودي."""
    return f"{value:,.2f} ريال"

def to_excel(df):
    """تحويل DataFrame إلى ملف Excel في الذاكرة."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Report')
    processed_data = output.getvalue()
    return processed_data

def to_pdf(title, df=None, report_data=None):
    """تحويل البيانات إلى ملف PDF في الذاكرة."""
    
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, title, 0, 1, 'C')
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

        def chapter_title(self, title):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 6, title, 0, 1, 'L')
            self.ln(2)

        def chapter_body(self, body):
            self.set_font('Arial', '', 10)
            self.multi_cell(0, 5, body)
            self.ln()

        def print_table(self, df):
            # عرض الجدول
            self.set_font('Arial', 'B', 10)
            col_widths = [self.w / (len(df.columns) + 1)] * len(df.columns)
            
            # رؤوس الأعمدة
            for i, header in enumerate(df.columns):
                self.cell(col_widths[i], 7, str(header), 1, 0, 'C')
            self.ln()
            
            # صفوف البيانات
            self.set_font('Arial', '', 10)
            for index, row in df.iterrows():
                for i, col in enumerate(df.columns):
                    self.cell(col_widths[i], 6, str(row[col]), 1, 0, 'C')
                self.ln()

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # إضافة محتوى التقرير
    if df is not None and not df.empty:
        pdf.print_table(df)
    
    if report_data is not None:
        for section, items in report_data.items():
            pdf.chapter_title(section)
            if isinstance(items, dict):
                for item, value in items.items():
                    pdf.chapter_body(f"{item}: {format_currency(value)}")
            else:
                pdf.chapter_body(f"{section}: {format_currency(items)}")

    # ملاحظة: FPDF لا يدعم اللغة العربية بشكل كامل بدون خطوط مخصصة.
    # قد تحتاج إلى استخدام مكتبة أخرى أو تثبيت خط يدعم العربية على نظام التشغيل.
    
    return pdf.output(dest='S').encode('latin-1')

def display_dataframe(title, df):
    """عرض جدول بيانات مع عنوان وأزرار تصدير."""
    st.subheader(title)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        # أزرار التصدير
        col1, col2 = st.columns(2)
        
        # تصدير Excel
        excel_data = to_excel(df)
        col1.download_button(
            label="📥 تصدير إلى Excel",
            data=excel_data,
            file_name=f"{title.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        # تصدير PDF
        pdf_data = to_pdf(title, df=df)
        col2.download_button(
            label="📥 تصدير إلى PDF",
            data=pdf_data,
            file_name=f"{title.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.info(f"لا توجد بيانات لعرضها في {title}.")

def display_report_metrics(title, report_data):
    """عرض تقارير قائمة الدخل والتدفقات النقدية والميزانية العمومية باستخدام st.metric وأزرار تصدير."""
    st.subheader(title)
    
    # عرض التقرير
    if title == "قائمة الدخل":
        st.markdown("#### الإيرادات")
        for item, value in report_data['الإيرادات'].items():
            st.metric(item, format_currency(value))
            
        st.markdown("#### المصروفات")
        for item, value in report_data['المصروفات'].items():
            st.metric(item, format_currency(value))
            
        st.markdown("---")
        st.metric("صافي الدخل", format_currency(report_data['صافي الدخل']), 
                  delta=format_currency(report_data['صافي الدخل']))
                  
    elif title == "قائمة التدفقات النقدية":
        for item, value in report_data.items():
            st.metric(item, format_currency(value))
            
    elif title == "الميزانية العمومية":
        for section, items in report_data.items():
            st.markdown(f"#### {section}")
            for item, value in items.items():
                st.metric(item, format_currency(value))

    # أزرار التصدير للتقارير غير الجدولية
    col1, col2 = st.columns(2)
    
    # تصدير PDF
    pdf_data = to_pdf(title, report_data=report_data)
    col1.download_button(
        label="📥 تصدير إلى PDF",
        data=pdf_data,
        file_name=f"{title.replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

def display_summary_metrics(income, cash_flow, balance_sheet):
    """عرض الملخص السريع في لوحة التحكم."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💰 إجمالي الإيرادات", format_currency(income['الإيرادات']['إجمالي الإيرادات']))
        st.metric("💸 إجمالي المصروفات", format_currency(income['المصروفات']['إجمالي المصروفات']))
    
    with col2:
        st.metric("📈 صافي الدخل", format_currency(income['صافي الدخل']), 
                  delta=format_currency(income['صافي الدخل']))
        st.metric("🏦 الرصيد النهائي", format_currency(cash_flow['الرصيد النقدي في نهاية الفترة']))
    
    with col3:
        st.metric("💳 التدفق النقدي الصافي", format_currency(cash_flow['صافي الزيادة (النقص) في النقد']))
        st.metric("📊 إجمالي الأصول", format_currency(balance_sheet['الأصول']['إجمالي الأصول']))
