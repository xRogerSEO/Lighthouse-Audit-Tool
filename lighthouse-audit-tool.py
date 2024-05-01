!pip install aiohttp
import aiohttp
import asyncio
import pandas as pd
from datetime import date
import streamlit as st

# Function to read URLs from a file
def read_urls_from_file(file_path):
    urls = []
    with open(file_path, 'r') as file:
        for line in file:
            urls.append(line.strip())  
    return urls

# Function to Extract API Data
async def webcorevitals(session, url, device, category, today, key):
    headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
    }

    async with session.get(
        f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={key}&strategy={device}&category={category}&locale=en",
        headers=headers
    ) as response:
        data = await response.json()

        print('Running URL #', url, device)

        test = url
        date = today
        
        try:
            data_loading = data['loadingExperience']
            data = data['lighthouseResult']
        except KeyError:
            print('No Values')
            data = 'No Values.'

        try:
            fcp = data['audits']['first-contentful-paint']['displayValue']
        except KeyError:
            print('No Values')
            fcp = 0

        try:
            lcp = data['audits']['largest-contentful-paint']['displayValue']
        except KeyError:
            print('No Values')
            lcp = 0

        try:
            cls = data['audits']['cumulative-layout-shift']['displayValue']
        except KeyError:
            print('No Values')
            cls = 0

        try:
            si = data['audits']['speed-index']['displayValue']
        except KeyError:
            print('No Values')
            si = 0

        try:
            tti = data['audits']['interactive']['displayValue']
        except KeyError:
            print('No Values')
            tti = 0

        try:
            bytes = data['audits']['total-byte-weight']['numericValue']
        except KeyError:
            print('No Values')
            bytes = 0
            
        try:
            tbt = data['audits']['total-blocking-time']['displayValue']
        except KeyError:
            print('No Values')
            tbt = 0
            
        try:
            score = data['categories']['performance']['score']
        except KeyError:
            print('No Values')
            
        try:
            fid = data_loading["metrics"]["FIRST_INPUT_DELAY_MS"]["percentile"]
        except KeyError:
            print('No Values')
            
        try:
            inp = data_loading["metrics"]["INTERACTION_TO_NEXT_PAINT"]["percentile"]
        except KeyError:
            print('No Values')
            
        try:
            ttfb = data_loading["metrics"]["EXPERIMENTAL_TIME_TO_FIRST_BYTE"]["percentile"]
        except KeyError:
            print('No Values')

        values = [test, score, fid, inp, ttfb, fcp, si, lcp, tti, tbt, cls, bytes, date, device]

        df_score = pd.DataFrame(values)

        df_score = df_score.transpose()

        df_score.columns = ['URL', 'Score', 'FID', 'INP', 'TTFB', 'FCP', 'SI', 'LCP', 'TTI', 'TBT', 'CLS', 'Size in MB', 'Date', 'Device']

        df_score['FID'] = df_score['FID'].astype(str).str.replace(r',', '').astype(float)
        df_score['INP'] = df_score['INP'].astype(str).str.replace(r',', '').astype(float)
        df_score['TTFB'] = df_score['TTFB'].astype(float) / 1000
        df_score['LCP'] = df_score['LCP'].astype(str).str.replace(r's', '').astype(float)
        df_score['FCP'] = df_score['FCP'].astype(str).str.replace(r's', '').astype(float)
        df_score['SI'] = df_score['SI'].astype(str).str.replace(r's', '').astype(float)
        df_score['TTI'] = df_score['TTI'].astype(str).str.replace(r's', '').astype(float)
        df_score['TBT'] = df_score['TBT'].astype(str).str.replace(r'ms', '').astype(float)
        df_score['Score'] = df_score['Score'].astype(float) * 100
        df_score['CLS'] = df_score['CLS'].astype(float)
        df_score['Size in MB'] = df_score['Size in MB'] / (1024 * 1024)
        df_score['Device'] = device
        
        df_score = df_score[['Date', 'URL', 'Score', 'FID', 'INP', 'TTFB', 'FCP', 'SI', 'LCP', 'TTI', 'TBT', 'CLS', 'Size in MB', 'Device']]
        df_score.columns = ['Date', 'URL', 'Score', 'First Input Delay (FID)', 'Interaction to Next Paint (INP)', 'Time to First Byte (TTFB)', 'First Contentful Paint (FCP)', 'Speed Index (SI)', 'Largest Contentful Paint (LCP)', 'Time to Interactive (TTI)', 'Total Blocking Time (TBT)', 'Cumulative Layout Shift (CLS)', 'Size in MB', 'Device']
       
        return df_score

# Function to run the Requests and build the DataFrame with Desktop and Mobile data
async def main(uploaded_file, api_key):
    urls = read_urls_from_file(uploaded_file)
    today = date.today().strftime("%Y-%m-%d")
    category = 'performance'

    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(webcorevitals(session, url, 'mobile', category, today, api_key))
            tasks.append(webcorevitals(session, url, 'desktop', category, today, api_key))

        results = await asyncio.gather(*tasks)

        df_final = pd.concat(results, ignore_index=True)
        
        st.write(df_final)  # Write DataFrame to Streamlit app
        
        # Save the DataFrame to an Excel file (optional)
        # df_final.to_excel('output.xlsx', index=False)

# Streamlit app
def main_streamlit():
    st.title("Lighthouse Audit Tool")
    uploaded_file = st.file_uploader("Upload a file", type=["txt", "csv"])

    if uploaded_file is not None:
        api_key = st.text_input("Enter your Google PageSpeed Insights API key")
        if st.button("Run Analysis"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main(uploaded_file, api_key))

if __name__ == "__main__":
    main_streamlit()
