import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Expense Manager",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
    /* Remove default padding */
    .main {
        padding-top: 2rem;
    }
    
    /* Custom header styling */
    h1 {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #FF6B6B;
        border-bottom: 2px solid #FF6B6B;
        padding-bottom: 0.5rem;
    }
    
    /* Metric styling */
    .metric-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #252d3d 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #FF6B6B;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        padding: 0.75rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 8px;
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
        color: white;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(255, 107, 107, 0.3);
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 2px solid #2a3142;
        background-color: #1a1f2e;
        color: white;
        padding: 0.75rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 1.5rem;
        background-color: transparent;
        border-bottom: 3px solid transparent;
        color: #888;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        color: #FF6B6B;
        border-bottom-color: #FF6B6B;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: #2d5a3d;
        border-left: 4px solid #4caf50;
    }
    
    .stError {
        background-color: #5a2d2d;
        border-left: 4px solid #f44336;
    }
    
    .stInfo {
        background-color: #2d4a5a;
        border-left: 4px solid #2196f3;
    }
    
    /* Dataframe styling */
    .dataframe {
        width: 100%;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f2e 0%, #0f1419 100%);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONSTANTS
# ============================================================================

API_BASE_URL = "http://127.0.0.1:8000"

# ============================================================================
# HEADER & HERO SECTION
# ============================================================================

col1, col2 = st.columns([1, 3])
with col1:
    st.markdown("# 💰")
with col2:
    st.markdown("# Expense Manager")

st.markdown("### Track your spending with precision and intelligence")
st.divider()

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")
    
    # API Status
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Error")
    except:
        st.error("❌ Cannot reach API")
    
    st.markdown("---")
    st.markdown("### 📱 About")
    st.info("""
    **Expense Manager v1.0**
    
    Built with:
    - FastAPI (Backend)
    - Streamlit (Frontend)
    - MySQL (Database)
    
    [GitHub](https://github.com) | [Docs](http://localhost:8000/docs)
    """)

# ============================================================================
# CREATE TABS
# ============================================================================

tab1, tab2, tab3 = st.tabs(["➕ Add Expense", "📊 Analytics", "📋 History"])

# ============================================================================
# TAB 1: ADD/UPDATE EXPENSE
# ============================================================================

with tab1:
    st.markdown("### Add or Update an Expense")
    
    # Create form
    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            expense_date = st.date_input(
                "📅 Date",
                value=datetime.now().date(),
                help="When did you spend this?"
            )
        
        with col2:
            # Fetch categories
            try:
                response = requests.get(f"{API_BASE_URL}/categories/")
                categories = response.json()["categories"]
            except:
                categories = ["Food", "Rent", "Transport", "Other"]
            
            category = st.selectbox(
                "🏷️ Category",
                options=categories,
                help="What type of expense?"
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            amount = st.number_input(
                "💵 Amount ($)",
                min_value=0.0,
                step=0.01,
                help="How much did you spend?"
            )
        
        with col2:
            notes = st.text_input(
                "📝 Notes (optional)",
                placeholder="Add details about this expense...",
                help="Additional context"
            )
        
        # Submit button
        submitted = st.form_submit_button(
            "💾 Save Expense",
            use_container_width=True
        )
        
        if submitted:
            if not category or amount <= 0:
                st.error("⚠️ Please fill all required fields and enter amount > $0")
            else:
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/expenses/{expense_date}",
                        json={
                            "date": str(expense_date),
                            "category": category,
                            "amount": amount,
                            "notes": notes
                        }
                    )
                    
                    if response.status_code == 200:
                        st.success(f"✅ Saved {category}: ${amount:.2f}")
                        st.balloons()
                    else:
                        st.error(f"❌ Error: {response.json()}")
                except Exception as e:
                    st.error(f"❌ Connection error: {e}")
    
    # Display expenses for selected date
    st.markdown("---")
    st.markdown(f"### 📅 Expenses for {expense_date}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/expenses/{expense_date}")
        data = response.json()
        
        if data["expenses"]:
            # Metrics row
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Total", f"${data['total']:.2f}")
            with col2:
                st.metric("📊 Count", len(data["expenses"]))
            with col3:
                if len(data["expenses"]) > 0:
                    avg = data['total'] / len(data["expenses"])
                    st.metric("📈 Average", f"${avg:.2f}")
            
            st.markdown("---")
            
            # Display table
            df = pd.DataFrame(data["expenses"])
            df['amount'] = df['amount'].apply(lambda x: f"${x:.2f}")
            st.dataframe(
                df[['category', 'amount', 'notes']].rename(
                    columns={
                        'category': '🏷️ Category',
                        'amount': '💵 Amount',
                        'notes': '📝 Notes'
                    }
                ),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("📭 No expenses recorded for this date yet.")
    except Exception as e:
        st.error(f"❌ Error fetching expenses: {e}")

# ============================================================================
# TAB 2: ANALYTICS DASHBOARD
# ============================================================================

with tab2:
    st.markdown("### 📊 Expense Analytics Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input(
            "📅 Start Date",
            value=datetime.now().date() - timedelta(days=30),
            key="start_date"
        )
    
    with col2:
        end_date = st.date_input(
            "📅 End Date",
            value=datetime.now().date(),
            key="end_date"
        )
    
    with col3:
        st.write("")
        st.write("")
        generate_report = st.button(
            "📈 Generate Report",
            use_container_width=True,
            key="analytics_button"
        )
    
    if generate_report or True:  # Auto-generate on load
        try:
            response = requests.post(
                f"{API_BASE_URL}/analytics/",
                json={
                    "start_date": str(start_date),
                    "end_date": str(end_date)
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # KEY METRICS
                st.markdown("### 🎯 Key Metrics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "💰 Total Expense",
                        f"${data['total_expense']:.2f}",
                        delta=f"{data['expense_count']} transactions"
                    )
                
                with col2:
                    st.metric(
                        "📊 Transactions",
                        data['expense_count']
                    )
                
                with col3:
                    if data['expense_count'] > 0:
                        avg = data['total_expense'] / data['expense_count']
                        st.metric("📈 Avg per Transaction", f"${avg:.2f}")
                    else:
                        st.metric("📈 Avg per Transaction", "$0.00")
                
                with col4:
                    num_categories = len(data['by_category'])
                    st.metric("🏷️ Categories", num_categories)
                
                st.markdown("---")
                
                # CATEGORY BREAKDOWN
                if data['by_category']:
                    st.markdown("### 📊 Breakdown by Category")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Pie Chart
                        df_pie = pd.DataFrame(
                            list(data['by_category'].items()),
                            columns=['Category', 'Amount']
                        )
                        fig_pie = px.pie(
                            df_pie,
                            values='Amount',
                            names='Category',
                            title="Expense Distribution",
                            color_discrete_sequence=px.colors.sequential.RdBu
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                    
                    with col2:
                        # Bar Chart
                        df_bar = pd.DataFrame(
                            list(data['by_category'].items()),
                            columns=['Category', 'Amount']
                        ).sort_values('Amount', ascending=True)
                        
                        fig_bar = px.bar(
                            df_bar,
                            x='Amount',
                            y='Category',
                            orientation='h',
                            title="Amount by Category",
                            color='Amount',
                            color_continuous_scale='Reds'
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)
                    
                    st.markdown("---")
                    
                    # Detailed Table
                    st.markdown("### 📋 Category Details")
                    table_data = []
                    total = sum(data['by_category'].values())
                    
                    for cat, amt in sorted(data['by_category'].items(), key=lambda x: x[1], reverse=True):
                        percentage = (amt / total * 100) if total > 0 else 0
                        table_data.append({
                            "🏷️ Category": cat,
                            "💵 Amount": f"${amt:.2f}",
                            "📊 %": f"{percentage:.1f}%"
                        })
                    
                    st.dataframe(
                        pd.DataFrame(table_data),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("📭 No expenses in this date range")
            else:
                st.error(f"❌ Error: {response.json()}")
        except Exception as e:
            st.error(f"❌ Connection error: {e}")

# ============================================================================
# TAB 3: EXPENSE HISTORY
# ============================================================================

with tab3:
    st.markdown("### 📋 Full Expense History")
    
    col1, col2 = st.columns(2)
    
    with col1:
        history_start = st.date_input(
            "📅 From Date",
            value=datetime.now().date() - timedelta(days=90),
            key="history_start"
        )
    
    with col2:
        history_end = st.date_input(
            "📅 To Date",
            value=datetime.now().date(),
            key="history_end"
        )
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/analytics/",
            json={
                "start_date": str(history_start),
                "end_date": str(history_end)
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Fetch detailed expenses
            all_expenses = []
            current_date = history_start
            while current_date <= history_end:
                try:
                    resp = requests.get(f"{API_BASE_URL}/expenses/{current_date}")
                    if resp.status_code == 200:
                        all_expenses.extend(resp.json()["expenses"])
                except:
                    pass
                current_date += timedelta(days=1)
            
            if all_expenses:
                df_history = pd.DataFrame(all_expenses)
                df_history['amount'] = df_history['amount'].apply(lambda x: f"${x:.2f}")
                
                st.dataframe(
                    df_history[['expense_date', 'category', 'amount', 'notes']].rename(
                        columns={
                            'expense_date': '📅 Date',
                            'category': '🏷️ Category',
                            'amount': '💵 Amount',
                            'notes': '📝 Notes'
                        }
                    ),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("📭 No expenses found in this period")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 2rem 0;'>
    <p>💰 <strong>Expense Manager</strong> v1.0</p>
    <p>Built with ❤️ using Streamlit • FastAPI • MySQL</p>
    <p style='font-size: 0.85rem;'>Data is secure and stored locally in your MySQL database</p>
</div>
""", unsafe_allow_html=True)