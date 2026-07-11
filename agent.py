import os
import sys
import subprocess

def force_install(package_name):
    try:
        __import__(package_name)
    except ImportError:
        print(f"⚠️ {package_name} module missing. Initiating forced install...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} successfully installed and loaded!")

force_install("pandas")
force_install("openai")
#The openai module is used to read and understand human conversations within the project log, thus converting sentiments into structured data(for risk analysis).
#It also gives intelligent error resilience by using semantic reasoning to bypass unparseable cells and does not crash on error-prone mathematical formulas.


import pandas as pd
from openai import OpenAI

# Initialize the AI client
client = OpenAI("OPEN_API_KEY")

def read_project_data(summary_path, details_path, comments_path=None):
    context_str = ""
    
    # Process Summary File
    try:
        if os.path.exists(summary_path):
            df_sum = pd.read_csv(summary_path, header=None)
            df_sum.columns = ['Metric', 'Value']
            context_str += f"### SUMMARY METRICS ({summary_path}):\n"
            context_str += df_sum.to_string(index=False) + "\n\n"
        else:
            context_str += f"### SUMMARY METRICS ({summary_path}): [File not found]\n\n"
    except Exception as e:
        context_str += f"### SUMMARY METRICS ({summary_path}): [Error reading: {e}]\n\n"

    # Process Granular Plan File
    try:
        if os.path.exists(details_path):
            df_plan = pd.read_csv(details_path)
            context_str += f"### GRANULAR PLAN SAMPLE ({details_path}):\n"
            context_str += df_plan.head(30).to_string(index=False) + "\n\n"
        else:
            context_str += f"### GRANULAR PLAN SAMPLE ({details_path}): [File not found]\n\n"
    except Exception as e:
        context_str += f"### GRANULAR PLAN SAMPLE ({details_path}): [Error reading: {e}]\n\n"
        
    # Process Comments File
    if comments_path:
        try:
            if os.path.exists(comments_path):
                df_comm = pd.read_csv(comments_path)
                context_str += f"### STAKEHOLDER COMMENTS LOG ({comments_path}):\n"
                context_str += df_comm.to_string(index=False) + "\n\n"
            else:
                context_str += f"### STAKEHOLDER COMMENTS LOG ({comments_path}): [File not found]\n\n"
        except Exception as e:
            context_str += f"### STAKEHOLDER COMMENTS LOG ({comments_path}): [Error reading: {e}]\n\n"
            
    return context_str

def run_pmo_agent(project_name, summary_file, details_file, comments_file=None):
    print(f"\n Agent executing analysis for: {project_name}...")
    raw_data_context = read_project_data(summary_file, details_file, comments_file)
    
    system_prompt = (
        "You are an expert Project Management Officer (PMO) Agent. Your task is to analyze project data "
        "and determine an accurate RAG status using strict pessimistic logic: if any single pillar "
        "exhibits critical failure, default the entire project status to Red."
    )
    
    user_prompt = f"""
    Analyze the following extracted project tracking data. 
    Note: Real-world data is messy; bypass strings like '#UNPARSEABLE' by relying on completion ratios and comment sentiment.

    {raw_data_context}

    Apply these core evaluation rules from our framework:
    1. Hard Metric Domination: If an explicit 'Schedule Health' row is Red, prioritize it.
    2. Volatility Check: High quantities of 'Not Started' tasks deep in a timeline warrant an Amber warning.
    3. Sentiment Engine: Scan stakeholder comments for words like 'pending', 'impacted', 'remain to complete'. Downgrade health if functional bottlenecks exist.

    Provide your response in this exact format:
    PROJECT: [Project Name]
    FINAL AUTOMATED RAG STATUS: [GREEN / AMBER / RED]
    
    PLAIN-ENGLISH REASONING:
    [Provide clear, executive-ready sentences detailing the exact numbers and text logs that led to this choice.]
    
    KEY RISKS & UNRESOLVED BLOCKERS:
    - [Item 1]
    - [Item 2]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Agent Runtime Error: {str(e)}"

if __name__ == "__main__":
    # Project A: Outokumpu S2P Project
    outokumpu_report = run_pmo_agent(
        project_name="Outokumpu S2P Project (Managed by Aftab Hashambhai)",
        summary_file="S2P Project .xlsx - Summary.csv",
        details_file="S2P Project .xlsx - Outokumpu- S2P Project.csv",
        comments_file="S2P Project .xlsx - Comments.csv"
    )
    print(outokumpu_report)
    print("\n" + "="*80 + "\n")

    # Project B: UniSan S2P Project
    unisan_report = run_pmo_agent(
        project_name="UniSan S2P Project (Managed by Rajat Bothra)",
        summary_file="Project Plan B .xlsx - Summary.csv",
        details_file="Project Plan B .xlsx - Project Plan.csv",
        comments_file=None
    )
    print(unisan_report)
