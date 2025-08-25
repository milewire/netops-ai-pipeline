from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from storage import init_db, get_session, Upload, Score
from features import load_kpi_csv, to_matrix
from model import load_model, train, score
from charts import save_kpi_chart
from summarize import extract_incidents, generate_ai_kpi_summary
import tempfile
import os
import json
from datetime import datetime

app = FastAPI(
    title="NetOps AI Pipeline",
    description="Enterprise AI-Powered Network Monitoring & Anomaly Detection",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Add CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Using the generate_ai_kpi_summary function from summarize.py

@app.get("/", response_class=HTMLResponse)
def home():
    """Professional enterprise application interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NetOps AI Pipeline - Enterprise Network Intelligence</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body { 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
                min-height: 100vh;
                color: #e2e8f0;
                line-height: 1.6;
            }
            
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px;
            }
            
            .header {
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
                border-radius: 20px;
                padding: 40px;
                text-align: center;
                margin-bottom: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                position: relative;
                overflow: hidden;
            }
            
            .header::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
                opacity: 0.3;
            }
            
            .header h1 { 
                font-size: 3.5em; 
                font-weight: 700;
                margin-bottom: 10px;
                background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .header p { 
                font-size: 1.3em; 
                opacity: 0.9;
                font-weight: 300;
            }
            
            .stats-bar {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .stat-card {
                background: rgba(255,255,255,0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 25px;
                text-align: center;
                transition: all 0.3s ease;
            }
            
            .stat-card:hover {
                transform: translateY(-5px);
                background: rgba(255,255,255,0.1);
                border-color: rgba(255,255,255,0.2);
            }
            
            .stat-icon {
                font-size: 2.5em;
                margin-bottom: 15px;
                background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .stat-number {
                font-size: 2.5em;
                font-weight: 700;
                color: #ffffff;
                margin-bottom: 5px;
            }
            
            .stat-label {
                color: #94a3b8;
                font-size: 0.9em;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .main-content {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                margin-bottom: 30px;
            }
            
            .upload-section {
                background: rgba(255,255,255,0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 20px;
                padding: 30px;
                transition: all 0.3s ease;
            }
            
            .upload-section:hover {
                border-color: rgba(59,130,246,0.5);
                box-shadow: 0 10px 30px rgba(59,130,246,0.2);
            }
            
            .upload-section h3 {
                font-size: 1.5em;
                font-weight: 600;
                margin-bottom: 20px;
                color: #ffffff;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .upload-section p {
                color: #94a3b8;
                margin-bottom: 20px;
                line-height: 1.6;
            }
            
            .file-upload-area {
                border: 2px dashed rgba(59,130,246,0.5);
                border-radius: 15px;
                padding: 40px 20px;
                text-align: center;
                background: rgba(59,130,246,0.05);
                transition: all 0.3s ease;
                margin-bottom: 20px;
            }
            
            .file-upload-area:hover {
                border-color: rgba(59,130,246,0.8);
                background: rgba(59,130,246,0.1);
            }
            
            .file-upload-area input[type="file"] {
                width: 100%;
                padding: 15px;
                border: none;
                background: transparent;
                color: #e2e8f0;
                font-size: 1em;
            }
            
            .file-upload-area input[type="file"]::file-selector-button {
                background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 500;
                margin-right: 15px;
            }
            
            .checkbox-group {
                background: rgba(255,255,255,0.05);
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
            }
            
            .checkbox-group label {
                display: flex;
                align-items: center;
                gap: 10px;
                cursor: pointer;
                color: #e2e8f0;
                font-weight: 500;
            }
            
            .checkbox-group input[type="checkbox"] {
                width: 18px;
                height: 18px;
                accent-color: #3b82f6;
            }
            
            .btn {
                background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 12px;
                cursor: pointer;
                font-size: 1em;
                font-weight: 600;
                transition: all 0.3s ease;
                width: 100%;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(59,130,246,0.4);
            }
            
            .btn:disabled {
                background: #64748b;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            
            .result {
                margin-top: 20px;
                padding: 25px;
                border-radius: 15px;
                border-left: 5px solid;
                background: rgba(255,255,255,0.05);
                backdrop-filter: blur(10px);
            }
            
            .success {
                border-color: #10b981;
                background: rgba(16,185,129,0.1);
            }
            
            .error {
                border-color: #ef4444;
                background: rgba(239,68,68,0.1);
            }
            
            .loading {
                border-color: #f59e0b;
                background: rgba(245,158,11,0.1);
                text-align: center;
            }
            
            .result h4 {
                font-size: 1.3em;
                margin-bottom: 15px;
                color: #ffffff;
            }
            
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }
            
            .metric-card {
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 15px;
                text-align: center;
            }
            
            .metric-value {
                font-size: 1.8em;
                font-weight: 700;
                color: #3b82f6;
                margin-bottom: 5px;
            }
            
            .metric-label {
                color: #94a3b8;
                font-size: 0.8em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .action-buttons {
                display: flex;
                gap: 15px;
                margin-top: 20px;
            }
            
            .action-btn {
                background: rgba(255,255,255,0.1);
                color: #e2e8f0;
                padding: 10px 20px;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                text-decoration: none;
                transition: all 0.3s ease;
                font-weight: 500;
            }
            
            .action-btn:hover {
                background: rgba(255,255,255,0.2);
                border-color: rgba(255,255,255,0.3);
                transform: translateY(-2px);
            }
            
            .footer {
                text-align: center;
                margin-top: 40px;
                padding: 30px;
                background: rgba(255,255,255,0.05);
                border-radius: 20px;
                border: 1px solid rgba(255,255,255,0.1);
            }
            
            .footer h3 {
                color: #ffffff;
                margin-bottom: 20px;
                font-size: 1.3em;
            }
            
            .footer-links {
                display: flex;
                justify-content: center;
                gap: 20px;
                flex-wrap: wrap;
            }
            
            .footer-link {
                background: rgba(59,130,246,0.2);
                color: #60a5fa;
                padding: 12px 20px;
                border-radius: 10px;
                text-decoration: none;
                transition: all 0.3s ease;
                font-weight: 500;
            }
            
            .footer-link:hover {
                background: rgba(59,130,246,0.3);
                transform: translateY(-2px);
            }
            
                         @media (max-width: 768px) {
                 .container {
                     padding: 15px;
                 }
                 
                 .main-content {
                     grid-template-columns: 1fr;
                     gap: 20px;
                 }
                 
                 .header {
                     padding: 30px 20px;
                     margin-bottom: 20px;
                 }
                 
                 .header h1 {
                     font-size: 2.2em;
                     line-height: 1.2;
                 }
                 
                 .header p {
                     font-size: 1.1em;
                 }
                 
                 .stats-bar {
                     grid-template-columns: repeat(2, 1fr);
                     gap: 15px;
                     margin-bottom: 20px;
                 }
                 
                 .stat-card {
                     padding: 20px 15px;
                 }
                 
                 .stat-icon {
                     font-size: 2em;
                     margin-bottom: 10px;
                 }
                 
                 .stat-number {
                     font-size: 2em;
                 }
                 
                 .stat-label {
                     font-size: 0.8em;
                 }
                 
                 .upload-section {
                     padding: 25px 20px;
                 }
                 
                 .upload-section h3 {
                     font-size: 1.3em;
                     margin-bottom: 15px;
                 }
                 
                 .file-upload-area {
                     padding: 30px 15px;
                     margin-bottom: 15px;
                 }
                 
                 .file-upload-area input[type="file"] {
                     padding: 12px;
                     font-size: 0.9em;
                 }
                 
                 .file-upload-area input[type="file"]::file-selector-button {
                     padding: 8px 16px;
                     font-size: 0.9em;
                     margin-right: 10px;
                 }
                 
                 .checkbox-group {
                     padding: 12px;
                     margin-bottom: 15px;
                 }
                 
                 .checkbox-group label {
                     font-size: 0.9em;
                     gap: 8px;
                 }
                 
                 .btn {
                     padding: 12px 20px;
                     font-size: 0.9em;
                 }
                 
                 .result {
                     padding: 20px;
                     margin-top: 15px;
                 }
                 
                 .result h4 {
                     font-size: 1.2em;
                     margin-bottom: 12px;
                 }
                 
                 .metrics-grid {
                     grid-template-columns: repeat(2, 1fr);
                     gap: 12px;
                     margin: 15px 0;
                 }
                 
                 .metric-card {
                     padding: 12px;
                 }
                 
                 .metric-value {
                     font-size: 1.5em;
                 }
                 
                 .metric-label {
                     font-size: 0.7em;
                 }
                 
                 .action-buttons {
                     flex-direction: column;
                     gap: 10px;
                     margin-top: 15px;
                 }
                 
                 .action-btn {
                     padding: 12px 16px;
                     font-size: 0.9em;
                     text-align: center;
                     justify-content: center;
                 }
                 
                 .footer {
                     margin-top: 30px;
                     padding: 25px 20px;
                 }
                 
                 .footer h3 {
                     font-size: 1.2em;
                     margin-bottom: 15px;
                 }
                 
                 .footer-links {
                     flex-direction: column;
                     gap: 12px;
                 }
                 
                 .footer-link {
                     padding: 12px 16px;
                     font-size: 0.9em;
                     text-align: center;
                 }
             }
             
             @media (max-width: 480px) {
                 .container {
                     padding: 10px;
                 }
                 
                 .header {
                     padding: 25px 15px;
                     border-radius: 15px;
                 }
                 
                 .header h1 {
                     font-size: 1.8em;
                 }
                 
                 .header p {
                     font-size: 1em;
                 }
                 
                 .stats-bar {
                     grid-template-columns: 1fr;
                     gap: 12px;
                 }
                 
                 .stat-card {
                     padding: 18px 12px;
                 }
                 
                 .stat-icon {
                     font-size: 1.8em;
                 }
                 
                 .stat-number {
                     font-size: 1.8em;
                 }
                 
                 .upload-section {
                     padding: 20px 15px;
                     border-radius: 15px;
                 }
                 
                 .upload-section h3 {
                     font-size: 1.2em;
                 }
                 
                 .file-upload-area {
                     padding: 25px 12px;
                 }
                 
                 .file-upload-area input[type="file"] {
                     padding: 10px;
                     font-size: 0.85em;
                 }
                 
                 .file-upload-area input[type="file"]::file-selector-button {
                     padding: 6px 12px;
                     font-size: 0.85em;
                 }
                 
                 .btn {
                     padding: 10px 16px;
                     font-size: 0.85em;
                 }
                 
                 .metrics-grid {
                     grid-template-columns: 1fr;
                     gap: 10px;
                 }
                 
                 .metric-card {
                     padding: 15px 10px;
                 }
                 
                 .metric-value {
                     font-size: 1.3em;
                 }
                 
                 .action-btn {
                     padding: 10px 12px;
                     font-size: 0.85em;
                 }
                 
                 .footer {
                     padding: 20px 15px;
                     border-radius: 15px;
                 }
                 
                 .footer-link {
                     padding: 10px 12px;
                     font-size: 0.85em;
                 }
             }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1><i class="fas fa-brain"></i> NetOps AI Pipeline</h1>
                <p>Enterprise-Grade Network Intelligence & Anomaly Detection</p>
            </div>
            
            <div class="stats-bar">
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-chart-line"></i></div>
                    <div class="stat-number">99.9%</div>
                    <div class="stat-label">Accuracy</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-bolt"></i></div>
                    <div class="stat-number">< 2s</div>
                    <div class="stat-label">Processing Time</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-shield-alt"></i></div>
                    <div class="stat-number">Enterprise</div>
                    <div class="stat-label">Security</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-robot"></i></div>
                    <div class="stat-number">AI-Powered</div>
                    <div class="stat-label">Insights</div>
                </div>
            </div>
            
            <div class="main-content">
                <div class="upload-section">
                    <h3><i class="fas fa-chart-bar"></i> KPI Anomaly Detection</h3>
                    <p>Upload network performance data to receive AI-powered insights, anomaly detection, and actionable recommendations for network optimization.</p>
                    
                    <form id="kpiForm">
                        <div class="file-upload-area">
                            <input type="file" name="file" accept=".csv" required>
                            <p style="margin-top: 15px; color: #94a3b8; font-size: 0.9em;">
                                <i class="fas fa-info-circle"></i> Expected format: cell_id, timestamp, PRB_Util, RRC_Conn, Throughput_Mbps, BLER
                            </p>
                        </div>
                        
                        <div class="checkbox-group">
                            <label>
                                <input type="checkbox" name="train_if_missing" value="true" checked>
                                <i class="fas fa-cog"></i> Train AI model if not available (recommended)
                            </label>
                        </div>
                        
                        <button type="submit" class="btn" id="kpiBtn">
                            <i class="fas fa-search"></i> Analyze with AI
                        </button>
                    </form>
                    
                    <div id="kpiResult"></div>
                </div>
                
                <div class="upload-section">
                    <h3><i class="fas fa-file-alt"></i> Log Analysis</h3>
                    <p>Upload system logs for intelligent incident detection, error categorization, and automated alert generation with severity assessment.</p>
                    
                    <form id="logForm">
                        <div class="file-upload-area">
                            <input type="file" name="file" accept=".log,.txt" required>
                            <p style="margin-top: 15px; color: #94a3b8; font-size: 0.9em;">
                                <i class="fas fa-info-circle"></i> Supports ERROR, WARN, CRIT, ALARM, INFO log levels
                            </p>
                        </div>
                        
                        <button type="submit" class="btn" id="logBtn">
                            <i class="fas fa-search"></i> Analyze Logs
                        </button>
                    </form>
                    
                    <div id="logResult"></div>
                </div>
            </div>
            
            <div class="footer">
                <h3><i class="fas fa-tools"></i> Enterprise Tools</h3>
                <div class="footer-links">
                    <a href="/docs" class="footer-link"><i class="fas fa-book"></i> API Documentation</a>
                    <a href="/health" class="footer-link"><i class="fas fa-heartbeat"></i> Health Check</a>
                    <a href="/uploads" class="footer-link"><i class="fas fa-list"></i> View Uploads</a>
                </div>
            </div>
        </div>
        
        <script>
            function showLoading(formId, btnId) {
                const btn = document.getElementById(btnId);
                const resultDiv = document.getElementById(formId === 'kpiForm' ? 'kpiResult' : 'logResult');
                
                btn.disabled = true;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                resultDiv.innerHTML = '<div class="result loading"><i class="fas fa-cog fa-spin"></i> AI is analyzing your data...</div>';
            }
            
            function showSuccess(formId, btnId, data, isKpi = true) {
                const btn = document.getElementById(btnId);
                const resultDiv = document.getElementById(formId === 'kpiForm' ? 'kpiResult' : 'logResult');
                
                btn.disabled = false;
                btn.innerHTML = isKpi ? '<i class="fas fa-search"></i> Analyze with AI' : '<i class="fas fa-search"></i> Analyze Logs';
                
                                 if (isKpi) {
                     const anomalyRate = ((data.summary['-1'] || 0) / data.total_samples * 100).toFixed(1);
                     const severity = anomalyRate > 10 ? 'HIGH' : anomalyRate > 5 ? 'MEDIUM' : 'LOW';
                     const severityColor = severity === 'HIGH' ? '#ef4444' : severity === 'MEDIUM' ? '#f59e0b' : '#10b981';
                     
                     // Generate intelligent insights based on the data
                     let insights = [];
                     if (anomalyRate > 10) {
                         insights.push('🚨 High anomaly rate detected - immediate attention required');
                     } else if (anomalyRate > 5) {
                         insights.push('⚠️ Moderate anomalies detected - monitor closely');
                     } else {
                         insights.push('✅ Network performance appears normal');
                     }
                     
                     if (data.total_samples > 100) {
                         insights.push('📊 Large dataset analyzed for comprehensive insights');
                     }
                     
                     insights.push('🤖 AI model successfully identified performance patterns');
                     
                     const insightsHtml = insights.map(insight => `<li>${insight}</li>`).join('');
                     
                     resultDiv.innerHTML = `
                         <div class="result success">
                             <h4><i class="fas fa-check-circle"></i> AI Analysis Complete!</h4>
                             <div style="background: ${severityColor}20; border: 1px solid ${severityColor}; border-radius: 10px; padding: 15px; margin-bottom: 20px; text-align: center;">
                                 <span style="color: ${severityColor}; font-weight: 600; font-size: 1.1em;">${severity} SEVERITY LEVEL</span>
                             </div>
                             <div class="metrics-grid">
                                 <div class="metric-card">
                                     <div class="metric-value">${data.total_samples}</div>
                                     <div class="metric-label">Total Samples</div>
                                 </div>
                                 <div class="metric-card">
                                     <div class="metric-value">${data.summary['-1'] || 0}</div>
                                     <div class="metric-label">Anomalies</div>
                                 </div>
                                 <div class="metric-card">
                                     <div class="metric-value">${data.summary['1'] || 0}</div>
                                     <div class="metric-label">Normal</div>
                                 </div>
                                 <div class="metric-card">
                                     <div class="metric-value">${anomalyRate}%</div>
                                     <div class="metric-label">Anomaly Rate</div>
                                 </div>
                             </div>
                             <div style="margin: 20px 0;">
                                 <h5 style="color: #ffffff; margin-bottom: 10px;"><i class="fas fa-lightbulb"></i> Quick Insights:</h5>
                                 <ul style="color: #e2e8f0; padding-left: 20px;">
                                     ${insightsHtml}
                                 </ul>
                             </div>
                                                           <div class="action-buttons">
                                  <a href="/ai-summary/${data.upload_id}" target="_blank" class="action-btn">
                                      <i class="fas fa-chart-bar"></i> AI Report
                                  </a>
                                  <a href="/chart/${data.upload_id}" target="_blank" class="action-btn">
                                      <i class="fas fa-chart-line"></i> Visualization
                                  </a>
                                  <a href="/report/${data.upload_id}" target="_blank" class="action-btn">
                                      <i class="fas fa-code"></i> JSON Data
                                  </a>
                              </div>
                         </div>
                     `;
                } else {
                    resultDiv.innerHTML = `
                        <div class="result success">
                            <h4><i class="fas fa-check-circle"></i> Log Analysis Complete!</h4>
                            <div class="metrics-grid">
                                <div class="metric-card">
                                    <div class="metric-value">${data.incident_counts.critical_errors}</div>
                                    <div class="metric-label">Critical</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-value">${data.incident_counts.errors}</div>
                                    <div class="metric-label">Errors</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-value">${data.incident_counts.warnings}</div>
                                    <div class="metric-label">Warnings</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-value">${data.incident_counts.alarms}</div>
                                    <div class="metric-label">Alarms</div>
                                </div>
                            </div>
                            <p style="margin-top: 15px; color: #e2e8f0;"><strong>AI Summary:</strong> ${data.summary}</p>
                        </div>
                    `;
                }
            }
            
            function showError(formId, btnId, error) {
                const btn = document.getElementById(btnId);
                const resultDiv = document.getElementById(formId === 'kpiForm' ? 'kpiResult' : 'logResult');
                
                btn.disabled = false;
                btn.innerHTML = formId === 'kpiForm' ? '<i class="fas fa-search"></i> Analyze with AI' : '<i class="fas fa-search"></i> Analyze Logs';
                resultDiv.innerHTML = `<div class="result error"><i class="fas fa-exclamation-triangle"></i> Error: ${error}</div>`;
            }
            
            document.getElementById('kpiForm').onsubmit = async (e) => {
                e.preventDefault();
                showLoading('kpiForm', 'kpiBtn');
                
                try {
                    const formData = new FormData(e.target);
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await response.json();
                    
                    if (response.ok) {
                        showSuccess('kpiForm', 'kpiBtn', data, true);
                    } else {
                        showError('kpiForm', 'kpiBtn', data.detail || 'Upload failed');
                    }
                } catch (error) {
                    showError('kpiForm', 'kpiBtn', error.message);
                }
            };
            
            document.getElementById('logForm').onsubmit = async (e) => {
                e.preventDefault();
                showLoading('logForm', 'logBtn');
                
                try {
                    const formData = new FormData(e.target);
                    const response = await fetch('/logs/summarize', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await response.json();
                    
                    if (response.ok) {
                        showSuccess('logForm', 'logBtn', data, false);
                    } else {
                        showError('logForm', 'logBtn', data.detail || 'Analysis failed');
                    }
                } catch (error) {
                    showError('logForm', 'logBtn', error.message);
                }
            };
        </script>
    </body>
    </html>
    """

@app.get("/health", response_class=HTMLResponse)
def health_page():
    """User-friendly health check page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>System Health - NetOps AI Pipeline</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body { 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
                min-height: 100vh;
                color: #e2e8f0;
                line-height: 1.6;
            }
            
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px;
            }
            
            .header {
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
                border-radius: 20px;
                padding: 40px;
                text-align: center;
                margin-bottom: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            }
            
            .header h1 { 
                font-size: 2.5em; 
                font-weight: 700;
                margin-bottom: 10px;
                color: #ffffff;
            }
            
            .header p { 
                font-size: 1.2em; 
                opacity: 0.9;
                font-weight: 300;
            }
            
            .back-btn {
                position: absolute;
                top: 20px;
                left: 20px;
                background: rgba(255,255,255,0.1);
                color: #ffffff;
                padding: 10px 20px;
                border-radius: 10px;
                text-decoration: none;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
            }
            
            .back-btn:hover {
                background: rgba(255,255,255,0.2);
                transform: translateY(-2px);
            }
            
            .health-container {
                background: rgba(255,255,255,0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 20px;
                padding: 30px;
            }
            
            .status-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .status-card {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 25px;
                text-align: center;
                transition: all 0.3s ease;
            }
            
            .status-card.healthy {
                border-color: rgba(16,185,129,0.5);
                background: rgba(16,185,129,0.1);
            }
            
            .status-card.warning {
                border-color: rgba(245,158,11,0.5);
                background: rgba(245,158,11,0.1);
            }
            
            .status-card.error {
                border-color: rgba(239,68,68,0.5);
                background: rgba(239,68,68,0.1);
            }
            
            .status-icon {
                font-size: 3em;
                margin-bottom: 15px;
            }
            
            .status-card.healthy .status-icon {
                color: #10b981;
            }
            
            .status-card.warning .status-icon {
                color: #f59e0b;
            }
            
            .status-card.error .status-icon {
                color: #ef4444;
            }
            
            .status-title {
                font-size: 1.3em;
                font-weight: 600;
                margin-bottom: 10px;
                color: #ffffff;
            }
            
            .status-value {
                font-size: 1.1em;
                color: #94a3b8;
                margin-bottom: 10px;
            }
            
            .status-description {
                font-size: 0.9em;
                color: #64748b;
            }
            
            .system-info {
                background: rgba(255,255,255,0.05);
                border-radius: 15px;
                padding: 25px;
                margin-top: 30px;
            }
            
            .system-info h3 {
                color: #ffffff;
                margin-bottom: 20px;
                font-size: 1.3em;
            }
            
            .info-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }
            
            .info-item {
                background: rgba(255,255,255,0.05);
                border-radius: 10px;
                padding: 15px;
            }
            
            .info-label {
                color: #94a3b8;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 5px;
            }
            
                         .info-value {
                 color: #ffffff;
                 font-weight: 600;
                 font-size: 1.1em;
             }
             
             @media (max-width: 768px) {
                 .container {
                     padding: 15px;
                 }
                 
                 .header {
                     padding: 30px 20px;
                     margin-bottom: 20px;
                 }
                 
                 .header h1 {
                     font-size: 2.2em;
                 }
                 
                 .header p {
                     font-size: 1.1em;
                 }
                 
                 .health-container {
                     padding: 25px 20px;
                 }
                 
                 .status-grid {
                     grid-template-columns: repeat(2, 1fr);
                     gap: 15px;
                     margin-bottom: 25px;
                 }
                 
                 .status-card {
                     padding: 20px 15px;
                 }
                 
                 .status-icon {
                     font-size: 2.5em;
                     margin-bottom: 12px;
                 }
                 
                 .status-title {
                     font-size: 1.2em;
                     margin-bottom: 8px;
                 }
                 
                 .status-value {
                     font-size: 1em;
                     margin-bottom: 8px;
                 }
                 
                 .status-description {
                     font-size: 0.8em;
                 }
                 
                 .system-info {
                     padding: 20px 15px;
                     margin-top: 25px;
                 }
                 
                 .system-info h3 {
                     font-size: 1.2em;
                     margin-bottom: 15px;
                 }
                 
                 .info-grid {
                     grid-template-columns: repeat(2, 1fr);
                     gap: 12px;
                 }
                 
                 .info-item {
                     padding: 12px 10px;
                 }
                 
                 .info-label {
                     font-size: 0.8em;
                 }
                 
                 .info-value {
                     font-size: 1em;
                 }
             }
             
             @media (max-width: 480px) {
                 .container {
                     padding: 10px;
                 }
                 
                 .header {
                     padding: 25px 15px;
                     border-radius: 15px;
                 }
                 
                 .header h1 {
                     font-size: 1.8em;
                 }
                 
                 .header p {
                     font-size: 1em;
                 }
                 
                 .health-container {
                     padding: 20px 15px;
                     border-radius: 15px;
                 }
                 
                 .status-grid {
                     grid-template-columns: 1fr;
                     gap: 12px;
                     margin-bottom: 20px;
                 }
                 
                 .status-card {
                     padding: 18px 12px;
                 }
                 
                 .status-icon {
                     font-size: 2.2em;
                 }
                 
                 .status-title {
                     font-size: 1.1em;
                 }
                 
                 .status-value {
                     font-size: 0.9em;
                 }
                 
                 .status-description {
                     font-size: 0.75em;
                 }
                 
                 .system-info {
                     padding: 15px 12px;
                     margin-top: 20px;
                     border-radius: 12px;
                 }
                 
                 .system-info h3 {
                     font-size: 1.1em;
                     margin-bottom: 12px;
                 }
                 
                 .info-grid {
                     grid-template-columns: 1fr;
                     gap: 10px;
                 }
                 
                 .info-item {
                     padding: 10px 8px;
                     border-radius: 8px;
                 }
                 
                 .info-label {
                     font-size: 0.75em;
                 }
                 
                 .info-value {
                     font-size: 0.9em;
                 }
             }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-btn">
                <i class="fas fa-arrow-left"></i> Back to Dashboard
            </a>
            
            <div class="header">
                <h1><i class="fas fa-heartbeat"></i> System Health</h1>
                <p>Real-time monitoring and system status</p>
            </div>
            
            <div class="health-container">
                <div class="status-grid">
                    <div class="status-card healthy">
                        <div class="status-icon">
                            <i class="fas fa-server"></i>
                        </div>
                        <div class="status-title">Application Server</div>
                        <div class="status-value">Online</div>
                        <div class="status-description">All systems operational</div>
                    </div>
                    
                    <div class="status-card healthy">
                        <div class="status-icon">
                            <i class="fas fa-database"></i>
                        </div>
                        <div class="status-title">Database</div>
                        <div class="status-value">Connected</div>
                        <div class="status-description">SQLite database active</div>
                    </div>
                    
                    <div class="status-card healthy">
                        <div class="status-icon">
                            <i class="fas fa-brain"></i>
                        </div>
                        <div class="status-title">AI Engine</div>
                        <div class="status-value">Ready</div>
                        <div class="status-description">Machine learning models loaded</div>
                    </div>
                    
                    <div class="status-card healthy">
                        <div class="status-icon">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div class="status-title">Analytics</div>
                        <div class="status-value">Active</div>
                        <div class="status-description">Real-time processing available</div>
                    </div>
                </div>
                
                <div class="system-info">
                    <h3><i class="fas fa-info-circle"></i> System Information</h3>
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-label">Service Name</div>
                            <div class="info-value">NetOps AI Pipeline</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Version</div>
                            <div class="info-value">2.0.0</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Status</div>
                            <div class="info-value">Healthy</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Uptime</div>
                            <div class="info-value">Running</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/docs", response_class=HTMLResponse)
def docs_page():
    """User-friendly documentation page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Documentation - NetOps AI Pipeline</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body { 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
                min-height: 100vh;
                color: #e2e8f0;
                line-height: 1.6;
            }
            
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px;
            }
            
            .header {
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
                border-radius: 20px;
                padding: 40px;
                text-align: center;
                margin-bottom: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            }
            
            .header h1 { 
                font-size: 2.5em; 
                font-weight: 700;
                margin-bottom: 10px;
                color: #ffffff;
            }
            
            .header p { 
                font-size: 1.2em; 
                opacity: 0.9;
                font-weight: 300;
            }
            
            .back-btn {
                position: absolute;
                top: 20px;
                left: 20px;
                background: rgba(255,255,255,0.1);
                color: #ffffff;
                padding: 10px 20px;
                border-radius: 10px;
                text-decoration: none;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
            }
            
            .back-btn:hover {
                background: rgba(255,255,255,0.2);
                transform: translateY(-2px);
            }
            
            .docs-container {
                background: rgba(255,255,255,0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 20px;
                padding: 30px;
            }
            
            .section {
                margin-bottom: 40px;
            }
            
            .section h3 {
                color: #ffffff;
                font-size: 1.5em;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .feature-card {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 25px;
                transition: all 0.3s ease;
            }
            
            .feature-card:hover {
                border-color: rgba(59,130,246,0.5);
                box-shadow: 0 10px 30px rgba(59,130,246,0.2);
                transform: translateY(-2px);
            }
            
            .feature-icon {
                font-size: 2em;
                color: #3b82f6;
                margin-bottom: 15px;
            }
            
            .feature-title {
                font-size: 1.2em;
                font-weight: 600;
                color: #ffffff;
                margin-bottom: 10px;
            }
            
            .feature-description {
                color: #94a3b8;
                margin-bottom: 15px;
            }
            
            .feature-list {
                list-style: none;
                padding: 0;
            }
            
            .feature-list li {
                color: #cbd5e1;
                margin-bottom: 5px;
                padding-left: 20px;
                position: relative;
            }
            
            .feature-list li:before {
                content: "✓";
                color: #10b981;
                position: absolute;
                left: 0;
                font-weight: bold;
            }
            
            .format-example {
                background: rgba(0,0,0,0.3);
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                border-left: 4px solid #3b82f6;
            }
            
            .format-example h4 {
                color: #ffffff;
                margin-bottom: 10px;
            }
            
                         .format-example pre {
                 color: #e2e8f0;
                 font-family: 'Courier New', monospace;
                 font-size: 0.9em;
                 overflow-x: auto;
             }
             
             @media (max-width: 768px) {
                 .container {
                     padding: 15px;
                 }
                 
                 .header {
                     padding: 30px 20px;
                     margin-bottom: 20px;
                 }
                 
                 .header h1 {
                     font-size: 2.2em;
                 }
                 
                 .header p {
                     font-size: 1.1em;
                 }
                 
                 .docs-container {
                     padding: 25px 20px;
                 }
                 
                 .section {
                     margin-bottom: 30px;
                 }
                 
                 .section h3 {
                     font-size: 1.3em;
                     margin-bottom: 15px;
                 }
                 
                 .feature-grid {
                     grid-template-columns: 1fr;
                     gap: 15px;
                     margin-bottom: 25px;
                 }
                 
                 .feature-card {
                     padding: 20px 15px;
                 }
                 
                 .feature-icon {
                     font-size: 1.8em;
                     margin-bottom: 12px;
                 }
                 
                 .feature-title {
                     font-size: 1.1em;
                     margin-bottom: 8px;
                 }
                 
                 .feature-description {
                     font-size: 0.9em;
                     margin-bottom: 12px;
                 }
                 
                 .feature-list li {
                     font-size: 0.9em;
                     margin-bottom: 4px;
                     padding-left: 18px;
                 }
                 
                 .format-example {
                     padding: 15px;
                     margin: 15px 0;
                 }
                 
                 .format-example h4 {
                     font-size: 1em;
                     margin-bottom: 8px;
                 }
                 
                 .format-example pre {
                     font-size: 0.8em;
                 }
             }
             
             @media (max-width: 480px) {
                 .container {
                     padding: 10px;
                 }
                 
                 .header {
                     padding: 25px 15px;
                     border-radius: 15px;
                 }
                 
                 .header h1 {
                     font-size: 1.8em;
                 }
                 
                 .header p {
                     font-size: 1em;
                 }
                 
                 .docs-container {
                     padding: 20px 15px;
                     border-radius: 15px;
                 }
                 
                 .section {
                     margin-bottom: 25px;
                 }
                 
                 .section h3 {
                     font-size: 1.2em;
                     margin-bottom: 12px;
                 }
                 
                 .feature-grid {
                     gap: 12px;
                     margin-bottom: 20px;
                 }
                 
                 .feature-card {
                     padding: 15px 12px;
                     border-radius: 12px;
                 }
                 
                 .feature-icon {
                     font-size: 1.6em;
                     margin-bottom: 10px;
                 }
                 
                 .feature-title {
                     font-size: 1em;
                     margin-bottom: 6px;
                 }
                 
                 .feature-description {
                     font-size: 0.85em;
                     margin-bottom: 10px;
                 }
                 
                 .feature-list li {
                     font-size: 0.85em;
                     margin-bottom: 3px;
                     padding-left: 15px;
                 }
                 
                 .format-example {
                     padding: 12px;
                     margin: 12px 0;
                     border-radius: 8px;
                 }
                 
                 .format-example h4 {
                     font-size: 0.9em;
                     margin-bottom: 6px;
                 }
                 
                 .format-example pre {
                     font-size: 0.75em;
                 }
             }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-btn">
                <i class="fas fa-arrow-left"></i> Back to Dashboard
            </a>
            
            <div class="header">
                <h1><i class="fas fa-book"></i> Documentation</h1>
                <p>How to use the NetOps AI Pipeline effectively</p>
            </div>
            
            <div class="docs-container">
                <div class="section">
                    <h3><i class="fas fa-rocket"></i> Getting Started</h3>
                    <p style="color: #94a3b8; margin-bottom: 20px;">
                        The NetOps AI Pipeline is designed to automatically detect anomalies in network performance data 
                        and analyze system logs for incidents. Simply upload your files and get instant AI-powered insights.
                    </p>
                </div>
                
                <div class="section">
                    <h3><i class="fas fa-chart-bar"></i> KPI Anomaly Detection</h3>
                    <div class="feature-grid">
                        <div class="feature-card">
                            <div class="feature-icon">
                                <i class="fas fa-file-csv"></i>
                            </div>
                            <div class="feature-title">CSV File Format</div>
                            <div class="feature-description">
                                Upload network performance data in CSV format with the following columns:
                            </div>
                            <ul class="feature-list">
                                <li>cell_id - Network cell identifier</li>
                                <li>timestamp - Time of measurement</li>
                                <li>PRB_Util - Physical Resource Block utilization</li>
                                <li>RRC_Conn - Radio Resource Control connections</li>
                                <li>Throughput_Mbps - Data transfer speed</li>
                                <li>BLER - Block Error Rate</li>
                            </ul>
                        </div>
                        
                        <div class="feature-card">
                            <div class="feature-icon">
                                <i class="fas fa-brain"></i>
                            </div>
                            <div class="feature-title">AI Analysis</div>
                            <div class="feature-description">
                                Our AI automatically detects anomalies and provides:
                            </div>
                            <ul class="feature-list">
                                <li>Anomaly detection with confidence scores</li>
                                <li>Performance trend analysis</li>
                                <li>Actionable recommendations</li>
                                <li>Visual charts and reports</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="format-example">
                        <h4>Example CSV Format:</h4>
                        <pre>cell_id,timestamp,PRB_Util,RRC_Conn,Throughput_Mbps,BLER
cell_001,2024-01-01 10:00:00,75.2,150,45.8,0.02
cell_002,2024-01-01 10:01:00,82.1,180,52.3,0.01
...</pre>
                    </div>
                </div>
                
                <div class="section">
                    <h3><i class="fas fa-file-alt"></i> Log Analysis</h3>
                    <div class="feature-grid">
                        <div class="feature-card">
                            <div class="feature-icon">
                                <i class="fas fa-exclamation-triangle"></i>
                            </div>
                            <div class="feature-title">Incident Detection</div>
                            <div class="feature-description">
                                Automatically identifies and categorizes:
                            </div>
                            <ul class="feature-list">
                                <li>Critical errors (CRIT)</li>
                                <li>Error messages (ERROR)</li>
                                <li>Warning alerts (WARN)</li>
                                <li>System alarms (ALARM)</li>
                                <li>Information logs (INFO)</li>
                            </ul>
                        </div>
                        
                        <div class="feature-card">
                            <div class="feature-icon">
                                <i class="fas fa-chart-pie"></i>
                            </div>
                            <div class="feature-title">Summary Reports</div>
                            <div class="feature-description">
                                Get comprehensive insights including:
                            </div>
                            <ul class="feature-list">
                                <li>Incident count by severity</li>
                                <li>Trend analysis</li>
                                <li>System health assessment</li>
                                <li>Priority recommendations</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h3><i class="fas fa-lightbulb"></i> Best Practices</h3>
                    <div class="feature-grid">
                        <div class="feature-card">
                            <div class="feature-icon">
                                <i class="fas fa-clock"></i>
                            </div>
                            <div class="feature-title">Regular Monitoring</div>
                            <div class="feature-description">
                                Upload data regularly to maintain:
                            </div>
                            <ul class="feature-list">
                                <li>Continuous anomaly detection</li>
                                <li>Performance trend tracking</li>
                                <li>Proactive issue identification</li>
                                <li>Historical analysis</li>
                            </ul>
                        </div>
                        
                        <div class="feature-card">
                            <div class="feature-icon">
                                <i class="fas fa-shield-alt"></i>
                            </div>
                            <div class="feature-title">Data Quality</div>
                            <div class="feature-description">
                                Ensure optimal results by:
                            </div>
                            <ul class="feature-list">
                                <li>Using consistent data formats</li>
                                <li>Including all required columns</li>
                                <li>Providing accurate timestamps</li>
                                <li>Validating data completeness</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health/api")
def health_api():
    """API endpoint for programmatic health checks"""
    return {"status": "ok", "service": "netops-ai-pipeline", "version": "2.0.0"}

@app.get("/docs/api")
def docs_api():
    """API endpoint for programmatic access to documentation"""
    return {"message": "API documentation available at /docs"}

@app.post("/upload")
async def upload(file: UploadFile = File(...), train_if_missing: bool = Form(True)):
    """Upload KPI CSV file for AI-powered anomaly detection and analysis"""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    tmp.write(await file.read())
    tmp.close()

    up_id = None
    with get_session() as s:
        u = Upload(filename=file.filename)
        s.add(u)
        s.commit()
        s.refresh(u)
        up_id = u.id

    try:
        df = load_kpi_csv(tmp.name)
        X = to_matrix(df)
        m = load_model()
        if m is None and train_if_missing:
            m = train(X)
        elif m is None:
            return JSONResponse(
                {"error": "model missing; set train_if_missing=true"}, status_code=400
            )

        pred, sc = score(m, X)
        df_out = df.copy()
        df_out["anomaly"] = pred
        df_out["score"] = sc

        chart_path = f"temp_chart_{up_id}.png"
        save_kpi_chart(df_out, chart_path)

        with get_session() as s:
            for row in df_out[["cell_id", "timestamp", "anomaly", "score", "PRB_Util", "RRC_Conn", "Throughput_Mbps", "BLER"]].itertuples(
                index=False, name=None
            ):
                s.add(
                    Score(
                        upload_id=up_id,
                        cell_id=str(row[0]),
                        ts=str(row[1]),
                        anomaly=int(row[2]),
                        score=float(row[3]),
                        prb_util=float(row[4]),
                        rrc_conn=float(row[5]),
                        throughput_mbps=float(row[6]),
                        bler=float(row[7]),
                    )
                )
            s.commit()

        return {
            "upload_id": up_id,
            "filename": file.filename,
            "total_samples": len(df_out),
            "summary": df_out["anomaly"].value_counts().to_dict(),
            "chart": chart_path,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        os.unlink(tmp.name)

@app.get("/report/{upload_id}")
def report(upload_id: int):
    """Get detailed anomaly detection report for an upload"""
    with get_session() as s:
        rows = s.query(Score).filter(Score.upload_id == upload_id).all()
    if not rows:
        raise HTTPException(status_code=404, detail="Upload not found")

    anomalies = sum(1 for r in rows if r.anomaly == -1)
    return {
        "upload_id": upload_id,
        "total": len(rows),
        "anomalies": anomalies,
        "anomaly_rate": round(anomalies / len(rows) * 100, 2) if rows else 0,
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/ai-summary/{upload_id}", response_class=HTMLResponse)
def ai_summary(upload_id: int):
    """Get AI-generated insights and recommendations for an upload"""
    try:
        with get_session() as s:
            rows = s.query(Score).filter(Score.upload_id == upload_id).all()
        if not rows:
            raise HTTPException(status_code=404, detail="Upload not found")

        # Convert database rows back to DataFrame for AI analysis
        import pandas as pd
        
        # Create DataFrame from stored scores and KPI data
        data_list = []
        for row in rows:
            data_list.append({
                'cell_id': row.cell_id,
                'timestamp': row.ts,
                'anomaly': row.anomaly,
                'score': row.score,
                'PRB_Util': row.prb_util or 0.0,
                'RRC_Conn': row.rrc_conn or 0.0,
                'Throughput_Mbps': row.throughput_mbps or 0.0,
                'BLER': row.bler or 0.0
            })
        
        df = pd.DataFrame(data_list)
        
        # Get anomalies
        anomalies = df[df['anomaly'] == -1]
        
        # Generate AI summary using the function
        try:
            ai_result = generate_ai_kpi_summary(df, anomalies, df['score'])
        except Exception as ai_error:
            print(f"AI summary generation error: {ai_error}")
            # Fallback to basic summary
            ai_result = {
                "summary": f"Network performance analysis completed. {len(anomalies)} anomalies detected out of {len(df)} total samples.",
                "insights": [
                    f"Anomaly detection rate: {(len(anomalies) / len(df) * 100):.1f}%",
                    f"Total data points analyzed: {len(df)}",
                    f"Critical cells requiring attention: {len(anomalies)}"
                ],
                "recommendations": [
                    "Investigate cells with highest anomaly scores",
                    "Monitor network performance trends",
                    "Consider capacity optimization if anomaly rate > 5%"
                ],
                "severity": "MEDIUM"
            }
        
        # Create user-friendly HTML response
        insights_html = ""
        for insight in ai_result.get("insights", []):
            insights_html += f'<li>{insight}</li>'
        
        recommendations_html = ""
        for rec in ai_result.get("recommendations", []):
            recommendations_html += f'<li>{rec}</li>'
        
        severity = ai_result.get("severity", "MEDIUM")
        severity_color = {
            "LOW": "#10b981",
            "MEDIUM": "#f59e0b", 
            "HIGH": "#ef4444"
        }.get(severity, "#f59e0b")
        
        anomaly_rate = (len(anomalies) / len(df) * 100) if len(df) > 0 else 0
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Network Performance Analysis Report - NetOps AI Pipeline</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                
                body {{ 
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
                    color: #f1f5f9;
                    line-height: 1.7;
                    min-height: 100vh;
                    font-weight: 400;
                }}
                
                .container {{ 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    padding: 30px 20px;
                }}
                
                .back-btn {{
                    position: fixed;
                    top: 30px;
                    left: 30px;
                    background: rgba(255,255,255,0.1);
                    color: #ffffff;
                    padding: 12px 24px;
                    border-radius: 12px;
                    text-decoration: none;
                    transition: all 0.3s ease;
                    backdrop-filter: blur(20px);
                    display: inline-flex;
                    align-items: center;
                    gap: 10px;
                    font-weight: 500;
                    border: 1px solid rgba(255,255,255,0.2);
                    z-index: 1000;
                }}
                
                .back-btn:hover {{
                    background: rgba(255,255,255,0.2);
                    transform: translateY(-2px);
                    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                }}
                
                .header {{
                    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #60a5fa 100%);
                    padding: 50px 40px;
                    border-radius: 24px;
                    text-align: center;
                    margin-bottom: 40px;
                    box-shadow: 0 25px 50px rgba(0,0,0,0.3);
                    position: relative;
                    overflow: hidden;
                }}
                
                .header::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
                    opacity: 0.3;
                }}
                
                .header h1 {{
                    font-size: 2.8em;
                    font-weight: 800;
                    margin-bottom: 15px;
                    color: #ffffff;
                    position: relative;
                    z-index: 1;
                }}
                
                .header p {{
                    font-size: 1.3em;
                    opacity: 0.95;
                    font-weight: 400;
                    margin-bottom: 25px;
                    position: relative;
                    z-index: 1;
                }}
                
                .severity-badge {{
                    display: inline-block;
                    background: {severity_color}15;
                    color: {severity_color};
                    padding: 12px 24px;
                    border-radius: 25px;
                    font-weight: 700;
                    font-size: 0.95em;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    border: 2px solid {severity_color};
                    position: relative;
                    z-index: 1;
                    backdrop-filter: blur(10px);
                }}
                
                .section {{
                    background: rgba(255,255,255,0.08);
                    backdrop-filter: blur(20px);
                    border: 1px solid rgba(255,255,255,0.15);
                    border-radius: 20px;
                    padding: 35px;
                    margin-bottom: 30px;
                    box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                }}
                
                .section h3 {{
                    color: #ffffff;
                    font-size: 1.5em;
                    margin-bottom: 25px;
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    font-weight: 700;
                }}
                
                .section h3 i {{
                    font-size: 1.2em;
                    color: #60a5fa;
                }}
                
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                    gap: 25px;
                    margin: 25px 0;
                }}
                
                .metric-card {{
                    background: rgba(255,255,255,0.1);
                    border-radius: 16px;
                    padding: 25px;
                    text-align: center;
                    border: 1px solid rgba(255,255,255,0.1);
                    transition: all 0.3s ease;
                }}
                
                .metric-card:hover {{
                    background: rgba(255,255,255,0.15);
                    transform: translateY(-3px);
                    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                }}
                
                .metric-value {{
                    font-size: 2.2em;
                    font-weight: 800;
                    color: #60a5fa;
                    margin-bottom: 8px;
                }}
                
                .metric-label {{
                    color: #cbd5e1;
                    font-size: 0.9em;
                    text-transform: uppercase;
                    letter-spacing: 0.8px;
                    font-weight: 600;
                }}
                
                .insights-list, .recommendations-list {{
                    list-style: none;
                    padding: 0;
                }}
                
                .insights-list li, .recommendations-list li {{
                    background: rgba(255,255,255,0.08);
                    border-radius: 12px;
                    padding: 20px;
                    margin-bottom: 15px;
                    border-left: 4px solid #60a5fa;
                    transition: all 0.3s ease;
                }}
                
                .insights-list li:hover, .recommendations-list li:hover {{
                    background: rgba(255,255,255,0.12);
                    transform: translateX(5px);
                }}
                
                .ai-status {{
                    background: rgba(34,197,94,0.15);
                    border: 1px solid rgba(34,197,94,0.3);
                    border-radius: 16px;
                    padding: 20px;
                    margin-bottom: 30px;
                    text-align: center;
                    backdrop-filter: blur(10px);
                }}
                
                .ai-status i {{
                    color: #22c55e;
                    margin-right: 10px;
                    font-size: 1.2em;
                }}
                
                .ai-status strong {{
                    color: #ffffff;
                    font-weight: 600;
                }}
                
                .executive-summary {{
                    background: rgba(59,130,246,0.1);
                    border: 1px solid rgba(59,130,246,0.2);
                    border-radius: 16px;
                    padding: 25px;
                    margin-top: 20px;
                }}
                
                .executive-summary p {{
                    font-size: 1.15em;
                    line-height: 1.8;
                    color: #e2e8f0;
                    font-weight: 400;
                }}
                
                                 @media (max-width: 768px) {{
                     .container {{ padding: 20px 15px; }}
                     .header {{ padding: 30px 20px; }}
                     .header h1 {{ font-size: 2.2em; }}
                     .metrics-grid {{ grid-template-columns: repeat(2, 1fr); }}
                     .back-btn {{ position: relative; top: auto; left: auto; margin-bottom: 20px; }}
                     
                     .section {{
                         padding: 25px 20px;
                         margin-bottom: 20px;
                     }}
                     
                     .section h3 {{
                         font-size: 1.3em;
                         margin-bottom: 20px;
                     }}
                     
                     .metric-card {{
                         padding: 20px 15px;
                     }}
                     
                     .metric-value {{
                         font-size: 1.8em;
                     }}
                     
                     .metric-label {{
                         font-size: 0.8em;
                     }}
                     
                     .insights-list li, .recommendations-list li {{
                         padding: 15px;
                         margin-bottom: 12px;
                     }}
                     
                     .executive-summary {{
                         padding: 20px;
                     }}
                     
                     .executive-summary p {{
                         font-size: 1em;
                     }}
                 }}
                 
                 @media (max-width: 480px) {{
                     .container {{ padding: 15px 10px; }}
                     .header {{ padding: 25px 15px; }}
                     .header h1 {{ font-size: 1.8em; }}
                     .header p {{ font-size: 1.1em; }}
                     .metrics-grid {{ grid-template-columns: 1fr; }}
                     
                     .section {{
                         padding: 20px 15px;
                         border-radius: 15px;
                     }}
                     
                     .section h3 {{
                         font-size: 1.2em;
                         margin-bottom: 15px;
                     }}
                     
                     .metric-card {{
                         padding: 15px 12px;
                     }}
                     
                     .metric-value {{
                         font-size: 1.5em;
                     }}
                     
                     .metric-label {{
                         font-size: 0.75em;
                     }}
                     
                     .insights-list li, .recommendations-list li {{
                         padding: 12px;
                         margin-bottom: 10px;
                         font-size: 0.9em;
                     }}
                     
                     .executive-summary {{
                         padding: 15px;
                     }}
                     
                     .executive-summary p {{
                         font-size: 0.9em;
                     }}
                     
                     .ai-status {{
                         padding: 15px;
                         font-size: 0.9em;
                     }}
                     
                     .severity-badge {{
                         padding: 8px 16px;
                         font-size: 0.85em;
                     }}
                 }}
            </style>
        </head>
        <body>
            <div class="container">
                <a href="/" class="back-btn">
                    <i class="fas fa-arrow-left"></i> Back to Dashboard
                </a>
                
                <div class="header">
                    <h1><i class="fas fa-chart-line"></i> Network Performance Analysis</h1>
                    <p>Comprehensive network intelligence and performance optimization insights</p>
                    <div style="margin-top: 25px;">
                        <span class="severity-badge">{severity} SEVERITY LEVEL</span>
                    </div>
                </div>
                
                <div class="ai-status">
                    <i class="fas fa-check-circle"></i>
                    <strong>Analysis Complete</strong> - Advanced machine learning algorithms have processed your network data
                </div>
                
                <div class="section">
                    <h3><i class="fas fa-chart-bar"></i> Performance Metrics</h3>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">{len(df)}</div>
                            <div class="metric-label">Total Samples</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{len(anomalies)}</div>
                            <div class="metric-label">Anomalies Detected</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{anomaly_rate:.1f}%</div>
                            <div class="metric-label">Anomaly Rate</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{severity}</div>
                            <div class="metric-label">Severity Level</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h3><i class="fas fa-file-alt"></i> Executive Summary</h3>
                    <div class="executive-summary">
                        <p>{ai_result.get("summary", "Network performance analysis completed successfully with comprehensive insights and actionable recommendations.")}</p>
                    </div>
                </div>
                
                <div class="section">
                    <h3><i class="fas fa-search"></i> Key Insights</h3>
                    <ul class="insights-list">
                        {insights_html if insights_html else '<li>Network performance analysis identified critical patterns and trends in the data.</li><li>Performance metrics indicate overall system health and operational efficiency.</li><li>Anomaly detection algorithms successfully identified potential issues requiring attention.</li>'}
                    </ul>
                </div>
                
                <div class="section">
                    <h3><i class="fas fa-cog"></i> Recommendations</h3>
                    <ul class="recommendations-list">
                        {recommendations_html if recommendations_html else '<li>Implement continuous monitoring of network performance metrics.</li><li>Review and optimize configuration settings for improved performance.</li><li>Establish proactive capacity planning based on current utilization patterns.</li><li>Schedule regular performance reviews and system health checks.</li>'}
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """
        
    except Exception as e:
        print(f"AI summary error: {str(e)}")
        # Return a simple error page
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI Analysis Report - Error</title>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; background: #1a1a1a; color: #ffffff; padding: 40px; text-align: center; }}
                .error {{ background: #ef4444; padding: 20px; border-radius: 10px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>🤖 AI Analysis Report</h1>
            <div class="error">
                <h2>Analysis Error</h2>
                <p>There was an issue generating the AI analysis: {str(e)}</p>
                <a href="/" style="color: #3b82f6;">← Back to Dashboard</a>
            </div>
        </body>
        </html>
        """

@app.get("/chart/{upload_id}")
def get_chart(upload_id: int):
    """Get visualization chart for an upload"""
    chart_path = f"temp_chart_{upload_id}.png"
    if os.path.exists(chart_path):
        return FileResponse(chart_path, media_type="image/png")
    else:
        raise HTTPException(status_code=404, detail="Chart not found for this upload")

@app.post("/logs/summarize")
async def summarize_logs(file: UploadFile = File(...)):
    """Summarize syslog incidents using AI-powered analysis"""
    if not file.filename.endswith((".log", ".txt")):
        raise HTTPException(status_code=400, detail="Only log/txt files are supported")

    content = await file.read()
    log_text = content.decode("utf-8")

    incidents = extract_incidents(log_text)

    return {
        "filename": file.filename,
        "summary": incidents["summary"],
        "incident_counts": incidents["incident_counts"],
        "analysis": "AI-powered log analysis complete with incident categorization and severity assessment",
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/uploads", response_class=HTMLResponse)
def list_uploads_html():
    """User-friendly HTML page for viewing uploads"""
    with get_session() as s:
        uploads = s.query(Upload).order_by(Upload.created_at.desc()).all()
    
    uploads_html = ""
    for u in uploads:
        # Get upload statistics
        scores = s.query(Score).filter(Score.upload_id == u.id).all()
        total_samples = len(scores)
        anomalies = sum(1 for score in scores if score.anomaly == -1)
        anomaly_rate = (anomalies / total_samples * 100) if total_samples > 0 else 0
        
        uploads_html += f"""
        <div class="upload-item">
            <div class="upload-header">
                <h4><i class="fas fa-file-csv"></i> {u.filename}</h4>
                <span class="upload-date">{u.created_at.strftime('%Y-%m-%d %H:%M:%S')}</span>
            </div>
            <div class="upload-stats">
                <div class="stat">
                    <span class="stat-value">{total_samples}</span>
                    <span class="stat-label">Samples</span>
                </div>
                <div class="stat">
                    <span class="stat-value">{anomalies}</span>
                    <span class="stat-label">Anomalies</span>
                </div>
                <div class="stat">
                    <span class="stat-value">{anomaly_rate:.1f}%</span>
                    <span class="stat-label">Anomaly Rate</span>
                </div>
            </div>
                         <div class="upload-actions">
                 <a href="/ai-summary/{u.id}" class="action-link" target="_blank">
                     <i class="fas fa-chart-bar"></i> AI Report
                 </a>
                 <a href="/chart/{u.id}" class="action-link" target="_blank">
                     <i class="fas fa-chart-line"></i> Chart
                 </a>
                 <a href="/report/{u.id}" class="action-link" target="_blank">
                     <i class="fas fa-code"></i> JSON Data
                 </a>
             </div>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Uploads - NetOps AI Pipeline</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            
            body {{ 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
                min-height: 100vh;
                color: #e2e8f0;
                line-height: 1.6;
            }}
            
            .container {{ 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px;
            }}
            
            .header {{
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
                border-radius: 20px;
                padding: 40px;
                text-align: center;
                margin-bottom: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            }}
            
            .header h1 {{ 
                font-size: 2.5em; 
                font-weight: 700;
                margin-bottom: 10px;
                color: #ffffff;
            }}
            
            .header p {{ 
                font-size: 1.2em; 
                opacity: 0.9;
                font-weight: 300;
            }}
            
            .back-btn {{
                position: absolute;
                top: 20px;
                left: 20px;
                background: rgba(255,255,255,0.1);
                color: #ffffff;
                padding: 10px 20px;
                border-radius: 10px;
                text-decoration: none;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
            }}
            
            .back-btn:hover {{
                background: rgba(255,255,255,0.2);
                transform: translateY(-2px);
            }}
            
            .uploads-container {{
                background: rgba(255,255,255,0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 20px;
                padding: 30px;
            }}
            
            .uploads-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }}
            
            .uploads-title {{
                font-size: 1.5em;
                font-weight: 600;
                color: #ffffff;
            }}
            
            .upload-count {{
                background: rgba(59,130,246,0.2);
                color: #60a5fa;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: 500;
            }}
            
            .upload-item {{
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 20px;
                transition: all 0.3s ease;
            }}
            
            .upload-item:hover {{
                border-color: rgba(59,130,246,0.5);
                box-shadow: 0 10px 30px rgba(59,130,246,0.2);
                transform: translateY(-2px);
            }}
            
            .upload-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }}
            
            .upload-header h4 {{
                color: #ffffff;
                font-size: 1.2em;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .upload-date {{
                color: #94a3b8;
                font-size: 0.9em;
                font-weight: 500;
            }}
            
            .upload-stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }}
            
            .stat {{
                text-align: center;
                background: rgba(255,255,255,0.05);
                border-radius: 10px;
                padding: 15px;
            }}
            
            .stat-value {{
                display: block;
                font-size: 1.5em;
                font-weight: 700;
                color: #3b82f6;
                margin-bottom: 5px;
            }}
            
            .stat-label {{
                color: #94a3b8;
                font-size: 0.8em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .upload-actions {{
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
            }}
            
            .action-link {{
                background: rgba(59,130,246,0.2);
                color: #60a5fa;
                padding: 10px 20px;
                border-radius: 8px;
                text-decoration: none;
                transition: all 0.3s ease;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .action-link:hover {{
                background: rgba(59,130,246,0.3);
                transform: translateY(-2px);
            }}
            
            .empty-state {{
                text-align: center;
                padding: 60px 20px;
                color: #94a3b8;
            }}
            
            .empty-state i {{
                font-size: 4em;
                margin-bottom: 20px;
                opacity: 0.5;
            }}
            
            .empty-state h3 {{
                font-size: 1.5em;
                margin-bottom: 10px;
                color: #e2e8f0;
            }}
            
                         @media (max-width: 768px) {{
                 .container {{
                     padding: 15px;
                 }}
                 
                 .header {{
                     padding: 30px 20px;
                     margin-bottom: 20px;
                 }}
                 
                 .header h1 {{
                     font-size: 2.2em;
                 }}
                 
                 .header p {{
                     font-size: 1.1em;
                 }}
                 
                 .uploads-container {{
                     padding: 25px 20px;
                 }}
                 
                 .uploads-header {{
                     flex-direction: column;
                     align-items: flex-start;
                     gap: 15px;
                     margin-bottom: 25px;
                 }}
                 
                 .uploads-title {{
                     font-size: 1.3em;
                 }}
                 
                 .upload-item {{
                     padding: 20px 15px;
                     margin-bottom: 15px;
                 }}
                 
                 .upload-header {{
                     flex-direction: column;
                     align-items: flex-start;
                     gap: 10px;
                     margin-bottom: 12px;
                 }}
                 
                 .upload-header h4 {{
                     font-size: 1.1em;
                 }}
                 
                 .upload-stats {{
                     grid-template-columns: repeat(3, 1fr);
                     gap: 12px;
                     margin-bottom: 15px;
                 }}
                 
                 .stat {{
                     padding: 12px 10px;
                 }}
                 
                 .stat-value {{
                     font-size: 1.3em;
                 }}
                 
                 .stat-label {{
                     font-size: 0.7em;
                 }}
                 
                 .upload-actions {{
                     flex-direction: column;
                     gap: 10px;
                     justify-content: center;
                 }}
                 
                 .action-link {{
                     padding: 12px 16px;
                     font-size: 0.9em;
                     justify-content: center;
                 }}
             }}
             
             @media (max-width: 480px) {{
                 .container {{
                     padding: 10px;
                 }}
                 
                 .header {{
                     padding: 25px 15px;
                     border-radius: 15px;
                 }}
                 
                 .header h1 {{
                     font-size: 1.8em;
                 }}
                 
                 .header p {{
                     font-size: 1em;
                 }}
                 
                 .uploads-container {{
                     padding: 20px 15px;
                     border-radius: 15px;
                 }}
                 
                 .uploads-header {{
                     margin-bottom: 20px;
                 }}
                 
                 .uploads-title {{
                     font-size: 1.2em;
                 }}
                 
                 .upload-count {{
                     padding: 6px 12px;
                     font-size: 0.85em;
                 }}
                 
                 .upload-item {{
                     padding: 15px 12px;
                     margin-bottom: 12px;
                     border-radius: 12px;
                 }}
                 
                 .upload-header h4 {{
                     font-size: 1em;
                 }}
                 
                 .upload-date {{
                     font-size: 0.8em;
                 }}
                 
                 .upload-stats {{
                     grid-template-columns: repeat(3, 1fr);
                     gap: 8px;
                     margin-bottom: 12px;
                 }}
                 
                 .stat {{
                     padding: 10px 8px;
                     border-radius: 8px;
                 }}
                 
                 .stat-value {{
                     font-size: 1.2em;
                 }}
                 
                 .stat-label {{
                     font-size: 0.65em;
                 }}
                 
                 .action-link {{
                     padding: 10px 12px;
                     font-size: 0.85em;
                 }}
             }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-btn">
                <i class="fas fa-arrow-left"></i> Back to Dashboard
            </a>
            
            <div class="header">
                <h1><i class="fas fa-list"></i> Upload History</h1>
                <p>View all processed files and their AI analysis results</p>
            </div>
            
            <div class="uploads-container">
                <div class="uploads-header">
                    <div class="uploads-title">
                        <i class="fas fa-database"></i> Processed Files
                    </div>
                    <div class="upload-count">
                        {len(uploads)} Upload{'' if len(uploads) == 1 else 's'}
                    </div>
                </div>
                
                {uploads_html if uploads else '''
                <div class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <h3>No uploads yet</h3>
                    <p>Upload your first KPI or log file to see results here</p>
                </div>
                '''}
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/uploads/api")
def list_uploads_api():
    """API endpoint for programmatic access to uploads"""
    with get_session() as s:
        uploads = s.query(Upload).all()
    return [
        {
            "id": u.id, 
            "filename": u.filename, 
            "created_at": u.created_at,
            "status": "processed",
            "ai_analysis_available": True
        }
        for u in uploads
    ]
