from __future__ import annotations

import os
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_PREFIX = "/api/v1"

WRITE_ROLES = {"SUPER_ADMIN", "ABS_ENGINEER", "CLIENT_ADMIN", "CLIENT_ENGINEER"}
ADMIN_ROLES = {"SUPER_ADMIN", "ABS_ENGINEER", "CLIENT_ADMIN"}
ABS_ROLES = {"SUPER_ADMIN", "ABS_ENGINEER"}


st.set_page_config(
    page_title="ABS Industrial Intelligence Platform",
    page_icon="A",
    layout="wide",
)


def _headers() -> dict[str, str]:
    token = st.session_state.get("token", "")
    tenant_id = st.session_state.get("active_tenant_id", "")
    headers = {"Authorization": f"Bearer {token}"}
    if tenant_id:
        headers["X-Tenant-ID"] = tenant_id
    return headers


def api_get(path: str, params: dict[str, Any] | None = None, auth: bool = True):
    headers = _headers() if auth else {}
    response = requests.get(f"{BACKEND_URL}{API_PREFIX}{path}", headers=headers, params=params, timeout=60)
    if response.status_code >= 400:
        raise RuntimeError(response.json().get("detail", response.text))
    return response.json()


def api_post(path: str, json_data: dict[str, Any] | None = None, files=None, data=None):
    response = requests.post(
        f"{BACKEND_URL}{API_PREFIX}{path}",
        headers=_headers(),
        json=json_data,
        files=files,
        data=data,
        timeout=120,
    )
    if response.status_code >= 400:
        raise RuntimeError(response.json().get("detail", response.text))
    return response.json()


def api_put(path: str, json_data: dict[str, Any]):
    response = requests.put(
        f"{BACKEND_URL}{API_PREFIX}{path}",
        headers=_headers(),
        json=json_data,
        timeout=60,
    )
    if response.status_code >= 400:
        raise RuntimeError(response.json().get("detail", response.text))
    return response.json()


def api_patch(path: str, json_data: dict[str, Any]):
    response = requests.patch(
        f"{BACKEND_URL}{API_PREFIX}{path}",
        headers=_headers(),
        json=json_data,
        timeout=60,
    )
    if response.status_code >= 400:
        raise RuntimeError(response.json().get("detail", response.text))
    return response.json()


def render_landing() -> None:
    st.markdown("""
    <div style='padding:24px; background:linear-gradient(135deg,#0f4c81,#1f2937); border-radius:14px; color:white;'>
      <h1 style='margin:0;'>ABS Industrial Intelligence Platform</h1>
      <p style='margin:6px 0 0;'>Multi-tenant engineering quality intelligence for industrial tightening integrity.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Access Portal")
    role_col1, role_col2 = st.columns(2)
    with role_col1:
        st.button("Login as ABS Engineer", use_container_width=True, key="abs_btn")
    with role_col2:
        st.button("Login as Client", use_container_width=True, key="client_btn")


def login_form() -> None:
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In")

    if submitted:
        try:
            response = requests.post(
                f"{BACKEND_URL}{API_PREFIX}/auth/login",
                json={"email": email, "password": password},
                timeout=60,
            )
            if response.status_code >= 400:
                st.error(response.json().get("detail", response.text))
                return

            token = response.json()["access_token"]
            st.session_state["token"] = token

            me = requests.get(
                f"{BACKEND_URL}{API_PREFIX}/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=60,
            ).json()
            st.session_state["user"] = me
            st.session_state["active_tenant_id"] = me["tenant_id"]
            st.rerun()
        except Exception as exc:
            st.error(str(exc))


def render_topbar() -> None:
    user = st.session_state["user"]
    left, right = st.columns([4, 1])

    with left:
        st.markdown(
            f"**User:** {user['full_name']} | **Role:** {user['role']} | **Tenant:** {st.session_state.get('active_tenant_id')}"
        )

    with right:
        if st.button("Logout", use_container_width=True):
            for key in ["token", "user", "active_tenant_id"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    if user["role"] in ABS_ROLES:
        with st.expander("ABS Tenant Switch"):
            try:
                tenants = api_get("/tenants")
                options = {f"{item['name']} ({item['slug']})": item["id"] for item in tenants}
                label = st.selectbox("Active tenant", list(options.keys()))
                if st.button("Apply Tenant"):
                    st.session_state["active_tenant_id"] = options[label]
                    st.rerun()
            except Exception as exc:
                st.warning(f"Unable to list tenants: {exc}")


def render_dashboard_tab() -> None:
    st_autorefresh(interval=15000, key="dashboard_refresh")

    projects = api_get("/projects")
    project_options = {"All Projects": None}
    for item in projects:
        project_options[item["name"]] = item["id"]

    selected = st.selectbox("Project Filter", list(project_options.keys()), key="dash_project_filter")
    project_id = project_options[selected]

    analytics = api_get("/analytics/dashboard", params={"project_id": project_id} if project_id else None)

    kpi = analytics["kpis"]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Joints", kpi["total_joints"])
    c2.metric("Certified", kpi["certified_joints"])
    c3.metric("Pending", kpi["pending_joints"])
    c4.metric("Completion %", kpi["completion_percentage"])
    c5.metric("FPY %", kpi["fpy"])

    left, right = st.columns(2)
    with left:
        st.subheader("Torque vs Angle")
        df = pd.DataFrame(analytics["torque_vs_angle"])
        if df.empty:
            st.info("No execution data yet")
        else:
            fig = px.scatter(df, x="actual_angle", y="actual_torque", color="status", hover_data=["bolt_no", "joint_id"])
            st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Joint Completion Gauge")
        comp_df = pd.DataFrame(analytics["joint_completion"])
        if comp_df.empty:
            st.info("No joint completion records yet")
        else:
            top = comp_df.sort_values("completion", ascending=False).head(6)
            fig = go.Figure()
            for _, row in top.iterrows():
                fig.add_trace(
                    go.Bar(
                        x=[row["joint_id"]],
                        y=[row["completion"]],
                        text=[f"{row['completion']}%"],
                        textposition="auto",
                    )
                )
            fig.update_layout(yaxis_title="Completion %", barmode="group")
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Bolt Compliance Heatmap")
    heat_df = pd.DataFrame(analytics["compliance_heatmap"])
    if heat_df.empty:
        st.info("No compliance heatmap data")
    else:
        pivot = heat_df.pivot_table(index="joint_id", columns="bolt_no", values="status", aggfunc="first")
        mapping = {"OK": 1, "NOK": 0, "OutOfTolerance": -0.2, "Missing": -1}
        num = pivot.replace(mapping)
        fig = go.Figure(data=go.Heatmap(z=num.values, x=[f"B{c}" for c in num.columns], y=num.index))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Tool Health")
    st.dataframe(pd.DataFrame(analytics["tool_health"]), use_container_width=True)

    st.subheader("Operator Performance")
    st.dataframe(pd.DataFrame(analytics["operator_analytics"]), use_container_width=True)

    warnings = pd.DataFrame(analytics["ai_warnings"])
    st.subheader("AI Quality Warnings")
    if warnings.empty:
        st.success("No active AI warnings")
    else:
        st.dataframe(warnings, use_container_width=True)


def render_projects_tab() -> None:
    role = st.session_state["user"]["role"]
    can_write = role in WRITE_ROLES

    st.subheader("Sites")
    if can_write:
        with st.form("site_form"):
            name = st.text_input("Site Name")
            location = st.text_input("Site Location")
            if st.form_submit_button("Create Site"):
                try:
                    api_post("/projects/sites", json_data={"name": name, "location": location})
                    st.success("Site created")
                except Exception as exc:
                    st.error(str(exc))

    sites = pd.DataFrame(api_get("/projects/sites"))
    st.dataframe(sites, use_container_width=True)

    st.subheader("Projects")
    if can_write:
        with st.form("project_form"):
            pname = st.text_input("Project Name")
            cname = st.text_input("Client Name")
            plocation = st.text_input("Location")
            start = st.date_input("Start Date")
            end = st.date_input("Expected Completion")
            site_id = st.text_input("Site ID (optional)")
            if st.form_submit_button("Create Project"):
                try:
                    api_post(
                        "/projects",
                        json_data={
                            "name": pname,
                            "client_name": cname,
                            "location": plocation,
                            "start_date": str(start),
                            "expected_completion": str(end),
                            "site_id": site_id or None,
                        },
                    )
                    st.success("Project created")
                except Exception as exc:
                    st.error(str(exc))

    projects = pd.DataFrame(api_get("/projects"))
    st.dataframe(projects, use_container_width=True)


def render_work_orders_tab() -> None:
    role = st.session_state["user"]["role"]
    can_write = role in WRITE_ROLES

    projects = api_get("/projects")
    if not projects:
        st.info("Create a project first")
        return

    project_map = {f"{item['name']} ({item['id'][:8]})": item["id"] for item in projects}

    if can_write:
        st.subheader("Upload Work Order")
        with st.form("wo_upload_form"):
            project_label = st.selectbox("Project", list(project_map.keys()))
            code = st.text_input("Work Order Code")
            name = st.text_input("Work Order Name")
            file = st.file_uploader("Excel File", type=["xlsx", "xls", "xlsm"], key="wo_file")
            if st.form_submit_button("Upload Work Order"):
                if file is None:
                    st.warning("Upload a file")
                else:
                    try:
                        data = {
                            "project_id": project_map[project_label],
                            "code": code,
                            "name": name,
                        }
                        files = {"file": (file.name, file.getvalue(), file.type)}
                        result = api_post("/work-orders/upload", files=files, data=data)
                        st.success(f"Created joints: {result['joints_created']}, bolts: {result['bolts_created']}")
                    except Exception as exc:
                        st.error(str(exc))

    st.subheader("Work Orders")
    work_orders = pd.DataFrame(api_get("/work-orders"))
    st.dataframe(work_orders, use_container_width=True)


def render_joints_tab() -> None:
    role = st.session_state["user"]["role"]
    can_write = role in WRITE_ROLES

    joints = api_get("/joints")
    if not joints:
        st.info("No joints available")
        return

    joint_map = {f"{item['joint_id']} ({item['status']})": item["id"] for item in joints}
    selected_label = st.selectbox("Select Joint", list(joint_map.keys()))
    joint_uuid = joint_map[selected_label]

    detail = api_get(f"/joints/{joint_uuid}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Joint", detail["joint_id"])
    c2.metric("Status", detail["status"])
    c3.metric("Bolt Count", detail["bolt_count"])

    if can_write:
        with st.expander("Assign VIN"):
            vin = st.text_input("AGS VIN")
            tool_id = st.text_input("Assigned Tool ID (optional)")
            if st.button("Assign VIN", key="assign_vin_joint"):
                try:
                    api_patch(
                        f"/joints/{joint_uuid}/assign-vin",
                        {"assigned_vin": vin, "assigned_tool_id": tool_id or None},
                    )
                    st.success("VIN assigned")
                except Exception as exc:
                    st.error(str(exc))

    layout = api_get(f"/joints/{joint_uuid}/layout")
    nodes = pd.DataFrame(layout["nodes"])
    fig = px.scatter(
        nodes,
        x="x",
        y="y",
        color="status",
        hover_data=["bolt_no"],
        title="Digital Circular Bolt Layout",
    )
    fig.update_traces(marker=dict(size=16))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    st.plotly_chart(fig, use_container_width=True)

    bolts = pd.DataFrame(api_get("/bolts", params={"joint_id": joint_uuid}))
    st.dataframe(bolts, use_container_width=True)


def render_execution_tab() -> None:
    role = st.session_state["user"]["role"]
    can_write = role in WRITE_ROLES

    st.subheader("Upload Torque Execution File")
    if not can_write:
        st.info("Read-only role: upload disabled")

    work_orders = api_get("/work-orders")
    wo_map = {f"{item['code']} ({item['name']})": item["id"] for item in work_orders}

    if can_write:
        with st.form("execution_upload_form"):
            selected_wo = st.selectbox("Work Order (optional)", ["Auto-match VIN"] + list(wo_map.keys()))
            file = st.file_uploader("Execution file (Excel/CSV)", type=["xlsx", "xls", "xlsm", "csv"], key="exec_upload")
            if st.form_submit_button("Process Execution Data"):
                if file is None:
                    st.warning("Upload a file")
                else:
                    try:
                        data = {}
                        if selected_wo != "Auto-match VIN":
                            data["work_order_id"] = wo_map[selected_wo]
                        files = {"file": (file.name, file.getvalue(), file.type)}
                        result = api_post("/executions/upload", data=data, files=files)
                        st.success(
                            f"Joint {result['joint_id']} updated: {result['updated_joint_status']} | "
                            f"OK {result['ok_bolts']} NOK {result['nok_bolts']} Missing {result['missing_bolts']}"
                        )
                    except Exception as exc:
                        st.error(str(exc))

    st.subheader("Recent Execution Records")
    records = pd.DataFrame(api_get("/executions"))
    st.dataframe(records.head(500), use_container_width=True)


def render_reports_tab() -> None:
    role = st.session_state["user"]["role"]
    can_write = role in WRITE_ROLES

    projects = api_get("/projects")
    work_orders = api_get("/work-orders")
    joints = api_get("/joints")

    if can_write:
        st.subheader("Generate Report")
        with st.form("report_form"):
            report_type = st.selectbox(
                "Report Type",
                [
                    "Joint Certification Report",
                    "Work Order Report",
                    "Project Quality Report",
                ],
            )
            project_id = st.selectbox("Project", [""] + [p["id"] for p in projects])
            work_order_id = st.selectbox("Work Order", [""] + [w["id"] for w in work_orders])
            joint_id = st.selectbox("Joint", [""] + [j["id"] for j in joints])
            if st.form_submit_button("Generate PDF"):
                try:
                    payload = {
                        "report_type": report_type,
                        "project_id": project_id or None,
                        "work_order_id": work_order_id or None,
                        "joint_id": joint_id or None,
                    }
                    report = api_post("/reports", json_data=payload)
                    st.success(f"Report generated: {report['id']}")
                except Exception as exc:
                    st.error(str(exc))

    st.subheader("Reports")
    reports = api_get("/reports")
    if not reports:
        st.info("No reports available")
    else:
        for rep in reports:
            st.write(f"{rep['report_type']} | {rep['id']} | QR {rep['qr_token']}")
            download_url = f"{BACKEND_URL}{API_PREFIX}/reports/{rep['id']}/download"
            st.markdown(f"[Download PDF]({download_url})")


def render_notifications_tab() -> None:
    notifications = pd.DataFrame(api_get("/notifications"))
    if notifications.empty:
        st.success("No notifications")
        return
    st.dataframe(notifications, use_container_width=True)

    target = st.text_input("Notification ID to mark read")
    if st.button("Mark Read") and target:
        try:
            api_patch(f"/notifications/{target}", {"is_read": True})
            st.success("Notification updated")
        except Exception as exc:
            st.error(str(exc))


def render_billing_tab() -> None:
    st.subheader("Subscription Plans")
    plans = pd.DataFrame(api_get("/billing/plans"))
    st.dataframe(plans, use_container_width=True)

    st.subheader("Current Subscription")
    sub = api_get("/billing/subscription")
    st.json(sub)


def render_audit_tab() -> None:
    role = st.session_state["user"]["role"]
    if role not in ADMIN_ROLES:
        st.info("Admin role required")
        return

    logs = pd.DataFrame(api_get("/audit-logs"))
    st.dataframe(logs, use_container_width=True)


def render_branding_tab() -> None:
    role = st.session_state["user"]["role"]
    can_admin = role in ADMIN_ROLES

    st.subheader("Tenant Branding")
    try:
        current = api_get("/branding")
        if current:
            st.json(current)
    except Exception:
        pass

    if can_admin:
        with st.form("branding_form"):
            client_name = st.text_input("Client Display Name")
            primary = st.color_picker("Primary Color", "#0f4c81")
            secondary = st.color_picker("Secondary Color", "#1f2937")
            logo_path = st.text_input("Company Logo Path")
            if st.form_submit_button("Update Branding"):
                try:
                    api_put(
                        "/branding",
                        {
                            "client_display_name": client_name,
                            "primary_color": primary,
                            "secondary_color": secondary,
                            "company_logo_path": logo_path or None,
                        },
                    )
                    st.success("Branding updated")
                except Exception as exc:
                    st.error(str(exc))


render_landing()

if "token" not in st.session_state:
    login_form()
    st.stop()

render_topbar()

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Projects",
        "Work Orders",
        "Joints",
        "Execution Upload",
        "Reports",
        "Notifications",
        "Billing",
        "Branding",
        "Audit Logs",
    ],
)

try:
    if page == "Dashboard":
        render_dashboard_tab()
    elif page == "Projects":
        render_projects_tab()
    elif page == "Work Orders":
        render_work_orders_tab()
    elif page == "Joints":
        render_joints_tab()
    elif page == "Execution Upload":
        render_execution_tab()
    elif page == "Reports":
        render_reports_tab()
    elif page == "Notifications":
        render_notifications_tab()
    elif page == "Billing":
        render_billing_tab()
    elif page == "Branding":
        render_branding_tab()
    elif page == "Audit Logs":
        render_audit_tab()
except Exception as exc:
    st.error(f"API error: {exc}")

