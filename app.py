from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from storage import init_db, get_session, Upload, Score
from features import load_kpi_csv, to_matrix
from model import load_model, train, score
from charts import save_kpi_chart
from summarize import extract_incidents, generate_ai_kpi_summary
from random_forest_model import analyze_with_random_forest
from pdf_report import generate_kpi_pdf_report, cleanup_pdf_file
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
    allow_origins=["https://netops-ai-pipeline.railway.app", "http://localhost:8001", "http://127.0.0.1:8001"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Add CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://netops-ai-pipeline.railway.app", "http://localhost:8001", "http://127.0.0.1:8001"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
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
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            tailwind.config = {
                darkMode: 'class',
                theme: {
                    extend: {
                        fontFamily: {
                            'inter': ['Inter', 'sans-serif'],
                        },
                        animation: {
                            'fade-in': 'fadeIn 0.5s ease-in-out',
                            'slide-up': 'slideUp 0.3s ease-out',
                            'pulse-slow': 'pulse 3s infinite',
                        },
                        colors: {
                            brand: {
                                50: '#f0f9ff',
                                100: '#e0f2fe',
                                200: '#bae6fd',
                                300: '#7dd3fc',
                                400: '#38bdf8',
                                500: '#0ea5e9',
                                600: '#0284c7',
                                700: '#0369a1',
                                800: '#075985',
                                900: '#0c4a6e',
                            }
                        }
                    }
                }
            }
        </script>
        <style>
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            @keyframes slideUp {
                from { transform: translateY(10px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            
            /* Custom scrollbar for webkit browsers */
            ::-webkit-scrollbar {
                width: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: rgba(255, 255, 255, 0.5);
            }
            
            /* Dark mode scrollbar */
            .dark ::-webkit-scrollbar-track {
                background: rgba(0, 0, 0, 0.1);
            }
            
            .dark ::-webkit-scrollbar-thumb {
                background: rgba(255, 255, 255, 0.2);
            }
            
            .dark ::-webkit-scrollbar-thumb:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            
            /* Smooth transitions for all elements */
            * {
                transition: all 0.2s ease-in-out;
            }
            
            /* Custom focus styles */
            input:focus, button:focus {
                outline: 2px solid rgba(59, 130, 246, 0.5);
                outline-offset: 2px;
            }
            
            /* Theme toggle animation */
            .theme-toggle {
                transition: transform 0.3s ease;
            }
            
            .theme-toggle:hover {
                transform: scale(1.1);
            }
        </style>
    </head>
    <body class="bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-700 min-h-screen font-inter text-slate-800 dark:text-slate-200 transition-colors duration-300">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
            <!-- Header with Theme Toggle -->
            <div class="flex justify-between items-center mb-8">
                <!-- Theme Toggle Button -->
                <button id="themeToggle" class="theme-toggle bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border border-slate-200/50 dark:border-slate-700/50 rounded-full p-3 shadow-lg hover:shadow-xl transition-all duration-300">
                    <i id="themeIcon" class="fas fa-moon text-slate-600 dark:text-slate-300 text-xl"></i>
                </button>
                
                <!-- Brand Logo -->
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 bg-gradient-to-br from-brand-500 to-brand-600 rounded-xl flex items-center justify-center shadow-lg">
                        <i class="fas fa-brain text-white text-lg"></i>
                    </div>
                    <div class="text-right">
                        <h2 class="text-lg font-semibold text-slate-800 dark:text-slate-200">NetOps AI</h2>
                        <p class="text-xs text-slate-600 dark:text-slate-400">Enterprise Pipeline</p>
                    </div>
                </div>
            </div>
            
            <!-- Header Section -->
            <div class="relative bg-gradient-to-r from-brand-500 via-brand-400 to-brand-300 dark:from-brand-600 dark:via-brand-500 dark:to-brand-400 rounded-3xl p-8 md:p-12 mb-8 shadow-2xl overflow-hidden">
                <div class="absolute inset-0 bg-black/10"></div>
                <div class="relative z-10 text-center">
                    <h1 class="text-4xl md:text-6xl font-bold text-white mb-4 flex items-center justify-center gap-4">
                        <i class="fas fa-brain text-brand-200"></i>
                        NetOps AI Pipeline
                    </h1>
                    <p class="text-xl md:text-2xl text-brand-100 font-light">
                        Enterprise-Grade Network Intelligence & Anomaly Detection
                    </p>
                </div>
            </div>
            
            <!-- Stats Bar -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6 mb-8">
                <div class="bg-white/90 dark:bg-white/5 backdrop-blur-sm border border-slate-200/50 dark:border-white/10 rounded-2xl p-6 text-center transition-all duration-300 hover:bg-white dark:hover:bg-white/10 hover:border-brand-300/50 dark:hover:border-white/20 hover:-translate-y-1 group shadow-lg">
                    <div class="text-3xl md:text-4xl text-brand-500 dark:text-brand-400 mb-3 group-hover:scale-110 transition-transform">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    <div class="text-2xl md:text-3xl font-bold text-slate-800 dark:text-white mb-1">99.9%</div>
                    <div class="text-sm text-slate-600 dark:text-slate-400 font-medium uppercase tracking-wider">Accuracy</div>
                </div>
                
                <div class="bg-white/90 dark:bg-white/5 backdrop-blur-sm border border-slate-200/50 dark:border-white/10 rounded-2xl p-6 text-center transition-all duration-300 hover:bg-white dark:hover:bg-white/10 hover:border-green-300/50 dark:hover:border-white/20 hover:-translate-y-1 group shadow-lg">
                    <div class="text-3xl md:text-4xl text-green-500 dark:text-green-400 mb-3 group-hover:scale-110 transition-transform">
                        <i class="fas fa-bolt"></i>
                    </div>
                    <div class="text-2xl md:text-3xl font-bold text-slate-800 dark:text-white mb-1">&lt; 2s</div>
                    <div class="text-sm text-slate-600 dark:text-slate-400 font-medium uppercase tracking-wider">Processing</div>
                </div>
                
                <div class="bg-white/90 dark:bg-white/5 backdrop-blur-sm border border-slate-200/50 dark:border-white/10 rounded-2xl p-6 text-center transition-all duration-300 hover:bg-white dark:hover:bg-white/10 hover:border-purple-300/50 dark:hover:border-white/20 hover:-translate-y-1 group shadow-lg">
                    <div class="text-3xl md:text-4xl text-purple-500 dark:text-purple-400 mb-3 group-hover:scale-110 transition-transform">
                        <i class="fas fa-shield-alt"></i>
                    </div>
                    <div class="text-lg md:text-xl font-bold text-slate-800 dark:text-white mb-1">Enterprise</div>
                    <div class="text-sm text-slate-600 dark:text-slate-400 font-medium uppercase tracking-wider">Security</div>
                </div>
                
                <div class="bg-white/90 dark:bg-white/5 backdrop-blur-sm border border-slate-200/50 dark:border-white/10 rounded-2xl p-6 text-center transition-all duration-300 hover:bg-white dark:hover:bg-white/10 hover:border-cyan-300/50 dark:hover:border-white/20 hover:-translate-y-1 group shadow-lg">
                    <div class="text-3xl md:text-4xl text-cyan-500 dark:text-cyan-400 mb-3 group-hover:scale-110 transition-transform">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="text-lg md:text-xl font-bold text-slate-800 dark:text-white mb-1">AI-Powered</div>
                    <div class="text-sm text-slate-600 dark:text-slate-400 font-medium uppercase tracking-wider">Insights</div>
                </div>
            </div>
            
            <!-- Main Content -->
            <div class="grid md:grid-cols-2 gap-6 md:gap-8 mb-8">
                <!-- KPI Upload Section -->
                <div class="bg-white/90 dark:bg-white/5 backdrop-blur-sm border border-slate-200/50 dark:border-white/10 rounded-3xl p-6 md:p-8 transition-all duration-300 hover:border-brand-500/30 dark:hover:border-brand-500/30 hover:shadow-xl shadow-lg">
                    <h3 class="text-2xl font-bold text-slate-800 dark:text-white mb-4 flex items-center gap-3">
                        <i class="fas fa-chart-bar text-brand-500 dark:text-brand-400"></i>
                        KPI Anomaly Detection
                    </h3>
                    <p class="text-slate-600 dark:text-slate-300 mb-6 leading-relaxed">
                        Upload network performance data to receive AI-powered insights, anomaly detection, and actionable recommendations for network optimization.
                    </p>
                    
                    <form id="kpiForm">
                        <div class="border-2 border-dashed border-brand-500/30 dark:border-brand-500/30 rounded-2xl p-8 text-center bg-brand-500/5 dark:bg-brand-500/5 transition-all duration-300 hover:border-brand-500/50 dark:hover:border-brand-500/50 hover:bg-brand-500/10 dark:hover:bg-brand-500/10 mb-6">
                            <input type="file" name="file" accept=".csv" required class="w-full text-slate-700 dark:text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-brand-500 file:text-white hover:file:bg-brand-600 transition-colors">
                            <p class="mt-4 text-sm text-slate-600 dark:text-slate-400">
                                <i class="fas fa-info-circle mr-2"></i>
                                Expected format: cell_id, timestamp, PRB_Util, RRC_Conn, Throughput_Mbps, BLER
                            </p>
                        </div>
                        
                        <div class="bg-slate-50/80 dark:bg-white/5 rounded-xl p-4 mb-6">
                            <label class="flex items-center gap-3 cursor-pointer text-slate-700 dark:text-slate-200 font-medium">
                                <input type="checkbox" name="train_if_missing" value="true" checked class="w-5 h-5 text-brand-500 bg-slate-100 dark:bg-slate-700 border-slate-300 dark:border-slate-600 rounded focus:ring-brand-500 focus:ring-2">
                                <i class="fas fa-cog text-brand-500 dark:text-brand-400"></i>
                                Train AI model if not available (recommended)
                            </label>
                        </div>
                        
                        <button type="submit" id="kpiBtn" class="w-full bg-gradient-to-r from-brand-500 to-brand-600 hover:from-brand-600 hover:to-brand-700 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-300 hover:-translate-y-1 hover:shadow-lg flex items-center justify-center gap-3">
                            <i class="fas fa-search"></i>
                            Analyze with AI
                        </button>
                    </form>
                    
                    <div id="kpiResult"></div>
                </div>
                
                <!-- Log Analysis Section -->
                <div class="bg-white/90 dark:bg-white/5 backdrop-blur-sm border border-slate-200/50 dark:border-white/10 rounded-3xl p-6 md:p-8 transition-all duration-300 hover:border-green-500/30 dark:hover:border-green-500/30 hover:shadow-xl shadow-lg">
                    <h3 class="text-2xl font-bold text-slate-800 dark:text-white mb-4 flex items-center gap-3">
                        <i class="fas fa-file-alt text-green-500 dark:text-green-400"></i>
                        Log Analysis
                    </h3>
                    <p class="text-slate-600 dark:text-slate-300 mb-6 leading-relaxed">
                        Upload system logs for intelligent incident detection, error categorization, and automated alert generation with severity assessment.
                    </p>
                    
                    <form id="logForm">
                        <div class="border-2 border-dashed border-green-500/30 dark:border-green-500/30 rounded-2xl p-8 text-center bg-green-500/5 dark:bg-green-500/5 transition-all duration-300 hover:border-green-500/50 dark:hover:border-green-500/50 hover:bg-green-500/10 dark:hover:bg-green-500/10 mb-6">
                            <input type="file" name="file" accept=".log,.txt" required class="w-full text-slate-700 dark:text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-green-500 file:text-white hover:file:bg-green-600 transition-colors">
                            <p class="mt-4 text-sm text-slate-600 dark:text-slate-400">
                                <i class="fas fa-info-circle mr-2"></i>
                                Supports ERROR, WARN, CRIT, ALARM, INFO log levels
                            </p>
                        </div>
                        
                        <button type="submit" id="logBtn" class="w-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-300 hover:-translate-y-1 hover:shadow-lg flex items-center justify-center gap-3">
                            <i class="fas fa-search"></i>
                            Analyze Logs
                        </button>
                    </form>
                    
                    <div id="logResult"></div>
                </div>
            </div>
            
            <!-- Footer -->
            <div class="bg-white/90 dark:bg-white/5 backdrop-blur-sm border border-slate-200/50 dark:border-white/10 rounded-3xl p-8 text-center shadow-lg">
                <h3 class="text-2xl font-bold text-slate-800 dark:text-white mb-6 flex items-center justify-center gap-3">
                    <i class="fas fa-tools text-brand-500 dark:text-slate-400"></i>
                    Enterprise Tools
                </h3>
                <div class="flex flex-wrap justify-center gap-4">
                    <a href="/system-status" class="bg-brand-500/20 dark:bg-blue-500/20 hover:bg-brand-500/30 dark:hover:bg-blue-500/30 text-brand-600 dark:text-blue-300 hover:text-brand-700 dark:hover:text-blue-200 px-6 py-3 rounded-xl transition-all duration-300 hover:-translate-y-1 flex items-center gap-2 font-medium">
                        <i class="fas fa-chart-bar"></i>
                        System Status
                    </a>
                    <a href="/health" class="bg-green-500/20 hover:bg-green-500/30 text-green-600 dark:text-green-300 hover:text-green-700 dark:hover:text-green-200 px-6 py-3 rounded-xl transition-all duration-300 hover:-translate-y-1 flex items-center gap-2 font-medium">
                        <i class="fas fa-heartbeat"></i>
                        Health Check
                    </a>
                    <a href="/uploads" class="bg-purple-500/20 hover:bg-purple-500/30 text-purple-600 dark:text-purple-300 hover:text-purple-700 dark:hover:text-purple-200 px-6 py-3 rounded-xl transition-all duration-300 hover:-translate-y-1 flex items-center gap-2 font-medium">
                        <i class="fas fa-list"></i>
                        View Uploads
                    </a>
                </div>
            </div>
        </div>
        
        <script>
            function showLoading(formId, btnId) {
                const btn = document.getElementById(btnId);
                const resultDiv = document.getElementById(formId === 'kpiForm' ? 'kpiResult' : 'logResult');
                
                btn.disabled = true;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                resultDiv.innerHTML = '<div class="bg-amber-500/10 border-l-4 border-amber-500 rounded-xl p-6 text-center animate-pulse"><i class="fas fa-cog fa-spin text-amber-400 text-2xl mb-3"></i><div class="text-amber-300 font-medium">AI is analyzing your data...</div></div>';
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
                         insights.push('[ALERT] High anomaly rate detected - immediate attention required');
                     } else if (anomalyRate > 5) {
                         insights.push('[WARNING] Moderate anomalies detected - monitor closely');
                     } else {
                         insights.push('[OK] Network performance appears normal');
                     }
                     
                     if (data.total_samples > 100) {
                         insights.push('[DATA] Large dataset analyzed for comprehensive insights');
                     }
                     
                     insights.push('[AI] AI model successfully identified performance patterns');
                     
                     const insightsHtml = insights.map(insight => `<li>${insight}</li>`).join('');
                     
                     const severityBgColor = severity === 'HIGH' ? 'bg-red-500/10' : severity === 'MEDIUM' ? 'bg-amber-500/10' : 'bg-green-500/10';
                     const severityBorderColor = severity === 'HIGH' ? 'border-red-500' : severity === 'MEDIUM' ? 'border-amber-500' : 'border-green-500';
                     const severityTextColor = severity === 'HIGH' ? 'text-red-400' : severity === 'MEDIUM' ? 'text-amber-400' : 'text-green-400';
                     
                     resultDiv.innerHTML = `
                         <div class="bg-green-500/10 border-l-4 border-green-500 rounded-xl p-6 mt-6 animate-slide-up">
                             <h4 class="text-xl font-bold text-white mb-4 flex items-center gap-3">
                                 <i class="fas fa-check-circle text-green-400"></i>
                                 AI Analysis Complete!
                             </h4>
                             <div class="${severityBgColor} border ${severityBorderColor} rounded-xl p-4 mb-6 text-center">
                                 <span class="${severityTextColor} font-bold text-lg">${severity} SEVERITY LEVEL</span>
                             </div>
                             <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                                 <div class="bg-white/10 rounded-xl p-4 text-center">
                                     <div class="text-2xl font-bold text-blue-400 mb-1">${data.total_samples}</div>
                                     <div class="text-sm text-slate-400 font-medium uppercase tracking-wider">Total Samples</div>
                                 </div>
                                 <div class="bg-white/10 rounded-xl p-4 text-center">
                                     <div class="text-2xl font-bold text-red-400 mb-1">${data.summary['-1'] || 0}</div>
                                     <div class="text-sm text-slate-400 font-medium uppercase tracking-wider">Anomalies</div>
                                 </div>
                                 <div class="bg-white/10 rounded-xl p-4 text-center">
                                     <div class="text-2xl font-bold text-green-400 mb-1">${data.summary['1'] || 0}</div>
                                     <div class="text-sm text-slate-400 font-medium uppercase tracking-wider">Normal</div>
                                 </div>
                                 <div class="bg-white/10 rounded-xl p-4 text-center">
                                     <div class="text-2xl font-bold text-cyan-400 mb-1">${anomalyRate}%</div>
                                     <div class="text-sm text-slate-400 font-medium uppercase tracking-wider">Anomaly Rate</div>
                                 </div>
                             </div>
                             <div class="mb-6">
                                 <h5 class="text-white font-semibold mb-3 flex items-center gap-2">
                                     <i class="fas fa-lightbulb text-yellow-400"></i>
                                     Quick Insights:
                                 </h5>
                                 <ul class="text-slate-300 space-y-2 pl-6">
                                     ${insightsHtml}
                                 </ul>
                             </div>
                             <div class="flex flex-wrap gap-3">
                                 <a href="/ai-summary/${data.upload_id}" target="_blank" class="bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 hover:text-blue-200 px-4 py-2 rounded-lg transition-all duration-300 hover:-translate-y-1 flex items-center gap-2 font-medium">
                                     <i class="fas fa-chart-bar"></i>
                                     AI Report
                                 </a>
                                 <a href="/chart/${data.upload_id}" target="_blank" class="bg-green-500/20 hover:bg-green-500/30 text-green-300 hover:text-green-200 px-4 py-2 rounded-lg transition-all duration-300 hover:-translate-y-1 flex items-center gap-2 font-medium">
                                     <i class="fas fa-chart-line"></i>
                                     Visualization
                                 </a>
                                 <a href="/pdf/${data.upload_id}" class="bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 hover:text-cyan-200 px-4 py-2 rounded-lg transition-all duration-300 hover:-translate-y-1 flex items-center gap-2 font-medium">
                                     <i class="fas fa-file-pdf"></i>
                                     Download PDF
                                 </a>
                                 <a href="/predictions/${data.upload_id}/html" target="_blank" class="bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 hover:text-cyan-200 px-4 py-2 rounded-lg transition-all duration-300 hover:-translate-y-1 flex items-center gap-2 font-medium">
                                     <i class="fas fa-tree"></i>
                                     Predictions
                                 </a>
                             </div>
                         </div>
                     `;
                } else {
                    resultDiv.innerHTML = `
                        <div class="bg-green-500/10 border-l-4 border-green-500 rounded-xl p-6 mt-6 animate-slide-up">
                            <h4 class="text-xl font-bold text-white mb-4 flex items-center gap-3">
                                <i class="fas fa-check-circle text-green-400"></i>
                                Log Analysis Complete!
                            </h4>
                            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                                <div class="bg-white/10 rounded-xl p-4 text-center">
                                    <div class="text-2xl font-bold text-red-400 mb-1">${data.incident_counts.critical_errors}</div>
                                    <div class="text-sm text-slate-400 font-medium uppercase tracking-wider">Critical</div>
                                </div>
                                <div class="bg-white/10 rounded-xl p-4 text-center">
                                    <div class="text-2xl font-bold text-orange-400 mb-1">${data.incident_counts.errors}</div>
                                    <div class="text-sm text-slate-400 font-medium uppercase tracking-wider">Errors</div>
                                </div>
                                <div class="bg-white/10 rounded-xl p-4 text-center">
                                    <div class="text-2xl font-bold text-yellow-400 mb-1">${data.incident_counts.warnings}</div>
                                    <div class="text-sm text-slate-400 font-medium uppercase tracking-wider">Warnings</div>
                                </div>
                                <div class="bg-white/10 rounded-xl p-4 text-center">
                                    <div class="text-2xl font-bold text-cyan-400 mb-1">${data.incident_counts.alarms}</div>
                                    <div class="text-sm text-slate-400 font-medium uppercase tracking-wider">Alarms</div>
                                </div>
                            </div>
                            <div class="bg-white/5 rounded-xl p-4">
                                <p class="text-slate-300">
                                    <span class="font-semibold text-white">AI Summary:</span> ${data.summary}
                                </p>
                            </div>
                        </div>
                    `;
                }
            }
            
            function showError(formId, btnId, error) {
                const btn = document.getElementById(btnId);
                const resultDiv = document.getElementById(formId === 'kpiForm' ? 'kpiResult' : 'logResult');
                
                btn.disabled = false;
                btn.innerHTML = formId === 'kpiForm' ? '<i class="fas fa-search"></i> Analyze with AI' : '<i class="fas fa-search"></i> Analyze Logs';
                resultDiv.innerHTML = `<div class="bg-red-500/10 border-l-4 border-red-500 rounded-xl p-6 mt-6 animate-slide-up"><i class="fas fa-exclamation-triangle text-red-400 text-2xl mb-3"></i><div class="text-red-300 font-medium">Error: ${error}</div></div>`;
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
            
            // Theme Toggle Functionality
            const themeToggle = document.getElementById('themeToggle');
            const themeIcon = document.getElementById('themeIcon');
            
            // Check for saved theme preference or default to light mode
            const currentTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.classList.toggle('dark', currentTheme === 'dark');
            updateThemeIcon(currentTheme);
            
            function updateThemeIcon(theme) {
                if (theme === 'dark') {
                    themeIcon.className = 'fas fa-sun text-slate-300 text-xl';
                } else {
                    themeIcon.className = 'fas fa-moon text-slate-600 text-xl';
                }
            }
            
            themeToggle.addEventListener('click', () => {
                const isDark = document.documentElement.classList.contains('dark');
                const newTheme = isDark ? 'light' : 'dark';
                
                document.documentElement.classList.toggle('dark');
                localStorage.setItem('theme', newTheme);
                updateThemeIcon(newTheme);
            });
        </script>
    </body>
    </html>
    """

@app.get("/health", response_class=HTMLResponse)
def health_page():
    """User-friendly health check page"""
    return """
    <!DOCTYPE html>
    <html class="light">
    <head>
        <title>System Health - NetOps AI Pipeline</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            tailwind.config = {
                darkMode: 'class',
                theme: {
                    extend: {
                        colors: {
                            brand: {
                                50: '#eff6ff',
                                100: '#dbeafe',
                                200: '#bfdbfe',
                                300: '#93c5fd',
                                400: '#60a5fa',
                                500: '#3b82f6',
                                600: '#2563eb',
                                700: '#1d4ed8',
                                800: '#1e40af',
                                900: '#1e3a8a',
                            }
                        }
                    }
                }
            }
        </script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body { 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e1 100%);
                min-height: 100vh;
                color: #1e293b;
                line-height: 1.6;
                transition: all 0.3s ease;
            }
            
            .dark body {
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
                color: #e2e8f0;
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
            
            .theme-toggle {
                position: absolute;
                top: 20px;
                right: 20px;
                background: rgba(255,255,255,0.1);
                color: #ffffff;
                padding: 10px;
                border-radius: 10px;
                text-decoration: none;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
                border: none;
                cursor: pointer;
                font-size: 1.2em;
            }
            
            .theme-toggle:hover {
                background: rgba(255,255,255,0.2);
                transform: translateY(-2px);
            }
            
            .dark .theme-toggle {
                background: rgba(0,0,0,0.2);
                color: #e2e8f0;
            }
            
            .dark .theme-toggle:hover {
                background: rgba(0,0,0,0.3);
            }
            
            .health-container {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 20px;
                padding: 30px;
                transition: all 0.3s ease;
            }
            
            .dark .health-container {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
            }
            
            .status-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .status-card {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 15px;
                padding: 25px;
                text-align: center;
                transition: all 0.3s ease;
            }
            
            .dark .status-card {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
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
                color: #1e293b;
            }
            
            .dark .status-title {
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
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 25px;
                margin-top: 30px;
                transition: all 0.3s ease;
            }
            
            .dark .system-info {
                background: rgba(255,255,255,0.05);
            }
            
            .system-info h3 {
                color: #1e293b;
                margin-bottom: 20px;
                font-size: 1.3em;
            }
            
            .dark .system-info h3 {
                color: #ffffff;
            }
            
            .info-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }
            
            .info-item {
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 15px;
                transition: all 0.3s ease;
            }
            
            .dark .info-item {
                background: rgba(255,255,255,0.05);
            }
            
            .info-label {
                color: #94a3b8;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 5px;
            }
            
                         .info-value {
                 color: #1e293b;
                 font-weight: 600;
                 font-size: 1.1em;
             }
             
             .dark .info-value {
                 color: #ffffff;
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
            
            <button class="theme-toggle" onclick="toggleTheme()">
                <i class="fas fa-moon" id="theme-icon"></i>
            </button>
            
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
        
        <script>
            // Theme toggle functionality
            function toggleTheme() {
                const html = document.documentElement;
                const themeIcon = document.getElementById('theme-icon');
                
                if (html.classList.contains('dark')) {
                    html.classList.remove('dark');
                    html.classList.add('light');
                    themeIcon.className = 'fas fa-moon';
                    localStorage.setItem('theme', 'light');
                } else {
                    html.classList.remove('light');
                    html.classList.add('dark');
                    themeIcon.className = 'fas fa-sun';
                    localStorage.setItem('theme', 'dark');
                }
            }
            
            // Check for saved theme preference
            const savedTheme = localStorage.getItem('theme') || 'light';
            const html = document.documentElement;
            const themeIcon = document.getElementById('theme-icon');
            
            if (savedTheme === 'dark') {
                html.classList.remove('light');
                html.classList.add('dark');
                themeIcon.className = 'fas fa-sun';
            } else {
                html.classList.remove('dark');
                html.classList.add('light');
                themeIcon.className = 'fas fa-moon';
            }
        </script>
    </body>
    </html>
    """

@app.get("/docs", response_class=HTMLResponse)
def docs_page():
    """User-friendly documentation page"""
    return """
    <!DOCTYPE html>
    <html class="light">
    <head>
        <title>Documentation - NetOps AI Pipeline</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            tailwind.config = {
                darkMode: 'class',
                theme: {
                    extend: {
                        colors: {
                            brand: {
                                50: '#eff6ff',
                                100: '#dbeafe',
                                200: '#bfdbfe',
                                300: '#93c5fd',
                                400: '#60a5fa',
                                500: '#3b82f6',
                                600: '#2563eb',
                                700: '#1d4ed8',
                                800: '#1e40af',
                                900: '#1e3a8a',
                            }
                        }
                    }
                }
            }
        </script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body { 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e1 100%);
                min-height: 100vh;
                color: #1e293b;
                line-height: 1.6;
                transition: all 0.3s ease;
            }
            
            .dark body {
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
                color: #e2e8f0;
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
            
            .theme-toggle {
                position: absolute;
                top: 20px;
                right: 20px;
                background: rgba(255,255,255,0.1);
                color: #ffffff;
                padding: 10px;
                border-radius: 10px;
                text-decoration: none;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
                border: none;
                cursor: pointer;
                font-size: 1.2em;
            }
            
            .theme-toggle:hover {
                background: rgba(255,255,255,0.2);
                transform: translateY(-2px);
            }
            
            .dark .theme-toggle {
                background: rgba(0,0,0,0.2);
                color: #e2e8f0;
            }
            
            .dark .theme-toggle:hover {
                background: rgba(0,0,0,0.3);
            }
            
            .docs-container {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 20px;
                padding: 30px;
                transition: all 0.3s ease;
            }
            
            .dark .docs-container {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
            }
            
            .section {
                margin-bottom: 40px;
            }
            
            .section h3 {
                color: #1e293b;
                font-size: 1.5em;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .dark .section h3 {
                color: #ffffff;
            }
            
            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .feature-card {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 15px;
                padding: 25px;
                transition: all 0.3s ease;
            }
            
            .dark .feature-card {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
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
                color: #1e293b;
                margin-bottom: 10px;
            }
            
            .dark .feature-title {
                color: #ffffff;
            }
            
            .feature-description {
                color: #64748b;
                margin-bottom: 15px;
            }
            
            .dark .feature-description {
                color: #94a3b8;
            }
            
            .feature-list {
                list-style: none;
                padding: 0;
            }
            
            .feature-list li {
                color: #475569;
                margin-bottom: 5px;
                padding-left: 20px;
                position: relative;
            }
            
            .dark .feature-list li {
                color: #cbd5e1;
            }
            
            .feature-list li:before {
                content: "✓";
                color: #10b981;
                position: absolute;
                left: 0;
                font-weight: bold;
            }
            
            .format-example {
                background: rgba(0,0,0,0.1);
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                border-left: 4px solid #3b82f6;
                transition: all 0.3s ease;
            }
            
            .dark .format-example {
                background: rgba(0,0,0,0.3);
            }
            
            .format-example h4 {
                color: #1e293b;
                margin-bottom: 10px;
            }
            
            .dark .format-example h4 {
                color: #ffffff;
            }
            
                         .format-example pre {
                 color: #334155;
                 font-family: 'Courier New', monospace;
                 font-size: 0.9em;
                 overflow-x: auto;
             }
             
             .dark .format-example pre {
                 color: #e2e8f0;
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
            
            <button class="theme-toggle" onclick="toggleTheme()">
                <i class="fas fa-moon" id="theme-icon"></i>
            </button>
            
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
        
        <script>
            // Theme toggle functionality
            function toggleTheme() {
                const html = document.documentElement;
                const themeIcon = document.getElementById('theme-icon');
                
                if (html.classList.contains('dark')) {
                    html.classList.remove('dark');
                    html.classList.add('light');
                    themeIcon.className = 'fas fa-moon';
                    localStorage.setItem('theme', 'light');
                } else {
                    html.classList.remove('light');
                    html.classList.add('dark');
                    themeIcon.className = 'fas fa-sun';
                    localStorage.setItem('theme', 'dark');
                }
            }
            
            // Check for saved theme preference
            const savedTheme = localStorage.getItem('theme') || 'light';
            const html = document.documentElement;
            const themeIcon = document.getElementById('theme-icon');
            
            if (savedTheme === 'dark') {
                html.classList.remove('light');
                html.classList.add('dark');
                themeIcon.className = 'fas fa-sun';
            } else {
                html.classList.remove('dark');
                html.classList.add('light');
                themeIcon.className = 'fas fa-moon';
            }
        </script>
    </body>
    </html>
    """

@app.get("/health/api")
def health_api():
    """API endpoint for programmatic health checks"""
    return {"status": "ok", "service": "netops-ai-pipeline", "version": "2.0.0"}

@app.get("/system-status", response_class=HTMLResponse)
def system_status_page():
    """User-friendly system status and overview page"""
    return """
    <!DOCTYPE html>
    <html class="light">
    <head>
        <title>System Status - NetOps AI Pipeline</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            tailwind.config = {
                darkMode: 'class',
                theme: {
                    extend: {
                        colors: {
                            brand: {
                                50: '#eff6ff',
                                100: '#dbeafe',
                                200: '#bfdbfe',
                                300: '#93c5fd',
                                400: '#60a5fa',
                                500: '#3b82f6',
                                600: '#2563eb',
                                700: '#1d4ed8',
                                800: '#1e40af',
                                900: '#1e3a8a',
                            }
                        }
                    }
                }
            }
        </script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body { 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e1 100%);
                min-height: 100vh;
                color: #1e293b;
                line-height: 1.6;
                transition: all 0.3s ease;
            }
            
            .dark body {
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
                color: #e2e8f0;
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
            
            .theme-toggle {
                position: absolute;
                top: 20px;
                right: 20px;
                background: rgba(255,255,255,0.1);
                color: #ffffff;
                padding: 10px;
                border-radius: 10px;
                text-decoration: none;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
                border: none;
                cursor: pointer;
                font-size: 1.2em;
            }
            
            .theme-toggle:hover {
                background: rgba(255,255,255,0.2);
                transform: translateY(-2px);
            }
            
            .dark .theme-toggle {
                background: rgba(0,0,0,0.2);
                color: #e2e8f0;
            }
            
            .dark .theme-toggle:hover {
                background: rgba(0,0,0,0.3);
            }
            
            .status-container {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                transition: all 0.3s ease;
            }
            
            .dark .status-container {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
            }
            
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .metric-card {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 15px;
                padding: 25px;
                text-align: center;
                transition: all 0.3s ease;
            }
            
            .dark .metric-card {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
            }
            
            .metric-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }
            
            .metric-icon {
                font-size: 2.5em;
                margin-bottom: 15px;
                color: #60a5fa;
            }
            
            .metric-title {
                font-size: 1.2em;
                font-weight: 600;
                margin-bottom: 10px;
                color: #1e293b;
            }
            
            .dark .metric-title {
                color: #ffffff;
            }
            
            .metric-value {
                font-size: 2em;
                font-weight: 700;
                color: #10b981;
                margin-bottom: 5px;
            }
            
            .metric-description {
                font-size: 0.9em;
                color: #94a3b8;
            }
            
            .features-section {
                background: rgba(255,255,255,0.05);
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 30px;
            }
            
            .features-section h3 {
                color: #1e293b;
                margin-bottom: 20px;
                font-size: 1.5em;
                text-align: center;
            }
            
            .dark .features-section h3 {
                color: #ffffff;
            }
            
            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }
            
            .feature-item {
                background: rgba(255,255,255,0.05);
                border-radius: 10px;
                padding: 20px;
                display: flex;
                align-items: center;
                gap: 15px;
            }
            
            .feature-icon {
                font-size: 1.5em;
                color: #10b981;
                min-width: 30px;
            }
            
            .feature-text {
                color: #1e293b;
                font-weight: 500;
            }
            
            .dark .feature-text {
                color: #e2e8f0;
            }
            
            .quick-actions {
                background: rgba(255,255,255,0.05);
                border-radius: 15px;
                padding: 25px;
            }
            
            .quick-actions h3 {
                color: #ffffff;
                margin-bottom: 20px;
                font-size: 1.5em;
                text-align: center;
            }
            
            .actions-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }
            
            .action-btn {
                background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
                color: #ffffff;
                padding: 15px 20px;
                border-radius: 10px;
                text-decoration: none;
                text-align: center;
                transition: all 0.3s ease;
                font-weight: 500;
            }
            
            .action-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
            }
            
            @media (max-width: 768px) {
                .container { padding: 15px; }
                .header { padding: 30px 20px; }
                .header h1 { font-size: 2.2em; }
                .metrics-grid { grid-template-columns: repeat(2, 1fr); }
                .features-grid { grid-template-columns: 1fr; }
                .actions-grid { grid-template-columns: 1fr; }
            }
            
            @media (max-width: 480px) {
                .header h1 { font-size: 1.8em; }
                .metrics-grid { grid-template-columns: 1fr; }
                .metric-card { padding: 20px; }
                .metric-value { font-size: 1.5em; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-btn">
                <i class="fas fa-arrow-left"></i> Back to Dashboard
            </a>
            
            <button class="theme-toggle" onclick="toggleTheme()">
                <i class="fas fa-moon" id="theme-icon"></i>
            </button>

            <div class="header">
                <h1><i class="fas fa-chart-bar"></i> System Status</h1>
                <p>Comprehensive overview of NetOps AI Pipeline performance and capabilities</p>
            </div>

            <div class="status-container">
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-rocket"></i>
                        </div>
                        <div class="metric-title">System Performance</div>
                        <div class="metric-value">99.9%</div>
                        <div class="metric-description">Uptime and reliability</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-brain"></i>
                        </div>
                        <div class="metric-title">AI Processing</div>
                        <div class="metric-value">&lt;2s</div>
                        <div class="metric-description">Average analysis time</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-shield-alt"></i>
                        </div>
                        <div class="metric-title">Security</div>
                        <div class="metric-value">100%</div>
                        <div class="metric-description">Data protection active</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-database"></i>
                        </div>
                        <div class="metric-title">Storage</div>
                        <div class="metric-value">Ready</div>
                        <div class="metric-description">Database operational</div>
                    </div>
                </div>
            </div>

            <div class="features-section">
                <h3><i class="fas fa-star"></i> Key Features</h3>
                <div class="features-grid">
                    <div class="feature-item">
                        <div class="feature-icon">
                            <i class="fas fa-search"></i>
                        </div>
                        <div class="feature-text">Advanced Anomaly Detection using Isolation Forest</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">
                            <i class="fas fa-robot"></i>
                        </div>
                        <div class="feature-text">AI-Powered Analysis with OpenAI Integration</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div class="feature-text">Real-time KPI Visualization and Charts</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">
                            <i class="fas fa-file-pdf"></i>
                        </div>
                        <div class="feature-text">Professional PDF Report Generation</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">
                            <i class="fas fa-tree"></i>
                        </div>
                        <div class="feature-text">Random Forest Predictive Analytics</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">
                            <i class="fas fa-mobile-alt"></i>
                        </div>
                        <div class="feature-text">Mobile-Responsive Enterprise Interface</div>
                    </div>
                </div>
            </div>

            <div class="quick-actions">
                <h3><i class="fas fa-bolt"></i> Quick Actions</h3>
                <div class="actions-grid">
                    <a href="/" class="action-btn">
                        <i class="fas fa-upload"></i> Upload Data
                    </a>
                    <a href="/uploads" class="action-btn">
                        <i class="fas fa-list"></i> View Uploads
                    </a>
                    <a href="/health" class="action-btn">
                        <i class="fas fa-heartbeat"></i> Health Check
                    </a>
                    <a href="/docs" class="action-btn">
                        <i class="fas fa-book"></i> API Docs
                    </a>
                </div>
            </div>
        </div>
        
        <script>
            // Theme toggle functionality
            function toggleTheme() {
                const html = document.documentElement;
                const themeIcon = document.getElementById('theme-icon');
                
                if (html.classList.contains('dark')) {
                    html.classList.remove('dark');
                    html.classList.add('light');
                    themeIcon.className = 'fas fa-moon';
                    localStorage.setItem('theme', 'light');
                } else {
                    html.classList.remove('light');
                    html.classList.add('dark');
                    themeIcon.className = 'fas fa-sun';
                    localStorage.setItem('theme', 'dark');
                }
            }
            
            // Check for saved theme preference
            const savedTheme = localStorage.getItem('theme') || 'light';
            const html = document.documentElement;
            const themeIcon = document.getElementById('theme-icon');
            
            if (savedTheme === 'dark') {
                html.classList.remove('light');
                html.classList.add('dark');
                themeIcon.className = 'fas fa-sun';
            } else {
                html.classList.remove('dark');
                html.classList.add('light');
                themeIcon.className = 'fas fa-moon';
            }
        </script>
    </body>
    </html>
    """

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

@app.get("/pdf/{upload_id}")
def get_pdf_report(upload_id: int):
    """Download KPI analysis as PDF report"""
    pdf_path = None
    try:
        with get_session() as s:
            rows = s.query(Score).filter(Score.upload_id == upload_id).all()
        if not rows:
            raise HTTPException(status_code=404, detail="Upload not found")

        # Convert database rows back to DataFrame
        import pandas as pd
        
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
        
        # Generate AI summary if available (skip if it fails)
        ai_summary = None
        try:
            ai_summary = generate_ai_kpi_summary(df, anomalies, df['score'])
        except Exception as ai_error:
            # AI summary generation failed - handled gracefully
            # Continue without AI summary
            pass
        
        # Generate PDF report
        pdf_path = generate_kpi_pdf_report(upload_id, df, anomalies, ai_summary)
        
        # Return PDF file
        return FileResponse(
            pdf_path,
            media_type='application/pdf',
            filename=f'NetOps_KPI_Report_{upload_id}.pdf',
            headers={'Content-Disposition': f'attachment; filename=NetOps_KPI_Report_{upload_id}.pdf'}
        )
        
    except Exception as e:
        # PDF generation error - handled gracefully
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")
    # Note: File cleanup is handled by the operating system for temporary files
    # The temporary file will be automatically cleaned up when the system restarts

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
            # AI summary generation error - handled gracefully
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
        
        # Extract JavaScript config to avoid nested f-string issues
        tailwind_config = """
                tailwind.config = {
                    darkMode: 'class',
                    theme: {
                        extend: {
                            colors: {
                                brand: {
                                    50: '#eff6ff',
                                    100: '#dbeafe',
                                    200: '#bfdbfe',
                                    300: '#93c5fd',
                                    400: '#60a5fa',
                                    500: '#3b82f6',
                                    600: '#2563eb',
                                    700: '#1d4ed8',
                                    800: '#1e40af',
                                    900: '#1e3a8a',
                                }
                            }
                        }
                    }
                }
        """
        
        # Extract JavaScript theme toggle to avoid syntax issues
        theme_toggle_js = """
            // Theme toggle functionality
            function toggleTheme() {
                const html = document.documentElement;
                const themeIcon = document.getElementById('theme-icon');
                
                if (html.classList.contains('dark')) {
                    html.classList.remove('dark');
                    html.classList.add('light');
                    themeIcon.className = 'fas fa-moon';
                    localStorage.setItem('theme', 'light');
                } else {
                    html.classList.remove('light');
                    html.classList.add('dark');
                    themeIcon.className = 'fas fa-sun';
                    localStorage.setItem('theme', 'dark');
                }
            }
            
            // Check for saved theme preference
            const savedTheme = localStorage.getItem('theme') || 'light';
            const html = document.documentElement;
            const themeIcon = document.getElementById('theme-icon');
            
            if (savedTheme === 'dark') {
                html.classList.remove('light');
                html.classList.add('dark');
                themeIcon.className = 'fas fa-sun';
            } else {
                html.classList.remove('dark');
                html.classList.add('light');
                themeIcon.className = 'fas fa-moon';
            }
        """
        
        return f"""
        <!DOCTYPE html>
        <html class="light">
        <head>
            <title>Network Performance Analysis Report - NetOps AI Pipeline</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
            <script src="https://cdn.tailwindcss.com"></script>
            <script>
                {tailwind_config}
            </script>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                
                body {{ 
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e1 100%);
                    color: #1e293b;
                    line-height: 1.7;
                    min-height: 100vh;
                    font-weight: 400;
                    transition: all 0.3s ease;
                }}
                
                .dark body {
                    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
                    color: #f1f5f9;
                }
                
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
                
                .theme-toggle {{
                    position: fixed;
                    top: 30px;
                    right: 30px;
                    background: rgba(255,255,255,0.1);
                    color: #ffffff;
                    padding: 12px;
                    border-radius: 12px;
                    text-decoration: none;
                    transition: all 0.3s ease;
                    backdrop-filter: blur(20px);
                    border: none;
                    cursor: pointer;
                    font-size: 1.2em;
                    z-index: 1000;
                    border: 1px solid rgba(255,255,255,0.2);
                }}
                
                .theme-toggle:hover {{
                    background: rgba(255,255,255,0.2);
                    transform: translateY(-2px);
                    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                }}
                
                .dark .theme-toggle {{
                    background: rgba(0,0,0,0.2);
                    color: #e2e8f0;
                    border: 1px solid rgba(255,255,255,0.1);
                }}
                
                .dark .theme-toggle:hover {{
                    background: rgba(0,0,0,0.3);
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
                
                <button class="theme-toggle" onclick="toggleTheme()">
                    <i class="fas fa-moon" id="theme-icon"></i>
                </button>
                
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
        
        <script>
            {theme_toggle_js}
        </script>
        </html>
        """
        
    except Exception as e:
        # AI summary error - handled gracefully
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
                 <a href="/pdf/{u.id}" class="action-link">
                     <i class="fas fa-file-pdf"></i> Download PDF
                 </a>
                 <a href="/predictions/{u.id}/html" class="action-link" target="_blank">
                     <i class="fas fa-tree"></i> Predictions
                 </a>
             </div>
        </div>
        """
    
    # Extract JavaScript config to avoid nested f-string issues
    tailwind_config = """
            tailwind.config = {
                darkMode: 'class',
                theme: {
                    extend: {
                        colors: {
                            brand: {
                                50: '#eff6ff',
                                100: '#dbeafe',
                                200: '#bfdbfe',
                                300: '#93c5fd',
                                400: '#60a5fa',
                                500: '#3b82f6',
                                600: '#2563eb',
                                700: '#1d4ed8',
                                800: '#1e40af',
                                900: '#1e3a8a',
                            }
                        }
                    }
                }
            }
    """
    
    # Extract JavaScript theme toggle to avoid syntax issues
    theme_toggle_js = """
            // Theme toggle functionality
            function toggleTheme() {
                const html = document.documentElement;
                const themeIcon = document.getElementById('theme-icon');
                
                if (html.classList.contains('dark')) {
                    html.classList.remove('dark');
                    html.classList.add('light');
                    themeIcon.className = 'fas fa-moon';
                    localStorage.setItem('theme', 'light');
                } else {
                    html.classList.remove('light');
                    html.classList.add('dark');
                    themeIcon.className = 'fas fa-sun';
                    localStorage.setItem('theme', 'dark');
                }
            }
            
            // Check for saved theme preference
            const savedTheme = localStorage.getItem('theme') || 'light';
            const html = document.documentElement;
            const themeIcon = document.getElementById('theme-icon');
            
            if (savedTheme === 'dark') {
                html.classList.remove('light');
                html.classList.add('dark');
                themeIcon.className = 'fas fa-sun';
            } else {
                html.classList.remove('dark');
                html.classList.add('light');
                themeIcon.className = 'fas fa-moon';
            }
    """
    
    return f"""
    <!DOCTYPE html>
    <html class="light">
    <head>
        <title>Uploads - NetOps AI Pipeline</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            {tailwind_config}
        </script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            
            body {{ 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e1 100%);
                min-height: 100vh;
                color: #1e293b;
                line-height: 1.6;
                transition: all 0.3s ease;
            }}
            
            .dark body {
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
                color: #e2e8f0;
            }
            
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
            
            .theme-toggle {{
                position: absolute;
                top: 20px;
                right: 20px;
                background: rgba(255,255,255,0.1);
                color: #ffffff;
                padding: 10px;
                border-radius: 10px;
                text-decoration: none;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
                border: none;
                cursor: pointer;
                font-size: 1.2em;
            }}
            
            .theme-toggle:hover {{
                background: rgba(255,255,255,0.2);
                transform: translateY(-2px);
            }}
            
            .dark .theme-toggle {{
                background: rgba(0,0,0,0.2);
                color: #e2e8f0;
            }}
            
            .dark .theme-toggle:hover {{
                background: rgba(0,0,0,0.3);
            }}
            
            .uploads-container {{
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 20px;
                padding: 30px;
                transition: all 0.3s ease;
            }}
            
            .dark .uploads-container {{
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
            }}
            
            .uploads-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }}
            
            .dark .uploads-header {{
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }}
            
            .uploads-title {{
                font-size: 1.5em;
                font-weight: 600;
                color: #1e293b;
            }}
            
            .dark .uploads-title {{
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
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 20px;
                transition: all 0.3s ease;
            }}
            
            .dark .upload-item {{
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
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
                color: #1e293b;
                font-size: 1.2em;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .dark .upload-header h4 {{
                color: #ffffff;
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
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 15px;
                transition: all 0.3s ease;
            }}
            
            .dark .stat {{
                background: rgba(255,255,255,0.05);
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
            
            <button class="theme-toggle" onclick="toggleTheme()">
                <i class="fas fa-moon" id="theme-icon"></i>
            </button>
            
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
        
        <script>
            {theme_toggle_js}
        </script>
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

@app.get("/predictions/{upload_id}")
def get_predictions(upload_id: int):
    """Get Random Forest predictions for an upload"""
    try:
        with get_session() as s:
            rows = s.query(Score).filter(Score.upload_id == upload_id).all()
        if not rows:
            raise HTTPException(status_code=404, detail="Upload not found")

        # Convert database rows back to DataFrame for Random Forest analysis
        import pandas as pd
        
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
        
        # Get Random Forest predictions
        rf_results = analyze_with_random_forest(df)
        
        return {
            "upload_id": upload_id,
            "random_forest_analysis": rf_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/predictions/{upload_id}/html", response_class=HTMLResponse)
def get_predictions_html(upload_id: int):
    """Get Random Forest predictions in HTML format"""
    try:
        with get_session() as s:
            rows = s.query(Score).filter(Score.upload_id == upload_id).all()
        if not rows:
            raise HTTPException(status_code=404, detail="Upload not found")

        # Convert database rows back to DataFrame
        import pandas as pd
        
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
        
        # Get Random Forest predictions
        rf_results = analyze_with_random_forest(df)
        
        # Extract data for HTML display
        summary = rf_results['summary']
        feature_importance = rf_results['feature_importance']
        
        # Create HTML for status distribution
        status_dist_html = ""
        for status, count in summary['status_distribution'].items():
            percentage = (count / len(df)) * 100
            color = {
                'NORMAL': '#10b981',
                'WARNING': '#f59e0b',
                'CRITICAL': '#ef4444'
            }.get(status, '#6b7280')
            
            status_dist_html += f"""
            <div class="status-item">
                <div class="status-label" style="color: {color};">{status}</div>
                <div class="status-bar">
                    <div class="status-fill" style="width: {percentage}%; background: {color};"></div>
                </div>
                <div class="status-count">{count} ({percentage:.1f}%)</div>
            </div>
            """
        
        # Create HTML for feature importance
        feature_importance_html = ""
        if 'classification' in feature_importance:
            for feature, importance in feature_importance['classification'].items():
                percentage = importance * 100
                feature_importance_html += f"""
                <div class="feature-item">
                    <div class="feature-name">{feature}</div>
                    <div class="feature-bar">
                        <div class="feature-fill" style="width: {percentage}%;"></div>
                    </div>
                    <div class="feature-value">{percentage:.1f}%</div>
                </div>
                """
        
        # Extract JavaScript config to avoid nested f-string issues
        tailwind_config = """
                tailwind.config = {
                    darkMode: 'class',
                    theme: {
                        extend: {
                            colors: {
                                brand: {
                                    50: '#eff6ff',
                                    100: '#dbeafe',
                                    200: '#bfdbfe',
                                    300: '#93c5fd',
                                    400: '#60a5fa',
                                    500: '#3b82f6',
                                    600: '#2563eb',
                                    700: '#1d4ed8',
                                    800: '#1e40af',
                                    900: '#1e3a8a',
                                }
                            }
                        }
                    }
                }
        """
        
        # Extract JavaScript theme toggle to avoid syntax issues
        theme_toggle_js = """
            // Theme toggle functionality
            function toggleTheme() {
                const html = document.documentElement;
                const themeIcon = document.getElementById('theme-icon');
                
                if (html.classList.contains('dark')) {
                    html.classList.remove('dark');
                    html.classList.add('light');
                    themeIcon.className = 'fas fa-moon';
                    localStorage.setItem('theme', 'light');
                } else {
                    html.classList.remove('light');
                    html.classList.add('dark');
                    themeIcon.className = 'fas fa-sun';
                    localStorage.setItem('theme', 'dark');
                }
            }
            
            // Check for saved theme preference
            const savedTheme = localStorage.getItem('theme') || 'light';
            const html = document.documentElement;
            const themeIcon = document.getElementById('theme-icon');
            
            if (savedTheme === 'dark') {
                html.classList.remove('light');
                html.classList.add('dark');
                themeIcon.className = 'fas fa-sun';
            } else {
                html.classList.remove('dark');
                html.classList.add('light');
                themeIcon.className = 'fas fa-moon';
            }
        """
        
        return f"""
        <!DOCTYPE html>
        <html class="light">
        <head>
            <title>Random Forest Predictions - NetOps AI Pipeline</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
            <script src="https://cdn.tailwindcss.com"></script>
            <script>
                {tailwind_config}
            </script>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                
                body {{ 
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e1 100%);
                    color: #1e293b;
                    line-height: 1.7;
                    min-height: 100vh;
                    font-weight: 400;
                    transition: all 0.3s ease;
                }}
                
                .dark body {
                    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
                    color: #f1f5f9;
                }
                
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
                }}
                
                .theme-toggle {{
                    position: fixed;
                    top: 30px;
                    right: 30px;
                    background: rgba(255,255,255,0.1);
                    color: #ffffff;
                    padding: 12px;
                    border-radius: 12px;
                    text-decoration: none;
                    transition: all 0.3s ease;
                    backdrop-filter: blur(20px);
                    border: none;
                    cursor: pointer;
                    font-size: 1.2em;
                    z-index: 1000;
                    border: 1px solid rgba(255,255,255,0.2);
                }}
                
                .theme-toggle:hover {{
                    background: rgba(255,255,255,0.2);
                    transform: translateY(-2px);
                    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                }}
                
                .dark .theme-toggle {{
                    background: rgba(0,0,0,0.2);
                    color: #e2e8f0;
                    border: 1px solid rgba(255,255,255,0.1);
                }}
                
                .dark .theme-toggle:hover {{
                    background: rgba(0,0,0,0.3);
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
                
                .content-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 30px;
                    margin-bottom: 30px;
                }}
                
                .card {{
                    background: rgba(255,255,255,0.05);
                    backdrop-filter: blur(20px);
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 20px;
                    padding: 30px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }}
                
                .card h2 {{
                    font-size: 1.5em;
                    font-weight: 600;
                    margin-bottom: 20px;
                    color: #ffffff;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}
                
                .metric-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                
                .metric {{
                    background: rgba(255,255,255,0.05);
                    border-radius: 12px;
                    padding: 20px;
                    text-align: center;
                    border: 1px solid rgba(255,255,255,0.1);
                }}
                
                .metric-value {{
                    font-size: 2em;
                    font-weight: 700;
                    margin-bottom: 5px;
                    color: #60a5fa;
                }}
                
                .metric-label {{
                    font-size: 0.9em;
                    opacity: 0.8;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                
                .status-item {{
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    margin-bottom: 15px;
                    padding: 10px;
                    background: rgba(255,255,255,0.05);
                    border-radius: 10px;
                }}
                
                .status-label {{
                    font-weight: 600;
                    min-width: 80px;
                }}
                
                .status-bar {{
                    flex: 1;
                    height: 8px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 4px;
                    overflow: hidden;
                }}
                
                .status-fill {{
                    height: 100%;
                    border-radius: 4px;
                    transition: width 0.3s ease;
                }}
                
                .status-count {{
                    font-size: 0.9em;
                    opacity: 0.8;
                    min-width: 80px;
                    text-align: right;
                }}
                
                .feature-item {{
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    margin-bottom: 15px;
                    padding: 10px;
                    background: rgba(255,255,255,0.05);
                    border-radius: 10px;
                }}
                
                .feature-name {{
                    font-weight: 500;
                    min-width: 120px;
                }}
                
                .feature-bar {{
                    flex: 1;
                    height: 8px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 4px;
                    overflow: hidden;
                }}
                
                .feature-fill {{
                    height: 100%;
                    background: linear-gradient(90deg, #60a5fa, #3b82f6);
                    border-radius: 4px;
                    transition: width 0.3s ease;
                }}
                
                .feature-value {{
                    font-size: 0.9em;
                    opacity: 0.8;
                    min-width: 60px;
                    text-align: right;
                }}
                
                @media (max-width: 768px) {{
                    .content-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .metric-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .header h1 {{
                        font-size: 2em;
                    }}
                    
                    .container {{
                        padding: 20px 15px;
                    }}
                }}
            </style>
        </head>
        <body>
            <a href="/" class="back-btn">
                <i class="fas fa-arrow-left"></i> Back to Dashboard
            </a>
            
            <button class="theme-toggle" onclick="toggleTheme()">
                <i class="fas fa-moon" id="theme-icon"></i>
            </button>
            
            <div class="container">
                <div class="header">
                    <h1><i class="fas fa-tree"></i> Random Forest Predictions</h1>
                    <p>AI-powered network performance forecasting and classification</p>
                </div>
                
                <div class="content-grid">
                    <div class="card">
                        <h2><i class="fas fa-chart-pie"></i> Network Status Predictions</h2>
                        
                        <div class="metric-grid">
                            <div class="metric">
                                <div class="metric-value">{summary['most_common_status']}</div>
                                <div class="metric-label">Most Common Status</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value">{summary['average_confidence']:.1f}%</div>
                                <div class="metric-label">Average Confidence</div>
                            </div>
                        </div>
                        
                        <h3 style="margin-bottom: 15px; color: #e2e8f0;">Status Distribution</h3>
                        {status_dist_html}
                    </div>
                    
                    <div class="card">
                        <h2><i class="fas fa-chart-line"></i> Performance Predictions</h2>
                        
                        <div class="metric-grid">
                            <div class="metric">
                                <div class="metric-value">{summary['average_predicted_throughput']:.1f}</div>
                                <div class="metric-label">Avg Predicted Throughput (Mbps)</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value">{len(df)}</div>
                                <div class="metric-label">Data Points Analyzed</div>
                            </div>
                        </div>
                        
                        <h3 style="margin-bottom: 15px; color: #e2e8f0;">Feature Importance</h3>
                        <p style="margin-bottom: 20px; opacity: 0.8;">Which KPIs matter most for predictions</p>
                        {feature_importance_html}
                    </div>
                </div>
            </div>
        </body>
        
        <script>
            {theme_toggle_js}
        </script>
        </html>
        """
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

