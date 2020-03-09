#!python3
import bs4, requests, csv, time, json
from datetime import date
from selenium import webdriver


browser = webdriver.Firefox()
browser.get('industrial-auction-site-goes-here')


def soldDetection(browser):
    #Select the timer and check if it == "Lot Closed" once lot is closed send the entire container information to getData() to extract price and details
   
    while True:
        elems = browser.find_elements_by_xpath("//*[contains(text(), 'Closing bid')]")
        if not elems:
            print('Watching', end="\r")
            continue
        label = elems[0].text
        if label == 'Closing bid': # Once the words "Closing bid is detected" collect soup
            # TODO bug where item has 0 bids and doesn't contain "Closing bid" and prevents watching others.
            # grab entire div for the card with data for the getData()
            soup = bs4.BeautifulSoup(browser.page_source,'html.parser')
            #html = soup.contents # Optional export of html once collected
            #html = soup.prettify("utf-8")
            # with open("output1.html", "wb") as file:
            #     file.write(html)
            browser.refresh()          
            return soup

def locateSale(soup): #FIXME if lot has no bids and closes locate Sale loops endlessly without finding anything
    while True:
        container = soup.find_all('li', class_='current-price')
        for child in container:
            soldLabel = child.contents[1].contents[0].string
            #soldLabel.replace('<span>', '')
            #print (soldLabel)
            if soldLabel == 'Closing bid':
                # grab entire div for the card with data for the getData()
                print('Found')
                parentDiv = soldLabel.find_parent('div', class_='lot-single')
                #print(parentDiv)
                return parentDiv
            if soldLabel == "Current Bid": 
                continue
            #TODO detect if lot closed with no bids, maybe this should be saved elseware to have a list of items not sold
        else:
            continue

def getData(parentDiv): # This function takes in the div that contained the trigger 'Lot Closed' and extracts the price and details of the item
    auctionDict = dict()
    #print(parentDiv)

    # Scrape the price of the item for sale store in dict
    priceElems = parentDiv.find('strong').find_all_next(string=True) #this returns the $ value currency is collected later by selecting the [2] in array
    
    # Scrape the details of the item for sale
    discElems = parentDiv.find('div', class_='description').p.contents #this returns the discription at the moment the program is run
    
    # Scrape the Auctioneer for item
    auctioneerElem = parentDiv.find('a', class_='a-wrapped click-track').contents

    price = priceElems[0]
    currency = priceElems[2]
    disc = discElems[0]
    auctioneer = auctioneerElem[0]
    today = date.today()

    auctionDict['Discription'] = disc
    auctionDict['Price'] = price 
    auctionDict['Currency'] = currency
    auctionDict['Date'] = today
    auctionDict['auctioneer'] = auctioneer
    print(auctionDict)

    #Write Dict to a CSV file
    with open('auctionscrape.csv', 'a', newline='') as csvFile:
        wr = csv.writer(csvFile)
        for key, value in auctionDict.items():
            wr.writerow([key, value])  
    csvFile.close()
    
        


def main():
    while True:
        
        getData(locateSale(soldDetection(browser))) #soldDetection(browser) when running complete
        time.sleep(1)
        continue

if __name__ == '__main__':
    main()