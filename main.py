import time
import json
import streamlit as st
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import matplotlib.pyplot as plt
import numpy as np
import chromedriver_autoinstaller


def convert_views_to_numeric(views_str):
                views_str = views_str.lower().replace(" views", "").strip()
                if 'k' in views_str:
                    return float(views_str.replace('k', '')) * 1000
                elif 'm' in views_str:
                    return float(views_str.replace('m', '')) * 1000000
                else:
                    try:
                        return float(views_str)
                    except ValueError:
                        return 0

def get_video_results(search_term, count):
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(f'https://www.youtube.com/results?search_query={"+".join(search_term.split())}')

    youtube_data = []

    previous_height = driver.execute_script("return document.documentElement.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)

        current_height = driver.execute_script("return document.documentElement.scrollHeight")
        if current_height == previous_height:
            break 
        previous_height = current_height

    results = driver.find_elements(By.CSS_SELECTOR, '.style-scope.ytd-video-renderer')
    seen_links = set()
    for result in results:
        try:
            title = result.find_element(By.CSS_SELECTOR, '#video-title').text
        except:
            title = None

        try:
            link = result.find_element(By.CSS_SELECTOR, '#video-title').get_attribute('href')
        except:
            link = None

        try:
            views = result.find_element(By.CSS_SELECTOR, '.style-scope.ytd-video-meta-block').text.split('\n')[0]
        except:
            views = None


        if title and link and views:
            if link[:30] == "https://www.youtube.com/shorts":
                if link not in seen_links:
                    if views.split()[0][-1] == 'M':
                        youtube_data.append({
                            'title': title,
                            'link': link,
                            'views': views,
                        })
                        seen_links.add(link)

        if len(youtube_data) >= count:
            break

    return youtube_data


st.set_page_config(
    page_title="YouTube Video Scraper", 
    page_icon="https://upload.wikimedia.org/wikipedia/commons/4/42/YouTube_icon_%282013-2017%29.png",
)

st.markdown("# YouTube Video Scraper")
st.title("\n")

if 'youtube_data' not in st.session_state:
    st.session_state['youtube_data'] = []
    st.session_state['search_term'] = ""
    st.session_state['count'] = 10

search_term = st.text_input("Enter the search term (e.g., 'RIP Harambe'):", value=st.session_state['search_term'])
count = st.number_input("Enter the number of results to scrape:", min_value=1, value=st.session_state['count'])

if st.button("Scrape Videos"):
    if search_term:
        with st.spinner(f"Scraping {count} results for '{search_term}'..."):
            youtube_data = get_video_results(search_term, count)
            st.session_state['youtube_data'] = youtube_data
            st.session_state['search_term'] = search_term
            st.session_state['count'] = count
            st.success(f"Scraping Complete!")
            

            youtube_link = st.text_input("Enter YouTube video link to play:")
            play_video_button = st.button("Play Video")

            if play_video_button and youtube_link:
                st.video(youtube_link.replace('shorts', 'embed'))

            
            views = [convert_views_to_numeric(video["views"]) for video in youtube_data]

            num_bins = 10
            plt.figure(figsize=(10, 6))
            plt.hist(views, bins=num_bins, edgecolor='black')
            plt.xlabel('Number of Views (in thousands)', fontsize=12)
            plt.ylabel('Frequency', fontsize=12)
            plt.title('Distribution of YouTube Video Views', fontsize=14)
            
            st.pyplot(plt)
            plt.close()

            st.write("### Scraped Video Data")
            st.dataframe(youtube_data)

            json_data = json.dumps(youtube_data, ensure_ascii=False, indent=2)
            st.download_button(
                label="Download JSON Data",
                data=json_data,
                file_name=f"{search_term.replace(' ', '_')}_youtube_data.json",
                mime="application/json"
            )

else:
    if st.session_state['youtube_data']:
        youtube_data = st.session_state['youtube_data']
        st.success(f"Displaying previous data for '{st.session_state['search_term']}'")
        
        youtube_link = st.text_input("Enter YouTube video link to play:")
        play_video_button = st.button("Play Video")

        if play_video_button and youtube_link:
            st.video(youtube_link.replace('shorts', 'embed'))

        views = [convert_views_to_numeric(video["views"]) for video in youtube_data]

        num_bins = 10
        plt.figure(figsize=(10, 6))
        plt.hist(views, bins=num_bins, edgecolor='black')
        plt.xlabel('Number of Views (in thousands)', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.title('Distribution of YouTube Video Views', fontsize=14)
        
        st.pyplot(plt)
        plt.close()

        st.write("### Scraped Video Data")
        st.dataframe(youtube_data)

        json_data = json.dumps(youtube_data, ensure_ascii=False, indent=2)
        st.download_button(
            label="Download JSON Data",
            data=json_data,
            file_name=f"{st.session_state['search_term'].replace(' ', '_')}_youtube_data.json",
            mime="application/json"
        )