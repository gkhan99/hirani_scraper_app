import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os

# Function to install Google Chrome and ChromeDriver
def install_chrome_and_driver():
    # Download Google Chrome
    os.system("wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
    os.system("apt-get update && apt-get install -y ./google-chrome-stable_current_amd64.deb")

    # Download ChromeDriver
    os.system("wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip")
    os.system("unzip chromedriver_linux64.zip -d /usr/local/bin/")
    os.system("chmod +x /usr/local/bin/chromedriver")

# Scraping function for Port Authority Construction Opportunities using Selenium
def fetch_table_port_authority():
    # Install Chrome and ChromeDriver
    install_chrome_and_driver()

    # Set up Selenium WebDriver with headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/google-chrome"  # Path to Google Chrome

    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=chrome_options)

    # Go to the URL
    url = 'https://panynj.gov/port-authority/en/business-opportunities/solicitations-advertisements/Construction.html'
    driver.get(url)

    # Wait for the table to load
    time.sleep(5)

    # Get the page source and close the browser
    content = driver.page_source
    driver.quit()

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')

    # Locate all table elements
    table_containers = soup.find_all('div', {'class': 'Text med black'})

    table_names = [
        "Solicitations/Advertisements",
        "Catalog of Upcoming Procurements at John F. Kennedy (JFK) International Airport",
        "RTQ (Request to Qualify)",
        "VVP (Verification and Validation Process)",
        "Others"
    ]

    all_tables = []
    table_counter = 0

    # Process each table
    for container in table_containers:
        tables = container.find_all('table')
        for table in tables:
            if table is None or table_counter >= len(table_names):
                continue

            # Extract table headers
            headers = ['Full Description']
            for th in table.find_all('th'):
                headers.append(th.get_text(strip=True))

            # Extract table rows
            rows = []
            base_url = 'https://panynj.gov'
            for tr in table.find_all('tr')[1:]:  # Skip the header row
                cells = []
                full_description = ''
                for idx, td in enumerate(tr.find_all('td')):
                    cell_content = []
                    # Extract the text content and handle <a> tags
                    if td.find('a'):
                        for a in td.find_all('a'):
                            href = a['href']
                            if not href.startswith('http'):
                                href = base_url + href
                            cell_content.append(f'<a href="{href}" target="_blank">{a.get_text(strip=True)}</a>')
                        cells.append("<br>".join(cell_content))
                    else:
                        cells.append(td.get_text(strip=True))

                    # If this is the third column, capture the text content before any <br> tag
                    if idx == 2:
                        first_paragraph = td.find('p')
                        if first_paragraph and first_paragraph.contents:
                            full_description = str(first_paragraph.contents[0]).strip()

                cells.insert(0, full_description)  # Insert the full description at the beginning
                rows.append(cells)

            # Create a DataFrame for the current table
            df = pd.DataFrame(rows, columns=headers)
            all_tables.append((table_names[table_counter], df))
            table_counter += 1

    return all_tables

# Function to show the page in Streamlit
def show_page():
    # Embedded hyperlink in the title
    title_html = """
    <h2><a href='https://panynj.gov/port-authority/en/business-opportunities/solicitations-advertisements/Construction.html' 
    target='_blank'>Port Authority Construction Opportunities</a></h2>
    """
    st.markdown(title_html, unsafe_allow_html=True)

    # Check if the user has clicked the scrape button
    if st.button("Scrape Port Authority Construction Opportunities"):
        all_tables = fetch_table_port_authority()
        st.session_state["scraped_tables"] = all_tables  # Store the scraped tables in session state
        st.success("Scraping completed! Now you can filter the tables.")

    # If the tables have been scraped, display them with a search filter
    if "scraped_tables" in st.session_state:
        all_tables = st.session_state["scraped_tables"]

        # Text input for keyword filter
        filter_keyword = st.text_input("Filter for relevant keywords:", "")

        # Display each table
        for table_name, df in all_tables:
            st.markdown(f"### {table_name}")

            # Filter the DataFrame if a keyword is entered
            if filter_keyword:
                df_filtered = df[df.apply(lambda row: row.astype(str).str.contains(filter_keyword, case=False).any(), axis=1)]
            else:
                df_filtered = df

            # Convert filtered DataFrame to HTML
            table_html = df_filtered.to_html(index=False, escape=False)
            st.markdown(table_html, unsafe_allow_html=True)

    # Back to Home button
    if st.button("Back to Home"):
        st.session_state['page'] = 'main'
