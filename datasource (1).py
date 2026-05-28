# %% [markdown]
import sys
#!{sys.executable} -m pip install --upgrade --force-reinstall --no-cache-dir python-dotenv langchain-core langchain-groq pandas requests
#%%
#!python -m pip install --upgrade pip
# %%
import os
import json
import re
import xml.etree.ElementTree as ET
import pandas as pd
import requests
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

def extract_body_with_requests(real_url):
    try:
        if not real_url:
            return "Missing URL"
            
        browser_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
            
        res = requests.get(real_url, headers=browser_headers, timeout=8)
        if res.status_code != 200:
            return f"Network Error Status {res.status_code}"
            
        clean_html = re.sub(r'<script.*?</script>|<style.*?</style>', '', res.text, flags=re.DOTALL)
        text_content = re.sub(r'<[^>]+>', ' ', clean_html)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        return text_content[:1500] if len(text_content) > 100 else "Content body too short"
    except Exception as e:
        return f"Fetch Error: {str(e)}"

def run_market_intelligence_pipeline():
    """
    Wraps the backend extraction and analysis pipeline so that it can be cleanly
    triggered on-demand by the Streamlit user interface without causing compilation loops.
    """
    load_dotenv()
    groq_key = os.getenv("GROQ_API_KEY")
    
    if not groq_key:
        raise ValueError("❌ GROQ_API_KEY is missing from your environment configuration.")
        
    os.environ['GROQ_API_KEY'] = groq_key

    # 1. Harvest Dataset from RSS
    url = "https://phys.org/rss-feed/technology-news/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    response = requests.get(url, headers=headers, timeout=10)
    articles_list = []
    
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        for item in root.findall('.//item')[:5]:
            title = item.find('title').text if item.find('title') is not None else None
            link = item.find('link').text if item.find('link') is not None else None
            summary = item.find('description').text if item.find('description') is not None else None
            articles_list.append({"title": title, "link": link, "summary": summary})
        df = pd.DataFrame(articles_list)
    else:
        return pd.DataFrame()  # Return empty DataFrame on network initialization errors

    if not df.empty:
        # 2. Align data payloads
        df["raw_body_content"] = df["link"].apply(extract_body_with_requests)
        df["summary_cleaned"] = df["summary"].fillna("").str.replace(r'[^\n\w\s\(\)\.,]', '', regex=True)
        
        df = df.rename(columns={
            "title": "Market_Intelligence_Headline",
            "summary_cleaned": "Scraped_Text_Payload"
        })

        # 3. Setup LangChain Engine
        llm = ChatGroq(
            temperature=0.1,
            model_name="llama-3.3-70b-versatile",
            groq_api_key=groq_key
        )

        system_message = (
            "You are an Elite Market Intelligence Agent specializing in risk analysis.\n"
            "Analyze the provided raw article text and determine if it represents a market threat.\n"
            "Your entire response must be a single, valid JSON object and absolutely nothing else.\n"
            "Do NOT wrap your response in markdown code blocks like ```json ... ```.\n"
            "The JSON keys must be exactly:\n"
            "- 'market_threat_level': (Must be exactly 'High', 'Medium', or 'Low')\n"
            "- 'threat_score': (An integer from 1 to 10 based on severity)\n"
            "- 'key_vulnerability': (A clear 1-sentence summary of the business risk/problem found)\n"
        )

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("user", "Analyze this market intel text:\n\n{article_text}")
        ])

        agent_chain = prompt_template | llm | StrOutputParser()

        def analyze_row_with_agent(text_content):
            if not text_content or len(str(text_content).strip()) < 10:
                return {"market_threat_level": "Unknown", "threat_score": 0, "key_vulnerability": "Skipped due to empty extraction bounds."}
            try:
                response_text = agent_chain.invoke({"article_text": text_content}).strip()
                if "{" in response_text:
                    start_idx = response_text.find("{")
                    end_idx = response_text.rfind("}") + 1
                    if start_idx != -1 and end_idx != -1:
                        response_text = response_text[start_idx:end_idx]
                return json.loads(response_text)
            except Exception as e:
                return {"market_threat_level": "Medium", "threat_score": 5, "key_vulnerability": f"Parsing issue: {str(e)}"}

        # 4. Process data via agent loop
        ai_results = [analyze_row_with_agent(body) for body in df["Scraped_Text_Payload"]]
        df_ai = pd.DataFrame(ai_results)
        
        # Concat original data metrics along with agent predictions
        final_enriched_df = pd.concat([df.reset_index(drop=True), df_ai.reset_index(drop=True)], axis=1)
        return final_enriched_df
        
    return pd.DataFrame()
# %%
