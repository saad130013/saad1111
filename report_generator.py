import pandas as pd
import numpy as np

class ReportGenerator:
    """
    مسؤول عن توليد التقارير المالية والتحليلية المختلفة.
    """
    def __init__(self, df):
        self.df = df
        # تعريف أنواع الحسابات (يمكن توسيعها)
        self.account_types = {
            'إيرادات': ['إيرادات عمليات', 'إيرادات تحويلات', 'إيرادات متنوعة', 'إيرادات مبيعات', 'إيرادات إيداعات'],
            'مصروفات': ['مصاريف تشغيل', 'مصاريف مشتريات', 'مصاريف ضرائب', 'مصاريف بنكية', 'مصاريف سداد قروض', 'مصاريف رواتب', 'مصاريف إيجار', 'مصاريف خدمات'],
            'أصول': ['البنك', 'النقد', 'سحوبات نقدية'], # سحوبات نقدية هي سحب من الأصل (البنك)
            'خصوم_وحقوق_ملكية': ['حسابات متنوعة'] # يجب تحديدها بدقة أكبر في نظام محاسبي حقيقي
        }

    def get_account_type(self, account_name):
        """تحديد نوع الحساب (إيراد، مصروف، أصل، خصم/حقوق ملكية)."""
        for acc_type, accounts in self.account_types.items():
            if account_name in accounts:
                return acc_type
        return 'حسابات متنوعة'

    def generate_trial_balance(self, journal_entries):
        """إنشاء ميزان المراجعة من قيود اليومية."""
        trial_balance = {}
        
        for entry in journal_entries:
            debit_account = entry['الحساب المدين']
            credit_account = entry['الحساب الدائن']
            debit_amount = entry['المبلغ المدين']
            credit_amount = entry['المبلغ الدائن']
            
            # تحديث الحساب المدين
            if debit_account not in trial_balance:
                trial_balance[debit_account] = {'مدين': 0, 'دائن': 0}
            trial_balance[debit_account]['مدين'] += debit_amount
            
            # تحديث الحساب الدائن
            if credit_account not in trial_balance:
                trial_balance[credit_account] = {'مدين': 0, 'دائن': 0}
            trial_balance[credit_account]['دائن'] += credit_amount
        
        tb_data = []
        for account, balances in trial_balance.items():
            # تحديد الرصيد النهائي للحساب
            balance = balances['مدين'] - balances['دائن']
            
            # تحديد طبيعة الرصيد (مدين أو دائن)
            final_debit = balance if balance > 0 else 0
            final_credit = abs(balance) if balance < 0 else 0
            
            tb_data.append({
                'الحساب': account,
                'مجموع المدين': balances['مدين'],
                'مجموع الدائن': balances['دائن'],
                'الرصيد النهائي (مدين)': final_debit,
                'الرصيد النهائي (دائن)': final_credit
            })
        
        trial_balance_df = pd.DataFrame(tb_data)
        
        # إضافة إجمالي المجاميع
        total_row = {
            'الحساب': 'الإجمالي',
            'مجموع المدين': trial_balance_df['مجموع المدين'].sum(),
            'مجموع الدائن': trial_balance_df['مجموع الدائن'].sum(),
            'الرصيد النهائي (مدين)': trial_balance_df['الرصيد النهائي (مدين)'].sum(),
            'الرصيد النهائي (دائن)': trial_balance_df['الرصيد النهائي (دائن)'].sum()
        }
        
        # التأكد من توازن ميزان المراجعة
        if total_row['مجموع المدين'] != total_row['مجموع الدائن']:
            print("تحذير: ميزان المراجعة غير متوازن في المجاميع!")
        if total_row['الرصيد النهائي (مدين)'] != total_row['الرصيد النهائي (دائن)']:
            print("تحذير: ميزان المراجعة غير متوازن في الأرصدة!")
            
        trial_balance_df = pd.concat([trial_balance_df, pd.Series(total_row).to_frame().T], ignore_index=True)
        
        return trial_balance_df

    def generate_income_statement(self):
        """إنشاء قائمة الدخل (المصروفات والإيرادات)."""
        revenue_accounts = self.account_types['إيرادات']
        expense_accounts = self.account_types['مصروفات']
        
        # الإيرادات (الحركات الدائنة في كشف الحساب)
        revenue_data = self.df[self.df['الحساب المحاسبي'].isin(revenue_accounts)]
        total_revenue = revenue_data['دائن'].sum()
        
        # المصروفات (الحركات المدينة في كشف الحساب)
        expense_data = self.df[self.df['الحساب المحاسبي'].isin(expense_accounts)]
        total_expenses = expense_data['مدين'].sum()
        
        net_income = total_revenue - total_expenses
        
        # تجميع الإيرادات والمصروفات حسب الحساب
        revenues_by_account = revenue_data.groupby('الحساب المحاسبي')['دائن'].sum().to_dict()
        expenses_by_account = expense_data.groupby('الحساب المحاسبي')['مدين'].sum().to_dict()
        
        income_statement = {
            'الإيرادات': {**revenues_by_account, 'إجمالي الإيرادات': total_revenue},
            'المصروفات': {**expenses_by_account, 'إجمالي المصروفات': total_expenses},
            'صافي الدخل': net_income
        }
        
        return income_statement

    def generate_cash_flow_statement(self):
        """إنشاء قائمة التدفقات النقدية (الطريقة المباشرة المبسطة)."""
        
        # التدفقات النقدية من الأنشطة التشغيلية (الإيرادات التشغيلية - المصروفات التشغيلية)
        operating_revenue = self.df[self.df['الحساب المحاسبي'].isin(self.account_types['إيرادات'])]['دائن'].sum()
        operating_expense = self.df[self.df['الحساب المحاسبي'].isin(self.account_types['مصروفات'])]['مدين'].sum()
        cash_from_operations = operating_revenue - operating_expense
        
        # التدفقات النقدية من الأنشطة الاستثمارية (افتراض صفر لعدم وجود بيانات)
        cash_from_investing = 0
        
        # التدفقات النقدية من الأنشطة التمويلية (القروض، السحوبات الشخصية)
        financing_activities = self.df[self.df['الحساب المحاسبي'].isin(['مصاريف سداد قروض', 'سحوبات نقدية'])]
        cash_from_financing = financing_activities['دائن'].sum() - financing_activities['مدين'].sum()
        
        # صافي التغير في النقد
        net_cash_change = cash_from_operations + cash_from_investing + cash_from_financing
        
        # الرصيد النقدي في نهاية الفترة
        ending_balance = self.df['الرصيد'].iloc[-1] if not self.df.empty and 'الرصيد' in self.df.columns else 0
        
        # الرصيد النقدي في بداية الفترة
        opening_balance = ending_balance - net_cash_change
        
        cash_flow_statement = {
            'التدفقات النقدية من الأنشطة التشغيلية': cash_from_operations,
            'التدفقات النقدية من الأنشطة الاستثمارية': cash_from_investing,
            'التدفقات النقدية من الأنشطة التمويلية': cash_from_financing,
            'صافي الزيادة (النقص) في النقد': net_cash_change,
            'الرصيد النقدي في بداية الفترة': opening_balance,
            'الرصيد النقدي في نهاية الفترة': ending_balance
        }
        
        return cash_flow_statement

    def generate_balance_sheet(self):
        """إنشاء الميزانية العمومية (الميزانية)."""
        
        # الأصول (النقد والبنك)
        cash_balance = self.df['الرصيد'].iloc[-1] if not self.df.empty and 'الرصيد' in self.df.columns else 0
        total_assets = cash_balance
        
        # حقوق الملكية (رأس المال + صافي الدخل - سحوبات)
        income_statement = self.generate_income_statement()
        net_income = income_statement['صافي الدخل']
        
        # السحوبات الشخصية (افتراض أن السحوبات النقدية هي سحوبات شخصية)
        withdrawals = self.df[self.df['الحساب المحاسبي'] == 'سحوبات نقدية']['مدين'].sum()
        
        # افتراض أن رأس المال هو الفرق المتبقي لتوازن المعادلة
        # الأصول = الخصوم + حقوق الملكية
        # حقوق الملكية = رأس المال + صافي الدخل - سحوبات
        # الخصوم (افتراض صفر لعدم وجود بيانات)
        total_liabilities = 0
        
        # رأس المال = الأصول - الخصوم - (صافي الدخل - سحوبات)
        capital = total_assets - total_liabilities - (net_income - withdrawals)
        
        total_equity = capital + net_income - withdrawals
        
        balance_sheet = {
            'الأصول': {
                'النقد والبنك': cash_balance,
                'إجمالي الأصول': total_assets
            },
            'الخصوم': {
                'إجمالي الخصوم': total_liabilities
            },
            'حقوق الملكية': {
                'رأس المال': capital,
                'صافي الدخل': net_income,
                'سحوبات شخصية': withdrawals,
                'إجمالي حقوق الملكية': total_equity
            }
        }
        
        # التأكد من توازن الميزانية
        if round(total_assets, 2) != round(total_liabilities + total_equity, 2):
            print(f"تحذير: الميزانية غير متوازنة! الأصول: {total_assets}, الخصوم وحقوق الملكية: {total_liabilities + total_equity}")
            
        return balance_sheet

    @staticmethod
    def generate_detailed_expense_report(df):
        """توليد تقرير تفصيلي لحركات المصروفات."""
        expense_accounts = ['مصاريف تشغيل', 'مصاريف مشتريات', 'مصاريف ضرائب', 'مصاريف بنكية', 'مصاريف سداد قروض', 'مصاريف رواتب', 'مصاريف إيجار', 'مصاريف خدمات']
        
        # تصفية الحركات التي تم تصنيفها كمصروفات وكانت مدينة (سحب من البنك)
        detailed_expenses = df[
            (df['الحساب المحاسبي'].isin(expense_accounts)) & 
            (df['مدين'] > 0)
        ].copy()
        
        # اختيار الأعمدة المطلوبة للتقرير
        report_columns = ['التاريخ', 'التفاصيل', 'الحساب المحاسبي', 'مدين']
        if all(col in detailed_expenses.columns for col in report_columns):
            detailed_expenses = detailed_expenses[report_columns]
            detailed_expenses.rename(columns={'مدين': 'المبلغ', 'التفاصيل': 'الوصف_الأصلي_للحركة'}, inplace=True)
            return detailed_expenses.sort_values(by='التاريخ', ascending=False)
        else:
            return pd.DataFrame()

    @staticmethod
    def generate_detailed_revenue_report(df):
        """توليد تقرير تفصيلي لحركات الإيرادات."""
        revenue_accounts = ['إيرادات عمليات', 'إيرادات تحويلات', 'إيرادات متنوعة', 'إيرادات مبيعات', 'إيرادات إيداعات']
        
        # تصفية الحركات التي تم تصنيفها كإيرادات وكانت دائنة (إيداع في البنك)
        detailed_revenues = df[
            (df['الحساب المحاسبي'].isin(revenue_accounts)) & 
            (df['دائن'] > 0)
        ].copy()
        
        # اختيار الأعمدة المطلوبة للتقرير
        report_columns = ['التاريخ', 'التفاصيل', 'الحساب المحاسبي', 'دائن']
        if all(col in detailed_revenues.columns for col in report_columns):
            detailed_revenues = detailed_revenues[report_columns]
            detailed_revenues.rename(columns={'دائن': 'المبلغ', 'التفاصيل': 'الوصف_الأصلي_للحركة'}, inplace=True)
            return detailed_revenues.sort_values(by='التاريخ', ascending=False)
        else:
            return pd.DataFrame()

    @staticmethod
    def generate_expense_analysis(df):
        """تحليل المصروفات التفصيلي (دالة ثابتة)."""
        expense_data = df[df['مدين'] > 0].copy()
        
        if not expense_data.empty:
            expense_analysis = expense_data.groupby('الحساب المحاسبي').agg({
                'مدين': ['sum', 'count', 'mean', 'max']
            }).round(2)
            
            expense_analysis.columns = ['إجمالي المصروفات', 'عدد الحركات', 'متوسط المبلغ', 'أعلى مبلغ']
            expense_analysis = expense_analysis.sort_values(by='إجمالي المصروفات', ascending=False)
        else:
            expense_analysis = pd.DataFrame()
        
        return expense_analysis

    @staticmethod
    def generate_revenue_analysis(df):
        """تحليل الإيرادات التفصيلي (دالة ثابتة)."""
        revenue_data = df[df['دائن'] > 0].copy()
        
        if not revenue_data.empty:
            revenue_analysis = revenue_data.groupby('الحساب المحاسبي').agg({
                'دائن': ['sum', 'count', 'mean', 'max']
            }).round(2)
            
            revenue_analysis.columns = ['إجمالي الإيرادات', 'عدد الحركات', 'متوسط المبلغ', 'أعلى مبلغ']
            revenue_analysis = revenue_analysis.sort_values(by='إجمالي الإيرادات', ascending=False)
        else:
            revenue_analysis = pd.DataFrame()
        
        return revenue_analysis

    @staticmethod
    def generate_monthly_reports(df):
        """إنشاء تقارير شهرية (دالة ثابتة)."""
        if 'السنة' not in df.columns or 'الشهر' not in df.columns:
            return pd.DataFrame()
            
        monthly_data = df.groupby(['السنة', 'الشهر']).agg({
            'مدين': 'sum',
            'دائن': 'sum',
            'الرصيد': 'last'
        }).reset_index()
        
        monthly_data['صافي الحركة'] = monthly_data['دائن'] - monthly_data['مدين']
        
        # تحويل الشهر والسنة إلى تنسيق تاريخ
        monthly_data['الفترة'] = monthly_data.apply(lambda row: f"{int(row['السنة'])}-{int(row['الشهر']):02d}", axis=1)
        
        return monthly_data[['الفترة', 'دائن', 'مدين', 'صافي الحركة', 'الرصيد']]
