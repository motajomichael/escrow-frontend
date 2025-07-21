import streamlit as st
from login import render_login_ui
from dashboard import render_dashboard
from state import init_session_state
from utils import authorized_post
import requests

st.set_page_config(page_title="Escrow App", page_icon="💼")
init_session_state()

query_params = st.query_params
if "paid_invoice" in query_params:
    invoice_id = query_params["paid_invoice"][0]
    if st.session_state.token:
        confirm = authorized_post(f"/payments/{invoice_id}/confirm", st.session_state.token)
        if confirm.status_code == 200:
            st.success(f"✅ Payment confirmed for invoice #{invoice_id}")
        else:
            st.error("Payment completed but could not confirm invoice.")
    else:
        st.info("Please log in to confirm payment.")
elif "payment" in query_params and query_params["payment"][0] == "cancelled":
    st.warning("❌ Payment was cancelled.")

# Show appropriate UI
if st.session_state.token:
    render_dashboard()
else:
    render_login_ui()
