import praw
import config
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import schedule
import time


def authenticate():
    print('Authenticating User....')
    reddit = praw.Reddit(client_id=config.client_id,
                         client_secret=config.client_secret,
                         user_agent=config.user_agent,
                         username=config.username,
                         password=config.password)
    print("User '{user}' Authenticated".format(user=reddit.user.me()))
    return reddit


def reddit_posting(title, url):
    reddit = authenticate()
    subreddit = reddit.subreddit('DragaliaLost')

    subreddit.submit(title, url=url)
    print('Posted {} {}'.format(title, url))


def get_website_data():
    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.get('https://dragalialost.com/en/news/')

    c = browser.page_source
    soup = BeautifulSoup(c, "html.parser")
    browser.close()
    return soup


def scrape_data(soup):
    articles = soup.find_all("article")
    df = pd.read_csv('data.csv')

    data = []
    for i, x in enumerate(articles):
        link = 'https://dragalialost.com' + articles[i].find('a').get('href')
        title = articles[i].find('div', {"class": 'title'}).text

        if link not in list(df['link']):
            try:
                reddit_posting(title, link)
                print(f'Posting\n{title}: {link}')

            except Exception as e:
                print(e)
                print('Did not post \n{}:\n {}'.format(title, link))

        data.append([link, title])

    new_df = pd.DataFrame(data, columns=['link', 'title'])
    df = pd.concat([df, new_df], ignore_index=True, sort=False)
    df.drop_duplicates('link', inplace=True)
    df.to_csv('data.csv', index=False)


def main():
    soup = get_website_data()
    scrape_data(soup)


if __name__ == '__main__':
    schedule.every().hour.do(main)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
