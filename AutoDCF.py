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

def calculate_revenue_growth(df):
    """Prints all revenues with their respective period, calculates growth, and computes the average growth rate and CAGR."""
    if 'Revenue' in df.columns and 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values(by='Date')
        df['Revenue Growth'] = df['Revenue'].pct_change() * 100
        
        initial_revenue = df['Revenue'].iloc[0]
        final_revenue = df['Revenue'].iloc[-1]
        num_periods = len(df) - 1
        
        avg_growth = df['Revenue Growth'].mean()
        cagr = ((final_revenue / initial_revenue) ** (1 / num_periods) - 1) * 100 if num_periods > 0 else 0
        
        print("\nRevenue Data with Growth Rates:")
        print(df[['Date', 'Revenue', 'Revenue Growth']])
        
        print(f"\nAverage Revenue Growth: {avg_growth:.2f}%")
        print(f"Compound Annual Growth Rate (CAGR): {cagr:.2f}%")
    else:
        print("Revenue data is missing from the dataset.")

# Adding function call to analyze revenue if Income Statement is available
if "Income Statement" in financial_data:
    calculate_revenue_growth(financial_data["Income Statement"])
