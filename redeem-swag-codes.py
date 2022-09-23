import requests, pickle, warnings, config, bs4
from bs4 import BeautifulSoup
from bs4.builder import XMLParsedAsHTMLWarning
from re import search
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import JavascriptException
from time import sleep

warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)

options = Options()
# Headless chrome = True
options.headless = True
driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
}
URL = "https://sbcodez.com/feed/"
SWAGBUCKS_URL = "https://www.swagbucks.com/"

class ReadSBCodezRss:
    """
    The ReadSBCodezRSS object scrapes the Swag Codes and their links from the RSS feed
    """
    def __init__(self, url: str, headers: dict):
        """
        Initiate ReadSBCodezRss object and compute its attributes

        Parameters
        ----------
        @url: str: SBCodez RSS Feed URL
        @headers: dict: Headers for GET request for URL
        """
        self.url = url
        self.headers = headers
        self.r = requests.get(url, headers=self.headers)
        #self.r = open('feed.xml', 'r')
        self.soup = BeautifulSoup(self.r.text, features='lxml')
        with open("feed.xml", "w") as f:
            f.write(str(self.soup))
        # all posts
        self.posts = self.soup.find_all('item')
        # today's day
        self.day = str(datetime.now().day) + ','
        self.today_posts = self.get_today_posts(self.posts, self.day)
        self.codes = self.get_codes(self.today_posts)
        self.code_links = self.get_today_posts_links(self.today_posts)

    def get_today_posts(self, posts: bs4.element.ResultSet, day: str) -> bs4.element.ResultSet:
        """
        Get posts only from today

        Parameters
        ----------
        @posts: bs4.element.ResultSet: ResultSet of all most recent posts
        @day: str: day from today's date with comma at the end (Ex. '22,')
        
        Returns
        -------
        @posts: bs4.element.ResultSet: ResultSet of today's posts
        """
        # DEFAULT WORKS FOR 'US'
        # REPLACE ONE OF THE VALUES FOR THE country_filter LIST WITH 'US' AND REPLACE 'US' WITH YOUR COUNTRY IN country IF YOU WANT THE BOT TO WORK FOR A DIFFERENT COUNTRY
        country_filter = ['CA', 'UK', 'AU']
        country = 'US'
        print(f'Filtering out {country_filter[0]}, {country_filter[1]}, and {country_filter[2]} while keeping {country} and iSPY codes for today...')
        for post in posts:
            try:
                # keep only 'country' and iSPY current date posts
                if ((search(country_filter[0], post.find('title').get_text()) or search(country_filter[1], post.find('title').get_text()) or search(country_filter[2], post.find('title').get_text())) and (bool(search(country, post.find('title').get_text())) == False)) and bool(search('iSPY', post.find('title').get_text())) == False or bool(search(day, post.find('title').get_text())) == False:
                    post.decompose()
            except ValueError:
                continue
        return posts
    
    def get_today_posts_links(self, posts: bs4.element.ResultSet) -> list:
        """
        Get code location links from today's posts

        Parameters
        ----------
        @posts: bs4.element.ResultSet: ResultSet of today's posts
        
        Returns
        -------
        @links: list[str]: List of links from today's posts
        """
        links = []
        for post in posts:
            try:
                if str(post) != '<None></None>':
                    codeLocation = post.find('span', {'class': 'codeLocation'})
                    link = codeLocation.find('a')['href']
                    links.append(link)
            except:
                links.append('N/A')
        return links
    
    def get_codes(self, posts: bs4.element.ResultSet) -> list:
        """
        Get Swag Codes from posts

        Parameters
        ----------
        @posts: bs4.element.ResultSet: ResultSet of today's posts
        
        Returns
        -------
        @codes: list[str]: List of Swag Codes from today's posts
        """
        bold = []
        codes = []
        # codes are always in bolded tags
        for b in posts:
            bold.extend(b.find_all('b'))
        for element in bold:
            codes.append(element.text)
        codes = list(dict.fromkeys(codes))
        return codes

def login_SB(email: str, password: str, driver: WebDriver):
    """
    Login to swagbucks.com in the driver

    Parameters
    ----------
    @email: str: Email of your Swagbucks account
    @password: str: Email of your Swagbucks account
    @driver: WebDriver: Instance of the chrome driver
    """
    # load cookies into Swagbucks if cookies.pkl is detected
    try:
        driver.get('https://www.swagbucks.com/')
        cookies = pickle.load(open('cookies.pkl', 'rb'))
        for cookie in cookies:
            driver.add_cookie(cookie)
        print('Loaded cookies')
    # login into Swagbucks and save cookies to cookies.pkl for future runs of script
    except FileNotFoundError:
        print('Cookies not found. Logging in and then creating cookies...')
        driver.get('https://www.swagbucks.com/p/login') 
        sleep(3)
        driver.find_element('xpath', '//input[@name=\"emailAddress\"]').send_keys(email)
        sleep(2)
        driver.find_element('xpath', '//input[@name=\"password\"]').send_keys(password)
        sleep(2)
        driver.find_element('xpath', '//button[@id="loginBtn"]').click()
        sleep(3) # captcha
        pickle.dump(driver.get_cookies(), open('cookies.pkl', 'wb'))
        print('Saved cookies as cookies.pkl')
    finally:
        sleep(3)

def get_swag_code_offer_page(code: str, link: str) -> str:
    """
    Get the Swag Code from the offer page link

    Parameters
    ----------
    @code: str: Main part of the Swag Code without the 'XXXX'
    @code: str: Link of the offer page

    Returns
    -------
    @swag_offer_code: str: Swag Code from the offer page
    """
    driver.get(link)
    html = driver.page_source
    soup = BeautifulSoup(html, features='html.parser')
    # code without the 'XXXX' at the end
    main_code = code.split('XXXX')[0]
    # get description of the offer page
    description = soup.find('div', {'id': 'ofDesc'}).get_text()
    description_split = description.split(' ')
    swag_offer_code = ''
    Box = False
    Mobile_App = False
    SwagButton = False
    for text in description_split:
        # detect if box, app, and/or swagbutton is in the description
        if text.replace(',','').lower() == 'box':
            Box = True
        if text.replace(',','').lower() == 'app':
            Mobile_App = True
        if text.replace(',','').lower() == 'swagbutton':
            SwagButton = True  
        # detect the swag code
        #if text[:len(main_code)] == main_code.upper():
        if text[:len(main_code)].isupper() and text[:len(main_code)] != 'SWAG' and text[:len(main_code)] != 'CODE' and text[:len(main_code)] != 'ALERT!':
            swag_offer_code = text
            print('FOUND SWAG CODE:', swag_offer_code)

    # no swag code found
    if swag_offer_code == '':
        print(f'Swag Code {code} is already redeemed or expired')
        return swag_offer_code
    else:
        # if swag code box is described
        if Box:
            print(f'Swag Code {swag_offer_code} can be entered on the website')
            return swag_offer_code
        # if both mobile app AND swagbutton, but not swag code box is described
        elif Mobile_App and SwagButton and (Box == False):
            print(f'Swag Code {swag_offer_code} can only be entered on the Mobile App or SwagButton')
            swag_offer_code = 'm/b'
            return swag_offer_code
        # if ONLY mobile app is described
        elif Mobile_App and (SwagButton == False) and (Box == False):
            print(f'Swag Code {swag_offer_code} can only be entered on the Mobile App')
            swag_offer_code = 'm'
            return swag_offer_code
        # if ONLY swagbutton is described
        elif (Mobile_App == False) and SwagButton and (Box == False):
            print(f'Swag Code {swag_offer_code} can only be entered on SwagButton')
            swag_offer_code = 'b'
            return swag_offer_code
    return swag_offer_code

def redeem_swag_code(code: str, offer: bool=True):
    """
    Redeem the Swag Code on swagbucks.com

    Parameters
    ----------
    @code: str: Swag Code
    @offer: bool: True if the link is an offer page. False if the link is not an offer page
    """
    # print information about code that is not an offer-page code
    if offer == False:
        print(f'{code} is a code that can be entered anywhere.')
    try:
        driver.execute_script("document.getElementById('sbUserMenuToggle').click();")
        driver.implicitly_wait(2)
        driver.execute_script("document.getElementById('sbMainNavUserMenuSwagCodeCta').click();")
        #driver.execute_script(f"document.getElementById('swag-code__input--QEQ0m').value = '{code}';")
        driver.implicitly_wait(2)
        driver.find_element(By.ID, 'swag-code__input--QEQ0m').send_keys(code)
        driver.implicitly_wait(2)
        driver.execute_script("document.getElementById('swag-code__submitCta--FSc8Q').click();")
        driver.implicitly_wait(2)
        print(f'Redeemed the Swag Code (unknown if successful or not. Read the above message for more details): {code}')
    except JavascriptException:
        print(f'Error redeeming the Swag Code: {code}')

def main():
    """
    Main function
    """
    feed = ReadSBCodezRss(URL, headers)
    if feed.codes == []:
        raise Exception('No new Swag codes have been posted today yet')
    print('CODES FOUND:', feed.codes)
    print('LINKS FOUND:',feed.code_links)

    code_link_dict = {feed.codes[i]: feed.code_links[i] for i in range(len(feed.codes))}
    #print(code_link_dict)
    login_SB(config.EMAIL,config.PASSWORD, driver)

    # go through all Swag Codes and try to redeem them
    for code in code_link_dict.keys():
        if search('facebook', code_link_dict[code]) or search('twitter', code_link_dict[code]):
            # non-offer-page Swag Code
            print(f'DETECTED FACEBOOK / TWITTER / ISPY / EXTRAVAGANZA CODE for {code}')
            driver.get(SWAGBUCKS_URL)
            sleep(2)
            redeem_swag_code(code, offer=False)
        elif search('offer-page', code_link_dict[code]):
            print(f'DETECTED OFFER PAGE for {code}')
            swag_offer_code = get_swag_code_offer_page(code, code_link_dict[code])
            # if Swag Code is not empty or a mobileapp / swagbutton code
            if swag_offer_code != '' and swag_offer_code != 'm/b' and swag_offer_code != 'm' and swag_offer_code != 'b':
                redeem_swag_code(swag_offer_code, offer=True)


if __name__ == '__main__':
    main()