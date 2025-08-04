import streamlit as st
from datetime import datetime
from collections import defaultdict



def group_by_type(array, type_name):
    grouped = defaultdict(list)
    for x in array:
        grouped[x[type_name]].append(x)
    return grouped


def process_content(content):
    return "" if content is None else str(content).replace("\n", "<br>")


def format_time(time):
    return (
        None
        if time is None
        else datetime.strptime(time, "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")
    )


def title(title):
    html = f"""
    <h5 style='margin-top: 1em; color: #ffffff; font-weight: bold;'>{title}</h5>
    """
    st.markdown(html, unsafe_allow_html=True)


def title_small(title):
    html = f"""
    <h6 style='margin-top: 1em; color: #ffffff; font-weight: bold;'>{title}</h6>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_vertical_table(kv_pairs):
    html = f"""
    <table style='width:100%; border-collapse:collapse; font-size:15px; background-color: #1e1e1e; color: #f0f0f0;'>
    """
    for label, value in kv_pairs:
        html += f"<tr>"
        html += f"<td style='border:1px solid #444; padding:10px; width:30%; background-color: #333; color: #ffffff; font-weight:bold;'>{label}</td>"
        html += f"<td style='border:1px solid #444; padding:10px; background-color: #1e1e1e;'>{process_content(value)}</td>"
        html += "</tr>"
    html += "</table><br/>"
    st.markdown(html, unsafe_allow_html=True)


def render_horizontal_table(headers, rows):
    html = f"""
    <table style='width:100%; border-collapse:collapse; font-size:15px; background-color: #1e1e1e; color: #f0f0f0;'>
        <thead>
            <tr style="background-color: #333;">
                {''.join(f'<th style="border:1px solid #444; padding:10px; font-weight:bold;">{h}</th>' for h in headers)}
            </tr>
        </thead>
        <tbody>
    """
    for i, row in enumerate(rows):
        bg_color = "#1e1e1e" if i % 2 == 0 else "#2a2a2a"
        html += f"<tr style='background-color:{bg_color};'>"
        html += "".join(
            f'<td style="border:1px solid #444; padding:10px;">{process_content(cell)}</td>'
            for cell in row
        )
        html += "</tr>"
    html += """
        </tbody>
    </table><br/>
    """
    st.markdown(html, unsafe_allow_html=True)
