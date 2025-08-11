import yfinance as yf


def get_fcf_info(ticker_symbol: str) -> dict:
    """
    Get financial statement data needed to calculate Free Cash Flow (FCF).

    :param ticker_symbol: Stock ticker (e.g., 'AAPL', 'MSFT')
    :return: Dictionary containing Pandas Series for each FCF component
    """
    ticker = yf.Ticker(ticker_symbol)

    # Financial statements
    income_statement = ticker.financials
    balance_sheet = ticker.balance_sheet
    cashflow_statement = ticker.cashflow

    # print(income_statement)
    # Extract EBIT / Operating profit
    ebit = income_statement.loc["EBIT"]

    # Tax rate
    try:
        tax_rate = income_statement.loc["Tax Rate For Calcs"]
    except KeyError:
        print("Warning: 'Tax Rate For Calcs' not found. Calculating effective tax rate.")
        income_before_tax = income_statement.loc["Pretax Income"]
        income_tax_expense = income_statement.loc["Income Tax Expense"]
        tax_rate = income_tax_expense / income_before_tax
        tax_rate = tax_rate.fillna(0)

    # Depreciation & Amortization
    # print(cashflow_statement)
    dep_and_amort = cashflow_statement.loc["Depreciation And Amortization"]
    # Capital Expenditures
    capex = cashflow_statement.loc["Capital Expenditure"]

    # Change in Net Working Capital
    # print(balance_sheet)
    current_assets = balance_sheet.loc["Current Assets"]
    current_liabilities = balance_sheet.loc["Current Liabilities"]
    net_working_capital = current_assets - current_liabilities
    delta_net_working_capital = net_working_capital.diff(periods=-1)  # yoy change

    fcf = ebit * (1 - tax_rate) + dep_and_amort - capex - delta_net_working_capital

    return {
        "EBIT": ebit,
        "Tax Rate": tax_rate,
        "D&A": dep_and_amort,
        "CapEx": capex,
        "Net Working Capital": delta_net_working_capital,
        "FCF": fcf
    }


if __name__ == "__main__":
    # Debug mode - test the function standalone
    from utility import util
    util.pretty_panda()
    data = get_fcf_info("AAPL")
    for key, value in data.items():
        print(f"\n{key}:\n{value}")
