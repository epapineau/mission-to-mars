# Import dependencies
import pandas as pd
import requests
from config import auth
from bs4 import BeautifulSoup as bs

# Setup splinter
from splinter import Browser
executable_path = {'executable_path': 'chromedriver.exe'}
browser = Browser('chrome', **executable_path, headless = True)

# Begin function
def scrape():
    # Get headlines from NASA Mars News
    print('Get headlines from NASA Mars News')
    mars_news = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    browser.visit(mars_news)
    html = browser.html
    soup = bs(html, 'html.parser')
    news_title = soup.find_all('div', class_ = 'image_and_description_container')[0].h3.text
    news_p = soup.find_all('div', class_ = 'image_and_description_container')[0].text

    # Get featured image from JPL
    print('Get featured image from JPL')
    mars_image = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(mars_image)
    browser.click_link_by_partial_text('FULL IMAGE')
    try: 
        html = browser.html
        soup = bs(html, 'html.parser')
        img = soup.find_all('div', class_ = 'fancybox-wrap')[0].img['src']
        featured_image_url = f"https://www.jpl.nasa.gov{img}"
    except:
        # For development - in case it fails; troubleshoot html chunks later
        featured_image_url = "https://www.jpl.nasa.gov/spaceimages/images/largesize/PIA17978_hires.jpg"

    # Twitter API access
    headers = {'Authorization': 'Basic ' + auth}
    data = [('grant_type', 'client_credentials')]
    response = requests.post('https://api.twitter.com/oauth2/token', headers = headers, data = data).json()
    headers = {'Authorization': 'Bearer ' + response['access_token']}

    # Get latest tweet from Mars Weather twitter
    print('Get latest tweet from Mars Weather twitter')
    twitter = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=MarsWxReport&exclude_replies=true&include_rts=false"
    request = requests.get(twitter, headers = headers).json()

    weather_tweets = []
    for i in range(0, len(request)):
        if(request[i]['text'][0:4] == 'Sol '):
            weather_tweets.append(request[i]['text'])

    mars_weather = weather_tweets[0]

    # Get mars facts table
    print('Get mars facts table')
    tables = pd.read_html("https://space-facts.com/mars/")
    mars_table_html = tables[0].to_html()

    # Get URLs for Mars hemisphere images
    hemisphere_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemisphere_url)
    html = browser.html
    soup = bs(html, 'html.parser')

    # Get list of hempisphere link names
    img_names = soup.find_all('div', class_ = 'item')

    # Loop through list and save url for each img
    hemisphere_image_urls = []
    for i in range(0, len(img_names)):
        # Get text to use to click through to image page
        link_text = img_names[i].h3.text
        print(f"Retreiving image for {link_text}")
        
        # Navigate browser, get page
        browser.click_link_by_partial_text(link_text)
        html = browser.html
        soup = bs(html, 'html.parser')
    
        # Find image link and save
        img = soup.find_all('div', class_ = 'downloads')[0].li.a['href']
        dictionary = {'title': link_text,
                    'img_url': img}
        hemisphere_image_urls.append(dictionary)
        
        # Click back to homepage
        browser.visit(hemisphere_url)

    # Compile scraped data into a dictionary
    mars_dict = {'mars_news_title': news_title,
                'mars_news_paragraph': news_p,
                'jpl_featured_image': featured_image_url,
                'mars_weather': mars_weather,
                'mars_table': mars_table_html,
                'hemisphere_image_urls': hemisphere_image_urls}

    return mars_dict

print(scrape())