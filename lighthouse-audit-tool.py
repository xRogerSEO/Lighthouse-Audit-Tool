import streamlit as st
import pandas as pd
import asyncio
import aiohttp
from datetime import date

# Function to read URLs from a file
def read_urls_from_file(uploaded_file):
    urls = []
    with uploaded_file:
        urls = uploaded_file.readlines()
    return [url.strip() for url in urls]

# Definition of analysis type, date, analysis location, and API key
category = 'performance'
today = date.today().strftime("%Y-%m-%d")
locale = 'en'
key = 'get your api key here: https://developers.google.com/speed/docs/insights/v5/get-started'

# Function to Extract API Data
async def webcorevitals(session, url, device, category, today):
    # Remaining code unchanged

# Function to run the Requests and build the DataFrame with Desktop and Mobile data
async def main(uploaded_file):
    async with aiohttp.ClientSession() as session:
        tasks = []
        url_list = read_urls_from_file(uploaded_file)
        for url in url_list:
            tasks.append(webcorevitals(session, url, 'mobile', category, today))
            tasks.append(webcorevitals(session, url, 'desktop', category, today))

        results = await asyncio.gather(*tasks)

        # Create an Empty DataFrame to Store the Results
        df_final = pd.concat(results, ignore_index=True)
        
        # Save the DataFrame to an Excel file
        df_final.to_excel('output.xlsx', index=False)
        st.success("Audit completed. Results saved to output.xlsx.")

if __name__ == '__main__':
    st.title("Lighthouse Audit Tool")

    uploaded_file = st.file_uploader("Upload a file", type=['txt', 'csv'])
    if uploaded_file is not None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main(uploaded_file))
