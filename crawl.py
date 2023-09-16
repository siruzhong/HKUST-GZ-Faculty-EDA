import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By

BASE_URL = 'https://facultyprofiles.hkust-gz.edu.cn/'


def download_html(url):
    """
    Downloads the HTML content from the given URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.HTTPError as e:
        logger.error(f"Failed to retrieve webpage {url}. Status code: {e.response.status_code}")
        return None


def download_html_using_selenium(url):
    """
    Downloads the HTML content using Selenium.
    Returns the HTML content and the browser instance.
    """
    browser = webdriver.Chrome()
    browser.get(url)
    time.sleep(1)  # Give some time for the page to load
    html_content = browser.page_source
    return html_content, browser


# Downloading an HTML page using existed Selenium
def download_html_using_existed_selenium(browser, url):
    browser.get(url)
    time.sleep(1)  # Allow the content to load
    return browser.page_source


def extract_teachers_data_from_html():
    """
    Extracts information about all teachers from the base faculty URL.
    """
    html_content, browser = download_html_using_selenium(BASE_URL)
    soup = BeautifulSoup(html_content, 'html.parser')
    rows = soup.select('.el-table__row')

    faculty_table = []
    faculty_grad_year = []

    for idx, row in enumerate(rows):
        # get basic information about teachers
        english_name = row.select_one('.el-table_1_column_1 .word-adjuest').text
        chinese_name = row.select_one('.el-table_1_column_2 .word-adjuest').text
        title = row.select_one('.el-table_1_column_3 .word-adjuest').text
        thrust = row.select_one('.el-table_1_column_4 .word-adjuest').text
        email = row.select_one('.el-table_1_column_5 .email-text').text

        location, homepage, overview, research_interests, degree, graduate_year = '', '', '', '', '', ''
        # Click more button
        more_buttons = browser.find_elements(By.CSS_SELECTOR, '.el-button.el-button--text.more-btn')
        if more_buttons and len(more_buttons) > idx:
            more_buttons[idx].click()
            browser.switch_to.window(browser.window_handles[1])
            more_link = browser.current_url
            # get detailed information about teachers
            email, location, homepage, overview, research_interests, degree, graduate_year = \
                extract_teacher_info_from_html(browser, more_link)
            # Close and switch back to main window
            browser.close()
            browser.switch_to.window(browser.window_handles[0])
        else:
            more_link = "Not Found"

        current_faculty = {
            'English Name': english_name,
            'Chinese Name': chinese_name,
            'Title': title,
            'Thrust/Department/Division': thrust,
            'Email': email,
            'Location': location,
            'Overview': overview,
            "Research Interest": research_interests,
            'Homepage': homepage,
            'More': more_link,
        }
        faculty_table.append(current_faculty)
        logger.info(current_faculty)

        if graduate_year != '':
            current_faculty_graduate_info = {
                'English Name': english_name,
                'Chinese Name': chinese_name,
                'Graduate Year': graduate_year,
                'Estimated age': 2023 + 23 - graduate_year,
            }
            faculty_grad_year.append(current_faculty_graduate_info)
            logger.info(current_faculty_graduate_info)

    browser.close()

    save_data_to_csv(faculty_table, faculty_grad_year)


def extract_teacher_info_from_html(browser, url):
    """
    Extract detailed information about a specific teacher.
    """
    html_content = download_html_using_existed_selenium(browser, url)
    soup = BeautifulSoup(html_content, 'html.parser')

    email, location, homepage = '', '', ''
    overview, research_interests, degree = '', [], []
    graduate_year = 0

    # Extract email, location, and homepage using direct selectors
    icon_texts = soup.select('.card-object-wrap .icon-text')
    if icon_texts:
        email = icon_texts[0].get_text() if len(icon_texts) > 0 else ''
        location = icon_texts[1].get_text() if len(icon_texts) > 1 else ''
        homepage = icon_texts[2]['href'] if 'href' in icon_texts[2].attrs else ''

    # Extract degree details
    degree_details = soup.select('.degree-detail p')
    for degree_detail in degree_details:
        degree_text = degree_detail.get_text()
        degree.append(degree_text)
        if ',' in degree_text:
            graduate_year_str = degree_text.split(',')[-1].strip()
            graduate_year = int(graduate_year_str) if graduate_year_str.isdigit() else 0

    # Extract overview
    overview_div = soup.select_one('.overview-div')
    if overview_div:
        overview = overview_div.get_text().strip()

    # Extract research interests
    tabs = soup.select('.el-tabs__nav.is-top.is-stretch .el-tabs__item.is-top')
    if tabs:
        research_interest_id = f'tab-{len(tabs) - 1}'
        browser.find_element(by=webdriver.common.by.By.ID, value=research_interest_id).click()
        time.sleep(1)  # Give some time for the new content to load
        updated_soup = BeautifulSoup(browser.page_source, 'html.parser')
        research_interest_div = updated_soup.select_one('div.overview-div[data-v-150f67ee]')
        if research_interest_div:
            research_interests = [p.get_text() for p in research_interest_div.select('p.content')]

    return email, location, homepage, overview, research_interests, degree, graduate_year


def save_data_to_csv(faculty_table, faculty_grad_year):
    """
    Saves the faculty data to CSV files.
    """
    faculty_table_df = pd.DataFrame(faculty_table)
    faculty_grad_year_df = pd.DataFrame(faculty_grad_year)

    logger.info("Saving faculty_table to faculty_table.csv")
    faculty_table_df.to_csv('faculty_table.csv', index=False)

    logger.info("Saving faculty_grad_year to faculty_grad_year.csv")
    faculty_grad_year_df.to_csv('faculty_grad_year.csv', index=False)


if __name__ == '__main__':
    extract_teachers_data_from_html()
