import pandas as pd
import numpy as np

class ReportGenerator:
    """
    مسؤول عن توليد التقارير المحاسبية المختلفة من البيانات المصنفة.
    """
    def __init__(self, df):
        self.df = df
        self.expense_accounts = ['مصاريف تشغيل', 'مصاريف مشتريات', 'مصاريف ضرائب', 'مصاريف بنكية', 'مصاريف أخرى']
        self.revenue_accounts = ['إيرادات متنوعة', 'إيرادات مبيعات', 'إيرادات أخرى']
        self.asset_accounts = ['البنك', 'أصول أخرى']
        self.liability_accounts = ['خصوم أخرى']
        self.equity_accounts = ['حقوق ملكية']

    def generate_trial_balance(self, journal_entries):
        """
        إنشاء ميزان المراجعة من قيود اليومية.
        """
        # 1. تجميع الحركات المدينة والدائنة لكل حساب
        debit_entries = journal_entries.groupby('الحساب المدين')['المبلغ المدين'].sum().reset_index()
        debit_entries.columns = ['الحساب', 'إجمالي المدين']
        
        credit_entries = journal_entries.groupby('الحساب الدائن')['المبلغ الدائن'].sum().reset_index()
        credit_entries.columns = ['الحساب', 'إجمالي الدائن']
        
        # 2. دمج الحسابات
        trial_balance = pd.merge(debit_entries, credit_entries, on='الحساب', how='outer').fillna(0)
        
        # 3. حساب الرصيد
        trial_balance['الرصيد المدين'] = np.where(trial_balance['إجمالي المدين'] >= trial_balance['إجمالي الدائن'], 
                                                  trial_balance['إجمالي المدين'] - trial_balance['إجمالي الدائن'], 0)
        trial_balance['الرصيد الدائن'] = np.where(trial_balance['إجمالي الدائن'] > trial_balance['إجمالي المدين'], 
                                                  trial_balance['إجمالي الدائن'] - trial_balance['إجمالي المدين'], 0)
        
        # 4. تجميع نهائي
        final_tb = trial_balance[['الحساب', 'إجمالي المدين', 'إجمالي الدائن', 'الرصيد المدين', 'الرصيد الدائن']]
        
        # 5. إضافة الإجماليات
        totals = pd.DataFrame({
            'الحساب': ['الإجمالي'],
            'إجمالي المدين': [final_tb['إجمالي المدين'].sum()],
            'إجمالي الدائن': [final_tb['إجمالي الدائن'].sum()],
            'الرصيد المدين': [final_tb['الرصيد المدين'].sum()],
            'الرصيد الدائن': [final_tb['الرصيد الدائن'].sum()]
        })
        
        final_tb = pd.concat([final_tb, totals], ignore_index=True)
        return final_tb

    def generate_income_statement(self):
        """
        إنشاء قائمة الدخل (الإيرادات والمصروفات).
        """
        # الإيرادات
        revenue_data = self.df[self.df['الحساب المحاسبي'].isin(self.revenue_accounts)]
        total_revenues = revenue_data['دائن'].sum()
        
        # المصروفات
        expense_data = self.df[self.df['الحساب المحاسبي'].isin(self.expense_accounts)]
        total_expenses = expense_data['مدين'].sum()
        
        net_income = total_revenues - total_expenses
        
        report = {
            'الإيرادات': {
                'إجمالي الإيرادات': total_revenues
            },
            'المصروفات': {
                'إجمالي المصروفات': total_expenses
            },
            'صافي الدخل': net_income
        }
        return report

    def generate_cash_flow_statement(self):
        """
        إنشاء قائمة التدفقات النقدية (بافتراض الطريقة المباشرة المبسطة).
        """
        # التدفقات التشغيلية (الفرق بين الإيرادات والمصروفات النقدية)
        income_statement = self.generate_income_statement()
        operating_cash_flow = income_statement['صافي الدخل']
        
        # التدفقات الاستثمارية (افتراض عدم وجود حركات استثمارية معقدة)
        investing_cash_flow = 0
        
        # التدفقات التمويلية (افتراض عدم وجود حركات تمويلية معقدة)
        financing_cash_flow = 0
        
        net_cash_flow = operating_cash_flow + investing_cash_flow + financing_cash_flow
        
        # الرصيد النقدي في بداية الفترة
        opening_balance = self.df['الرصيد'].iloc[0] - self.df['دائن'].iloc[0] + self.df['مدين'].iloc[0] if not self.df.empty else 0
        
        # الرصيد النقدي في نهاية الفترة
        closing_balance = self.df['الرصيد'].iloc[-1] if not self.df.empty else 0
        
        report = {
            'الرصيد النقدي في بداية الفترة': opening_balance,
            'التدفقات النقدية من الأنشطة التشغيلية': operating_cash_flow,
            'التدفقات النقدية من الأنشطة الاستثمارية': investing_cash_flow,
            'التدفقات النقدية من الأنشطة التمويلية': financing_cash_flow,
            'صافي الزيادة (النقص) في النقد': net_cash_flow,
            'الرصيد النقدي في نهاية الفترة': closing_balance
        }
        return report

    def generate_balance_sheet(self):
        """
        إنشاء الميزانية العمومية (المركز المالي).
        """
        # الأصول (رصيد البنك النهائي)
        total_assets = self.df['الرصيد'].iloc[-1] if not self.df.empty else 0
        
        # حقوق الملكية (رأس المال + صافي الدخل)
        net_income = self.generate_income_statement()['صافي الدخل']
        # نفترض أن رأس المال هو الرصيد الافتتاحي
        opening_balance = self.df['الرصيد'].iloc[0] - self.df['دائن'].iloc[0] + self.df['مدين'].iloc[0] if not self.df.empty else 0
        
        total_equity = opening_balance + net_income
        
        # الخصوم (افتراض صفر لتبسيط التحليل البنكي)
        total_liabilities = 0
        
        # التأكد من التوازن (الأصول = الخصوم + حقوق الملكية)
        difference = total_assets - (total_liabilities + total_equity)
        
        report = {
            'الأصول': {
                'إجمالي الأصول': total_assets
            },
            'الخصوم وحقوق الملكية': {
                'إجمالي الخصوم': total_liabilities,
                'إجمالي حقوق الملكية': total_equity,
                'الإجمالي': total_liabilities + total_equity
            },
            'فرق التوازن (يجب أن يكون صفر)': difference
        }
        return report

    def generate_expense_analysis(self, df):
        """
        تحليل المصروفات حسب الحسابات.
        """
        expense_df = df[df['الحساب المحاسبي'].isin(self.expense_accounts)]
        
        if expense_df.empty:
            return pd.DataFrame({'الحساب': ['لا توجد بيانات للمصروفات'], 'إجمالي المبلغ': [0], 'عدد الحركات': [0]})

        analysis = expense_df.groupby('الحساب المحاسبي')['مدين'].agg(
            إجمالي_المبلغ='sum',
            عدد_الحركات='count',
            متوسط_المبلغ='mean',
            أعلى_مبلغ='max'
        ).reset_index()
        
        analysis.columns = ['الحساب', 'إجمالي المصروفات', 'عدد الحركات', 'متوسط المبلغ', 'أعلى مبلغ']
        return analysis

    def generate_revenue_analysis(self, df):
        """
        تحليل الإيرادات حسب الحسابات.
        """
        revenue_df = df[df['الحساب المحاسبي'].isin(self.revenue_accounts)]
        
        if revenue_df.empty:
            return pd.DataFrame({'الحساب': ['لا توجد بيانات للإيرادات'], 'إجمالي المبلغ': [0], 'عدد الحركات': [0]})

        analysis = revenue_df.groupby('الحساب المحاسبي')['دائن'].agg(
            إجمالي_المبلغ='sum',
            عدد_الحركات='count',
            متوسط_المبلغ='mean',
            أعلى_مبلغ='max'
        ).reset_index()
        
        analysis.columns = ['الحساب', 'إجمالي الإيرادات', 'عدد الحركات', 'متوسط المبلغ', 'أعلى مبلغ']
        return analysis

    @staticmethod
    def generate_detailed_expense_report(df):
        """
        تقرير تفصيلي لحركات المصروفات.
        """
        expense_accounts = ['مصاريف تشغيل', 'مصاريف مشتريات', 'مصاريف ضرائب', 'مصاريف بنكية', 'مصاريف أخرى']
        
        expense_df = df[df['الحساب المحاسبي'].isin(expense_accounts)].copy()
        
        if expense_df.empty:
            return pd.DataFrame({'التاريخ': [], 'الوصف_الأصلي_للحركة': [], 'الحساب المحاسبي': [], 'المبلغ': []})

        report = expense_df[[
            '[SA]Processing Date', 
            'التفاصيل', 
            'الحساب المحاسبي', 
            'مدين'
        ]].rename(columns={
            '[SA]Processing Date': 'التاريخ',
            'التفاصيل': 'الوصف_الأصلي_للحركة',
            'مدين': 'المبلغ'
        })
        return report

    @staticmethod
    def generate_detailed_revenue_report(df):
        """
        تقرير تفصيلي لحركات الإيرادات.
        """
        revenue_accounts = ['إيرادات متنوعة', 'إيرادات مبيعات', 'إيرادات أخرى']
        
        revenue_df = df[df['الحساب المحاسبي'].isin(revenue_accounts)].copy()
        
        if revenue_df.empty:
            return pd.DataFrame({'التاريخ': [], 'الوصف_الأصلي_للحركة': [], 'الحساب المحاسبي': [], 'المبلغ': []})

        report = revenue_df[[
            '[SA]Processing Date', 
            'التفاصيل', 
            'الحساب المحاسبي', 
            'دائن'
        ]].rename(columns={
            '[SA]Processing Date': 'التاريخ',
            'التفاصيل': 'الوصف_الأصلي_للحركة',
            'دائن': 'المبلغ'
        })
        return report

    @staticmethod
    def generate_monthly_reports(df):
        """
        تقرير شهري للإيرادات والمصروفات.
        """
        if '[SA]Processing Date' not in df.columns:
            return pd.DataFrame()
            
        df['الشهر-السنة'] = df['[SA]Processing Date'].dt.to_period('M')
        
        # تجميع الإيرادات والمصروفات شهرياً
        monthly_data = df.groupby('الشهر-السنة').agg(
            إجمالي_الإيرادات=('دائن', 'sum'),
            إجمالي_المصروفات=('مدين', 'sum')
        ).reset_index()
        
        monthly_data['صافي_الدخل'] = monthly_data['إجمالي_الإيرادات'] - monthly_data['إجمالي_المصروفات']
        
        return monthly_data
