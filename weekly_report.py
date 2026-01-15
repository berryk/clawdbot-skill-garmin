#!/usr/bin/env python3
"""
Garmin Weekly Report Generator
Generates comprehensive weekly fitness summary with insights and recommendations
"""

import json
import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean

def load_garmin_data(csv_file):
    """Load Garmin data from CSV."""
    data = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def get_week_data(data, days=7):
    """Get last N days of data."""
    today = datetime.now().date()
    start_date = today - timedelta(days=days)
    
    week_data = []
    for row in data:
        row_date = datetime.fromisoformat(row['date']).date()
        if start_date <= row_date <= today:
            week_data.append(row)
    
    return sorted(week_data, key=lambda x: x['date'])

def safe_float(value, default=0.0):
    """Safely convert to float."""
    try:
        return float(value) if value and value != '' else default
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    """Safely convert to int."""
    try:
        return int(float(value)) if value and value != '' else default
    except (ValueError, TypeError):
        return default

def generate_weekly_summary(week_data):
    """Generate weekly summary statistics."""
    if not week_data:
        return None
    
    # Extract metrics
    steps = [safe_int(d['steps']) for d in week_data]
    distances = [safe_float(d['distance_km']) for d in week_data]
    calories = [safe_float(d['calories_total']) for d in week_data]
    sleep_hours = [safe_float(d['sleep_hours']) for d in week_data]
    sleep_scores = [safe_float(d['sleep_score']) for d in week_data if d.get('sleep_score')]
    resting_hrs = [safe_int(d['resting_hr']) for d in week_data if d.get('resting_hr')]
    stress_avgs = [safe_int(d['stress_avg']) for d in week_data if d.get('stress_avg')]
    
    # Active minutes
    active_mod = [safe_int(d['active_minutes_moderate']) for d in week_data]
    active_vig = [safe_int(d['active_minutes_vigorous']) for d in week_data]
    total_active = [m + v for m, v in zip(active_mod, active_vig)]
    
    # Body composition (most recent)
    latest = week_data[-1]
    weight = safe_float(latest.get('weight_kg'))
    body_fat = safe_float(latest.get('body_fat_pct'))
    muscle_mass = safe_float(latest.get('muscle_mass_kg'))
    waist_inches = safe_float(latest.get('waist_inches'))
    waist_cm = safe_float(latest.get('waist_cm'))
    
    summary = {
        'period': f"{week_data[0]['date']} to {week_data[-1]['date']}",
        'days_tracked': len(week_data),
        
        # Activity
        'avg_steps': int(mean(steps)) if steps else 0,
        'total_steps': sum(steps),
        'avg_distance': round(mean(distances), 1) if distances else 0,
        'total_distance': round(sum(distances), 1),
        'avg_calories': int(mean(calories)) if calories else 0,
        'total_calories': int(sum(calories)),
        'avg_active_minutes': int(mean(total_active)) if total_active else 0,
        'total_active_minutes': sum(total_active),
        
        # Sleep
        'avg_sleep_hours': round(mean(sleep_hours), 1) if sleep_hours else 0,
        'avg_sleep_score': int(mean(sleep_scores)) if sleep_scores else 0,
        
        # Health
        'avg_resting_hr': int(mean(resting_hrs)) if resting_hrs else 0,
        'avg_stress': int(mean(stress_avgs)) if stress_avgs else 0,
        
        # Body Composition
        'current_weight': weight,
        'current_body_fat': body_fat,
        'current_muscle_mass': muscle_mass,
        'current_waist_inches': waist_inches,
        'current_waist_cm': waist_cm,
        
        # Goals (10k steps, 7.5h sleep, <40 stress)
        'days_hit_step_goal': sum(1 for s in steps if s >= 10000),
        'days_hit_sleep_goal': sum(1 for s in sleep_hours if s >= 7.5),
        'days_low_stress': sum(1 for s in stress_avgs if s < 40),
    }
    
    return summary

def generate_insights(summary, week_data):
    """Generate insights and recommendations."""
    insights = []
    recommendations = []
    
    # Steps analysis
    if summary['avg_steps'] >= 10000:
        insights.append(f"✅ **Excellent step average:** {summary['avg_steps']:,} steps/day")
    elif summary['avg_steps'] >= 7500:
        insights.append(f"📊 **Good step average:** {summary['avg_steps']:,} steps/day")
        recommendations.append(f"📈 **Target:** Add {10000 - summary['avg_steps']:,} more steps/day to hit 10k goal")
    else:
        insights.append(f"⚠️ **Below target:** {summary['avg_steps']:,} steps/day")
        recommendations.append(f"🎯 **Action:** Increase daily steps by {10000 - summary['avg_steps']:,} to reach 10k goal")
    
    # Sleep analysis
    if summary['avg_sleep_hours'] >= 7.5:
        insights.append(f"✅ **Great sleep:** {summary['avg_sleep_hours']} hours/night avg")
    else:
        insights.append(f"⚠️ **Sleep deficit:** {summary['avg_sleep_hours']} hours/night avg")
        recommendations.append(f"😴 **Target:** Add {round(7.5 - summary['avg_sleep_hours'], 1)} more hours of sleep")
    
    if summary['avg_sleep_score'] >= 80:
        insights.append(f"⭐ **Excellent sleep quality:** {summary['avg_sleep_score']}/100")
    
    # Resting HR (lower is better for fitness)
    if summary['avg_resting_hr'] < 60:
        insights.append(f"❤️ **Excellent cardiovascular fitness:** {summary['avg_resting_hr']} bpm resting HR")
    
    # Stress analysis
    if summary['avg_stress'] < 40:
        insights.append(f"🧘 **Well-managed stress:** Average {summary['avg_stress']}")
    else:
        insights.append(f"⚠️ **Elevated stress:** Average {summary['avg_stress']}")
        recommendations.append("🧘 **Recovery:** Prioritize stress management and recovery activities")
    
    # Activity consistency
    consistency = (summary['days_hit_step_goal'] / summary['days_tracked']) * 100
    if consistency >= 70:
        insights.append(f"🔥 **Consistent activity:** Hit step goal {summary['days_hit_step_goal']}/{summary['days_tracked']} days")
    else:
        recommendations.append(f"📅 **Consistency:** Try to hit step goal more consistently ({int(consistency)}% this week)")
    
    # Body composition (if available)
    if summary['current_body_fat'] and summary['current_body_fat'] < 20:
        insights.append(f"💪 **Lean body composition:** {summary['current_body_fat']}% body fat")
    
    return insights, recommendations

def format_markdown_report(summary, insights, recommendations):
    """Format weekly report as markdown."""
    report = f"""# 📊 Weekly Fitness Report

**Period:** {summary['period']}  
**Days Tracked:** {summary['days_tracked']}

---

## 🏃‍♂️ Activity Summary

- **Steps:** {summary['avg_steps']:,} avg/day ({summary['total_steps']:,} total)
- **Distance:** {summary['avg_distance']} km avg/day ({summary['total_distance']} km total)
- **Calories:** {summary['avg_calories']:,} avg/day ({summary['total_calories']:,} total)
- **Active Minutes:** {summary['avg_active_minutes']} avg/day ({summary['total_active_minutes']} total)

**Goal Progress:**
- 🎯 Step Goal (10k): {summary['days_hit_step_goal']}/{summary['days_tracked']} days

---

## 💤 Sleep & Recovery

- **Sleep Duration:** {summary['avg_sleep_hours']} hours/night avg
- **Sleep Quality:** {summary['avg_sleep_score']}/100 avg score
- **Goal Progress:** {summary['days_hit_sleep_goal']}/{summary['days_tracked']} nights with 7.5+ hours

---

## ❤️ Health Metrics

- **Resting Heart Rate:** {summary['avg_resting_hr']} bpm avg
- **Stress Level:** {summary['avg_stress']} avg
- **Low Stress Days:** {summary['days_low_stress']}/{summary['days_tracked']} days

---

## ⚖️ Body Composition

- **Weight:** {summary['current_weight']} kg
- **Body Fat:** {summary['current_body_fat']}%
- **Muscle Mass:** {summary['current_muscle_mass']} kg
- **Waist:** {summary['current_waist_inches']} inches ({summary['current_waist_cm']} cm){' ⚠️ Manual measurement needed' if not summary['current_waist_inches'] else ''}

---

## 💡 Key Insights

"""
    
    for insight in insights:
        report += f"{insight}\n"
    
    report += "\n---\n\n## 🎯 Recommendations for Next Week\n\n"
    
    if recommendations:
        for rec in recommendations:
            report += f"{rec}\n"
    else:
        report += "✅ Keep up the great work! Maintain current habits.\n"
    
    report += "\n---\n\n*Generated automatically from Garmin Connect data*\n"
    
    return report

def main():
    csv_file = Path.home() / "clawd" / "fitness" / "garmin_data.csv"
    
    if not csv_file.exists():
        print(f"Error: CSV file not found: {csv_file}")
        sys.exit(1)
    
    # Load data
    data = load_garmin_data(csv_file)
    week_data = get_week_data(data, days=7)
    
    if not week_data:
        print("No data found for the last 7 days")
        sys.exit(1)
    
    # Generate summary
    summary = generate_weekly_summary(week_data)
    insights, recommendations = generate_insights(summary, week_data)
    
    # Generate report
    report = format_markdown_report(summary, insights, recommendations)
    
    # Save to file
    report_file = Path.home() / "clawd" / "fitness" / "weekly_report.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"✅ Weekly report generated: {report_file}")
    print("\n" + report)

if __name__ == "__main__":
    main()
