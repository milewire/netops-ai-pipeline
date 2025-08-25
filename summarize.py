import os
import re
import json
from dotenv import load_dotenv
import openai

load_dotenv()

# Initialize OpenAI client if API key is available
openai_client = None
api_key = os.getenv("OPENAI_API_KEY")
print(f"OpenAI API Key available: {bool(api_key)}")
if api_key:
    openai.api_key = api_key
    openai_client = openai
    print("OpenAI client initialized successfully")
else:
    print("No OpenAI API key found, will use fallback summary")

def generate_ai_kpi_summary(df, anomalies, scores):
    """Generate AI-powered insights using OpenAI"""
    print(f"generate_ai_kpi_summary called - openai_client available: {openai_client is not None}")
    if not openai_client:
        print("No OpenAI client available, using fallback summary")
        return generate_fallback_kpi_summary(df, anomalies, scores)
    
    try:
        # Prepare data for AI analysis
        total_samples = len(df)
        anomaly_count = len(anomalies)
        anomaly_rate = (anomaly_count / total_samples) * 100 if total_samples > 0 else 0
        
        # Calculate key metrics
        avg_prb_util = df['PRB_Util'].mean()
        avg_throughput = df['Throughput_Mbps'].mean()
        avg_bler = df['BLER'].mean()
        
        # Get worst performing cells
        worst_cells = df[df['anomaly'] == -1].sort_values('score', ascending=True).head(3)
        
        # Create prompt for OpenAI
        prompt = f"""
        As a network operations expert, analyze this network performance data and provide professional insights:

        DATA SUMMARY:
        - Total samples: {total_samples}
        - Anomalies detected: {anomaly_count} ({anomaly_rate:.1f}%)
        - Average PRB Utilization: {avg_prb_util:.1f}%
        - Average Throughput: {avg_throughput:.1f} Mbps
        - Average Block Error Rate: {avg_bler:.3f}

        WORST PERFORMING CELLS:
        {worst_cells[['cell_id', 'score', 'PRB_Util', 'Throughput_Mbps']].to_string()}

        Please provide:
        1. Executive Summary (2-3 sentences)
        2. Key Insights (3-4 bullet points)
        3. Actionable Recommendations (3-4 specific actions)
        4. Severity Assessment (LOW/MEDIUM/HIGH)

        Format as JSON with keys: executive_summary, key_insights (array), recommendations (array), severity_level
        """
        
        response = openai_client.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a network operations expert providing professional analysis of network performance data."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        # Parse AI response
        ai_response = response.choices[0].message.content.strip()
        
        # Try to parse as JSON, fallback to text if needed
        try:
            result = json.loads(ai_response)
            return {
                "summary": result.get("executive_summary", "AI analysis completed"),
                "insights": result.get("key_insights", []),
                "recommendations": result.get("recommendations", []),
                "severity": result.get("severity_level", "MEDIUM"),
                "ai_generated": True
            }
        except json.JSONDecodeError:
            return {
                "summary": ai_response,
                "insights": ["AI analysis provided", "Review the detailed summary above"],
                "recommendations": ["Contact network operations team", "Monitor performance trends"],
                "severity": "MEDIUM",
                "ai_generated": True
            }
            
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return generate_fallback_kpi_summary(df, anomalies, scores)

def generate_fallback_kpi_summary(df, anomalies, scores):
    """Fallback summary when OpenAI is not available"""
    total_samples = len(df)
    anomaly_count = len(anomalies)
    anomaly_rate = (anomaly_count / total_samples) * 100 if total_samples > 0 else 0
    
    # Calculate additional metrics for better insights
    avg_prb_util = df['PRB_Util'].mean() if 'PRB_Util' in df.columns else 0
    avg_throughput = df['Throughput_Mbps'].mean() if 'Throughput_Mbps' in df.columns else 0
    avg_bler = df['BLER'].mean() if 'BLER' in df.columns else 0
    
    # Determine severity based on multiple factors
    severity = "HIGH" if anomaly_rate > 10 else "MEDIUM" if anomaly_rate > 5 else "LOW"
    
    # Generate more detailed insights
    insights = [
        f"Anomaly detection rate: {anomaly_rate:.1f}% ({anomaly_count} out of {total_samples} samples)",
        f"Average PRB Utilization: {avg_prb_util:.1f}%",
        f"Average Throughput: {avg_throughput:.1f} Mbps",
        f"Average Block Error Rate: {avg_bler:.3f}"
    ]
    
    # Generate actionable recommendations
    recommendations = []
    if anomaly_rate > 10:
        recommendations.extend([
            "[ALERT] IMMEDIATE ACTION REQUIRED: High anomaly rate detected",
            "Investigate cells with highest anomaly scores for potential issues",
            "Review network capacity and resource allocation"
        ])
    elif anomaly_rate > 5:
        recommendations.extend([
            "[WARNING] MONITOR CLOSELY: Moderate anomalies detected",
            "Analyze performance trends in affected cells",
            "Consider proactive capacity planning"
        ])
    else:
        recommendations.extend([
            "[OK] NETWORK HEALTHY: Low anomaly rate indicates good performance",
            "Continue monitoring for any emerging issues",
            "Maintain current optimization strategies"
        ])
    
    recommendations.extend([
        "Schedule regular performance reviews",
        "Implement continuous monitoring alerts"
    ])
    
    return {
        "summary": f"Network performance analysis completed successfully. {anomaly_count} anomalies detected out of {total_samples} total samples, representing a {anomaly_rate:.1f}% anomaly rate. Overall severity level: {severity}.",
        "insights": insights,
        "recommendations": recommendations,
        "severity": severity,
        "ai_generated": False
    }

def summarize_logs(text: str) -> str:
    """Summarize logs using OpenAI if available, otherwise use heuristic"""
    if not openai_client:
        return summarize_logs_heuristic(text)
    
    try:
        # Count incidents
        patterns = {
            "critical_errors": len(re.findall(r"CRIT.*", text)),
            "errors": len(re.findall(r"ERROR.*", text)),
            "alarms": len(re.findall(r"ALARM.*", text)),
            "warnings": len(re.findall(r"WARN.*", text)),
        }
        
        total_incidents = sum(patterns.values())
        
        if total_incidents == 0:
            return "No incidents detected in the log file. System appears to be operating normally."
        
        # Create prompt for OpenAI
        prompt = f"""
        Analyze this system log file and provide a professional summary:

        INCIDENT COUNTS:
        - Critical Errors: {patterns['critical_errors']}
        - Errors: {patterns['errors']}
        - Alarms: {patterns['alarms']}
        - Warnings: {patterns['warnings']}
        - Total Incidents: {total_incidents}

        LOG CONTENT (first 1000 characters):
        {text[:1000]}

        Please provide:
        1. Executive Summary (2-3 sentences)
        2. Key Findings (3-4 bullet points)
        3. Recommended Actions (2-3 specific actions)
        4. Overall System Health Assessment (GOOD/ATTENTION/CRITICAL)

        Format as JSON with keys: summary, findings (array), actions (array), health_status
        """
        
        response = openai_client.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a system administrator analyzing log files for incidents and system health."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.3
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        try:
            result = json.loads(ai_response)
            return result.get("summary", "AI analysis completed")
        except json.JSONDecodeError:
            return ai_response
            
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return summarize_logs_heuristic(text)

def summarize_logs_heuristic(text: str) -> str:
    """Fallback heuristic log summarization"""
    top = sorted(
        (
            (m.group(0), len(m.group(0)))
            for m in re.finditer(r"(ERROR|CRIT|ALARM).+", text)
        ),
        key=lambda x: -x[1],
    )
    return f"Top incidents (heuristic analysis): {min(len(top),5)} lines flagged."

def extract_incidents(log_text: str) -> dict:
    """Extract incident patterns from syslog text"""
    patterns = {
        "critical_errors": re.findall(r"CRIT.*", log_text),
        "errors": re.findall(r"ERROR.*", log_text),
        "alarms": re.findall(r"ALARM.*", log_text),
        "warnings": re.findall(r"WARN.*", log_text),
    }

    return {
        "summary": summarize_logs(log_text),
        "incident_counts": {k: len(v) for k, v in patterns.items()},
        "top_incidents": patterns,
    }
