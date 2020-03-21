# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    # Set the executable path and initialize the chrome browser in splinter
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)
    hemisphere_images = mars_hemisphere(browser)
    
    # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "hemisphere_1_img": hemisphere_images[0].get('img_url'),
      "hemisphere_1_title": hemisphere_images[0].get('title'),
      "hemisphere_2_img": hemisphere_images[1].get('img_url'),
      "hemisphere_2_title": hemisphere_images[1].get('title'),
      "hemisphere_3_img": hemisphere_images[2].get('img_url'),
      "hemisphere_3_title": hemisphere_images[2].get('title'),
      "hemisphere_4_img": hemisphere_images[3].get('img_url'),
      "hemisphere_4_title": hemisphere_images[3].get('title'),
      "last_modified": dt.datetime.now()
    }

    return data

def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')
    
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()
        # Use the parent element to find the first paragraph text
        news_body = slide_elem.find("div", class_="article_teaser_body").get_text()
    except AttributeError:
        return None, None

    return news_title, news_body

# "### Featured Images"

def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
    
    return img_url

def mars_facts():
    try:
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None
    
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)
    
    return df.to_html()

def mars_hemisphere(browser):
    # Visit URL
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    
    # Parse html
    html = browser.html
    soup  = BeautifulSoup (html, 'html.parser')

    # Find all the hemispheres
    hemispheres = soup.find_all('div', class_="description")

    # Variable to hold data
    hemisphere_img = []

    # Loop throught the hemisphere data to gather title and image url 
    for item in hemispheres:
        img_title = item.find('h3').get_text()
        # Find image and click 
        elem = browser.find_link_by_partial_text(img_title)
        elem.click()

        # Parse resulting browser with BeautifulSoup
        html = browser.html
        soup = BeautifulSoup (html, 'html.parser')
        
        rel_url = soup.find('img', class_="wide-image").get('src')
        img_url = f'https://astrogeology.usgs.gov/{rel_url}'

        # Store as dictionary and append
        hemisphere ={"img_url":img_url, "title":img_title}
        hemisphere_img.append(hemisphere)
        
        # Back to initial url to get next data
        browser.visit(url)

    return hemisphere_img


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())