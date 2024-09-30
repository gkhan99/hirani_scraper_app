import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime


# Scraping function for NYS DOT Designation
def scrape_nys_dot_designation():
    url = 'https://www.dot.ny.gov/doing-business/opportunities/eng-designation'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching the webpage: {e}")
        return

    # Initialize lists to store scraped data
    dates = []
    descriptions = []

    # Find the main table
    main_table = soup.find('table', {'id': 'rg151694'})
    inner_tables = main_table.find_all('table', class_='bcbanregion1')

    for inner_table in inner_tables:
        rows = inner_table.find_all('tr')
        for row in rows:
            date_td = row.find('td', class_='bcgroup', valign='top')
            info_td = row.find('td', class_='bcbanregion2')
            
            if date_td and info_td:
                date = date_td.get_text(strip=True)
                
                if '2024' in date:
                    description_html = str(info_td)
                    description_start = description_html.find('<br>') + 4
                    description_end = description_html.find('</td>')
                    description = description_html[description_start:description_end].strip()
                    
                    soup_desc = BeautifulSoup(description, 'html.parser')
                    for strong_tag in soup_desc.find_all('strong'):
                        strong_tag.decompose()  # Remove <strong> tags
                    
                    description = soup_desc.get_text(strip=True)
                    description = description.replace('class="bcbanregion2">', '').strip()
                    
                    dates.append(date)
                    descriptions.append(description)

    # Create a DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Description': descriptions
    })

    # Sort the DataFrame by date
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values(by='Date', ascending=False, inplace=True)

    # Display the DataFrame in Streamlit
    st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)

# Function to show the page
def show_page():
    # Embedded hyperlink in the title
    title_html = """
    <h2><a href='https://www.dot.ny.gov/doing-business/opportunities/eng-designation' 
    target='_blank'>NYS DOT Designation</a></h2>
    """
    st.markdown(title_html, unsafe_allow_html=True)

    if st.button("Scrape NYS DOT Designation"):
        scrape_nys_dot_designation()
    
    if st.button("Back to Home"):
        st.session_state['page'] = 'main'
