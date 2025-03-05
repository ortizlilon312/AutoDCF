import pandas as pd
import easygui
import datetime

def detect_frequency(df):
    """Detects whether the financial data is quarterly or annual."""
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values(by='Date')
        date_diffs = df['Date'].diff().dt.days.dropna()
        
        if date_diffs.median() < 150:  # Assuming quarters are around 90 days apart
            return "Quarterly"
        else:
            return "Annual"
    return "Unknown"

def get_fiscal_year_end():
    """Asks the user for the company's fiscal year-end month."""
    fiscal_year_end = easygui.enterbox("Enter the fiscal year-end month (1-12):")
    try:
        fiscal_year_end = int(fiscal_year_end)
        if 1 <= fiscal_year_end <= 12:
            return fiscal_year_end
        else:
            print("Invalid month entered. Defaulting to December (12).")
            return 12
    except:
        print("Invalid input. Defaulting to December (12).")
        return 12

def calculate_revenue_growth(df):
    """Extracts revenue data, calculates growth, and computes CAGR."""
    possible_revenue_columns = ["Revenue", "Total Revenue", "Sales", "Net Sales"]
    revenue_column = None
    
    for col in df.columns:
        if any(keyword.lower() in str(col).lower() for keyword in possible_revenue_columns):
            revenue_column = col
            break
    
    if revenue_column:
        df_revenue = df[[df.columns[0], revenue_column]].dropna()
        df_revenue.columns = ['Period', 'Revenue']
        df_revenue['Revenue Growth'] = df_revenue['Revenue'].pct_change() * 100
        
        initial_revenue = df_revenue['Revenue'].iloc[0]
        final_revenue = df_revenue['Revenue'].iloc[-1]
        num_periods = len(df_revenue) - 1
        
        avg_growth = df_revenue['Revenue Growth'].mean()
        cagr = ((final_revenue / initial_revenue) ** (1 / num_periods) - 1) * 100 if num_periods > 0 else 0
        
        print("\nRevenue Data with Growth Rates:")
        print(df_revenue)
        
        print(f"\nAverage Revenue Growth: {avg_growth:.2f}%")
        print(f"Compound Annual Growth Rate (CAGR): {cagr:.2f}%")
    else:
        print("Revenue data is missing from the dataset.")

def analyze_financial_data(statements):
    """Analyzes the financial statements to determine frequency and historical periods."""
    fiscal_year_end = get_fiscal_year_end()
    periods = {}
    
    for statement, df in statements.items():
        if 'Date' in df.columns:
            frequency = detect_frequency(df)
            total_periods = len(df)
            full_years = total_periods // 4 if frequency == "Quarterly" else total_periods
            
            periods[statement] = {
                "Frequency": frequency,
                "Total Periods": total_periods,
                "Full Years": full_years,
                "Fiscal Year End": fiscal_year_end
            }
            
            if statement == "Income Statement":
                calculate_revenue_growth(df)
    
    return periods

def load_financial_data():
    """Prompts user to select financial statement files and loads them."""
    statements = {}
    
    for statement in ["Income Statement", "Balance Sheet", "Cash Flow Statement"]:
        print(f"Please select the {statement} file.")
        file_path = easygui.fileopenbox(title=f"Select {statement}", filetypes=["*.csv", "*.xls", "*.xlsx"])
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    data = pd.read_csv(file_path)
                else:
                    data = pd.read_excel(file_path)
                
                statements[statement] = data
                print(f"{statement} loaded successfully.")
            except Exception as e:
                print(f"Error loading {statement}: {e}")
        else:
            print(f"No file selected for {statement}.")
    
    return statements

# Example usage
if __name__ == "__main__":
    financial_data = load_financial_data()
    analysis = analyze_financial_data(financial_data)
    for statement, details in analysis.items():
        print(f"\n{statement} Analysis:")
        for key, value in details.items():
            print(f"{key}: {value}")
