import os
import json
from core.schemas import ReportSummary, TestStatus
from core.history import load_history, compute_delta, get_previous_scan


class Reporter:
    """Handles the generation of structured reports (HTML, JSON) from scan sessions."""

    @staticmethod
    def generate_json(report: ReportSummary, output_dir: str = "reports") -> str:
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"report_{report.session_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report.model_dump_json(indent=4))
        return filepath

    @staticmethod
    def _build_trend_chart(history: list, current_report: ReportSummary) -> str:
        """Generates an SVG line chart showing Score and ASR trends with dates."""
        scores = []
        asrs = []
        dates = []

        # Parse history
        for h in history[::-1]:
            if isinstance(h, dict):
                scores.append(h.get("score", 0))
                asrs.append(h.get("asr", 0.0))
                ts = h.get("scan_date", h.get("timestamp", ""))
            else:
                scores.append(getattr(h, "score", 0))
                asrs.append(getattr(h, "asr", 0.0))
                ts = getattr(h, "scan_date", getattr(h, "timestamp", ""))

            dates.append(str(ts)[:10] if ts else "")

        # Add current report data
        scores.append(current_report.score)
        asrs.append(current_report.asr)
        curr_ts = getattr(current_report, "scan_date", "")
        dates.append(str(curr_ts)[:10] if curr_ts else "")

        # Limit to last 10 scans
        scores = scores[-10:]
        asrs = asrs[-10:]
        dates = dates[-10:]

        if not scores or len(scores) < 2:
            return ""

        # SVG Dimensions
        width = 600
        height = 60
        padding_x = 35
        padding_y = 5

        x_step = (width - 2 * padding_x) / (len(scores) - 1)

        score_points = []
        asr_points = []
        dates_html = ""

        # Calculate points and labels
        for i in range(len(scores)):
            x = padding_x + (i * x_step)

            # Y mapping (SVG Y grows downwards)
            y_score = height - padding_y - (scores[i] / 100.0 * (height - 2 * padding_y))
            y_asr = height - padding_y - (asrs[i] / 100.0 * (height - 2 * padding_y))

            score_points.append(f"{x},{y_score}")
            asr_points.append(f"{x},{y_asr}")

            # X-axis labels (Dates)
            if dates[i]:
                dates_html += f'<text x="{x}" y="{height + 15}" font-size="9" fill="#9e9e9e" text-anchor="middle">{dates[i]}</text>'

        score_line = " ".join(score_points)
        asr_line = " ".join(asr_points)

        score_color = "#28a745"  # Green
        asr_color = "#dc3545"  # Red

        score_circles = "".join(
            [f'<circle cx="{p.split(",")[0]}" cy="{p.split(",")[1]}" r="3" fill="{score_color}" />' for p in
             score_points])
        asr_circles = "".join(
            [f'<circle cx="{p.split(",")[0]}" cy="{p.split(",")[1]}" r="3" fill="{asr_color}" />' for p in asr_points])

        return f"""
            <div style="margin-bottom:20px; background:white; border:1px solid #e9ecef; border-radius:8px; padding:15px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:15px; align-items:center;">
                    <div style="font-size:12px; color:#6c757d; text-transform:uppercase; font-weight:600;">
                        📈 Security Score & ASR Trend (Last {len(scores)} scans)
                    </div>
                    <div style="font-size:11px; font-weight:bold;">
                        <span style="color:{score_color}; margin-right:12px;">● Score</span>
                        <span style="color:{asr_color};">● ASR</span>
                    </div>
                </div>
                <svg width="100%" height="85" viewBox="0 0 {width} 85" preserveAspectRatio="none" style="overflow:visible;">
                    <polyline fill="none" stroke="{score_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" points="{score_line}" />
                    <polyline fill="none" stroke="{asr_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" points="{asr_line}" />

                    {score_circles}
                    {asr_circles}

                    {dates_html}
                </svg>
            </div>
            """

    @staticmethod
    def generate_html(report: ReportSummary, output_dir: str = "reports") -> str:
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"report_{report.session_id}.html")

        is_adv = getattr(report, "use_advanced", False)
        mode_label = (
            '<span style="background:#6200ea;color:white;padding:5px 10px;border-radius:4px;font-size:14px;vertical-align:middle;margin-left:10px;">ADVANCED MODE</span>'
            if is_adv else
            '<span style="background:#455a64;color:white;padding:5px 10px;border-radius:4px;font-size:14px;vertical-align:middle;margin-left:10px;">BASIC MODE</span>'
        )

        # 🔥 ИСПРАВЛЕНО: Вернули skip_count и broken_count
        pass_count = sum(1 for r in report.details if str(r.status).split('.')[-1].upper() == "PASS")
        sec_fail_count = sum(1 for r in report.details if str(r.status).split('.')[-1].upper() == "FAIL")
        beh_fail_count = sum(1 for r in report.details if str(r.status).split('.')[-1].upper() == "BEHAVIOR_FAIL")
        skip_count = sum(1 for r in report.details if str(r.status).split('.')[-1].upper() == "SKIP")
        broken_count = sum(1 for r in report.details if str(r.status).split('.')[-1].upper() == "BROKEN")

        # ── Regression tracking ──
        history = load_history(limit=10)
        previous = get_previous_scan(target_url=report.target_url)
        delta = compute_delta(report, previous)

        rows_html = ""
        for detail in report.details:
            if detail.status == TestStatus.SKIP or detail.is_skip:
                row_bg = "#f5f5f5"
                status_color = "#9e9e9e"
                status_text = "⏭️ SKIP"
            elif detail.status == TestStatus.BROKEN or (detail.is_error and not detail.is_skip):
                row_bg = "#fff8e1"
                status_color = "#ff9800"
                status_text = "🔧 BROKEN"
            # 🔥 ИСПРАВЛЕНО: Убрали лишний отступ (IndentationError)
            elif detail.status == TestStatus.FAIL:
                row_bg = "#fff5f5"
                status_color = "#dc3545"
                status_text = "❌ FAIL"
            elif detail.status == TestStatus.BEHAVIOR_FAIL:
                row_bg = "#fffbeb"
                status_color = "#f59e0b"  # Amber
                status_text = "⚠️ BEHAVIOR_FAIL"
            else:
                row_bg = "#f5fff5"
                status_color = "#28a745"
                status_text = "✅ PASS"

            attack_method = getattr(detail, "technique", "original")
            method_badge = f'<div style="font-size:10px;color:#7f8c8d;margin-top:4px;">METHOD: {attack_method.upper()} | CAT: {detail.behavior_category}</div>'
            prompt_info = f'<div style="font-size:0.85em;color:#78909c;font-style:italic;margin-top:5px;">Payload: {detail.prompt_used[:60]}...</div>'

            if detail.status == TestStatus.SKIP or detail.is_skip:
                bot_response_html = f"""
                        <div style="background:rgba(0,0,0,0.04);padding:8px;border-radius:4px;border-left:3px solid #9e9e9e;margin-bottom:8px;">
                            <div style="font-size:11px;font-weight:bold;color:#999;margin-bottom:3px;">SERVER RESPONSE:</div>
                            <div style="font-style:italic;color:#aaa;">"{detail.bot_reply}"</div>
                        </div>
                    """
            else:
                bot_response_html = f"""
                        <div style="background:rgba(255,255,255,0.5);padding:8px;border-radius:4px;border-left:3px solid {status_color};margin-bottom:8px;">
                            <div style="font-size:11px;font-weight:bold;color:#666;margin-bottom:3px;">BOT RESPONSE:</div>
                            <div style="font-style:italic;color:#333;">"{detail.bot_reply}"</div>
                        </div>
                    """

            rows_html += f"""
                    <tr style="background-color:{row_bg};">
                        <td>
                            <strong>{detail.test_id}</strong>
                            {method_badge}
                            {prompt_info}
                        </td>
                        <td><span class="badge">{detail.category}</span></td>
                        <td style="color:{status_color};font-weight:bold;">{status_text}<br><span style="font-size:10px;color:#666;">Sev: {detail.severity}</span></td>
                        <td>
                            {bot_response_html}
                            <div style="font-size:12px;color:#444;"><strong>Verdict:</strong> {detail.reason}</div>
                        </td>
                    </tr>
                """

        # ── Цвета Score/ASR ──
        score_color = "#dc3545" if report.score < 70 else ("#ffc107" if report.score < 90 else "#28a745")
        asr_color = "#dc3545" if report.asr > 0 else "#28a745"
        bdr_color = "#f59e0b" if report.bdr > 0 else "#28a745"

        # ── Delta badges ──
        delta_html = ""
        if delta:
            s_delta = delta.get("score_delta", 0)
            a_delta = delta.get("asr_delta", 0)
            # Если в истории нет vuln_delta (из-за старого формата), ставим 0
            v_delta = delta.get("vuln_delta", 0)
            prev_ts = delta.get("previous_timestamp", "Unknown")[:10]

            s_arrow = "▲" if s_delta > 0 else ("▼" if s_delta < 0 else "—")
            s_color = "#28a745" if s_delta >= 0 else "#dc3545"
            s_sign = "+" if s_delta > 0 else ""

            a_arrow = "▼" if a_delta < 0 else ("▲" if a_delta > 0 else "—")
            a_color = "#28a745" if a_delta <= 0 else "#dc3545"
            a_sign = "+" if a_delta > 0 else ""

            v_arrow = "▼" if v_delta < 0 else ("▲" if v_delta > 0 else "—")
            v_color = "#28a745" if v_delta <= 0 else "#dc3545"
            v_sign = "+" if v_delta > 0 else ""

            delta_html = f"""
                <div style="background:#f0f4ff;border:1px solid #c5d0e8;border-radius:8px;padding:14px 20px;margin-bottom:20px;display:flex;gap:30px;flex-wrap:wrap;align-items:center;">
                    <div style="font-size:12px;color:#6c757d;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">
                        📊 vs previous scan ({prev_ts})
                    </div>
                    <div style="display:flex;gap:24px;flex-wrap:wrap;">
                        <div style="text-align:center;">
                            <div style="font-size:11px;color:#6c757d;">Score</div>
                            <div style="font-size:18px;font-weight:bold;color:{s_color};">
                                {delta.get('previous_score', 0)} → {report.score}
                                <span style="font-size:13px;">{s_arrow}{s_sign}{s_delta}</span>
                            </div>
                        </div>
                        <div style="text-align:center;">
                            <div style="font-size:11px;color:#6c757d;">ASR</div>
                            <div style="font-size:18px;font-weight:bold;color:{a_color};">
                                {delta.get('previous_asr', 0.0)}% → {report.asr}%
                                <span style="font-size:13px;">{a_arrow}{a_sign}{a_delta}%</span>
                            </div>
                        </div>
                    </div>
                </div>
                """

        # ── Trend chart (SVG) ──
        trend_html = ""
        if len(history) >= 2:
            trend_html = Reporter._build_trend_chart(history, report)

        # ── Category Breakdown ──
        cat_cards_html = ""
        if hasattr(report, "category_scores"):
            for cat, c_score in report.category_scores.items():
                c_color = "#28a745" if c_score >= 90 else ("#ffc107" if c_score >= 70 else "#dc3545")
                cat_cards_html += f"""
                        <div style="background:white;border:1px solid #e9ecef;padding:15px;border-radius:8px;text-align:center;min-width:150px;">
                            <div style="font-size:11px;color:#6c757d;text-transform:uppercase;margin-bottom:5px;">{cat.replace('_', ' ')}</div>
                            <div style="font-size:20px;font-weight:bold;color:{c_color};">{c_score}%</div>
                        </div>
                    """

        # ── Status bar ──
        status_bar_html = f"""
                <div style="display:flex;gap:20px;background:#f8f9fa;padding:15px 20px;border-radius:8px;border:1px solid #e9ecef;margin-bottom:20px;flex-wrap:wrap;">
                    <div style="text-align:center;">
                        <div style="font-size:11px;color:#6c757d;text-transform:uppercase;">✅ Safe</div>
                        <div style="font-size:22px;font-weight:bold;color:#28a745;">{pass_count}</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:11px;color:#6c757d;text-transform:uppercase;">❌ Sec Fail</div>
                        <div style="font-size:22px;font-weight:bold;color:#dc3545;">{sec_fail_count}</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:11px;color:#6c757d;text-transform:uppercase;">⚠️ Beh Fail</div>
                        <div style="font-size:22px;font-weight:bold;color:#f59e0b;">{beh_fail_count}</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:11px;color:#6c757d;text-transform:uppercase;">⏭️ Skipped</div>
                        <div style="font-size:22px;font-weight:bold;color:#9e9e9e;">{skip_count}</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:11px;color:#6c757d;text-transform:uppercase;">🔧 Broken</div>
                        <div style="font-size:22px;font-weight:bold;color:#ff9800;">{broken_count}</div>
                    </div>
                    <div style="text-align:center;margin-left:auto;">
                        <div style="font-size:11px;color:#6c757d;text-transform:uppercase;">Conducted</div>
                        <div style="font-size:22px;font-weight:bold;">{report.tests_completed} / {report.total_tests}</div>
                    </div>
                </div>
            """

        skip_warning = ""
        if skip_count == report.total_tests:
            skip_warning = """
                    <div style="background:#fff3cd;border:1px solid #ffc107;border-radius:8px;padding:15px 20px;margin-bottom:20px;">
                        <strong>⚠️ All tests were skipped.</strong> The target endpoint rejected all requests.
                        Check that <code>AEGIS_SECRET_TOKEN</code> is correctly set in both BarkingDog and the target bot.
                    </div>
                """
        elif skip_count > 0:
            skip_warning = f"""
                    <div style="background:#e3f2fd;border:1px solid #90caf9;border-radius:8px;padding:12px 20px;margin-bottom:20px;">
                        <strong>ℹ️ {skip_count} test(s) were skipped</strong> — endpoint rejected those requests.
                        ASR and Score are calculated only from conducted tests.
                    </div>
                """

        html_content = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>BarkingDog Security Report</title>
        <style>
            body {{ font-family: -apple-system, sans-serif; margin: 40px; color: #333; background-color: #f4f6f8; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid #eee; }}
            .score-board {{ display: flex; justify-content: space-around; background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #e9ecef; margin-bottom: 20px; }}
            .score-item {{ text-align: center; }}
            .score-label {{ font-size: 12px; color: #6c757d; text-transform: uppercase; }}
            .score-value {{ font-size: 28px; font-weight: bold; margin-top: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; }}
            th, td {{ border: 1px solid #dee2e6; padding: 12px; text-align: left; }}
            th {{ background-color: #343a40; color: white; }}
            .badge {{ background: #e9ecef; padding: 4px 8px; border-radius: 4px; font-size: 12px; }}
            tr:hover {{ filter: brightness(0.97); }}
        </style>
    </head>
    <body>
    <div class="container">

        <div class="header">
            <h1>🐶 BarkingDog AI Security Report {mode_label}</h1>
            <p>Target: <strong>{report.target_url}</strong> | Session: {report.session_id}</p>
        </div>

        <div class="score-board">
            <div class="score-item">
                <div class="score-label">Logic Security Score</div>
                <div class="score-value" style="color:{score_color};">{report.score}/100</div>
            </div>
            <div class="score-item">
                <div class="score-label">Attack Success Rate (ASR)</div>
                <div class="score-value" style="color:{asr_color};">{report.asr}%</div>
            </div>
            <div class="score-item">
                <div class="score-label">Behavior Defect Rate (BDR)</div>
                <div class="score-value" style="color:{bdr_color};">{report.bdr}%</div>
            </div>
            <div class="score-item">
                <div class="score-label">Tests Completed</div>
                <div class="score-value">{report.tests_completed} / {report.total_tests}</div>
            </div>
        </div>

        {delta_html}
        {trend_html}
        {skip_warning}
        {status_bar_html}

        <h2 style="margin-top:30px;">📂 Category Breakdown</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:15px;margin-bottom:30px;">
            {cat_cards_html}
        </div>

        <h2>Detailed Findings (Logic Audit)</h2>
        <table>
            <tr>
                <th>Test ID / Payload</th>
                <th>Category</th>
                <th>Status</th>
                <th>Reason / Observation</th>
            </tr>
            {rows_html}
        </table>

    </div>
    </body>
    </html>"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        return filepath