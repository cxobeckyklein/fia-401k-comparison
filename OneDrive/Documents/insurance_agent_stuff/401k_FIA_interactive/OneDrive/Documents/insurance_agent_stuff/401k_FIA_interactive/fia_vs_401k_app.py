
import numpy as np
import pandas as pd

# Define S&P 500 price returns from 2003 to 2022
sp500_returns_2003_2022 = [
    0.2638, 0.0899, 0.0300, 0.1362, 0.0310, -0.3849, 0.2345, 0.1284, 0.0000, 0.1351,
    0.2960, 0.1139, -0.0007, 0.0954, 0.1922, -0.0624, 0.2888, 0.1633, 0.2651, -0.1954
]

def get_user_inputs():
    premium = float(input("Enter starting balance (e.g., 1000000): "))
    pr_start = float(input("Enter starting FIA participation rate (e.g., 1.0 for 100%): "))
    pr_end = float(input("Enter ending FIA participation rate (e.g., 0.35 for 35%): "))
    floor = float(input("Enter FIA floor rate (e.g., 0.0): "))
    fee = float(input("Enter 401(k) annual fee drag (e.g., 0.02 for 2%): "))
    inflation = float(input("Enter annual inflation rate (e.g., 0.03 for 3%): "))
    tax = float(input("Enter tax rate on RMDs (e.g., 0.30 for 30%): "))
    return premium, pr_start, pr_end, floor, fee, inflation, tax

def compound_growth(start, returns):
    balances = [start]
    for r in returns[:-1]:
        start *= (1 + r)
        balances.append(start)
    return balances

def calculate_rmds(balances, ages, tax_rate, inflation_rate):
    rmd_divisors = {
        age: div for age, div in zip(range(73, 95), [
            26.5, 25.5, 24.6, 23.7, 22.9, 22.0, 21.1, 20.2,
            19.4, 18.5, 17.7, 16.8, 16.0, 15.2, 14.4, 13.7,
            12.9, 12.2, 11.5, 10.8, 10.1, 9.5
        ])
    }
    start_bal, rmd, net_rmd, infl_adj_rmd = [], [], [], []
    infl_factor = 1.0
    for i, age in enumerate(ages):
        bal = balances[i]
        start_bal.append(bal)
        dist = bal / rmd_divisors[age] if age in rmd_divisors else 0
        rmd.append(dist)
        net = dist * (1 - tax_rate)
        net_rmd.append(net)
        infl_adj_rmd.append(net / infl_factor)
        infl_factor *= (1 + inflation_rate)
    return start_bal, rmd, net_rmd, infl_adj_rmd

def run_simulation():
    ages = list(range(55, 95))
    years = list(range(1, 41))
    premium, pr_start, pr_end, floor, fee, inflation_rate, tax_rate = get_user_inputs()

    returns_40yr = sp500_returns_2003_2022 * 2
    pr_decay = np.linspace(pr_start, pr_end, 40)
    fia_returns = np.maximum(floor, pr_decay * np.array(returns_40yr))
    k401_returns = [(1 + r) * (1 - fee) - 1 for r in returns_40yr]

    fia_bal = compound_growth(premium, fia_returns)
    k401_bal = compound_growth(premium, k401_returns)

    fia_start, fia_rmd, fia_net, fia_adj = calculate_rmds(fia_bal, ages, tax_rate, inflation_rate)
    k401_start, k401_rmd, k401_net, k401_adj = calculate_rmds(k401_bal, ages, tax_rate, inflation_rate)

    df = pd.DataFrame({
        "Year": years,
        "Age": ages,
        "FIA Start Balance": [f"${v:,.0f}" for v in fia_start],
        "FIA RMD": [f"${v:,.0f}" for v in fia_rmd],
        "FIA After-Tax RMD": [f"${v:,.0f}" for v in fia_net],
        "FIA Infl-Adj RMD": [f"${v:,.0f}" for v in fia_adj],
        "401k Start Balance": [f"${v:,.0f}" for v in k401_start],
        "401k RMD": [f"${v:,.0f}" for v in k401_rmd],
        "401k After-Tax RMD": [f"${v:,.0f}" for v in k401_net],
        "401k Infl-Adj RMD": [f"${v:,.0f}" for v in k401_adj],
    })

    df.to_csv("C:/Users/Becky/OneDrive/Documents/Insurance Agent Stuff/Marketing/401k_campaign/401k_FIA_interactive/fia_vs_401k_output.csv", index=False)
print("Output saved to: C:/Users/Becky/OneDrive/Documents/Insurance Agent Stuff/Marketing/401k_campaign/401k_FIA_interactive/")

if __name__ == "__main__":
    run_simulation()
