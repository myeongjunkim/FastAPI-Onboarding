from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

STOCK_DATA_SOURCE_URL = (
    "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201"
)


def stock_data_crawler():
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )
    driver.maximize_window()
    driver.implicitly_wait(20)

    driver.get(STOCK_DATA_SOURCE_URL)

    driver.find_element(
        "xpath",
        '//*[@id="jsMdiMenu"]/div[4]/ul/li[1]/ul/li[2]/div/div[1]/ul/li[2]/a',
    ).click()

    driver.find_element(
        "xpath",
        '//*[@id="jsMdiMenu"]/div[4]/ul/li[1]/ul/li[2]/div/div[1]/ul/li[2]/ul/li[1]/a',
    ).click()
    driver.find_element(
        "xpath",
        '//*[@id="jsMdiMenu"]/div[4]/ul/li[1]/ul/li[2]'
        "/div/div[1]/ul/li[2]/ul/li[1]/ul/li[1]/a",
    ).click()

    driver.find_element("xpath", '//*[@id="jsMdiContent"]/div/div[1]/div[1]/div[2]')

    element = driver.find_element(
        "xpath", '//*[@id="jsMdiContent"]/div/div[1]/div[1]/div[2]'
    )
    driver.execute_script("arguments[0].scrollBy(0,500);", element)

    table_tag = driver.find_element(
        "xpath",
        '//*[@id="jsMdiContent"]/div/div[1]/div[1]/div[1]/div[2]/div/div/table/tbody',
    )
    table_rows = table_tag.find_elements("tag name", "tr")

    for row in table_rows:
        table_data = row.find_elements("tag name", "td")
        code = table_data[0].text
        name = table_data[1].text
        market = table_data[2].text
        print(code, name, market)


stock_data_crawler()
