import gradio as gr
import requests

API_PREDICT = "http://localhost:5000/predict"
API_HEALTH  = "http://localhost:5000/health"

LABEL_STYLE = {
    "Pass":        ("✅ Pass",                "#1a7a3a", "#e6f4ea"),
    "PassViol":    ("⚠️ Pass with Violation", "#7a5c00", "#fff8e1"),
    "HE_Pass":     ("✅ HE Pass",             "#1a7a3a", "#e6f4ea"),
    "Fail":        ("❌ Fail",                "#9b1c1c", "#fdecea"),
    "Failed":      ("❌ Failed",              "#9b1c1c", "#fdecea"),
    "HE_Fail":     ("❌ HE Fail",             "#9b1c1c", "#fdecea"),
    "HE_FailExt":  ("❌ HE Fail Ext",         "#9b1c1c", "#fdecea"),
    "HE_FAILNOR":  ("❌ HE Fail NOR",         "#9b1c1c", "#fdecea"),
    "Closed":      ("🚫 Closed",              "#9b1c1c", "#fdecea"),
    "HE_Closure":  ("🚫 HE Closure",          "#9b1c1c", "#fdecea"),
    "HE_VolClos":  ("🚫 Voluntary Closure",   "#9b1c1c", "#fdecea"),
    "HE_OutBus":   ("🏚️ Out of Business",     "#3d3d3d", "#f0f0f0"),
    "HE_Filed":    ("📋 HE Filed",            "#003d80", "#e3f0ff"),
    "HE_Hearing":  ("📋 HE Hearing",          "#003d80", "#e3f0ff"),
    "HE_Hold":     ("⏸️ HE Hold",            "#003d80", "#e3f0ff"),
    "HE_TSOP":     ("⏸️ HE TSOP",            "#003d80", "#e3f0ff"),
    "HE_Misc":     ("📌 HE Misc",            "#3d3d3d", "#f0f0f0"),
    "HE_NotReq":   ("ℹ️ Not Required",        "#3d3d3d", "#f0f0f0"),
    "DATAERR":     ("⚠️ Data Error",          "#7a5c00", "#fff8e1"),
}

ADVICE = {
    "Pass":       "🎉 Passed inspection. No action required.",
    "PassViol":   "⚠️ Passed but violations noted. Review and correct minor issues.",
    "HE_Pass":    "🎉 Hearing examiner approved. Establishment is compliant.",
    "Fail":       "🔴 Failed inspection. Immediate corrective action required.",
    "Failed":     "🔴 Failed inspection. Immediate corrective action required.",
    "HE_Fail":    "🔴 Hearing examiner found violations. Must address all cited issues.",
    "HE_FailExt": "🔴 Extended failure. Multiple or repeat violations found.",
    "HE_FAILNOR": "🔴 Fail — no response. Contact the health department immediately.",
    "Closed":     "🚫 Establishment is closed. No inspection result available.",
    "HE_Closure": "🚫 Ordered closed by hearing examiner. Cannot operate until cleared.",
    "HE_VolClos": "🚫 Voluntarily closed. Must request re-inspection to reopen.",
    "HE_OutBus":  "🏚️ Out of business at time of inspection.",
    "HE_Filed":   "📋 Case filed with hearing examiner. Await hearing date.",
    "HE_Hearing": "📋 Hearing scheduled. Prepare documentation for examiner.",
    "HE_Hold":    "⏸️ Result on hold. Check with the health department.",
    "HE_TSOP":    "⏸️ Temporary suspension of permit. Resolve violations to reinstate.",
    "HE_Misc":    "📌 Miscellaneous outcome. Contact the health department for details.",
    "HE_NotReq":  "ℹ️ Inspection not required for this license category.",
    "DATAERR":    "⚠️ Data error in record. Needs manual review.",
}

LICENSE_CATS  = ["FOOD", "LIQUOR", "TAVERN", "UNKNOWN", "Unknown"]
DESCRIPTS     = ["RETAIL FOOD", "WHOLESALE FOOD", "RESTAURANT", "BAKERY",
                 "SHARED KITCHEN", "CATERING", "TAVERN", "GROCERY", "Unknown"]
VIOL_LEVELS   = ["CRITICAL", "SERIOUS", "MINOR", "Unknown"]
VIOL_STATUSES = ["OPEN", "Closed", "COMPLETED", "Unknown"]


def predict(businessname, city, address, licensecat, descript, viollevel, violstatus):
    payload = {
        "businessname": businessname.strip() or "Unknown",
        "city":         city.strip()         or "Unknown",
        "address":      address.strip()      or "Unknown",
        "licensecat":   licensecat,
        "descript":     descript,
        "viollevel":    viollevel,
        "violstatus":   violstatus,
    }
    try:
        response = requests.post(API_PREDICT, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            return f"<div style='color:#ff4444;font-size:16px'>❌ API Error: {result['error']}</div>", "", ""

        label = result["prediction_label"]
        code  = result["prediction_code"]
        display, fg, bg = LABEL_STYLE.get(label, (f"🔍 {label}", "#333", "#eee"))

        styled = f"""
        <div style="
            background:{bg}; color:{fg};
            border:2px solid {fg};
            border-radius:14px; padding:22px 32px;
            font-size:24px; font-weight:700;
            text-align:center; margin-top:10px;
            letter-spacing:0.5px;">
            {display}
        </div>"""

        return styled, f"Prediction code: {code}   |   Label: {label}", ADVICE.get(label, "")

    except requests.exceptions.ConnectionError:
        return (
            "<div style='color:#ff4444;background:#2a1a1a;padding:14px;"
            "border:2px solid #ff4444;border-radius:10px;font-size:15px'>"
            "⚠️ Cannot reach Flask API. Make sure <b>app.py</b> is running on port 5000.</div>",
            "", ""
        )
    except Exception as e:
        return f"<div style='color:#ff4444'>❌ Error: {e}</div>", "", ""


def get_health():
    try:
        r = requests.get(API_HEALTH, timeout=5)
        r.raise_for_status()
        data = r.json()

        is_running = data.get("status") == "running"

        # Status badge
        status_bg    = "#1a4a2a" if is_running else "#4a1a1a"
        status_color = "#4cde80" if is_running else "#ff6b6b"
        status_text  = "🟢  Running" if is_running else "🔴  Down"

        # Feature pills
        features_html = "".join(
            f"<span style='background:#2a3a4a;color:#7ec8f0;padding:5px 13px;"
            f"border-radius:20px;margin:4px;display:inline-block;"
            f"font-size:13px;font-weight:600;border:1px solid #3a5a7a'>{f}</span>"
            for f in data.get("features", [])
        )

        # Class pills — color by outcome type
        def class_color(c):
            if "Pass" in c:    return ("background:#1a3a1a;color:#4cde80;border:1px solid #2a6a2a", )
            if "Fail" in c or "Clos" in c: return ("background:#3a1a1a;color:#ff8080;border:1px solid #6a2a2a", )
            return ("background:#1a2a3a;color:#7ec8f0;border:1px solid #2a4a6a", )

        classes_html = "".join(
            f"<span style='{class_color(c)[0]};padding:4px 11px;"
            f"border-radius:20px;margin:3px;display:inline-block;"
            f"font-size:12px;font-weight:600'>{c}</span>"
            for c in data.get("classes", [])
        )

        html = f"""
        <div style="font-family:sans-serif;padding:10px">

            <div style="background:{status_bg};border:2px solid {status_color};
                        border-radius:12px;padding:18px 24px;margin-bottom:18px;">
                <span style="font-size:22px;font-weight:700;color:{status_color}">
                    API Status: {status_text}
                </span>
            </div>

            <div style="background:#1e2a38;border:1px solid #2a3a4a;
                        border-radius:12px;padding:18px 24px;margin-bottom:18px;">
                <div style="font-size:12px;color:#8899aa;margin-bottom:6px;
                            text-transform:uppercase;letter-spacing:1px">Model</div>
                <div style="font-size:18px;font-weight:700;color:#e8f4ff">
                    {data.get("model", "N/A")}
                </div>
            </div>

            <div style="background:#1e2a38;border:1px solid #2a3a4a;
                        border-radius:12px;padding:18px 24px;margin-bottom:18px;">
                <div style="font-size:12px;color:#8899aa;margin-bottom:10px;
                            text-transform:uppercase;letter-spacing:1px">
                    Features Used &nbsp;
                    <span style="background:#2a3a4a;color:#7ec8f0;padding:2px 9px;
                                 border-radius:10px;font-size:12px">
                        {len(data.get("features", []))}
                    </span>
                </div>
                <div>{features_html}</div>
            </div>

            <div style="background:#1e2a38;border:1px solid #2a3a4a;
                        border-radius:12px;padding:18px 24px;">
                <div style="font-size:12px;color:#8899aa;margin-bottom:10px;
                            text-transform:uppercase;letter-spacing:1px">
                    Prediction Classes &nbsp;
                    <span style="background:#2a3a4a;color:#7ec8f0;padding:2px 9px;
                                 border-radius:10px;font-size:12px">
                        {data.get("total_classes", len(data.get("classes", [])))}
                    </span>
                </div>
                <div>{classes_html}</div>
            </div>

        </div>
        """
        return html

    except requests.exceptions.ConnectionError:
        return """
        <div style='color:#ff6b6b;background:#2a1a1a;padding:20px;
                    border:2px solid #ff4444;border-radius:12px;font-size:15px;line-height:2'>
            ⚠️ <b>Cannot reach Flask API</b><br>
            Make sure app.py is running:<br>
            <code style='background:#1a1a1a;padding:4px 10px;border-radius:6px'>
                python app.py
            </code>
        </div>"""
    except Exception as e:
        return f"<div style='color:#ff6b6b'>❌ Error: {e}</div>"


# ── Gradio UI ─────────────────────────────────────────────────────────────────
with gr.Blocks(
    title="Food Inspection Predictor",
    theme=gr.themes.Soft(primary_hue="emerald", neutral_hue="slate"),
    css="""
    .tab-nav button { font-size: 15px !important; font-weight: 600 !important; }
    .label-text     { font-size: 14px !important; font-weight: 600 !important; color: #cdd9e5 !important; }
    textarea, input { font-size: 15px !important; }
    """
) as demo:

    gr.Markdown("""
    # 🍽️ Food Inspection Prediction System
    > Random Forest model trained on **645,684** Chicago food inspection records.
    """)

    with gr.Tabs():

        # ── Tab 1: Predict ─────────────────────────────────────────────────
        with gr.TabItem("🔍  Predict"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 🏢 Establishment Info")
                    businessname = gr.Textbox(label="Business Name", placeholder="e.g. Pizza Palace")
                    city         = gr.Textbox(label="City",          placeholder="e.g. Chicago", value="Chicago")
                    address      = gr.Textbox(label="Address",       placeholder="e.g. 123 Main St")
                    licensecat   = gr.Dropdown(label="License Category", choices=LICENSE_CATS,  value="FOOD")
                    descript     = gr.Dropdown(label="Business Type",    choices=DESCRIPTS,     value="RETAIL FOOD")

                with gr.Column():
                    gr.Markdown("### ⚠️ Violation Info")
                    viollevel  = gr.Dropdown(label="Violation Level",  choices=VIOL_LEVELS,   value="CRITICAL")
                    violstatus = gr.Dropdown(label="Violation Status", choices=VIOL_STATUSES, value="OPEN")

                    gr.Markdown("### 📊 Prediction Result")
                    result_html   = gr.HTML()
                    result_detail = gr.Textbox(label="Details",            interactive=False)
                    result_tip    = gr.Textbox(label="Recommended Action", interactive=False, lines=2)

            predict_btn = gr.Button("🔍  Predict Inspection Outcome", variant="primary", size="lg")

            gr.Markdown("### 🧪 Quick Examples")
            gr.Examples(
                examples=[
                    ["Pizza Palace",  "Chicago", "123 Main St",      "FOOD",   "RETAIL FOOD", "CRITICAL", "OPEN"],
                    ["Green Grocery", "Chicago", "456 Oak Ave",       "FOOD",   "GROCERY",     "MINOR",    "Closed"],
                    ["City Tavern",   "Chicago", "789 Lake Shore Dr", "TAVERN", "TAVERN",      "Unknown",  "COMPLETED"],
                    ["Fresh Bakery",  "Chicago", "321 Elm Blvd",      "FOOD",   "BAKERY",      "SERIOUS",  "OPEN"],
                ],
                inputs=[businessname, city, address, licensecat, descript, viollevel, violstatus],
            )

            predict_btn.click(
                fn=predict,
                inputs=[businessname, city, address, licensecat, descript, viollevel, violstatus],
                outputs=[result_html, result_detail, result_tip],
            )

        # ── Tab 2: Health ──────────────────────────────────────────────────
        with gr.TabItem("❤️  API Health"):
            gr.Markdown("### Live status of the Flask API and loaded model")
            health_html = gr.HTML()
            refresh_btn = gr.Button("🔄  Refresh Status", variant="secondary", size="lg")
            refresh_btn.click(fn=get_health, inputs=[], outputs=health_html)
            demo.load(fn=get_health, inputs=[], outputs=health_html)

if __name__ == "__main__":
    demo.launch(server_port=7860, share=False)