import pandas as pd
import numpy as np
from report_generator import ReportGenerator

class AccountingSystem:
    """
    مسؤول عن تجميع البيانات المصنفة وتوليد التقارير المحاسبية الرئيسية.
    """
    def __init__(self, df):
        self.df = df
        self.report_generator = ReportGenerator(df)
        self.journal_entries = None

    def create_journal_entries(self):
        """
        توليد قيود اليومية من حركات كشف الحساب.
        """
        if self.journal_entries is not None:
            return self.journal_entries
            
        journal_entries = []
        
        # 1. تحديد الحسابات المدينة والدائنة لكل حركة
        for index, row in self.df.iterrows():
            account = row['الحساب المحاسبي']
            amount_debit = row['مدين']
            amount_credit = row['دائن']
            details = row['التفاصيل']
            date = row['[SA]Processing Date']
            
            # الحركة المدينة (مصروفات، سحوبات، أصول)
            if amount_debit > 0:
                # القيد: [الحساب المصنف] مدين / [البنك] دائن
                journal_entries.append({
                    'التاريخ': date,
                    'الحساب المدين': account,
                    'الحساب الدائن': 'البنك',
                    'المبلغ المدين': amount_debit,
                    'المبلغ الدائن': amount_debit,
                    'الوصف': details
                })
            
            # الحركة الدائنة (إيرادات، إيداعات، خصوم)
            elif amount_credit > 0:
                # القيد: [البنك] مدين / [الحساب المصنف] دائن
                journal_entries.append({
                    'التاريخ': date,
                    'الحساب المدين': 'البنك',
                    'الحساب الدائن': account,
                    'المبلغ المدين': amount_credit,
                    'المبلغ الدائن': amount_credit,
                    'الوصف': details
                })
                
        self.journal_entries = pd.DataFrame(journal_entries)
        return self.journal_entries

    def generate_trial_balance(self):
        """
        توليد ميزان المراجعة.
        """
        journal_entries = self.create_journal_entries()
        return self.report_generator.generate_trial_balance(journal_entries)

    def generate_income_statement(self):
        """
        توليد قائمة الدخل.
        """
        return self.report_generator.generate_income_statement()

    def generate_cash_flow_statement(self):
        """
        توليد قائمة التدفقات النقدية.
        """
        return self.report_generator.generate_cash_flow_statement()

    def generate_balance_sheet(self):
        """
        توليد الميزانية العمومية.
        """
        return self.report_generator.generate_balance_sheet()
