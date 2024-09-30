import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime


# Scraping function for NYS DOT Detailed Ads
def scrape_nys_dot_detail_ads():
    url = 'https://www.dot.ny.gov/doing-business/opportunities/eng-detailad'
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
    links = []

    # Find the main table
    main_table = soup.find('table', {'id': 'rg151682'})
    inner_tables = main_table.find_all('table', class_='bcbanregion1')

    for inner_table in inner_tables:
        rows = inner_table.find_all('tr')
        for row in rows:
            date_td = row.find('td', class_='bcgroup')
            info_td = row.find('td', class_='bcbanregion2')
            
            if date_td and info_td:
                date = date_td.get_text(strip=True)
                # Change the date format to yyyy/mm/dd
                try:
                    date_obj = datetime.strptime(date, '%m/%d/%Y')  # Adjust the format if needed
                    date = date_obj.strftime('%Y/%m/%d')
                except ValueError:
                    pass  # Handle unexpected date formats
                
                # Extract the description and link
                description_html = str(info_td)
                description_start = description_html.find('&nbsp;') + 6
                description_end = description_html.find('<ul>')
                if description_end == -1:
                    description_end = description_html.find('</td>')
                description = description_html[description_start:description_end].strip()
                description = description.replace('lass="bcbanregion2">', '').replace('\n', '').strip()
                
                # Extract link
                link_tag = info_td.find('a', target='_blank')
                if link_tag:
                    link_href = link_tag['href']
                    full_link = 'https://www.dot.ny.gov' + link_href
                    link_text = link_tag.get_text(strip=True)
                    link = f'<a href="{full_link}" target="_blank">{link_text}</a>'
                else:
                    link = None
                
                # Append data to lists
                dates.append(date)
                descriptions.append(description)
                links.append(link)

    # Create a DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Description': descriptions,
        'Link': links
    })

    # Display the DataFrame in Streamlit with clickable links
    st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)

# Function to show the page
def show_page():
    # Embedded hyperlink in the title
    title_html = """
    <h2><a href='https://www.dot.ny.gov/doing-business/opportunities/eng-detailad' 
    target='_blank'>NYS DOT Detailed Ads</a></h2>
    """
    st.markdown(title_html, unsafe_allow_html=True)

    # Scrape the data when the button is clicked
    if st.button("Scrape NYS DOT Detailed Ads"):
        scrape_nys_dot_detail_ads()

    # Back to Home button
    if st.button("Back to Home"):
        st.session_state['page'] = 'main'
