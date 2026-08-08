# Personal Finance Knowledge Base
# This content is embedded into FAISS for RAG retrieval.

KNOWLEDGE_DOCUMENTS = [
    # Budgeting
    {
        "title": "50/30/20 Budget Rule",
        "content": """The 50/30/20 rule is a popular budgeting framework. Allocate 50% of your after-tax income to needs (rent, utilities, groceries, insurance), 30% to wants (dining out, entertainment, shopping), and 20% to savings and debt repayment. This provides a simple structure for managing personal finances without tracking every rupee. For example, if your monthly income is ₹50,000, you should spend ₹25,000 on needs, ₹15,000 on wants, and save ₹10,000.""",
    },
    {
        "title": "Emergency Fund",
        "content": """An emergency fund is money set aside for unexpected expenses like medical emergencies, job loss, or urgent home repairs. Financial experts recommend having 3-6 months of living expenses saved. Start by saving ₹1,000 per month and gradually increase. Keep the emergency fund in a high-yield savings account or liquid mutual fund for easy access. Do not invest emergency funds in stocks or long-term instruments.""",
    },
    {
        "title": "Zero-Based Budgeting",
        "content": """Zero-based budgeting means every rupee of income is assigned a purpose — expenses, savings, or investments — so that income minus outgo equals zero. This forces you to be intentional with every rupee. Start each month by listing all expected income, then allocate funds to categories until nothing is unassigned. This method is particularly effective for people who struggle with overspending.""",
    },
    # Investing
    {
        "title": "SIP (Systematic Investment Plan)",
        "content": """A SIP allows you to invest a fixed amount regularly (monthly or weekly) into mutual funds. Benefits include rupee cost averaging (buying more units when prices are low, fewer when high) and the power of compounding. Starting a SIP of even ₹500/month in an index fund can grow significantly over 10-20 years. SIPs are ideal for salaried individuals who want disciplined, long-term wealth creation.""",
    },
    {
        "title": "Mutual Fund Categories in India",
        "content": """Indian mutual funds are broadly categorized as: Equity funds (invest in stocks, higher risk/return), Debt funds (invest in bonds, lower risk), Hybrid funds (mix of equity and debt), and Index funds (track market indices like Nifty 50). For beginners, large-cap equity funds or Nifty 50 index funds are recommended. Always check the expense ratio — lower is better. ELSS funds offer tax deduction under Section 80C.""",
    },
    {
        "title": "Fixed Deposits vs Mutual Funds",
        "content": """Fixed Deposits (FDs) offer guaranteed returns (6-7% p.a.) with minimal risk but are taxed as per your income slab. Mutual funds carry market risk but historically deliver 10-15% p.a. for equity funds over the long term. For short-term goals (1-3 years), FDs or debt funds are safer. For long-term goals (5+ years), equity mutual funds generally outperform FDs after adjusting for inflation and taxes.""",
    },
    # Tax Planning
    {
        "title": "Section 80C Tax Deductions (India)",
        "content": """Under Section 80C of the Income Tax Act, you can claim deductions up to ₹1.5 lakh per year on investments like PPF, ELSS mutual funds, NSC, 5-year FDs, life insurance premiums, and tuition fees. EPF contributions by salaried employees also count. ELSS has the shortest lock-in period (3 years) among 80C options and offers potential for higher returns through equity exposure.""",
    },
    {
        "title": "New Tax Regime vs Old Tax Regime",
        "content": """India offers two tax regimes. The Old Regime allows deductions (80C, 80D, HRA, etc.) but has higher base rates. The New Regime (default from FY 2023-24) offers lower tax rates but no major deductions. If your total deductions exceed ₹3-4 lakh, the Old Regime is usually better. Use an online tax calculator to compare both regimes for your specific situation before choosing.""",
    },
    # Debt Management
    {
        "title": "Debt Avalanche vs Debt Snowball",
        "content": """Two popular debt repayment strategies: The Avalanche method pays off debts with the highest interest rate first (saves the most money). The Snowball method pays off the smallest debts first (provides quick psychological wins). Both require making minimum payments on all debts while putting extra money toward the target debt. The Avalanche method is mathematically optimal, but Snowball works better for motivation.""",
    },
    {
        "title": "Credit Card Best Practices",
        "content": """Always pay your full credit card bill by the due date to avoid 36-42% annual interest charges. Use credit cards for the rewards and cashback, but never spend more than you can pay in full. Keep credit utilization below 30% of your limit. Set up auto-pay for at least the minimum amount. Having 1-2 credit cards and using them responsibly builds a strong CIBIL score (aim for 750+).""",
    },
    # Savings Tips
    {
        "title": "Reducing Monthly Expenses",
        "content": """Common ways to cut monthly spending: 1) Review and cancel unused subscriptions (OTT, gym, apps). 2) Cook at home more — eating out can cost 3-5x more. 3) Use public transport or carpooling. 4) Switch to annual plans for services you use (often 20-40% cheaper). 5) Compare insurance premiums annually. 6) Use cashback apps and credit card rewards strategically. Track expenses for a month to identify leaks.""",
    },
    {
        "title": "Automating Your Finances",
        "content": """Set up automatic transfers on salary day: a fixed amount to savings/investment accounts, SIP auto-debits, and bill auto-pays. This 'pay yourself first' approach ensures saving happens before spending. Use separate bank accounts for spending, savings, and investments. Most Indian banks allow scheduled transfers and standing instructions at no extra cost.""",
    },
]
