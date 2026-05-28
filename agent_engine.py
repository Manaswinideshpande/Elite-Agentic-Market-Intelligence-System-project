import streamlit as st
import pandas as pd
import os
# Securely import the pipeline function from your datasource file
from datasource import run_market_intelligence_pipeline

# 1. Page Configuration Setup
st.set_page_config(
    page_title="Elite Market Intelligence Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Main Title and UI Subheaders
st.title("🎯 Elite Agentic Market Intelligence System")
st.markdown("This application monitors technology threat matrix signals using live RSS data streams and evaluates systemic business operational risks using `llama-3.3-70b-versatile` intelligence.")
st.divider()

# 3. Sidebar Infrastructure (Status Metrics & Controls)
st.sidebar.header("Configuration & Control")
st.sidebar.markdown("Click the execution trigger below to fetch current operational risk feeds.")

# Diagnostic Key Checks inside UI Frame
if not os.getenv("GROQ_API_KEY") and not os.path.exists(".env"):
    st.sidebar.error("⚠️ GROQ_API_KEY Missing! Please configure your workspace environment .env properties file.")
else:
    st.sidebar.success("🔒 System Authentication Properties Active.")

# Trigger Button Setup
start_pipeline = st.sidebar.button("🔄 Execute Intel Pipeline Run", use_container_width=True)

# 4. App Execution Logical Control Loop
if start_pipeline:
    st.subheader("⚙️ Processing Active Analytics Execution Pipeline Tracking Tracks")
    
    # Progress feedback spinners
    with st.status("Running complete agent loop steps...", expanded=True) as status:
        st.write("Harvesting data frameworks from live RSS streams...")
        try:
            # Running the wrapped pipeline from datasource.py safely
            enriched_data_matrix = run_market_intelligence_pipeline()
            
            if not enriched_data_matrix.empty:
                status.update(label="🚀 Pipeline Complete! Matrix Analyzed Successfully.", state="complete", expanded=False)
                
                # Create structured data display layouts inside the UI view metric summaries
                st.subheader("📊 Enriched Threat Intelligence Matrix")
                
                # Format Threat Metric badges or scores layout side by side
                high_threats_count = len(enriched_data_matrix[enriched_data_matrix["market_threat_level"] == "High"])
                med_threats_count = len(enriched_data_matrix[enriched_data_matrix["market_threat_level"] == "Medium"])
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Intel Documents Tracked", len(enriched_data_matrix))
                m2.metric("Critical Action Items (High Risk)", high_threats_count, delta_color="inverse")
                m3.metric("Medium Risk Warnings", med_threats_count)
                
                st.markdown("### 📋 Complete Analysis Breakdown View Matrix DataFrame")
                
                # Tailor interactive DataFrame presentation layouts columns
                presented_dataframe_view = enriched_data_matrix[[
                    "Market_Intelligence_Headline", 
                    "market_threat_level", 
                    "threat_score", 
                    "key_vulnerability",
                    "link"
                ]]
                
                # Apply conditional highlight coloring properties over columns for visual polish
                def color_threat_level(val):
                    if val == "High":
                        return "background-color: #ffcccc; color: #cc0000; font-weight: bold;"
                    elif val == "Medium":
                        return "background-color: #ffe6cc; color: #995c00;"
                    elif val == "Low":
                        return "background-color: #e6ffcc; color: #336600;"
                    return ""

                # FIXED: Moved out of the function block scope back to the main layout track
                styled_df = presented_dataframe_view.style.map(color_threat_level, subset=["market_threat_level"])
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
                
                # 5. Expanding detailed itemized metric cards layout view iteration mapping
                st.markdown("### 🔍 Itemized Agent Vulnerability Summaries")
                for index, row in enriched_data_matrix.iterrows():
                    # Decide emoji based on risk category
                    badge_emoji = "🔴" if row["market_threat_level"] == "High" else "🟡" if row["market_threat_level"] == "Medium" else "🟢"
                    
                    with st.expander(f"{badge_emoji} Headline: {row['Market_Intelligence_Headline']} (Score: {row['threat_score']}/10)"):
                        st.markdown(f"**Market Threat Assessment Rank:** `{row['market_threat_level']}`")
                        st.markdown(f"**Identified Operational Key Vulnerability:**")
                        st.info(row['key_vulnerability'])
                        st.markdown(f"[Read Original Publication Track Source Link]({row['link']})")
                        
            else:
                status.update(label="❌ Matrix Generation Engine Halted.", state="error")
                st.error("Data tracking process failed. Please check your internet connectivity or key authentications and try again.")
                
        except Exception as e:
            status.update(label="❌ Critical Script Exception Crash Encountered.", state="error")
            st.exception(e)
else:
    # Landing page message state before user runs anything
    st.info("💡 Application Standing By. Please select 'Execute Intel Pipeline Run' from the sidebar panel to trigger active tracking cycles.")