#!/usr/bin/env python
# coding: utf-8

#import BeautifulSoup
from bs4 import BeautifulSoup  
from splinter import Browser
import pandas as pd
import datetime as dt 

#Visit the mars NASA news site
def mars_news(browser):  # in video 
    url = 'https://mars.nasa.gov/news/' 
    browser.visit(url)
    #going too fast, get first list item and wait 1/2 sec
    browser.is_element_present_by_css('ul.item_list li.slide', wait_time=0.5)

    html= browser.html
    news_soup= BeautifulSoup(html, 'html.parser')
    #print(news_soup)
    #slide element, everything in the  <ul class="item_list" 
    # <li class = "slide">
    # ...
    #</
    slide_element = news_soup.select_one('ul.item_list li.slide')
    #print(slide_element)
    
    try:
        slide_element.find("div", class_="content_title") #at 35 mins in video, finally working!!
        slide_element.find("div",class_="content_title").get_text()  #i'm not sure I have two of these, Drew only had the one without the get_text() 
        news_title = slide_element.find('div', class_='content_title').get_text() #it's not finding this class, play around withh this
        news_title #worked, got the title 
        news_paragraph = slide_element.find('div', class_="article_teaser_body").get_text() #get_text() on the end is like strip
        news_paragraph
    except AttributeError:
        return None, None
    return news_title, news_paragraph #returns couple tuples

def featured_image(browser):   # 2:27 in video 
    url= 'https://www.jpl.nasa.gov/spaceimages/?seach=&category=Mars'
    browser.visit(url)

    #ask splinter to click on the button with class name 'full image'
    #<button class ='full_image'>Full Image</button>
    full_image_button = browser.find_by_id('full_image')
    full_image_button.click()

    #find the more info button and click that 
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_element = browser.find_link_by_partial_text('more info')
    more_info_element.click()

    #parse the results with HTML soup
    html = browser.html 
    image_soup= BeautifulSoup(html, 'html.parser') 

    #get the image
    img = image_soup.select_one('figure.lede a img').get('src')

  
    try:
        img_url = img.get('src')   #***************PROBLEM "IMG is not defined here" "img.get" - likely incorrect as I can't find on web or cd be to lack of BS4  
    except AttributeError:
        return None

    #use the base url to create an absolute url 
    img_url= f'https://www.jpl.nasa.gov{img_url}'
    return img_url

def twitter_weather(browser):   # in video 
    #don't think we need next 4, hence why commented out
    #set the executable path for the chrome browser
    #executable_path = {'executable_path': 'chromedriver.exe'}
    #executable_path = {'executable_path': './chromedriver.exe'}
    #browser = Browser('chrome', **executable_path) 
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)
    html=browser.html 
    weather_soup= BeautifulSoup(html, 'html.parser')
    #first find a tweet witht the data name 'Mars Weather' 
    mars_weather_tweet = weather_soup.find('div', 
                                        attrs={
                                            "class": "tweet",
                                            "data-name": "Mars Weather"
                                        }) 
    # Next search withing the tweet for p tag containing the tweet text                                    
    mars_weather =  mars_weather_tweet.find('p', 'tweet-text').get_text()
    return mars_weather

def hemisphere(browser):  # in video 2:32
    url= 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    hemisphere_image_urls= [] 
    #First get a list og all the hemispheres 
    links=browser.find_by_css('a.product-item h3') #had a lot of trouble getting this line to work 
    print(links)

    for item in range(len(links)):  #going through each of the thumbnails and grabbing the description and image, four of them I think 
        hemisphere = {} #make hemisphere a dictionary
        
        #we have to find the element on each loop to avoid a stale element exception
        browser.find_by_css('a.product-item h3')[item].click() #go thru each item and click on it   
        
        #next we find the sample image anchor tag and extract the href
        sample_element =  browser.find_link_by_text('Sample').first #sample is the slightly smaller of the two high resversions  
        #this line is now working but had problems with it ******************************************
        
        print(sample_element)
        hemisphere['img_url'] = sample_element['href']
        print(hemisphere)
        
        #Get Hemisphere title 
        hemisphere['title']=browser.find_by_css('h2.title').text
        
        #Append hemispere object to list 
        hemisphere_image_urls.append(hemisphere)
        
        #Finally, we navigate backward
        browser.back()
    return hemisphere_image_urls

def scrape_hemisphere(html_text): #2:39 vid
    hemisphere_soup=BeautifulSoup(html_text, 'html.parser')
    try:   
        title_element=hemisphere_soup('h2',class_="title").get_text()
        sample_element=hemisphere_soup.find('a', text="sample").get('href')
    except AttributeError:
        title_element = None    
        sample_element = None
    hemisphere = {
        "title": title_element,
        "img_url": sample_element
    }
    return hemisphere

def mars_facts(): #2:38 video
    try:
        df = pd.read_html('https://space-facts.com/mars/')[0]
    except BaseException:
        return None
    df.columns=['description','value']
    df.set_index('description', inplace=True)
    return df.to_html(classes="table table-striped")

def scrape_all():  #this is your main bot 2:51 vid
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path) 
    #print(mars_new(browser))
    #print(featured_image(browser))    
    news_title, news_paragraph = mars_news(browser) #scraping too fast 
    img_url =  featured_image(browser)
    mars_weather=twitter_weather(browser)
    hemisphere_image_urls = hemisphere(browser)
    facts = mars_facts()
    timestamp=dt.datetime.now()

    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": img_url,
        "hemispheres": hemisphere_image_urls,
        "weather": mars_weather,
        "facts": facts,
        "last_modified": timestamp
    }

    browser.quit
    return data 


if __name__ == "__main__":
    print(scrape_all())


