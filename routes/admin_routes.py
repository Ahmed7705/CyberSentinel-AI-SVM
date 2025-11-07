"""Admin dashboard routes."""
from __future__ import annotations

import os

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from database.database import execute, fetch_all, fetch_one
from services import alert_service, auth_service, report_service
from ai_engine.engine import generate_alert_insight
from flask import send_file
from services.report_service import generate_pdf_report, generate_ai_analyst_pdf
from datetime import datetime



admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
UPLOAD_ROOT = os.path.abspath(os.path.join(os.getcwd(), "uploads", "user_files"))


def _require_admin():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))
    return None


def _resolve_upload_path(stored_path: str) -> str:
    if not stored_path:
        raise ValueError("File path is empty")
    candidate = stored_path if os.path.isabs(stored_path) else os.path.join(os.getcwd(), stored_path)
    abs_path = os.path.abspath(candidate)
    if not abs_path.startswith(UPLOAD_ROOT):
        raise ValueError("File path escapes upload directory")
    return abs_path


@admin_bp.route("/dashboard", methods=["GET"])
def dashboard():
    guard = _require_admin()
    if guard:
        return guard

    metrics = alert_service.get_alert_metrics()
    users = auth_service.list_users(limit=10)
    alerts = alert_service.get_recent_alerts(limit=10)
    activity_stats = fetch_all(
        """
        SELECT event_type, COUNT(*) AS total
        FROM activity_logs
        GROUP BY event_type
        ORDER BY total DESC
        LIMIT 6
        """
    )
    return render_template(
        "admin-dashboard.html",
        metrics=metrics,
        users=users,
        alerts=alerts,
        activity_stats=activity_stats,
    )


@admin_bp.route("/profile", methods=["GET", "POST"])
def profile():
    guard = _require_admin()
    if guard:
        return guard

    admin_id = session["user_id"]

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip() or None
        department = request.form.get("department", "").strip() or None
        if full_name or department:
            execute(
                """
                UPDATE users
                SET full_name = COALESCE(%s, full_name),
                    department = COALESCE(%s, department)
                WHERE id = %s
                """,
                (full_name, department, admin_id),
            )
            if full_name:
                session["full_name"] = full_name
            if department:
                session["department"] = department
            flash("Profile updated successfully", "success")
        else:
            flash("No changes submitted", "warning")

    admin_user = auth_service.get_user_by_id(admin_id)
    if not admin_user:
        flash("Administrator not found", "error")
        return redirect(url_for("auth.logout"))

    return render_template(
        "user-profile.html",
        user=admin_user,
        active_user=session,
        is_admin_view=True,
    )


@admin_bp.route("/api/users", methods=["GET"])
def api_users():
    guard = _require_admin()
    if guard:
        return guard

    users = auth_service.list_users()

    def _serialise_user(row: dict) -> dict:
        return {
            "id": row.get("id"),
            "username": row.get("username"),
            "full_name": row.get("full_name"),
            "department": row.get("department"),
            "role": row.get("role"),
            "last_login": row["last_login"].isoformat() if row.get("last_login") else None,
        }

    return jsonify([_serialise_user(user) for user in users])


@admin_bp.route("/api/users/<int:user_id>/files", methods=["GET"])
def api_user_files(user_id: int):
    guard = _require_admin()
    if guard:
        return guard

    rows = fetch_all(
        """
        SELECT id, filename, file_type, file_size, risk_level, uploaded_at
        FROM user_files
        WHERE user_id = %s
        ORDER BY uploaded_at DESC
        LIMIT 50
        """,
        (user_id,),
    )

    def _serialise_file(row: dict) -> dict:
        return {
            "id": row.get("id"),
            "filename": row.get("filename"),
            "file_type": row.get("file_type"),
            "file_size": row.get("file_size"),
            "risk_level": row.get("risk_level"),
            "uploaded_at": row.get("uploaded_at").isoformat() if row.get("uploaded_at") else None,
        }

    return jsonify([_serialise_file(record) for record in rows])


@admin_bp.route("/files/<int:file_id>/download", methods=["GET"])
def admin_download_user_file(file_id: int):
    guard = _require_admin()
    if guard:
        return guard

    record = fetch_one(
        "SELECT filename, file_path FROM user_files WHERE id = %s",
        (file_id,),
    )
    if not record:
        flash("File not found", "error")
        return redirect(url_for("admin.monitoring"))

    try:
        abs_path = _resolve_upload_path(record.get("file_path"))
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("admin.monitoring"))

    if not os.path.exists(abs_path):
        flash("File is missing from storage", "error")
        return redirect(url_for("admin.monitoring"))

    return send_file(
        abs_path,
        as_attachment=True,
        download_name=record.get("filename") or "download",
    )


@admin_bp.route("/alerts", methods=["GET"])
def alerts():
    guard = _require_admin()
    if guard:
        return guard
    alerts = alert_service.get_recent_alerts(limit=50)
    return render_template("alerts.html", alerts=alerts)


# @admin_bp.route("/reports", methods=["GET"])
# def reports():
#     guard = _require_admin()
#     if guard:
#         return guard
#     alerts = alert_service.get_recent_alerts(limit=100)
#     report_html = report_service.build_alert_report(alerts)
#     return render_template("reports.html", alerts=alerts, report_html=report_html)


@admin_bp.route("/monitoring", methods=["GET"])
def employee_monitoring():
    guard = _require_admin()
    if guard:
        return guard

    user_profiles = fetch_all(
        """
        SELECT
            u.id,
            u.username,
            u.full_name,
            u.role,
            u.department,
            u.is_active,
            u.last_login,
            SUM(CASE WHEN a.id IS NOT NULL THEN 1 ELSE 0 END) AS total_alerts,
            SUM(CASE WHEN a.risk_level IN ('high','critical') THEN 1 ELSE 0 END) AS high_alerts,
            SUM(CASE WHEN a.status = 'open' THEN 1 ELSE 0 END) AS open_alerts,
            MAX(a.created_at) AS last_alert_at,
            SUM(CASE WHEN l.timestamp IS NOT NULL AND l.timestamp >= NOW() - INTERVAL 7 DAY THEN 1 ELSE 0 END) AS activity_week,
            MAX(l.timestamp) AS last_activity_at
        FROM users u
        LEFT JOIN alerts a ON a.user_id = u.id
        LEFT JOIN activity_logs l ON l.user_id = u.id
        GROUP BY u.id, u.username, u.full_name, u.role, u.department, u.is_active, u.last_login
        ORDER BY high_alerts DESC, total_alerts DESC, u.full_name
        """
    )

    recent_alerts = alert_service.get_recent_alerts(limit=8)
    recent_activity = fetch_all(
        """
        SELECT
            l.id,
            u.full_name,
            u.username,
            l.event_type,
            l.timestamp,
            l.source_ip,
            l.device,
            l.risk_score
        FROM activity_logs l
        JOIN users u ON u.id = l.user_id
        ORDER BY l.timestamp DESC
        LIMIT 12
        """
    )
    recent_uploads = fetch_all(
        """
        SELECT
            uf.id,
            uf.user_id,
            uf.filename,
            uf.file_size,
            uf.file_type,
            uf.risk_level,
            uf.uploaded_at,
            u.full_name,
            u.username,
            u.department
        FROM user_files uf
        JOIN users u ON u.id = uf.user_id
        ORDER BY uf.uploaded_at DESC
        LIMIT 12
        """
    )

    overall_metrics = {
        "total_users": len(user_profiles),
        "active_users": sum(1 for user in user_profiles if user.get("is_active")),
        "total_alerts": sum(int(user.get("total_alerts") or 0) for user in user_profiles),
        "high_alerts": sum(int(user.get("high_alerts") or 0) for user in user_profiles),
        "open_alerts": sum(int(user.get("open_alerts") or 0) for user in user_profiles),
    }

    ai_summary = None
    priority_slice = [
        row for row in user_profiles if int(row.get("high_alerts") or 0) > 0
    ][:5]
    if priority_slice:
        lines = []
        for entry in priority_slice:
            lines.append(
                f"{entry.get('full_name') or entry.get('username')} ({entry.get('department') or 'Dept N/A'}) "
                f"- high alerts: {entry.get('high_alerts') or 0}, open alerts: {entry.get('open_alerts') or 0}, "
                f"last activity: {entry.get('last_activity_at')}"
            )
        prompt = (
            "You are an enterprise security analyst. Provide a concise (<=120 words) overview of the following high-risk employees "
            "and recommend the top three immediate actions the SOC team should take.\n"
            + "\n".join(lines)
        )
        try:
            ai_summary = generate_alert_insight(prompt)
        except Exception:
            ai_summary = None

    if not ai_summary:
        ai_summary = "AI summary is currently unavailable. Review the monitoring table for manual assessment."

    return render_template(
        "employee-monitoring.html",
        user_profiles=user_profiles,
        recent_alerts=recent_alerts,
        recent_activity=recent_activity,
        recent_uploads=recent_uploads,
        overall_metrics=overall_metrics,
        ai_summary=ai_summary,
    )


@admin_bp.route("/api/alerts", methods=["GET"])
def alerts_json():
    guard = _require_admin()
    if guard:
        return guard
    return jsonify(alert_service.get_recent_alerts(limit=50))


@admin_bp.route("/api/users", methods=["GET"])
def users_json():
    guard = _require_admin()
    if guard:
        return guard
    return jsonify(auth_service.list_users())


# # --- AI Security Analyst Page ---
# @admin_bp.route("/ai-analyst", methods=["GET", "POST"])
# def ai_analyst():
#     """Admin interactive AI analyst page."""

#     ai_report = None
#     filters = {"users": [], "start_date": None, "end_date": None}

#     # جلب كل المستخدمين لعرضهم في واجهة الفلترة
#     users = fetch_all("SELECT id, username, full_name FROM users ORDER BY full_name")

#     if request.method == "POST":
#         try:
#             selected_users = request.form.getlist("users")
#             start_date = request.form.get("start_date")
#             end_date = request.form.get("end_date")
#             filters = {"users": selected_users, "start_date": start_date, "end_date": end_date}

#             query = """
#                 SELECT a.*, u.username, u.full_name
#                 FROM activity_logs a
#                 JOIN users u ON a.user_id = u.id
#                 WHERE (%(users)s = '' OR a.user_id IN %(users)s)
#                 AND (%(start)s IS NULL OR a.timestamp >= %(start)s)
#                 AND (%(end)s IS NULL OR a.timestamp <= %(end)s)
#                 ORDER BY a.timestamp DESC
#             """

#             user_tuple = tuple(selected_users) if selected_users else tuple()
#             activities = fetch_all(
#                 query,
#                 {"users": user_tuple, "start": start_date, "end": end_date}
#             )

#             if activities:
#                 ai_input = {
#                     "query_type": "behavior_analysis",
#                     "filters": filters,
#                     "records": activities,
#                 }
#                 ai_report = generate_alert_insight(ai_input) or "No AI insights available."
#             else:
#                 ai_report = "No matching activities found for the selected filters."
#         except Exception as e:
#             ai_report = f"Error during AI analysis: {str(e)}"

#     return render_template(
#         "ai-analyst.html",
#         users=users,
#         ai_report=ai_report,
#         filters=filters,
#         active_user=session.get("full_name", "Administrator")
#     )


@admin_bp.route("/ai-analyst", methods=["GET", "POST"])
def ai_analyst():
    """Admin interactive AI analyst page."""
    from database.database import fetch_all
    from ai_engine.engine import generate_alert_insight

    ai_report = None
    filters = {"users": [], "start_date": None, "end_date": None}

    # جلب المستخدمين للفلترة
    users = fetch_all("SELECT id, username, full_name FROM users ORDER BY full_name")

    if request.method == "POST":
        try:
            selected_users = request.form.getlist("users")
            start_date = request.form.get("start_date") or None
            end_date = request.form.get("end_date") or None
            filters = {"users": selected_users, "start_date": start_date, "end_date": end_date}

            # بناء الاستعلام الأساسي
            base_query = """
                SELECT a.*, u.username, u.full_name
                FROM activity_logs a
                JOIN users u ON a.user_id = u.id
                WHERE 1=1
            """
            params = []

            # فلترة المستخدمين
            if selected_users:
                placeholders = ','.join(['%s'] * len(selected_users))
                base_query += f" AND a.user_id IN ({placeholders})"
                params.extend(selected_users)

            # فلترة التاريخ
            if start_date:
                base_query += " AND a.timestamp >= %s"
                params.append(start_date)

            if end_date:
                base_query += " AND a.timestamp <= %s"
                params.append(end_date)

            base_query += " ORDER BY a.timestamp DESC LIMIT 200"

            # جلب الأنشطة من قاعدة البيانات
            activities = fetch_all(base_query, params)

            if activities:
                ai_input = {
                    "query_type": "behavior_analysis",
                    "filters": filters,
                    "records": activities,
                }
                ai_report = generate_alert_insight(ai_input) or "No AI insights available."
            else:
                ai_report = "No matching activities found for the selected filters."

        except Exception as e:
            ai_report = f"Error during AI analysis: {str(e)}"

    return render_template(
        "ai-analyst.html",
        users=users,
        ai_report=ai_report,
        filters=filters,
        active_user=session.get("full_name", "Administrator")
    )





@admin_bp.route("/reports/export-pdf", methods=["GET", "POST"])
def export_pdf_report():
    """Export filtered reports as PDF."""
    guard = _require_admin()
    if guard:
        return guard
    
    try:
        # جلب معايير الفلتر من request parameters (لـ GET) أو form data (لـ POST)
        if request.method == 'POST':
            start_date = request.form.get('start_date', '')
            end_date = request.form.get('end_date', '')
            risk_level = request.form.get('risk_level', '')
            status = request.form.get('status', '')
            report_type = request.form.get('report_type', 'comprehensive')
        else:
            start_date = request.args.get('start_date', '')
            end_date = request.args.get('end_date', '')
            risk_level = request.args.get('risk_level', '')
            status = request.args.get('status', '')
            report_type = request.args.get('report_type', 'comprehensive')

        # بناء query ديناميكي بناءً على الفلاتر
        query = """
            SELECT a.*, u.username, u.full_name 
            FROM alerts a 
            LEFT JOIN users u ON a.user_id = u.id 
            WHERE 1=1
        """
        params = []

        if start_date:
            query += " AND DATE(a.created_at) >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(a.created_at) <= %s"
            params.append(end_date)
        
        if risk_level:
            query += " AND a.risk_level = %s"
            params.append(risk_level)
        
        if status:
            query += " AND a.status = %s"
            params.append(status)

        query += " ORDER BY a.created_at DESC LIMIT 100"

        # جلب البيانات المصفاة من قاعدة البيانات
        alerts = fetch_all(query, tuple(params)) if params else fetch_all(query)

        # استخدام خدمة التقرير الحالية مع الفلاتر المطبقة
        filters = {
            'time_range': f"{start_date} to {end_date}" if start_date or end_date else 'Last 30 days',
            'report_type': report_type,
            'risk_level': risk_level,
            'status': status
        }
        
        pdf_buffer = generate_pdf_report(alerts, "security_alerts", filters)
        
        filename = f"cybersentinel-report-{datetime.now().strftime('%Y-%m-%d')}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"PDF export error: {str(e)}")
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500
    
    

@admin_bp.route("/ai-analyst/export-pdf", methods=["POST"])
def export_ai_analyst_pdf():
    """Export AI Analyst report as PDF."""
    guard = _require_admin()
    if guard:
        return guard
    
    try:
        ai_report = request.form.get('ai_report', '')
        analysis_type = request.form.get('analysis_type', 'comprehensive')
        users_analyzed = request.form.get('users_analyzed', 0)
        
        analysis_data = {
            'analysis_type': analysis_type,
            'time_period': 'Custom Analysis',
            'users_analyzed': users_analyzed,
            'confidence': 95
        }
        
        pdf_buffer = generate_ai_analyst_pdf(ai_report, analysis_data)
        
        filename = f"ai-analyst-report-{datetime.now().strftime('%Y-%m-%d-%H%M')}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500

@admin_bp.route("/reports/custom-pdf", methods=["POST"])
def generate_custom_pdf():
    """Generate custom PDF report with filters."""
    guard = _require_admin()
    if guard:
        return guard
    
    try:
        data = request.get_json()
        report_type = data.get('report_type', 'security')
        filters = data.get('filters', {})
        
        # جلب البيانات بناءً على الفلاتر
        if filters.get('users'):
            alerts = alert_service.get_recent_alerts(limit=200)
        else:
            alerts = alert_service.get_recent_alerts(limit=100)
        
        pdf_buffer = generate_pdf_report(alerts, report_type, filters)
        
        filename = f"custom-report-{datetime.now().strftime('%Y-%m-%d-%H%M')}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({"error": f"Custom PDF generation failed: {str(e)}"}), 500
    

@admin_bp.route("/reports", methods=["GET", "POST"])
def reports():
    """Reports page with filter support."""
    guard = _require_admin()
    if guard:
        return guard

    # جلب معايير الفلتر من request parameters
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    risk_level = request.args.get('risk_level', '')
    status = request.args.get('status', '')
    report_type = request.args.get('report_type', 'comprehensive')

    # بناء query ديناميكي بناءً على الفلاتر
    query = """
        SELECT a.*, u.username, u.full_name 
        FROM alerts a 
        LEFT JOIN users u ON a.user_id = u.id 
        WHERE 1=1
    """
    params = []

    if start_date:
        query += " AND DATE(a.created_at) >= %s"
        params.append(start_date)
    
    if end_date:
        query += " AND DATE(a.created_at) <= %s"
        params.append(end_date)
    
    if risk_level:
        query += " AND a.risk_level = %s"
        params.append(risk_level)
    
    if status:
        query += " AND a.status = %s"
        params.append(status)

    query += " ORDER BY a.created_at DESC LIMIT 100"

    # جلب البيانات المصفاة من قاعدة البيانات
    from database.database import fetch_all
    alerts = fetch_all(query, tuple(params)) if params else fetch_all(query)

    report_html = report_service.build_alert_report(alerts)
    
    return render_template(
        "reports.html", 
        alerts=alerts, 
        report_html=report_html,
        current_time=datetime.now(),
        filters={
            'start_date': start_date,
            'end_date': end_date,
            'risk_level': risk_level,
            'status': status,
            'report_type': report_type
        }
    )
