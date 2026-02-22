import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings

from assessment.models import DigitalAddictionAssessment
from ml.preprocessing import preprocess_assessment

import plotly.graph_objects as go
from plotly.offline import plot

from collections import Counter

@login_required
def assessment_result_page(request, pk):
    # Only allow the logged-in user to access their assessment
    assessment = get_object_or_404(
        DigitalAddictionAssessment,
        pk=pk,
        student=request.user
    )
    return render(
        request,
        "students/assessment_result.html",
        {"assessment": assessment}
    )

def generate_das_by_age_chart_interactive(assessments):
    """
    Generates an interactive Plotly bar chart of average DAS (0-100%)
    across age groups, showing the number of assessments per group.
    
    Returns HTML div string to embed in the template.
    """

    # Custom age groups
    age_groups = {
        "15-20": [],
        "21-25": [],
        "26-30": [],
        "31-35": [],
        "36-40": [],
        "41-45": [],
        "46+": [],
    }

    # Normalization parameters for DAS
    min_score, max_score = 1, 5  # 1–5 scale

    for assessment in assessments:
        numeric_features, _ = preprocess_assessment(assessment, fit=False)
        age = numeric_features.get("age")
        das = numeric_features.get("DAS_weighted", 0)

        # Convert Series / NumPy types to scalar
        if hasattr(age, "item"):
            age = age.item()
        if hasattr(das, "item"):
            das = das.item()

        if age is None:
            continue

        try:
            age = int(age)
            das = float(das)
        except (ValueError, TypeError):
            continue

        # Normalize DAS to 0-100%
        das_normalized = ((das - min_score) / (max_score - min_score)) * 100
        das_normalized = min(max(das_normalized, 0), 100)

        # Assign to age group
        if 15 <= age <= 20:
            age_groups["15-20"].append(das_normalized)
        elif 21 <= age <= 25:
            age_groups["21-25"].append(das_normalized)
        elif 26 <= age <= 30:
            age_groups["26-30"].append(das_normalized)
        elif 31 <= age <= 35:
            age_groups["31-35"].append(das_normalized)
        elif 36 <= age <= 40:
            age_groups["36-40"].append(das_normalized)
        elif 41 <= age <= 45:
            age_groups["41-45"].append(das_normalized)
        else:
            age_groups["46+"].append(das_normalized)

    # Compute averages and counts
    labels = list(age_groups.keys())
    avg_scores = [round(np.mean(values), 1) if values else 0 for values in age_groups.values()]
    counts = [len(values) for values in age_groups.values()]

    # Create interactive bar chart
    fig = go.Figure(
        data=go.Bar(
            x=labels,
            y=avg_scores,
            text=[f"{score} ({count})" for score, count in zip(avg_scores, counts)],
            textposition='auto',
            marker_color='#4a90e2',
            hovertemplate=
                'Age Group: %{x}<br>'+
                'Average DAS: %{y:.1f}%<br>'+
                'Number of assessments: %{text}<extra></extra>'
        )
    )

    fig.update_layout(
        title="Average Digital Addiction Score by Age Group (%)",
        xaxis_title="Age Group",
        yaxis_title="DAS (Normalized 0–100%)",
        yaxis=dict(range=[0, 100]),
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40)
    )

    # Return HTML div string
    chart_div = plot(fig, output_type='div', include_plotlyjs=False)
    return chart_div

# Mapping numeric values to labels
night_map = {
    "Never": 0,
    "<30m": 0.25,
    "30–60m": 0.75,
    "1–2h": 1.5,
    ">2h": 3
}

# Reverse mapping for dynamic chart
reverse_night_map = {v: k for k, v in night_map.items()}

def create_late_night_pie_chart(assessments):
    """
    Create a dynamic pie chart for Night-time Phone Usage.
    Maps numeric preprocessed values back to original labels.
    """
    # Fixed label order and colors
    labels = ["Never", "<30m", "30–60m", "1–2h", ">2h"]
    colors = ["#1f77b4", "#d62728", "#ff7f0e", "#2ca02c", "#9467bd"]

    # Collect raw numeric values from assessments
    raw_values = []
    for assessment in assessments:
        numeric_features, _ = preprocess_assessment(assessment, fit=False)
        night_use_value = numeric_features.get("night_phone_use", 0)
        if hasattr(night_use_value, 'iloc'):
            night_use_value = night_use_value.iloc[0]

        raw_values.append(night_use_value)

    # Map numeric values back to labels
    mapped_labels = [reverse_night_map.get(val, "Never") for val in raw_values]

    # Count occurrences for each label
    count_data = Counter(mapped_labels)
    values = [count_data.get(label, 0) for label in labels]

    # Handle empty dataset
    total_responses = sum(values)
    if total_responses == 0:
        values = [1] + [0]*(len(labels)-1)

    # Create pie chart
    pie_fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.3,
        sort=False,
        marker=dict(colors=colors),
        textinfo='label+percent',
        insidetextorientation='radial',
        hoverinfo='label+percent+value'
    ))

    pie_fig.update_layout(
        title=f"Night-time phone use after lights-off<br>{total_responses} responses"
    )

    # Convert to HTML div
    pie_div = plot(pie_fig, output_type='div', include_plotlyjs=True)
    return pie_div


from collections import Counter


# Numeric-to-label mapping
night_map = {
    "Never": 0,
    "<30m": 0.25,
    "30–60m": 0.75,
    "1–2h": 1.5,
    ">2h": 3
}
reverse_night_map = {v: k for k, v in night_map.items()}

# Custom age groups
age_groups = {
    "15-20": (15, 20),
    "21-25": (21, 25),
    "26-30": (26, 30),
    "31-35": (31, 35),
    "36-40": (36, 40),
    "41-45": (41, 45),
    "46+": (46, 200)  # assuming 200 as max age
}
age_group_order = list(age_groups.keys())

def get_age_group(age):
    for group, (low, high) in age_groups.items():
        if low <= age <= high:
            return group
    return "Unknown"

def create_night_phone_by_age_percentage_bar_chart(assessments):
    """
    Creates a stacked bar chart showing percentage distribution of night-time phone use
    across custom age groups (15-20, 21-25, …, 46+).
    """
    # Collect data
    data = []
    for assessment in assessments:
        numeric_features, _ = preprocess_assessment(assessment, fit=False)
        night_use_value = numeric_features.get("night_phone_use", 0)
        age = getattr(assessment, "age", None)
        
        if hasattr(night_use_value, 'iloc'):
            night_use_value = night_use_value.iloc[0]
        if hasattr(age, 'iloc'):
            age = age.iloc[0]
        
        night_label = reverse_night_map.get(night_use_value, "Never")
        age_group = get_age_group(age) if age is not None else "Unknown"
        data.append({"age_group": age_group, "night_use": night_label})
    
    df = pd.DataFrame(data)

    # Aggregate counts
    grouped_counts = df.groupby(["age_group", "night_use"]).size().unstack(fill_value=0)
    grouped_counts = grouped_counts.reindex(columns=list(night_map.keys()), fill_value=0)
    grouped_counts = grouped_counts.reindex(index=age_group_order, fill_value=0)

    # Convert counts to percentages
    percentages = grouped_counts.div(grouped_counts.sum(axis=1), axis=0) * 100

    # Create stacked bar chart
    colors = ["#1f77b4", "#d62728", "#ff7f0e", "#2ca02c", "#9467bd"]
    fig = go.Figure()
    for i, night_label in enumerate(night_map.keys()):
        fig.add_trace(go.Bar(
            x=percentages.index,
            y=percentages[night_label],
            name=night_label,
            marker_color=colors[i],
            text=percentages[night_label].round(1).astype(str) + '%',
            textposition='inside'
        ))

    fig.update_layout(
        barmode='stack',
        title="Night-time Phone Use by Age Group (Percentage)",
        xaxis_title="Age Group",
        yaxis_title="Percentage of Responses",
        legend_title="Night Phone Use",
        template="plotly_white"
    )

    # Convert to HTML div for Django
    bar_div = plot(fig, output_type='div', include_plotlyjs=True)
    return bar_div




def create_platform_bar_chart(assessments):
    """
    Creates a bar chart showing the count of users per platform.
    Platforms considered: YouTube, TikTok, Instagram, Facebook, WhatsApp, X, Snapchat, Gaming
    """
    # Full platform list in desired order
    platform_order = ["YouTube", "TikTok", "Instagram", "Facebook",
                      "WhatsApp", "X", "Snapchat", "Gaming"]

    # Collect all platforms used
    all_platforms = []
    for assessment in assessments:
        # Each assessment should have a 'platforms' attribute (list of platform names)
        platforms = getattr(assessment, "platforms", [])
        if platforms is None:
            platforms = []
        # If platforms is a Pandas series, get the first value
        if hasattr(platforms, 'iloc'):
            platforms = platforms.iloc[0]
        # Extend list
        all_platforms.extend(platforms)

    # Count occurrences of each platform
    platform_counts = Counter(all_platforms)
    counts_ordered = [platform_counts.get(p, 0) for p in platform_order]

    # Create bar chart
    fig = go.Figure(go.Bar(
        x=platform_order,
        y=counts_ordered,
        marker_color="#1f77b4",
        text=counts_ordered,
        textposition='auto'
    ))

    fig.update_layout(
        title="Platform Usage Counts",
        xaxis_title="Platform",
        yaxis_title="Number of Users",
        template="plotly_white"
    )

    # Convert to HTML div for Django template
    platform_bar_div = plot(fig, output_type='div', include_plotlyjs=True)
    return platform_bar_div



def create_platform_bar_chart_by_gender(assessments):
    """
    Creates an interactive grouped bar chart showing
    platform usage count segmented by gender.

    Platforms considered:
    YouTube, TikTok, Instagram, Facebook, WhatsApp, X, Snapchat, Gaming
    """

    # Platform order (fixed)
    platform_order = [
        "YouTube", "TikTok", "Instagram", "Facebook",
        "WhatsApp", "X", "Snapchat", "Gaming"
    ]

    # Supported genders (normalize if needed)
    gender_order = ["Male", "Female"]

    # Initialize counter: gender -> platform -> count
    gender_platform_counts = {
        gender: Counter() for gender in gender_order
    }

    # Collect data
    for assessment in assessments:
        gender = getattr(assessment, "gender", None)
        if gender not in gender_order:
            continue

        platforms = getattr(assessment, "platforms", [])
        if platforms is None:
            platforms = []

        # Handle pandas Series case
        if hasattr(platforms, "iloc"):
            platforms = platforms.iloc[0]

        for platform in platforms:
            if platform in platform_order:
                gender_platform_counts[gender][platform] += 1

    # Build Plotly traces
    traces = []
    for gender in gender_order:
        counts = [gender_platform_counts[gender].get(p, 0) for p in platform_order]

        traces.append(
            go.Bar(
                x=platform_order,
                y=counts,
                name=gender,
                text=counts,
                textposition="auto"
            )
        )

    # Create figure
    fig = go.Figure(data=traces)

    fig.update_layout(
        title="Platform Usage by Gender",
        xaxis_title="Platform",
        yaxis_title="Number of Users",
        barmode="group",
        template="plotly_white",
        legend_title="Gender"
    )

    # Convert to HTML div for Django template
    platform_gender_bar_div = plot(
        fig,
        output_type="div",
        include_plotlyjs=True
    )

    return platform_gender_bar_div




def create_self_rated_digital_addiction_pie_chart(assessments):
    """
    Google-Forms–style pie chart for self-rated digital addiction risk.
    Handles snake_case DB values correctly.
    """

    # 🔹 Mapping: DB value -> Display label
    risk_label_map = {
        "not_at_risk": "Not at risk",
        "mild": "Mild",
        "moderate": "Moderate",
        "severe": "Severe",
    }

    # Fixed display order
    risk_order = ["Not at risk", "Mild", "Moderate", "Severe"]

    # Google Forms colors
    color_map = {
        "Not at risk": "#3366CC",
        "Mild": "#DC3912",
        "Moderate": "#FF9900",
        "Severe": "#109618",
    }

    normalized_risks = []

    for assessment in assessments:
        raw_risk = getattr(assessment, "self_rated_da", None)

        if raw_risk:
            raw_risk = str(raw_risk).strip().lower()
            if raw_risk in risk_label_map:
                normalized_risks.append(risk_label_map[raw_risk])

    risk_counts = Counter(normalized_risks)
    counts_ordered = [risk_counts.get(risk, 0) for risk in risk_order]
    total_responses = sum(counts_ordered)

    if total_responses == 0:
        return "<p><strong>No self-rated digital addiction data available.</strong></p>"

    fig = go.Figure(
        go.Pie(
            labels=risk_order,
            values=counts_ordered,
            textinfo="percent",
            textposition="inside",
            marker=dict(
                colors=[color_map[r] for r in risk_order],
                line=dict(color="white", width=2),
            ),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "%{value} responses<br>"
                "%{percent}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=dict(
            text=f"Self-rated digital addiction risk<br><sup>{total_responses} responses</sup>",
            x=0,
            xanchor="left",
        ),
        legend=dict(x=1.02, y=0.5),
        template="plotly_white",
        margin=dict(t=80, r=120, l=40, b=40),
    )

    self_rated_pie_chart_div = plot(
        fig,
        output_type="div",
        include_plotlyjs=False,
    )

    return self_rated_pie_chart_div

