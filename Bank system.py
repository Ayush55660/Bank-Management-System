

import json
import random
import string
from pathlib import Path

import streamlit as st



class Bank:
    database = "data.json"

    def __init__(self):
        self.data = []
        if Path(self.database).exists():
            try:
                with open(self.database) as fs:
                    self.data = json.loads(fs.read() or "[]")
            except Exception as err:
                st.error(f"Could not read data.json: {err}")

    def __update(self):
        with open(self.database, "w") as fs:
            fs.write(json.dumps(self.data, indent=2))

    @staticmethod
    def __accountgenerate():
        alpha = random.choices(string.ascii_letters, k=3)
        num = random.choices(string.digits, k=3)
        spchar = random.choices("!@#$%^&*", k=1)
        id_ = alpha + num + spchar
        random.shuffle(id_)
        return "".join(id_)

    def Createaccount(self, name, age, email, pin):
        if age < 18 or len(str(pin)) != 4:
            return False, "Sorry, you cannot create an account (age must be 18+ and PIN must be 4 digits).", None

        info = {
            "name": name,
            "age": age,
            "email": email,
            "pin": pin,
            "accountNo.": Bank.__accountgenerate(),
            "balance": 0,
        }
        self.data.append(info)
        self.__update()
        return True, "Account has been created successfully!", info

    def depositmoney(self, accnumber, pin, amount):
        # NOTE: original code used `if userdata == False`, which never
        # matches an empty list — fixed to `if not userdata` here.
        userdata = [i for i in self.data if i["accountNo."] == accnumber and i["pin"] == pin]

        if not userdata:
            return False, "Sorry, no account found with that number and PIN.", None

        if amount > 10000 or amount < 0:
            return False, "Sorry, the amount is too much — you can deposit below ₹10,000 and above ₹0.", None

        userdata[0]["balance"] += amount
        self.__update()
        return True, "Amount deposited successfully!", userdata[0]["balance"]

    def withdrawmoney(self, accnumber, pin, amount):
        userdata = [i for i in self.data if i["accountNo."] == accnumber and i["pin"] == pin]

        if not userdata:
            return False, "Sorry, no account found with that number and PIN.", None

        if userdata[0]["balance"] < amount:
            return False, "Sorry, you don't have that much money.", None

        userdata[0]["balance"] -= amount
        self.__update()
        return True, "Amount withdrew successfully!", userdata[0]["balance"]

    def showdetails(self, accnumber, pin):
        userdata = [i for i in self.data if i["accountNo."] == accnumber and i["pin"] == pin]

        if not userdata:
            return False, "Sorry, no account found with that number and PIN.", None

        return True, "Account found.", userdata[0]

    def updatedetails(self, accnumber, pin, new_name, new_email, new_pin):
        userdata = [i for i in self.data if i["accountNo."] == accnumber and i["pin"] == pin]

        if not userdata:
            return False, "No such user found.", None

        newdata = {
            "name": new_name,
            "email": new_email,
            "pin": new_pin,
        }

        if newdata["name"] == "":
            newdata["name"] = userdata[0]["name"]
        if newdata["email"] == "":
            newdata["email"] = userdata[0]["email"]
        if newdata["pin"] == "":
            newdata["pin"] = userdata[0]["pin"]

        newdata["age"] = userdata[0]["age"]
        newdata["accountNo."] = userdata[0]["accountNo."]
        newdata["balance"] = userdata[0]["balance"]

        if isinstance(newdata["pin"], str):
            if not newdata["pin"].isdigit() or len(newdata["pin"]) != 4:
                return False, "New PIN must be exactly 4 digits.", None
            newdata["pin"] = int(newdata["pin"])

        for key in newdata:
            userdata[0][key] = newdata[key]

        self.__update()
        return True, "Details updated successfully!", userdata[0]

    def Delete(self, accnumber, pin):
        userdata = [i for i in self.data if i["accountNo."] == accnumber and i["pin"] == pin]

        if not userdata:
            return False, "Sorry, no such account exists."

        index = self.data.index(userdata[0])
        self.data.pop(index)
        self.__update()
        return True, "Account deleted successfully."

    def stats(self):
        total_accounts = len(self.data)
        total_balance = sum(r.get("balance", 0) for r in self.data)
        avg_balance = (total_balance / total_accounts) if total_accounts else 0
        return {
            "total_accounts": total_accounts,
            "total_balance": total_balance,
            "avg_balance": avg_balance,
        }


# =====================================================================
# STREAMLIT UI
# =====================================================================

st.set_page_config(
    page_title="Vault & Ledger | Bank Management System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_bank():
    return Bank()


bank = get_bank()

INK_TEXT = "#12202F"
GOLD = "#B8892B"
GOLD_SOFT = "#D8B569"
LEDGER_GREEN = "#3F6C4B"
STAMP_RED = "#A13D3D"
PARCHMENT = "#F6F1E2"

# ---------------------------------------------------------------------
# Global CSS — fonts, palette, and the "passbook" component styles
# ---------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp {{
        background:
            radial-gradient(1200px 600px at 10% -10%, #1c3252 0%, #0E1B2C 45%),
            #0E1B2C;
        color: #EDE6D6;
    }}

    section[data-testid="stSidebar"] {{
        background: #16283F;
        border-right: 1px solid rgba(184,137,43,0.35);
    }}
    section[data-testid="stSidebar"] * {{
        color: #EDE6D6 !important;
    }}
    .brand-wrap {{
        padding: 1.4rem 0.2rem 1rem 0.2rem;
        border-bottom: 1px solid rgba(184,137,43,0.35);
        margin-bottom: 0.8rem;
    }}
    .brand-mark {{
        font-family: 'Playfair Display', serif;
        font-weight: 800;
        font-size: 1.55rem;
        letter-spacing: 0.02em;
        color: {GOLD_SOFT};
        line-height: 1.15;
    }}
    .brand-tag {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #9FB0C4;
        margin-top: 0.25rem;
    }}

    section[data-testid="stSidebar"] .stRadio > label {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #9FB0C4 !important;
    }}
    section[data-testid="stSidebar"] .stRadio [role="radiogroup"] label {{
        padding: 0.35rem 0.5rem;
        border-radius: 6px;
        transition: background 0.15s ease;
    }}
    section[data-testid="stSidebar"] .stRadio [role="radiogroup"] label:hover {{
        background: rgba(184,137,43,0.12);
    }}

    h1, h2, h3 {{
        font-family: 'Playfair Display', serif !important;
        color: #F3ECD9 !important;
        letter-spacing: 0.01em;
    }}
    p, li, label, span {{
        color: #D8CFBC;
    }}

    .passbook {{
        background: {PARCHMENT};
        border-radius: 10px;
        padding: 2rem 2.2rem 1.6rem 2.2rem;
        box-shadow: 0 18px 40px rgba(0,0,0,0.35);
        border: 1px solid #E4DAC0;
        position: relative;
        margin-bottom: 1.4rem;
    }}
    .passbook::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 6px;
        border-radius: 10px 10px 0 0;
        background: linear-gradient(90deg, {GOLD} 0%, {GOLD_SOFT} 50%, {GOLD} 100%);
    }}
    .passbook-eyebrow {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: {STAMP_RED};
        margin-bottom: 0.25rem;
    }}
    .passbook-title {{
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        font-size: 1.6rem;
        color: {INK_TEXT} !important;
        margin-bottom: 0.15rem;
    }}
    .passbook-sub {{
        font-family: 'Inter', sans-serif;
        font-size: 0.92rem;
        color: #5b5342 !important;
        margin-bottom: 1.1rem;
    }}
    .passbook p, .passbook li, .passbook span, .passbook label {{
        color: {INK_TEXT} !important;
    }}

    .stub-row {{
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        margin: 1.2rem 0 1.8rem 0;
    }}
    .stub {{
        flex: 1 1 220px;
        background: {PARCHMENT};
        border: 1px dashed #B8A97C;
        border-radius: 8px;
        padding: 1.1rem 1.3rem;
        position: relative;
    }}
    .stub::after {{
        content: "";
        position: absolute;
        top: -7px; right: 14px;
        width: 14px; height: 14px;
        background: #0E1B2C;
        border-radius: 50%;
        border: 1px dashed #B8A97C;
    }}
    .stub-label {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #8a7c53;
    }}
    .stub-value {{
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        font-size: 1.9rem;
        color: {INK_TEXT};
        margin-top: 0.2rem;
    }}

    .acct-chip {{
        display: inline-block;
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.15rem;
        letter-spacing: 0.18em;
        background: {INK_TEXT};
        color: {GOLD_SOFT};
        padding: 0.55rem 1rem;
        border-radius: 6px;
        margin: 0.4rem 0 0.8rem 0;
    }}

    .seal {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        border: 1.5px solid {LEDGER_GREEN};
        color: {LEDGER_GREEN};
    }}

    .stButton > button, .stFormSubmitButton > button {{
        background: {GOLD};
        color: {INK_TEXT};
        border: none;
        border-radius: 6px;
        font-weight: 600;
        letter-spacing: 0.02em;
        padding: 0.55rem 1.3rem;
        transition: transform 0.12s ease, background 0.12s ease;
    }}
    .stButton > button:hover, .stFormSubmitButton > button:hover {{
        background: {GOLD_SOFT};
        transform: translateY(-1px);
    }}

    div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea,
    div[data-baseweb="select"] > div {{
        font-family: 'JetBrains Mono', monospace !important;
    }}

    div[data-testid="stForm"] {{
        border: none;
        padding: 0;
    }}

    hr {{
        border-color: rgba(184,137,43,0.3) !important;
    }}

    footer, #MainMenu {{ visibility: hidden; }}

    .app-footer {{
        text-align: center;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 0.08em;
        color: #6f8098;
        margin-top: 2.5rem;
        padding-top: 1.2rem;
        border-top: 1px solid rgba(184,137,43,0.25);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand-wrap">
            <div class="brand-mark">🏦 Vault &amp; Ledger</div>
            <div class="brand-tag">Digital Passbook · Est. 2026</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigate",
        [
            "🏠  Home",
            "🆕  Open an Account",
            "💰  Deposit",
            "🏧  Withdraw",
            "📖  Account Details",
            "✏️  Update Details",
            "❌  Close Account",
            "📚  Ledger (All Accounts)",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Built as a portfolio project · Python + Streamlit")

stats = bank.stats()

# =======================================================================
# HOME
# =======================================================================
if page.startswith("🏠"):
    left, right = st.columns([1.3, 1])
    with left:
        st.markdown('<div class="passbook-eyebrow">Bank Management System</div>', unsafe_allow_html=True)
        st.markdown("# Vault & Ledger")
        st.markdown(
            "A small, honest bank in your browser — open accounts, "
            "deposit and withdraw funds, and keep a running ledger, "
            "all backed by a simple JSON file instead of a real bank vault."
        )
        st.markdown(
            "Use the counter on the left to walk up to a window: "
            "**Open an Account**, **Deposit**, **Withdraw**, or check your "
            "**Account Details** with your account number and PIN."
        )
    with right:
        st.markdown(
            """
            <div class="passbook" style="margin-top:0.4rem;">
                <div class="passbook-eyebrow">Teller's Notice</div>
                <div class="passbook-title">How it works</div>
                <div class="passbook-sub">Three simple rules of the house</div>
                <ul style="margin-top:-0.4rem; line-height:1.9;">
                    <li>You must be <b>18+</b> to open an account.</li>
                    <li>Your PIN is exactly <b>4 digits</b> — keep it safe.</li>
                    <li>Deposits are capped at <b>₹10,000</b> per transaction.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="stub-row">
            <div class="stub">
                <div class="stub-label">Accounts Open</div>
                <div class="stub-value">{stats['total_accounts']}</div>
            </div>
            <div class="stub">
                <div class="stub-label">Total Deposits Held</div>
                <div class="stub-value">₹{stats['total_balance']:,.0f}</div>
            </div>
            <div class="stub">
                <div class="stub-label">Average Balance</div>
                <div class="stub-value">₹{stats['avg_balance']:,.0f}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "💡 New here? Head to **🆕 Open an Account** in the sidebar to get "
        "your account number, then come back any time to deposit, withdraw, "
        "or check your balance.",
        icon="💡",
    )

# =======================================================================
# OPEN ACCOUNT
# =======================================================================
elif page.startswith("🆕"):
    st.markdown(
        """
        <div class="passbook">
            <div class="passbook-eyebrow">New Account</div>
            <div class="passbook-title">Open an Account</div>
            <div class="passbook-sub">Fill out the form below — it takes less than a minute.</div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("create_account_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full name")
            age = st.number_input("Age", min_value=0, max_value=120, step=1, value=18)
        with c2:
            email = st.text_input("Email address")
            pin = st.text_input("Choose a 4-digit PIN", max_chars=4, type="password")

        submitted = st.form_submit_button("Open Account")

    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        if not name.strip():
            st.error("Please enter a name.")
        elif not pin.isdigit():
            st.error("PIN must contain only digits.")
        else:
            ok, msg, info = bank.Createaccount(name.strip(), int(age), email.strip(), int(pin))
            if ok:
                st.success(msg)
                st.markdown(
                    f"""
                    <div class="passbook">
                        <span class="seal">● Account Active</span>
                        <div class="passbook-title" style="margin-top:0.7rem;">Welcome, {info['name']}!</div>
                        <div class="passbook-sub">Note down your account number — you'll need it with your PIN for every transaction.</div>
                        <div class="acct-chip">{info['accountNo.']}</div>
                        <p style="margin-top:0.6rem;">Opening balance: <b>₹{info['balance']:,}</b></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.balloons()
            else:
                st.error(msg)

# =======================================================================
# DEPOSIT
# =======================================================================
elif page.startswith("💰"):
    st.markdown(
        """
        <div class="passbook">
            <div class="passbook-eyebrow">Teller Window · Deposits</div>
            <div class="passbook-title">Deposit Funds</div>
            <div class="passbook-sub">Maximum ₹10,000 per transaction.</div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("deposit_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            acc_no = st.text_input("Account number")
        with c2:
            pin = st.text_input("PIN", max_chars=4, type="password")
        with c3:
            amount = st.number_input("Amount (₹)", min_value=0, step=100)
        submitted = st.form_submit_button("Deposit")

    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        if not pin.isdigit():
            st.error("PIN must contain only digits.")
        else:
            ok, msg, balance = bank.depositmoney(acc_no, int(pin), int(amount))
            if ok:
                st.success(msg)
                st.metric("New Balance", f"₹{balance:,}")
            else:
                st.error(msg)

# =======================================================================
# WITHDRAW
# =======================================================================
elif page.startswith("🏧"):
    st.markdown(
        """
        <div class="passbook">
            <div class="passbook-eyebrow">Teller Window · Withdrawals</div>
            <div class="passbook-title">Withdraw Funds</div>
            <div class="passbook-sub">You can't withdraw more than your current balance.</div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("withdraw_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            acc_no = st.text_input("Account number")
        with c2:
            pin = st.text_input("PIN", max_chars=4, type="password")
        with c3:
            amount = st.number_input("Amount (₹)", min_value=0, step=100)
        submitted = st.form_submit_button("Withdraw")

    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        if not pin.isdigit():
            st.error("PIN must contain only digits.")
        else:
            ok, msg, balance = bank.withdrawmoney(acc_no, int(pin), int(amount))
            if ok:
                st.success(msg)
                st.metric("New Balance", f"₹{balance:,}")
            else:
                st.error(msg)

# =======================================================================
# ACCOUNT DETAILS
# =======================================================================
elif page.startswith("📖"):
    st.markdown(
        """
        <div class="passbook">
            <div class="passbook-eyebrow">Passbook Lookup</div>
            <div class="passbook-title">Account Details</div>
            <div class="passbook-sub">Enter your account number and PIN to view your passbook.</div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("details_form"):
        c1, c2 = st.columns(2)
        with c1:
            acc_no = st.text_input("Account number")
        with c2:
            pin = st.text_input("PIN", max_chars=4, type="password")
        submitted = st.form_submit_button("View Details")

    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        if not pin.isdigit():
            st.error("PIN must contain only digits.")
        else:
            ok, msg, record = bank.showdetails(acc_no, int(pin))
            if ok:
                st.markdown(
                    f"""
                    <div class="passbook">
                        <span class="seal">● Account Active</span>
                        <div class="passbook-title" style="margin-top:0.7rem;">{record['name']}</div>
                        <div class="acct-chip">{record['accountNo.']}</div>
                        <table style="width:100%; margin-top:0.6rem;">
                            <tr><td style="padding:0.3rem 0;">Email</td><td style="text-align:right;">{record['email']}</td></tr>
                            <tr><td style="padding:0.3rem 0;">Age</td><td style="text-align:right;">{record['age']}</td></tr>
                            <tr><td style="padding:0.3rem 0;">Balance</td><td style="text-align:right;"><b>₹{record['balance']:,}</b></td></tr>
                        </table>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.error(msg)

# =======================================================================
# UPDATE DETAILS
# =======================================================================
elif page.startswith("✏️"):
    st.markdown(
        """
        <div class="passbook">
            <div class="passbook-eyebrow">Amend Records</div>
            <div class="passbook-title">Update Details</div>
            <div class="passbook-sub">Name, email and PIN can be changed. Age, account number and balance cannot. Leave a field blank to keep it unchanged.</div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("update_form"):
        st.markdown("**Verify your identity**")
        c1, c2 = st.columns(2)
        with c1:
            acc_no = st.text_input("Account number")
        with c2:
            pin = st.text_input("Current PIN", max_chars=4, type="password")

        st.markdown("**New details** _(optional)_")
        c3, c4, c5 = st.columns(3)
        with c3:
            new_name = st.text_input("New name")
        with c4:
            new_email = st.text_input("New email")
        with c5:
            new_pin = st.text_input("New PIN", max_chars=4, type="password")

        submitted = st.form_submit_button("Update Details")

    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        if not pin.isdigit():
            st.error("Current PIN must contain only digits.")
        else:
            ok, msg, record = bank.updatedetails(acc_no, int(pin), new_name.strip(), new_email.strip(), new_pin.strip())
            if ok:
                st.success(msg)
            else:
                st.error(msg)

# =======================================================================
# CLOSE ACCOUNT
# =======================================================================
elif page.startswith("❌"):
    st.markdown(
        """
        <div class="passbook">
            <div class="passbook-eyebrow">Handle With Care</div>
            <div class="passbook-title">Close Account</div>
            <div class="passbook-sub">This permanently deletes the account. There's no undo.</div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("delete_form"):
        c1, c2 = st.columns(2)
        with c1:
            acc_no = st.text_input("Account number")
        with c2:
            pin = st.text_input("PIN", max_chars=4, type="password")
        confirm = st.checkbox("I understand this cannot be undone.")
        submitted = st.form_submit_button("Close Account")

    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        if not pin.isdigit():
            st.error("PIN must contain only digits.")
        elif not confirm:
            st.warning("Please confirm you understand this action is permanent.")
        else:
            ok, msg = bank.Delete(acc_no, int(pin))
            if ok:
                st.success(msg)
            else:
                st.error(msg)

# =======================================================================
# LEDGER (ALL ACCOUNTS)
# =======================================================================
elif page.startswith("📚"):
    st.markdown('<div class="passbook-eyebrow">Branch Ledger</div>', unsafe_allow_html=True)
    st.markdown("## All Accounts")
    st.caption("PINs are masked here — this view is for demo purposes only.")

    if not bank.data:
        st.info("The ledger is empty. Open the first account from the sidebar.")
    else:
        rows = [
            {
                "Account No.": r["accountNo."],
                "Name": r["name"],
                "Age": r["age"],
                "Email": r["email"],
                "Balance (₹)": r["balance"],
                "PIN": "••••",
            }
            for r in bank.data
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)

st.markdown(
    '<div class="app-footer">VAULT &amp; LEDGER — a Bank Management System built with Python &amp; Streamlit</div>',
    unsafe_allow_html=True,
)