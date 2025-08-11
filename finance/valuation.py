import pandas as pd
import yfinance as yf

def suggest_growth_rate(fcf_series: pd.Series) -> float:
    """
    Suggests an FCF growth rate based on CAGR of historical FCF.

    :param fcf_series: Pandas Series with DateTimeIndex or period-like index, values = FCF
    :return: Growth rate as decimal (ex., 0.05 for 5%)
    """
    # Drop NaNs just in case
    fcf_series = fcf_series.dropna()

    if len(fcf_series) < 2:
        raise ValueError("Need at least two years of FCF data to calculate growth rate.")

    # Sorted by date ascending
    fcf_series = fcf_series.sort_index()

    # Start and end values
    start_value = fcf_series.iloc[0]
    end_value = fcf_series.iloc[-1]
    periods = len(fcf_series) - 1  # number of intervals

    if start_value <= 0 or end_value <= 0:
        # If negatives in FCF, CAGR doesn't make sense so fallback to average YOY growth
        yoy_growth = fcf_series.pct_change().dropna()
        return yoy_growth.mean()

    # CAGR formula
    cagr = (end_value / start_value) ** (1 / periods) - 1
    return cagr


def suggest_wacc(ticker: str, risk_free_rate: float = 0.04, market_premium: float = 0.05) -> float:
    """
    Suggests WACC using Yahoo Finance data for the given ticker.

    :param ticker: Stock ticker (e.g., 'AAPL')
    :param risk_free_rate: Risk-free rate (default 4%)
    :param market_premium: Market risk premium (default 5%)
    :return: WACC as a decimal (e.g., 0.08 for 8%)
    """
    stock = yf.Ticker(ticker)

    # Market cap (latest)
    market_cap = stock.info.get("marketCap", None)

    # Beta (levered)
    beta = stock.info.get("beta", None)

    # Total debt and cash
    balance_sheet = stock.balance_sheet
    try:
        total_debt = balance_sheet.loc["Total Debt"].iloc[0]
    except KeyError:
        total_debt = 0
    try:
        cash = balance_sheet.loc["Cash"].iloc[0]
    except KeyError:
        cash = 0

    # Interest expense from financials (negative number)
    financials = stock.financials
    try:
        interest_expense = financials.loc["Interest Expense"].iloc[0]
    except KeyError:
        interest_expense = 0

    # Cost of equity via CAPM
    if beta is None:
        raise ValueError(f"No beta found for {ticker}")
    cost_of_equity = risk_free_rate + beta * market_premium

    # Cost of debt = interest expense / total debt (before tax)
    if total_debt > 0:
        cost_of_debt = abs(interest_expense) / total_debt
    else:
        cost_of_debt = 0

    # Tax rate from financials
    try:
        tax_expense = financials.loc["Income Tax Expense"].iloc[0]
        ebt = financials.loc["Ebit"].iloc[0]
        tax_rate = abs(tax_expense / ebt) if ebt else 0
    except KeyError:
        tax_rate = 0

    # Capital structure weights
    total_equity_value = market_cap if market_cap else 0
    total_debt_value = total_debt if total_debt else 0
    total_capital = total_equity_value + total_debt_value

    if total_capital == 0:
        raise ValueError("No capital structure data found.")

    equity_weight = total_equity_value / total_capital
    debt_weight = total_debt_value / total_capital

    # WACC formula
    wacc = equity_weight * cost_of_equity + debt_weight * cost_of_debt * (1 - tax_rate)
    return wacc
