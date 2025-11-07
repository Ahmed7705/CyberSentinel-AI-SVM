"""User dashboard routes."""
from __future__ import annotations

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for, send_file
import os
from werkzeug.utils import secure_filename
from datetime import datetime

from database.database import execute, fetch_all, fetch_one
from services import alert_service, auth_service

user_bp = Blueprint("user", __name__, url_prefix="/user")

# Make get_file_icon available in templates within this Blueprint
@user_bp.app_context_processor

def utility_processor():
    return dict(get_file_icon=get_file_icon)

# إعدادات رفع الملفات
UPLOAD_FOLDER = 'uploads/user_files'
BASE_SAFE_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'csv', 'zip'}
SUSPICIOUS_EXTENSIONS = {
    'exe', 'bat', 'cmd', 'ps1', 'js', 'msi', 'dll', 'bin', 'jar',
    'py', 'rb', 'go', 'php', 'sh', 'sql'
}
ALLOWED_EXTENSIONS = BASE_SAFE_EXTENSIONS | SUSPICIOUS_EXTENSIONS
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_ROOT = os.path.abspath(os.path.join(os.getcwd(), UPLOAD_FOLDER))
os.makedirs(UPLOAD_ROOT, exist_ok=True)

def _require_user():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    if session.get("role") == "admin":
        return redirect(url_for("admin.dashboard"))
    return None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_user_upload_folder(user_id):
    """Create user-specific upload folder"""
    user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
    if not os.path.exists(user_folder):
        os.makedirs(user_folder, exist_ok=True)
    return user_folder


def _resolve_storage_path(stored_path: str) -> str:
    """Resolve stored file path to an absolute path inside the upload directory."""
    if not stored_path:
        raise ValueError("Stored path is empty")
    candidate = stored_path if os.path.isabs(stored_path) else os.path.join(os.getcwd(), stored_path)
    abs_path = os.path.abspath(candidate)
    if not abs_path.startswith(UPLOAD_ROOT):
        raise ValueError("File path escapes upload directory")
    return abs_path

@user_bp.route("/dashboard", methods=["GET"])
def dashboard():
    guard = _require_user()
    if guard:
        return guard
    user_id = session["user_id"]
    alerts = alert_service.get_user_alerts(user_id, limit=10)
    activities = fetch_all(
        """
        SELECT event_type, timestamp, source_ip, device, location, risk_score
        FROM activity_logs
        WHERE user_id = %s
        ORDER BY timestamp DESC
        LIMIT 15
        """,
        (user_id,),
    )
    
    # جلب إحصائيات المستخدم
    user_stats = fetch_all(
        """
        SELECT 
            COUNT(*) as total_files,
            SUM(CASE WHEN risk_level IN ('high', 'critical') THEN 1 ELSE 0 END) as suspicious_files,
            MAX(uploaded_at) as last_upload
        FROM user_files 
        WHERE user_id = %s
        """,
        (user_id,)
    )
    
    stats = user_stats[0] if user_stats else {'total_files': 0, 'suspicious_files': 0, 'last_upload': None}
    recent_files = fetch_all(
        """
        SELECT filename, file_size, risk_level, uploaded_at
        FROM user_files
        WHERE user_id = %s
        ORDER BY uploaded_at DESC
        LIMIT 5
        """,
        (user_id,),
    )
    
    return render_template("user-dashboard.html", 
                         alerts=alerts, 
                         activities=activities,
                         user_stats=stats,
                         files=recent_files,
                         active_user=session)

@user_bp.route("/profile", methods=["GET", "POST"])
def profile():
    guard = _require_user()
    if guard:
        return guard

    user_id = session["user_id"]
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
                (full_name, department, user_id),
            )
            if full_name:
                session["full_name"] = full_name
            if department:
                session["department"] = department
            flash("Profile updated", "success")
        else:
            flash("No changes submitted", "warning")

    user = auth_service.get_user_by_id(user_id)
    if not user:
        flash("User not found", "error")
        return redirect(url_for("auth.login"))

    return render_template("user-profile.html", user=user, active_user=session)


@user_bp.route("/files", methods=["GET", "POST"])
def files():
    guard = _require_user()
    if guard:
        return guard

    user_id = session["user_id"]
    if request.method == "POST":
        if 'files' not in request.files:
            flash('No files selected', 'error')
            return redirect(request.url)

        files = request.files.getlist('files')
        uploaded_count = 0
        warning_count = 0
        actor_name = session.get("full_name") or session.get("username") or f"user-{user_id}"

        for file in files:
            original_name = file.filename or ""
            if not original_name:
                continue

            safe_name = secure_filename(original_name)
            file_ext = safe_name.rsplit('.', 1)[1].lower() if '.' in safe_name else ''
            is_allowed_type = allowed_file(safe_name)
            looks_suspicious = file_ext in SUSPICIOUS_EXTENSIONS or not is_allowed_type
            risk_level = "high" if looks_suspicious else "low"

            if looks_suspicious:
                alert_service.create_alert(
                    user_id=user_id,
                    alert_type="suspicious_file_type",
                    description=f"{actor_name} uploaded high-risk file {original_name}",
                    risk_level="high",
                    risk_score=0.85,
                )

            if not is_allowed_type:
                flash(f'File type not allowed: {original_name}', 'error')
                warning_count += 1
                continue

            file.seek(0, 2)
            file_size = file.tell()
            file.seek(0)

            if file_size > MAX_FILE_SIZE:
                size_mb = round(file_size / (1024 * 1024), 2)
                alert_service.create_alert(
                    user_id=user_id,
                    alert_type="large_file_upload",
                    description=f"{actor_name} attempted to upload {original_name} ({size_mb} MB)",
                    risk_level="medium",
                    risk_score=0.7,
                )
                flash(f'File {original_name} exceeds 10MB limit', 'warning')
                warning_count += 1
                continue

            filename = safe_name
            user_folder = create_user_upload_folder(user_id)
            file_path = os.path.join(user_folder, filename)

            try:
                file.save(file_path)
                execute(
                    "INSERT INTO user_files (user_id, filename, file_path, file_size, file_type, risk_level, uploaded_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (user_id, filename, file_path, file_size, file_ext, risk_level, datetime.now()),
                )
                uploaded_count += 1
            except Exception as exc:
                flash(f'Error uploading {filename}: {exc}', 'error')

        if uploaded_count > 0:
            flash(f'Successfully uploaded {uploaded_count} files', 'success')
        if warning_count > 0:
            flash(f'{warning_count} files skipped or flagged', 'warning')

    user_files = fetch_all(
        """
        SELECT id, filename, file_size, file_type, risk_level, uploaded_at
        FROM user_files 
        WHERE user_id = %s 
        ORDER BY uploaded_at DESC
        """,
        (user_id,)
    )

    return render_template("user-files.html", files=user_files, active_user=session)


@user_bp.route("/security", methods=["GET"])
def security():
    """User security settings and tools"""
    guard = _require_user()
    if guard:
        return guard
    
    user_id = session["user_id"]
    
    # جلب إحصائيات الأمان
    # Aggregate recent alerts by risk level for the logged-in user
    security_stats = fetch_all(
        """
        SELECT 
            COUNT(*) as total_alerts,
            COALESCE(SUM(CASE WHEN risk_level = 'critical' THEN 1 ELSE 0 END), 0) as critical_alerts,
            COALESCE(SUM(CASE WHEN risk_level = 'high' THEN 1 ELSE 0 END), 0) as high_alerts
        FROM alerts
        WHERE user_id = %s
          AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """,
        (user_id,)
    )
    
    stats_row = security_stats[0] if security_stats else None
    stats = {
        'total_alerts': stats_row['total_alerts'] if stats_row else 0,
        'critical_alerts': stats_row['critical_alerts'] if stats_row else 0,
        'high_alerts': stats_row['high_alerts'] if stats_row else 0,
    }
    
    last_activity = fetch_all(
        """
        SELECT MAX(timestamp) as last_activity
        FROM activity_logs
        WHERE user_id = %s
        """,
        (user_id,)
    )
    stats['last_activity'] = last_activity[0]['last_activity'] if last_activity else None
    
    # جلب آخر الأنشطة
    recent_activities = fetch_all(
        """
        SELECT event_type, timestamp, source_ip, device, location, risk_score
        FROM activity_logs
        WHERE user_id = %s
        ORDER BY timestamp DESC
        LIMIT 10
        """,
        (user_id,)
    )
    
    return render_template("user-security.html", 
                         security_stats=stats,
                         recent_activities=recent_activities,
                         active_user=session)

@user_bp.route("/api/upload-file", methods=["POST"])
def upload_file_api():
    """API endpoint for file upload"""
    guard = _require_user()
    if guard:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session["user_id"]
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        # التحقق من حجم الملف
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': 'File size exceeds 10MB limit'}), 400
        
        # حفظ الملف
        filename = secure_filename(file.filename)
        user_folder = create_user_upload_folder(user_id)
        file_path = os.path.join(user_folder, filename)
        
        try:
            file.save(file_path)
            
            # تسجيل الملف في قاعدة البيانات
            execute(
                """
                INSERT INTO user_files 
                (user_id, filename, file_path, file_size, file_type, risk_level, uploaded_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (user_id, filename, file_path, file_size, 
                 filename.rsplit('.', 1)[1].lower(), 'low', datetime.now())
            )
            
            # إنشاء تنبيه إذا كان الملف كبيراً
            if file_size > 5 * 1024 * 1024:
                alert_service.create_alert(
                    user_id=user_id,
                    alert_type="large_file_upload",
                    description=f"Large file uploaded via API: {filename} ({file_size} bytes)",
                    risk_level="medium",
                    risk_score=0.6
                )
            
            return jsonify({
                'success': True,
                'filename': filename,
                'size': file_size,
                'message': 'File uploaded successfully'
            })
            
        except Exception as e:
            return jsonify({'error': f'Upload failed: {str(e)}'}), 500
    
    return jsonify({'error': 'File type not allowed'}), 400

@user_bp.route("/api/scan-file", methods=["POST"])
def scan_file():
    """Scan file for security threats"""
    guard = _require_user()
    if guard:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session["user_id"]
    file_id = request.json.get('file_id')
    
    if not file_id:
        return jsonify({'error': 'File ID required'}), 400
    
    # محاكاة عملية المسح الضوئي
    # في التطبيق الحقيقي، هنا ستكون عملية تحليل الملف
    import random
    risk_score = round(random.uniform(0.1, 0.3), 2)  # مخاطر منخفضة عشوائياً
    
    # تحديث مستوى الخطورة في قاعدة البيانات
    execute(
        "UPDATE user_files SET risk_level = %s WHERE id = %s AND user_id = %s",
        ('low' if risk_score < 0.5 else 'medium', file_id, user_id)
    )
    
    return jsonify({
        'success': True,
        'risk_score': risk_score,
        'risk_level': 'low' if risk_score < 0.5 else 'medium',
        'message': 'File scan completed'
    })


@user_bp.route("/api/delete-file/<int:file_id>", methods=["DELETE"])
def delete_file_api(file_id: int):
    guard = _require_user()
    if guard:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session["user_id"]
    record = fetch_one(
        "SELECT id, filename, file_path FROM user_files WHERE id = %s AND user_id = %s",
        (file_id, user_id)
    )
    if not record:
        return jsonify({'error': 'File not found'}), 404

    try:
        abs_path = _resolve_storage_path(record["file_path"])
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    if os.path.exists(abs_path):
        try:
            os.remove(abs_path)
        except OSError:
            # We log but continue with db delete so metadata is consistent
            pass

    execute("DELETE FROM user_files WHERE id = %s AND user_id = %s", (file_id, user_id))
    return jsonify({'success': True, 'message': 'File deleted successfully'})


@user_bp.route("/api/download-file/<int:file_id>", methods=["GET"])
def download_file_api(file_id: int):
    guard = _require_user()
    if guard:
        return guard

    user_id = session["user_id"]
    record = fetch_one(
        "SELECT filename, file_path FROM user_files WHERE id = %s AND user_id = %s",
        (file_id, user_id)
    )
    if not record:
        flash("File not found or unavailable", "error")
        return redirect(url_for("user.files"))

    try:
        abs_path = _resolve_storage_path(record["file_path"])
    except ValueError:
        flash("File location is invalid", "error")
        return redirect(url_for("user.files"))

    if not os.path.exists(abs_path):
        flash("File is missing from storage", "error")
        return redirect(url_for("user.files"))

    return send_file(abs_path, as_attachment=True, download_name=record.get("filename") or "download")

@user_bp.route("/api/alerts", methods=["GET"])
def alerts_json():
    guard = _require_user()
    if guard:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(alert_service.get_user_alerts(session["user_id"], limit=50))

@user_bp.route("/api/activities", methods=["GET"])
def activities_json():
    guard = _require_user()
    if guard:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session["user_id"]
    activities = fetch_all(
        """
        SELECT event_type, timestamp, source_ip, device, risk_score
        FROM activity_logs
        WHERE user_id = %s
        ORDER BY timestamp DESC
        LIMIT 20
        """,
        (user_id,)
    )
    
    return jsonify(activities)


def get_file_icon(file_type):
    """Get appropriate icon for file type."""
    icon_map = {
        'pdf': 'file-pdf',
        'doc': 'file-word',
        'docx': 'file-word',
        'xls': 'file-excel',
        'xlsx': 'file-excel',
        'ppt': 'file-powerpoint',
        'pptx': 'file-powerpoint',
        'jpg': 'file-image',
        'jpeg': 'file-image',
        'png': 'file-image',
        'gif': 'file-image',
        'zip': 'file-archive',
        'txt': 'file-alt'
    }
    return icon_map.get(file_type.lower(), 'file')

