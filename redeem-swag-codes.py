import requests, pickle, warnings, config, bs4, string, argparse
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
from selenium.common.exceptions import JavascriptException, NoSuchElementException
from time import sleep
from rich.console import Console

warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)

options = Options()
# Headless chrome = True
options.headless = True
driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.implicitly_wait(2)


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
}
URL = "https://sbcodez.com/feed/"
SWAGBUCKS_URL = "https://www.swagbucks.com/"
# DEFAULT WORKS FOR 'US'
# REPLACE ONE OF THE VALUES FOR THE country_filter LIST WITH 'US' AND REPLACE 'US' WITH YOUR COUNTRY IN country IF YOU WANT THE BOT TO WORK FOR A DIFFERENT COUNTRY
COUNTRY_FILTER = ['CA', 'UK', 'AU']
COUNTRY = 'US'
# list of already redeemed Swag Codes when --hourly argument is passed
REDEEMED = []

console = Console()

# Parse arguments
parser = argparse.ArgumentParser(description='Redeem Swag Codes found on sbcodez.com on swagbucks.com.')
parser.add_argument('--hourly', action='store_true', help='Redeem Swag Codes found on sbcodez.com every hour.', required=False)
args = parser.parse_args()
HOURLY = False
if args.hourly:
    HOURLY = args.hourly

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
        console.print(f'Filtering out {COUNTRY_FILTER[0]}, {COUNTRY_FILTER[1]}, and {COUNTRY_FILTER[2]} while keeping {COUNTRY} and iSPY codes for today...', style = 'yellow')
        for post in posts:
            try:
                # keep only 'country' and iSPY current date posts
                if ((search(COUNTRY_FILTER[0], post.find('title').get_text()) or search(COUNTRY_FILTER[1], post.find('title').get_text()) or search(COUNTRY_FILTER[2], post.find('title').get_text())) and (bool(search(COUNTRY, post.find('title').get_text())) == False)) and bool(search('iSPY', post.find('title').get_text())) == False or bool(search(day, post.find('title').get_text())) == False:
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
            except AttributeError:
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
        driver.get(SWAGBUCKS_URL)
        cookies = pickle.load(open('cookies.pkl', 'rb'))
        for cookie in cookies:
            driver.add_cookie(cookie)
        console.print('Loaded cookies', style='yellow')
    # login into Swagbucks and save cookies to cookies.pkl for future runs of script
    except FileNotFoundError:
        console.print('Cookies not found. Logging in and then creating cookies...', style='yellow')
        driver.get('https://www.swagbucks.com/p/login') 
        sleep(3)
        driver.find_element('xpath', '//input[@name=\"emailAddress\"]').send_keys(email)
        sleep(2)
        driver.find_element('xpath', '//input[@name=\"password\"]').send_keys(password)
        sleep(2)
        driver.find_element('xpath', '//button[@id="loginBtn"]').click()
        sleep(3) # captcha
        pickle.dump(driver.get_cookies(), open('cookies.pkl', 'wb'))
        console.print('Saved cookies as cookies.pkl', style='green')
    finally:
        sleep(3)

def get_swag_code_offer_page(code: str, link: str) -> str:
    """
    Get the Swag Code from the offer page link

    Parameters
    ----------
    @code: str: Swag Code with the 'XXXX'
    @link: str: Link of the offer page

    Returns
    -------
    @swag_offer_code: str: Swag Code without the 'XXXX' from the offer page
    """
    driver.get(link)
    html = driver.page_source
    soup = BeautifulSoup(html, features='html.parser')
    # get description of the offer page
    description = soup.find('div', {'id': 'ofDesc'}).get_text()
    description_split = description.split(' ')
    swag_offer_code = ''
    Box = False
    Mobile_App = False
    SwagButton = False
    # remove punctuation and new line characters
    description_split = list(map(lambda text:text.translate(str.maketrans('', '', string.punctuation)), description_split))
    description_split = list(map(lambda text:text.replace('\n',''), description_split))
    # strip whitespace
    description_split = list(map(lambda text:text.strip(), description_split))
    # make description_split lowercase to detect if box, app, and/or swagbutton is in the description
    description_split_lower = list(map(lambda text:text.lower(), description_split))
    try:
        description_split_lower.index('swag')
        description_split_lower.index('code')
        description_split_lower.index('box')
        Box = True
    except ValueError:
        pass
    try:
        description_split_lower.index('mobile')
        description_split_lower.index('app')
        Mobile_App = True
    except ValueError:
        pass
    try:
        description_split_lower.index('swagbutton')
        SwagButton = True
    except ValueError:
        pass
    # detect Swag Code in CA/UK/AU
    if COUNTRY in {'CA', 'UK', 'AU'}:
        swag_offer_code = description_split[description_split.index('Swagcode')+2]
        console.print(f'[bold bright_cyan]FOUND SWAG CODE:[/bold bright_cyan] [bold green]{swag_offer_code}[/bold green]')
    # detect Swag Code in US
    else:
        swag_offer_code = description_split[description_split.index('Enter')+1]
        console.print(f'[bold bright_cyan]FOUND SWAG CODE:[/bold bright_cyan] [bold green]{swag_offer_code}[/bold green]')
    # Swag Code is expired
    if swag_offer_code == 'EXPIRED':
        console.print(f'Swag Code [bold green]{code}[/bold green] is expired', style='bold yellow')
        return swag_offer_code
    # Swag Code is already redeemed
    elif swag_offer_code == 'This':
        console.print(f'Swag Code [bold green]{code}[/bold green] is not available in your country', style='bold yellow')
        return swag_offer_code
    elif swag_offer_code == 'You':
        console.print(f'Swag Code [bold green]{code}[/bold green] has already been redeemed', style='bold yellow')
        return swag_offer_code
    else:
        # if both Mobile App AND SwagButton, but not Swag Code box is described
        if Mobile_App and SwagButton and (Box == False):
            console.print(f'Swag Code [bold green]{swag_offer_code}[/bold green] can only be entered on the [cyan2]Mobile App[/cyan2] or [cyan3]SwagButton[/cyan3]', style='white')
            swag_offer_code = 'm/b'
            return swag_offer_code
        # if ONLY Mobile App is described
        elif Mobile_App and (SwagButton == False) and (Box == False):
            console.print(f'Swag Code [bold green]{swag_offer_code}[/bold green] can only be entered on the [cyan2]Mobile App[/cyan2]')
            swag_offer_code = 'm'
            return swag_offer_code
        # if ONLY SwagButton is described
        elif (Mobile_App == False) and SwagButton and (Box == False):
            console.print(f'Swag Code [bold green]{swag_offer_code}[/bold green] can only be entered on [cyan3]SwagButton[/cyan3]')
            swag_offer_code = 'b'
            return swag_offer_code
        # Swag Code box is described or nothing (CA/UK/AU)
        else:
            console.print(f'Swag Code [bold green]{swag_offer_code}[/bold green] can be entered on the [blue1]website[/blue1]')
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
        console.print(f'[bold green]{code}[/bold green] is a code that can be entered anywhere.', style='yellow')
    try:
        driver.execute_script("document.getElementById('sbUserMenuToggle').click();")
        driver.execute_script("document.getElementById('sbMainNavUserMenuSwagCodeCta').click();")
        #driver.execute_script(f"document.getElementById('swag-code__input--QEQ0m').value = '{code}';")
        driver.find_element(By.ID, 'swag-code__input--QEQ0m').send_keys(code)
        driver.execute_script("document.getElementById('swag-code__submitCta--FSc8Q').click();")
        try:
            message = driver.find_element(By.CLASS_NAME, 'banner__description--uBErz').text
            console.print(f'[underline orange1]{message}[/underline orange1] :left-right_arrow: [bold cyan]SWAG CODE:[/bold cyan] [bold green]{code}[/bold green]')
        except NoSuchElementException:
            console.print(f'Error retrieving Swagbucks response message after redeeming Swag Code: [bold green]{code}[/bold green]', style='red')
    except JavascriptException:
        console.print(f'Error redeeming the Swag Code: [bold green]{code}[/bold green]', style='red')

def main():
    """
    Main function
    """
    feed = ReadSBCodezRss(URL, headers)
    if feed.codes == []:
        console.print('No new Swag codes have been posted today yet', style='bright_red')
        return
    console.print(f'[cyan]CODES FOUND:[/cyan] {feed.codes}')
    console.print(f'[cyan]LINKS FOUND:[/cyan] {feed.code_links}')

    code_link_dict = {feed.codes[i]: feed.code_links[i] for i in range(len(feed.codes))}
    #print(code_link_dict)
    # Login to Swagbucks/ Load cookies in main function if --hourly argument is not passed
    if not HOURLY:
        login_SB(config.EMAIL,config.PASSWORD, driver)

    # go through all Swag Codes and try to redeem them
    for code in code_link_dict.keys():
        # check if Swag Code has already been redeemed
        if code in REDEEMED and HOURLY:
            console.print(f'Swag Code [bold green]{code}[/bold green] has already been redeemed earlier during the time this bot has been running', style='orange1')
        else:
            if search('facebook', code_link_dict[code]) or search('twitter', code_link_dict[code]):
                # non-offer-page Swag Code
                console.print(f'DETECTED FACEBOOK / TWITTER / ISPY / EXTRAVAGANZA CODE for [bold green]{code}[/bold green]', style='magenta')
                driver.get(SWAGBUCKS_URL)
                sleep(2)
                redeem_swag_code(code, offer=False)
                REDEEMED.append(code)
            elif search('offer-page', code_link_dict[code]):
                # offer-page Swag Code
                console.print(f'DETECTED OFFER PAGE for [bold green]{code}[/bold green]', style='magenta2')
                swag_offer_code = get_swag_code_offer_page(code, code_link_dict[code])
                # if Swag Code is expired, already redeemed, or a Mobile App / SwagButton code
                if swag_offer_code != 'EXPIRED' and swag_offer_code != 'This' and swag_offer_code != 'You' and swag_offer_code != 'm/b' and swag_offer_code != 'm' and swag_offer_code != 'b':
                    redeem_swag_code(swag_offer_code, offer=True)
                    REDEEMED.append(code)


if __name__ == '__main__':
    if HOURLY:
        # Login to Swagbucks/ Load cookies once if --hourly argument is passed
        login_SB(config.EMAIL,config.PASSWORD, driver)
        while True:
            # Keep running the bot until you stop the bot or some unknown error occurs
            try:
                console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}][/bold green] [bold yellow]Fetching sbcodez.com for Swag Codes...[/bold yellow]")
                main()
                console.print(f"[bold green][{datetime.now().strftime('%H:%M:%S')}][/bold green] [bold yellow]Finished running bot this iteration. Fetching again for Swag Codes in 1 hour...[/bold yellow]")
                # run again in 1 hour
                sleep(3600)
            # Ctrl+C to exit bot
            except KeyboardInterrupt:
                console.print('\nExiting bot...', style='bold bright_red', highlight=False)
                break
            # Exit bot if some unknown error occurs
            except Exception as e:
                console.print(e, style='bold underline red')
                console.print('An error occurred. Exiting bot...', style='bold bright_red', highlight=False)
                break
    else:
        # run once
        main()