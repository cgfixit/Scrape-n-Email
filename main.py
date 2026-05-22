from bs4 import BeautifulSoup
import requests, io, os
import drudgeScraper, rcpScraper, clistScraper
import mailer

def main():
    rcpScraper.scrape()
    clistScraper.scrape()

if __name__ == "__main__":
    main()
    mailer.send_all()
    os.system('msg * "GrEaT sUcCes$!!" & timeout /t 003 && exit') #Comment out if not using windows or dont want the popup after completion
    quit()
