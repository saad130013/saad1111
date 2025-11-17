import streamlit as st
from accounting_system import AccountingSystem
from data_loader import DataLoader
from data_cleaner import DataCleaner
from transaction_classifier import TransactionClassifier
from report_generator import ReportGenerator
from ui_utils import display_report_metrics, display_dataframe, display_summary_metrics

# إعداد صفحة Streamlit
st.set_page_config(page_title="المحاسب الذكي المحترف", page_icon="🏦", layout="wide")

st.title("🏦 النظام المحاسبي المتكامل المحترف")
st.markdown("---")

def main():
    """الواجهة الرئيسية لتطبيق Streamlit"""
    st.sidebar.title("📁 رفع الملف")
    uploaded_file = st.sidebar.file_uploader("اختر ملف كشف الحساب البنكي (Excel)", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        try:
            # 1. تحميل وتنظيف البيانات
            st.info("جاري تحميل ومعالجة البيانات...")
            data_loader = DataLoader(uploaded_file)
            df = data_loader.load_data()
            
            if df is None:
                st.error("فشل تحميل البيانات. يرجى التأكد من صيغة الملف.")
                return

            data_cleaner = DataCleaner(df)
            df = data_cleaner.clean_data()
            
            # 2. تصنيف الحركات
            classifier = TransactionClassifier(df)
            df = classifier.classify_transactions()
            
            # 3. إنشاء النظام المحاسبي
            accounting_system = AccountingSystem(df)
            
            st.success("✅ تم تجهيز البيانات بنجاح للتحليل المحاسبي.")
            st.markdown("---")
            
            # عرض لوحة التحكم (Dashboard)
            st.subheader("لوحة التحكم والملخص السريع")
            
            # حساب وعرض الملخص السريع
            income_statement = accounting_system.generate_income_statement()
            cash_flow = accounting_system.generate_cash_flow_statement()
            balance_sheet = accounting_system.generate_balance_sheet()
            
            display_summary_metrics(income_statement, cash_flow, balance_sheet)
            
            st.markdown("---")
            st.subheader("📊 التقارير المحاسبية التفصيلية")
            
            # أزرار التقارير
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📖 قيود اليومية", use_container_width=True):
                    with st.spinner('📖 جاري إنشاء قيود اليومية...'):
                        journal_entries = accounting_system.create_journal_entries()
                        display_dataframe("قيود اليومية", journal_entries)
            
            with col2:
                if st.button("⚖️ ميزان المراجعة", use_container_width=True):
                    with st.spinner('⚖️ جاري إنشاء ميزان المراجعة...'):
                        trial_balance = accounting_system.generate_trial_balance()
                        display_dataframe("ميزان المراجعة", trial_balance)
            
            with col3:
                if st.button("📈 قائمة الدخل", use_container_width=True):
                    with st.spinner('📈 جاري إنشاء قائمة الدخل...'):
                        income_statement = accounting_system.generate_income_statement()
                        display_report_metrics("قائمة الدخل", income_statement)
            
            col4, col5, col6 = st.columns(3)
            
            with col4:
                if st.button("💸 التدفقات النقدية", use_container_width=True):
                    with st.spinner('💸 جاري إنشاء قائمة التدفقات النقدية...'):
                        cash_flow = accounting_system.generate_cash_flow_statement()
                        display_report_metrics("قائمة التدفقات النقدية", cash_flow)
            
            with col5:
                if st.button("🏦 الميزانية العمومية", use_container_width=True):
                    with st.spinner('🏦 جاري إنشاء الميزانية العمومية...'):
                        balance_sheet = accounting_system.generate_balance_sheet()
                        display_report_metrics("الميزانية العمومية", balance_sheet)
            
            with col6:
                if st.button("📊 تحليل المصروفات (ملخص)", use_container_width=True):
                    with st.spinner('📊 جاري إنشاء تحليل المصروفات...'):
                        expense_analysis = ReportGenerator.generate_expense_analysis(df)
                        display_dataframe("تحليل المصروفات (ملخص)", expense_analysis)
            
            # أزرار التقارير التفصيلية الجديدة
            st.markdown("---")
            st.subheader("📄 تقارير الحركات التفصيلية")
            
            col7, col8, col9 = st.columns(3)
            
            with col7:
                if st.button("⬇️ حركات المصروفات التفصيلية", use_container_width=True):
                    with st.spinner('⬇️ جاري إنشاء تقرير المصروفات...'):
                        detailed_expenses = ReportGenerator.generate_detailed_expense_report(df)
                        display_dataframe("حركات المصروفات التفصيلية", detailed_expenses)
            
            with col8:
                if st.button("⬆️ حركات الإيرادات التفصيلية", use_container_width=True):
                    with st.spinner('⬆️ جاري إنشاء تقرير الإيرادات...'):
                        detailed_revenues = ReportGenerator.generate_detailed_revenue_report(df)
                        display_dataframe("حركات الإيرادات التفصيلية", detailed_revenues)
            
            with col9:
                if st.button("📅 التقارير الشهرية", use_container_width=True):
                    with st.spinner('📅 جاري إنشاء التقارير الشهرية...'):
                        monthly_reports = ReportGenerator.generate_monthly_reports(df)
                        display_dataframe("التقارير الشهرية", monthly_reports)
            
            # تحليل الإيرادات (الملخص)
            st.markdown("---")
            if st.button("📈 تحليل الإيرادات (ملخص)", use_container_width=True):
                with st.spinner('📈 جاري إنشاء تحليل الإيرادات...'):
                    revenue_analysis = ReportGenerator.generate_revenue_analysis(df)
                    display_dataframe("تحليل الإيرادات (ملخص)", revenue_analysis)
                        
        except Exception as e:
            st.error(f"❌ حدث خطأ غير متوقع: {e}")
            st.exception(e)
    
    else:
        st.info("👆 يرجى رفع ملف كشف الحساب البنكي (Excel) لبدء التحليل")
        
        st.markdown("""
        ### 📋 الميزات المتاحة في النظام المحترف:
        - **هيكلة معيارية:** فصل منطق تحميل البيانات، التنظيف، التصنيف، والتقارير.
        - **تحليل محاسبي متكامل:** قيود يومية، ميزان مراجعة، قائمة دخل، تدفقات نقدية، وميزانية عمومية.
        - **تقارير تفصيلية:** تحليل المصروفات والإيرادات، وتقارير شهرية.
        - **واجهة مستخدم احترافية:** استخدام Streamlit لعرض النتائج بشكل جذاب ومنظم.
        """)

if __name__ == "__main__":
    main()
