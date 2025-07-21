import streamlit as st
from utils import authorized_get, authorized_post

def render_dashboard():
    user = st.session_state.user
    token = st.session_state.token
    role = user.get("role")

    st.sidebar.success(f"Logged in as: {user.get('name')} ({role})")
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.user = {}
        st.experimental_rerun()

    if role == "contractor":
        render_contractor_dashboard(token)
    elif role == "client":
        render_client_dashboard(token)

# --- Contractor View ---
def render_contractor_dashboard(token):
    st.header("🛠️ Contractor Dashboard")
    st.subheader("Your Projects")

    project_res = authorized_get("/projects", token)
    if project_res.status_code == 200:
        projects = project_res.json()
        for project in projects:
            with st.expander(f"{project['title']} ({project['clientEmail']})"):
                st.markdown(f"**Description:** {project['description']}")
                
                # Fetch milestones
                ms_res = authorized_get(f"/projects/{project['id']}/milestones", token)
                if ms_res.status_code == 200:
                    for m in ms_res.json():
                        st.markdown(f"- {m['title']}: ${m['amount']} — `{m['status']}`")
                        if m["status"] == "pending":
                            if st.button("✅ Mark as Completed", key=f"complete_{m['id']}"):
                                complete = authorized_post(f"/projects/{project['id']}/milestones/{m['id']}/complete", token)
                                if complete.status_code == 200:
                                    st.success("Milestone marked as completed.")
                                    st.experimental_rerun()
                                else:
                                    try:
                                        error_msg = complete.json().get("error", "Failed to complete milestone.")
                                    except Exception:
                                        error_msg = "Failed to complete milestone. (Invalid server response)"
                                    st.error(error_msg)
                        if m["status"] == "approved" and not m.get("paidOut"):
                            if not m.get("payoutRequested"):
                                if st.button("📤 Request Payout", key=f"request_{m['id']}"):
                                    payout_res = authorized_post(f"/projects/{project['id']}/milestones/{m['id']}/request-payout", token)
                                    if payout_res.status_code == 200:
                                        st.success("Payout requested.")
                                        st.experimental_rerun()
                                    else:
                                        st.error(payout_res.json().get("error", "Failed to request payout."))
                            else:
                                st.info("Payout request already submitted.")




                # Add new milestone
                st.markdown("---")
                st.markdown("**Add a Milestone**")
                m_title = st.text_input(f"Title for {project['id']}", key=f"title_{project['id']}")
                m_amount = st.number_input(f"Amount ($)", key=f"amount_{project['id']}")
                m_due = st.date_input("Due Date", key=f"due_{project['id']}")
                if st.button("Add Milestone", key=f"btn_{project['id']}"):
                    m_post = authorized_post(
                        f"/projects/{project['id']}/milestones", token,
                        {
                            "title": m_title,
                            "amount": m_amount,
                            "due_date": m_due.isoformat()
                        }
                    )
                    if m_post.status_code == 201:
                        st.success("Milestone added.")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to add milestone.")

    st.subheader("Create New Project")
    title = st.text_input("Project Title")
    desc = st.text_area("Project Description")
    client_email = st.text_input("Client Email")
    if st.button("Create Project"):
        post_res = authorized_post("/projects", token, {
            "title": title,
            "description": desc,
            "client_email": client_email
        })
        if post_res.status_code == 201:
            st.success("Project created.")
            st.experimental_rerun()
        else:
            st.error(post_res.json().get("error", "Failed to create project."))

# --- Client View ---
def render_client_dashboard(token):
    st.header("📂 Client Dashboard")

    res = authorized_get("/projects/client", token)
    if res.status_code != 200:
        st.error("Failed to load projects.")
        return

    projects = res.json()
    if not projects:
        st.info("No projects assigned to your email yet.")
        return

    for project in projects:
        with st.expander(f"{project['title']}"):
            st.markdown(f"**Description:** {project['description']}")
            st.markdown(f"**Contractor:** {project['contractor']['name']}")

            # Invoice
            invoice = project.get("invoice")
            if invoice:
                st.markdown(f"**Invoice Total:** ${invoice['totalAmount']}")
                st.markdown(f"**Status:** `{invoice['status']}`")

                if invoice["status"] != "paid":
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("💳 Pay Now", key=f"pay_{invoice['id']}"):
                            checkout = authorized_get(f"/payments/{invoice['id']}/checkout", token)
                            if checkout.status_code == 200:
                                url = checkout.json()["url"]
                                st.markdown(f"[Click here to complete payment]({url})")
                            else:
                                st.error("Could not create Stripe Checkout session.")

                    with col2:
                        if st.button("✅ Confirm Payment", key=f"confirm_{invoice['id']}"):
                            confirm = authorized_post(f"/payments/{invoice['id']}/confirm", token)
                            if confirm.status_code == 200:
                                st.success("Invoice marked as paid.")
                                st.experimental_rerun()
                            else:
                                st.error("Could not confirm payment.")
            else:
                if st.button("🧾 Generate Invoice", key=f"gen_inv_{project['id']}"):
                    inv_res = authorized_post(
                        f"/projects/{project['id']}/invoice", token
                    )
                    if inv_res.status_code == 201:
                        st.success("Invoice created.")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to create invoice.")

            # Milestones
            ms = authorized_get(f"/projects/{project['id']}/milestones", token)
            if ms.status_code == 200:
                st.markdown("**Milestones:**")
                for m in ms.json():
                    st.markdown(f"- `{m['status']}` — **{m['title']}** (${m['amount']})")
                    if m["status"] == "completed":
                        if st.button("✅ Approve Milestone", key=f"approve_{m['id']}"):
                            approve = authorized_post(f"/approvals/milestones/{m['id']}/approve", token)
                            if approve.status_code == 200:
                                st.success("Milestone approved.")
                                st.experimental_rerun()
                            else:
                                st.error("Approval failed.")
            else:
                st.warning("Couldn't load milestones.")
