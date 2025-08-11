import yfinance as yf
import pandas as pd
from utility import util

testing_tester = "AAPL"


def get_company_data(ticker_symbol: str) -> dict:
    ticker = yf.Ticker(ticker_symbol)

    info = ticker.info
    name = info.get('longName', 'N/A')
    sector = info.get('sector', 'N/A')
    market_cap = info.get('marketCap', 'N/A')
    beta = info.get('beta', 'N/A')
    pe_ratio = info.get('trailingPE', 'N/A')

    # Financial statements
    income_statement = ticker.financials
    balance_sheet = ticker.balance_sheet
    cashflow_statement = ticker.cashflow

    return {
        "name": name,
        "sector": sector,
        "market_cap": market_cap,
        "beta": beta,
        "pe_ratio": pe_ratio,
        "income_statement": income_statement,
        "balance_sheet": balance_sheet,
        "cashflow_statement": cashflow_statement,
    }


# Example usage
if __name__ == "__main__":
    util.pretty_panda()
    data = get_company_data(testing_tester)
    print("Company:", data["name"])
    print("Market Cap:", data["market_cap"])
    print("\nIncome Statement:\n", data["income_statement"])
