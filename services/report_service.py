# """Reporting service to render alert summaries as HTML."""
# from __future__ import annotations
# # CyberSentinel-AI-SVM\services\report_service.py
# from datetime import datetime
# from jinja2 import Template

# REPORT_TEMPLATE = Template(
#     """
#     <section>
#         <header>
#             <h2>CyberSentinel Alert Report</h2>
#             <p>Generated: {{ generated_at }}</p>
#         </header>
#         <article>
#             {% if alerts %}
#             <table border="1" cellpadding="6" cellspacing="0">
#                 <thead>
#                     <tr>
#                         <th>ID</th>
#                         <th>User</th>
#                         <th>Type</th>
#                         <th>Risk Level</th>
#                         <th>Score</th>
#                         <th>Status</th>
#                         <th>Created</th>
#                     </tr>
#                 </thead>
#                 <tbody>
#                     {% for alert in alerts %}
#                     <tr>
#                         <td>{{ alert.id }}</td>
#                         <td>{{ alert.full_name or alert.username or 'N/A' }}</td>
#                         <td>{{ alert.alert_type }}</td>
#                         <td>{{ alert.risk_level|capitalize }}</td>
#                         <td>{{ '%.2f'|format(alert.risk_score) }}</td>
#                         <td>{{ alert.status|capitalize }}</td>
#                         <td>{{ alert.created_at }}</td>
#                     </tr>
#                     {% endfor %}
#                 </tbody>
#             </table>
#             {% else %}
#             <p>No alerts were found for the selected timeframe.</p>
#             {% endif %}
#         </article>
#     </section>
#     """
# )


# def build_alert_report(alerts: list[dict]) -> str:
#     """Build an HTML snippet summarising the supplied alerts."""
#     return REPORT_TEMPLATE.render(alerts=alerts, generated_at=datetime.utcnow().isoformat())

"""Advanced reporting service with PDF generation."""
from __future__ import annotations

from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def build_alert_report(alerts: list[dict]) -> str:
    """Build an HTML snippet summarizing the supplied alerts."""
    html_template = """
    <div style="background: #1a1f35; border: 1px solid #00ff88; border-radius: 8px; padding: 20px; margin: 10px 0;">
        <h3 style="color: #00ff88; margin-bottom: 15px;">📊 Alert Summary Report</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px;">
            <div style="background: rgba(0, 255, 136, 0.1); padding: 15px; border-radius: 6px; border: 1px solid #00ff88;">
                <div style="font-size: 24px; font-weight: bold; color: #00ff88;">{total_alerts}</div>
                <div style="color: #94a3b8; font-size: 14px;">Total Alerts</div>
            </div>
            <div style="background: rgba(239, 68, 68, 0.1); padding: 15px; border-radius: 6px; border: 1px solid #ef4444;">
                <div style="font-size: 24px; font-weight: bold; color: #ef4444;">{critical_alerts}</div>
                <div style="color: #94a3b8; font-size: 14px;">Critical</div>
            </div>
            <div style="background: rgba(245, 158, 11, 0.1); padding: 15px; border-radius: 6px; border: 1px solid #f59e0b;">
                <div style="font-size: 24px; font-weight: bold; color: #f59e0b;">{open_alerts}</div>
                <div style="color: #94a3b8; font-size: 14px;">Open</div>
            </div>
        </div>
    </div>
    """
    
    total_alerts = len(alerts)
    critical_alerts = len([a for a in alerts if a.get('risk_level') == 'critical'])
    open_alerts = len([a for a in alerts if a.get('status') == 'open'])
    
    return html_template.format(
        total_alerts=total_alerts,
        critical_alerts=critical_alerts,
        open_alerts=open_alerts
    )

def generate_pdf_report(alerts: list[dict], report_type: str = "security", filters: dict = None) -> BytesIO:
    """Generate a professional PDF report with cyber security theme."""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # العناصر التي ستظهر في الـ PDF
    elements = []
    styles = getSampleStyleSheet()
    
    # إضافة تنسيقات مخصصة
    cyber_style = ParagraphStyle(
        'CyberTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#00ff88'),
        spaceAfter=30,
        alignment=1  # مركز
    )
    
    sub_style = ParagraphStyle(
        'CyberSub',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#94a3b8'),
        spaceAfter=20,
        alignment=1
    )
    
    # الهيدر
    elements.append(Paragraph("CYBERSENTINEL AI", cyber_style))
    elements.append(Paragraph("Security Intelligence Report", sub_style))
    elements.append(Spacer(1, 20))
    
    # معلومات التقرير
    info_data = [
        ['Report Type', report_type.title() + ' Analysis'],
        ['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        ['Total Records', str(len(alerts))],
        ['Time Range', filters.get('time_range', 'Last 30 days') if filters else 'Custom']
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1a1f35')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#00ff88')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('LINEBELOW', (0, 0), (-1, -1), 1, colors.HexColor('#00ff88')),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 30))
    
    # إحصائيات سريعة
    elements.append(Paragraph("Executive Summary", styles['Heading2']))
    
    stats = calculate_report_stats(alerts)
    stats_data = [
        ['Metric', 'Count', 'Percentage'],
        ['Total Alerts', str(stats['total']), '100%'],
        ['Critical Alerts', str(stats['critical']), f"{stats['critical_pct']}%"],
        ['High Risk', str(stats['high']), f"{stats['high_pct']}%"],
        ['Open Alerts', str(stats['open']), f"{stats['open_pct']}%"],
        ['Resolved', str(stats['resolved']), f"{stats['resolved_pct']}%"]
    ]
    
    stats_table = Table(stats_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00ff88')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#2d3748')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#00ff88'))
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 30))
    
    # التفاصيل إذا كان هناك تنبيهات
    if alerts:
        elements.append(Paragraph("Alert Details", styles['Heading2']))
        
        # تحضير بيانات الجدول
        table_data = [['ID', 'Type', 'User', 'Risk', 'Score', 'Status', 'Date']]
        
        for alert in alerts[:50]:  # تحد إلى 50 سجل لتجنب صفحات طويلة
            table_data.append([
                str(alert.get('id', '')),
                alert.get('alert_type', 'Unknown')[:20],
                (alert.get('full_name') or alert.get('username', 'Unknown'))[:15],
                alert.get('risk_level', 'Unknown').capitalize(),
                f"{alert.get('risk_score', 0):.2f}",
                alert.get('status', 'Unknown').capitalize(),
                format_date(alert.get('created_at'))
            ])
        
        # إنشاء الجدول
        detail_table = Table(table_data, colWidths=[0.5*inch, 1.2*inch, 1*inch, 0.8*inch, 0.7*inch, 1*inch, 1*inch])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#1a1f35')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#374151')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#1a1f35'), colors.HexColor('#2d3748')])
        ]))
        
        # تلوين الصفوف حسب مستوى الخطورة
        for i, alert in enumerate(alerts[:50], 1):
            risk_level = alert.get('risk_level', '').lower()
            if risk_level == 'critical':
                detail_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#ef4444')),
                    ('TEXTCOLOR', (0, i), (-1, i), colors.white)
                ]))
            elif risk_level == 'high':
                detail_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f59e0b')),
                    ('TEXTCOLOR', (0, i), (-1, i), colors.black)
                ]))
        
        elements.append(detail_table)
    
    # التذييل
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Confidential - CyberSentinel AI Security Platform", 
                            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, 
                                         textColor=colors.HexColor('#94a3b8'), alignment=1)))
    
    # بناء الـ PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_ai_analyst_pdf(ai_report: str, analysis_data: dict) -> BytesIO:
    """Generate PDF for AI Analyst reports."""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # العنوان
    title_style = ParagraphStyle(
        'AITitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#00ff88'),
        alignment=1
    )
    
    elements.append(Paragraph("AI SECURITY ANALYST REPORT", title_style))
    elements.append(Spacer(1, 20))
    
    # معلومات التحليل
    elements.append(Paragraph("Analysis Overview", styles['Heading2']))
    overview_data = [
        ['Analysis Type', analysis_data.get('analysis_type', 'Comprehensive')],
        ['Time Period', analysis_data.get('time_period', 'Custom Range')],
        ['Users Analyzed', str(analysis_data.get('users_analyzed', 0))],
        ['AI Confidence', f"{analysis_data.get('confidence', 95)}%"]
    ]
    
    overview_table = Table(overview_data)
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1a1f35')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#00ff88')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#374151'))
    ]))
    elements.append(overview_table)
    elements.append(Spacer(1, 20))
    
    # تقرير AI
    elements.append(Paragraph("AI Analysis Results", styles['Heading2']))
    
    # تقسيم تقرير AI إلى فقرات
    report_lines = ai_report.split('\n\n')
    for line in report_lines:
        if line.strip():
            # تحديد النمط بناءً على المحتوى
            if line.startswith('🔍') or line.startswith('⚠️') or line.startswith('👤') or line.startswith('🚨') or line.startswith('💡') or line.startswith('⚡'):
                style = ParagraphStyle(
                    'SectionHeader',
                    parent=styles['Heading3'],
                    textColor=colors.HexColor('#00ff88'),
                    leftIndent=10
                )
            else:
                style = ParagraphStyle(
                    'NormalText',
                    parent=styles['Normal'],
                    textColor=colors.white,
                    leftIndent=20
                )
            
            elements.append(Paragraph(line, style))
            elements.append(Spacer(1, 8))
    
    # التوصيات
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Key Recommendations", styles['Heading2']))
    
    recommendations = [
        "Implement multi-factor authentication for high-risk departments",
        "Enhance monitoring of after-hours activities", 
        "Conduct security awareness training",
        "Schedule comprehensive security audit"
    ]
    
    for rec in recommendations:
        elements.append(Paragraph(f"• {rec}", 
                                ParagraphStyle('Bullet', parent=styles['Normal'], 
                                             textColor=colors.HexColor('#f59e0b'))))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def calculate_report_stats(alerts: list[dict]) -> dict:
    """Calculate statistics for the report."""
    total = len(alerts)
    critical = len([a for a in alerts if a.get('risk_level') == 'critical'])
    high = len([a for a in alerts if a.get('risk_level') == 'high'])
    open_alerts = len([a for a in alerts if a.get('status') == 'open'])
    resolved = len([a for a in alerts if a.get('status') == 'resolved'])
    
    return {
        'total': total,
        'critical': critical,
        'high': high,
        'open': open_alerts,
        'resolved': resolved,
        'critical_pct': round((critical / total) * 100, 1) if total > 0 else 0,
        'high_pct': round((high / total) * 100, 1) if total > 0 else 0,
        'open_pct': round((open_alerts / total) * 100, 1) if total > 0 else 0,
        'resolved_pct': round((resolved / total) * 100, 1) if total > 0 else 0
    }

def format_date(date_str) -> str:
    """Format date for display."""
    if not date_str:
        return 'Unknown'
    
    if isinstance(date_str, str):
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime('%Y-%m-%d')
        except:
            return date_str[:10]
    
    return str(date_str)




def get_filtered_alerts(filters):
    """Get alerts based on filters."""
    from database.database import fetch_all
    
    query = "SELECT a.*, u.username, u.full_name FROM alerts a LEFT JOIN users u ON a.user_id = u.id WHERE 1=1"
    params = []

    if filters.get('start_date'):
        query += " AND DATE(a.created_at) >= %s"
        params.append(filters['start_date'])
    
    if filters.get('end_date'):
        query += " AND DATE(a.created_at) <= %s"
        params.append(filters['end_date'])
    
    if filters.get('risk_level'):
        query += " AND a.risk_level = %s"
        params.append(filters['risk_level'])
    
    if filters.get('status'):
        query += " AND a.status = %s"
        params.append(filters['status'])

    query += " ORDER BY a.created_at DESC LIMIT 100"
    
    return fetch_all(query, tuple(params)) if params else fetch_all(query)