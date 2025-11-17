import pandas as pd
import streamlit as st
from src.analysis.report_generator import ReportGenerator

class AccountingSystem:
    """
    النظام المحاسبي الأساسي الذي يحتوي على منطق إنشاء القيود والتقارير المالية.
    """
    def __init__(self, df):
        self.df = df
        self.journal_entries = None
        self.report_generator = ReportGenerator(df)

    def create_journal_entries(self):
        """
        إنشاء قيود اليومية (القيد المزدوج) من حركات البنك.
        الافتراض: البنك هو الحساب المقابل لكل حركة.
        """
        if self.journal_entries is not None:
            return pd.DataFrame(self.journal_entries)
            
        journal_entries = []
        
        # التأكد من وجود الأعمدة المطلوبة
        if not all(col in self.df.columns for col in ['[SA]Processing Date', 'التفاصيل', 'مدين', 'دائن', 'الحساب المحاسبي']):
            st.error("أعمدة البيانات غير مكتملة لإنشاء قيود اليومية.")
            return pd.DataFrame()

        for index, row in self.df.iterrows():
            date = row['[SA]Processing Date']
            description = row['التفاصيل']
            debit = row['مدين']
            credit = row['دائن']
            account = row.get('الحساب المحاسبي', 'حسابات متنوعة')
            
            # الحركة المدينة (سحب من البنك)
            if debit > 0:
                entry = {
                    'التاريخ': date,
                    'الحساب المدين': account,
                    'المبلغ المدين': debit,
                    'الحساب الدائن': 'البنك',
                    'المبلغ الدائن': debit, # يجب أن يكون المبلغ الدائن مساوياً للمبلغ المدين
                    'الوصف': description
                }
                journal_entries.append(entry)
                
            # الحركة الدائنة (إيداع في البنك)
            if credit > 0:
                entry = {
                    'التاريخ': date,
                    'الحساب المدين': 'البنك',
                    'المبلغ المدين': credit, # يجب أن يكون المبلغ المدين مساوياً للمبلغ الدائن
                    'الحساب الدائن': account,
                    'المبلغ الدائن': credit,
                    'الوصف': description
                }
                journal_entries.append(entry)
        
        self.journal_entries = journal_entries
        journal_df = pd.DataFrame(self.journal_entries)
        return journal_df

    def generate_trial_balance(self):
        """إنشاء ميزان المراجعة."""
        if self.journal_entries is None:
            self.create_journal_entries()
        
        return self.report_generator.generate_trial_balance(self.journal_entries)

    def generate_income_statement(self):
        """إنشاء قائمة الدخل."""
        return self.report_generator.generate_income_statement()

    def generate_cash_flow_statement(self):
        """إنشاء قائمة التدفقات النقدية."""
        return self.report_generator.generate_cash_flow_statement()

    def generate_balance_sheet(self):
        """إنشاء الميزانية العمومية."""
        return self.report_generator.generate_balance_sheet()
