#import libraries
import pandas as pd
import numpy as np
from numpy import nan
from numpy.polynomial import Polynomial as P

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException

import time
from tqdm import tqdm

import pymannkendall as mk

#from multiprocessing import Manager
import random
from multiprocessing import Lock
from functools import partial
import multiprocess as mp

import os
import re
import pdb
from locale import atof, setlocale, LC_NUMERIC
setlocale(LC_NUMERIC, '')

#Set up driver
if __name__ == '__main__':
    driver = webdriver.Chrome(ChromeDriverManager().install())
    #data = pd.read_csv('fa_stats.csv')

    '''Get tickers that pass initial finviz test'''
    def get_finviz_tickers(save_path, n=100):
        '''n must be greater than or equal to 20'''
        #url = 'https://finviz.com/screener.ashx?v=111&f=fa_eps5years_o15,fa_roe_o15&ft=2&o=-marketcap'
        url = 'https://finviz.com/screener.ashx?v=111&f=cap_midover,fa_eps5years_o15,fa_roe_o15&ft=4&o=-marketcap'
        driver.get(url)
        time.sleep(2)

        finviz_xpath = '//*[@id="screener-views-table"]/tbody/tr[4]/td/table/tbody'
        finviz = driver.find_element(By.XPATH, finviz_xpath).text
        finviz = finviz.split('\n')
        finviz = [s for s in finviz if not re.search(r'\d',s)]
        finviz = [s for s in finviz if s.isupper()]
        possible = list(pd.read_csv('listOfStockTickers.csv')['Symbol'])
        tickers = [t for t in finviz if t in possible]
        tickers = [t for t in finviz if t!='USA']

        n-=20
        k = n/20

        if(n > 0):
            for i in range(1, int(k+1)):
                url = f'https://finviz.com/screener.ashx?v=111&f=fa_eps5years_o15,fa_roe_o15&ft=2&o=-marketcap&r={21*i}'
                driver.get(url)
                time.sleep(2)

                finviz_xpath = '//*[@id="screener-views-table"]/tbody/tr[4]/td/table/tbody'
                finviz = driver.find_element(By.XPATH, finviz_xpath).text
                finviz = finviz.split('\n')
                finviz = [s for s in finviz if not re.search(r'\d',s)]
                finviz = [s for s in finviz if s.isupper()]
                for t in finviz:
                    if(t in possible and t!='USA'):
                        tickers.append(t)

        driver.close()

        df = pd.DataFrame(data={'Tickers': tickers})
        df.to_csv(save_path, index=False)

        return

    get_finviz_tickers('all_passed_tickers.csv', n=459) #get top 40 that passed the finviz test
    #data = pd.read_csv('fa_stats.csv')
    #buffet_data = pd.read_csv('buffet_fa.csv')

    '''Get a list of the last 10 years' and current ROE of the stock'''
    def update_stock_fastats(ticker, path):
        print(f'COLLECTING DATA FOR:{ticker}')
        print(f'SAVING TO:{path}')

        data = pd.read_csv(path)
        url = f'https://www.morningstar.com/search?query={ticker}'
        driver.get(url)

        #time.sleep(20) #!!!what is the optimal pause to ensure a crash doesn't happen? Or maybe the solution is not a pause?
        #Search the ticker on the morningstar home page
        #search_xpath = '//*[@id="__layout"]/div/div/div[2]/div[1]/div/header/div/div[1]/div/form/div/input'
        #search = driver.find_element(By.XPATH, search_xpath)
        #search.send_keys(ticker)
        #search.send_keys(Keys.ENTER)

        #Click on the first result, which should be the stock's info page
        ticker_page_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/main/div/div/div[1]/div/section[1]/div[2]/a'
        ticker_page = wait.until(ec.visibility_of_element_located((By.XPATH, ticker_page_xpath)))
        #ticker_page = wait.until(ec.visibility_of_element_located((By.XPATH, ticker_page_xpath)))
        ticker_page.click()
        #time.sleep(10)

        #Go to the stock's valuation page
        val_page = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="stock_tab-valuation"]')))
        #val_page = driver.find_element_by_id("stock__tab-valuation")
        val_page.click()
        #time.sleep(10)

        #Go to Operating and Efficiency
        oae = wait.until(ec.visibility_of_element_located((By.ID, 'keyStatsOperatingAndEfficiency')))
        #oae=driver.find_element_by_id("keyStatsOperatingAndEfficiency")
        oae.click();
        #time.sleep(10)

        #Get ROE
        #roe_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/main/div[2]/div/div/div[1]/sal-components/div/sal-components-stocks-valuation/div/div[2]/div/div/div[4]/div/div/div/div/div[1]/table/tbody/tr[7]'
        roe_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-valuation/div/div[2]/div/div/div[4]/div/div/div/div/div[1]/table/tbody/tr[7]'
        try:
            #roe = driver.find_element(By.XPATH, roe_xpath).text
            roe = wait.until(ec.visibility_of_element_located((By.XPATH, roe_xpath))).text
        except:
            pdb.set_trace()
        roe = roe.replace('Return on Equity % ','')
        roe = roe.split()
        roe = roe[:-1]

        '''Get a list of the last 10 years' and current EPSg of the stock'''
        #Go to Growth
        #growth = driver.find_element_by_id("keyStatsgrowthTable")
        growth = wait.until(ec.visibility_of_element_located((By.ID, 'keyStatsgrowthTable')))
        growth.click()
        #time.sleep(10)

        #Get EPSg
        #epsg_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/main/div[2]/div/div/div[1]/sal-components/div/sal-components-stocks-valuation/div/div[2]/div/div/div[3]/div/div/div/div/div[1]/table/tbody/tr[17]'
        epsg_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-valuation/div/div[2]/div/div/div[3]/div/div/div/div/div/div[1]/table/tbody/tr[17]'
        try:
            #epsg = driver.find_element(By.XPATH, epsg_xpath).text
            epsg = wait.until(ec.visibility_of_element_located((By.XPATH, epsg_xpath))).text
        except:
            pdb.set_trace()
        epsg = epsg.replace('Year Over Year ','')
        epsg = epsg.split()

        '''Get a list of the past 10 years' and current stock PE'''
        #pe_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/main/div[2]/div/div/div[1]/sal-components/div/sal-components-stocks-valuation/div/div[1]/div/div/div[2]/div/div/table/tbody/tr[3]'
        pe_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-valuation/div/div[1]/div/div/div[2]/div/div/table/tbody/tr[3]'
        try:
            #roe = driver.find_element(By.XPATH, roe_xpath).text
            pe = wait.until(ec.visibility_of_element_located((By.XPATH, pe_xpath))).text
        except:
            pdb.set_trace()
        #pe = driver.find_element(By.XPATH, pe_xpath).text
        pe = pe.replace("\n", " ")
        pe = pe.replace("Price/Earnings ","")
        pe = pe.split()
        pe_5yr = pe[-2] #5yr average according to morningstar
        pe = pe[:-2] #pe of the last 10 years and current

        '''Get the stock's free cash flow growth % for the past 10 years'''
        #Go the Cash Flow
        cf = wait.until(ec.visibility_of_element_located((By.ID, 'keyStatscashFlow')))
        #cf = driver.find_element_by_id("keyStatscashFlow")
        cf.click()
        #time.sleep(10)

        #Get the free cash flow growth
        free_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-valuation/div/div[2]/div/div/div[6]/div/div/div/div/div/div[1]/table/tbody/tr[2]'
        #free = driver.find_element(By.XPATH, free_xpath).text
        try:
            #roe = driver.find_element(By.XPATH, roe_xpath).text
            free = wait.until(ec.visibility_of_element_located((By.XPATH, free_xpath))).text
        except:
            pdb.set_trace()
        free = free.replace("Free Cash Flow Growth % YOY ","")
        free = free.split()
        free = free[:-1]

        '''!!!Get CFs. Add get_cf_eps'''


        '''Get EPS'''


        '''Get the stock's EPSg for next year and the EPSg 5 year average from finviz.com'''
        #Go to finviz.com
        url = f'https://finviz.com/quote.ashx?t={ticker}'
        driver.get(url)
        time.sleep(2)

        #Get next year's estimated epsg
        epsg_next_xpath = '/html/body/div[4]/div/table[2]/tbody/tr[5]/td[6]'
        epsg_next = driver.find_element(By.XPATH, epsg_next_xpath).text

        #Get the EPSg for the last 5 years
        epsg_5yavg_xpath = '/html/body/div[4]/div/table[2]/tbody/tr[7]/td[6]'
        epsg_5yavg = driver.find_element(By.XPATH, epsg_5yavg_xpath).text

        #pdb.set_trace()
        if(data['Ticker'].str.contains(ticker).any()):
            data.loc[data.index[data['Ticker']==ticker].to_list()[0], ['ROE (10yrs)','EPSg (10yrs)','Free Cash Flow Growth % (YOY)', 'PE','EPSg (next)','EPSg (5yr avg)']] = [roe, epsg, free, pe, epsg_next, epsg_5yavg]
        else:
            data.loc[len(data.index)] = [ticker, roe, epsg, free, pe, epsg_next, epsg_5yavg]

        data.to_csv(path,index=False)
        print(f'SAVED {ticker} TO CSV')

        return

    driver = webdriver.Chrome(ChromeDriverManager().install())
    wait = WebDriverWait(driver, 30)
    #update_stock_fastats('TSM', 'CFu_fa.csv')
    #buffet_tickers = ['AAPL','BAC','AXP','CVX','KO','KHC','MCO','OXY','USB','ATVI','DVA','HPQ','BK']
    #cfu_tickers = ['KO', 'V', 'MSFT', 'AMZN', 'TROW','CPRT','CDW','BAH','MA','COST','POOL','HD','UNH','PSA'
    #                ,'BBWI','WMT','ROST','LVMHF','RACE','VWAGY','QSR','MAR','QL']
    #cfu_tickers_missed = ['BAH','MA','COST','POOL','HD']
    for ticker in tqdm(tickers):
        update_stock_fastats(ticker, 'CFu_fa.csv')

    driver.close()


    '''Multiprocess the scraping process'''
    '''!!!Bug: if element does not appear, the process is just frozen and there is no break'''
    '''!!!Does multiprocess version work?'''
    def update_stock_fastats_mp(ticker, path, lock):
        print(f'COLLECTING DATA FOR:{ticker}')

        driver = webdriver.Chrome(ChromeDriverManager().install())
        wait = WebDriverWait(driver, 30)

        url = f'https://www.morningstar.com/search?query={ticker}'
        driver.get(url)

        #time.sleep(20) #!!!what is the optimal pause to ensure a crash doesn't happen? Or maybe the solution is not a pause?
        #Search the ticker on the morningstar home page
        #search_xpath = '//*[@id="__layout"]/div/div/div[2]/div[1]/div/header/div/div[1]/div/form/div/input'
        #search = driver.find_element(By.XPATH, search_xpath)
        #search.send_keys(ticker)
        #search.send_keys(Keys.ENTER)

        #Click on the first result, which should be the stock's info page
        ticker_page_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/main/div/div/div[1]/div/section[1]/div[2]/a'
        ticker_page = wait.until(ec.visibility_of_element_located((By.XPATH, ticker_page_xpath)))
        #ticker_page = wait.until(ec.visibility_of_element_located((By.XPATH, ticker_page_xpath)))
        ticker_page.click()
        #time.sleep(10)

        #Go to the stock's valuation page
        val_page = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="stock_tab-valuation"]')))
        #val_page = driver.find_element_by_id("stock__tab-valuation")
        val_page.click()
        #time.sleep(10)

        #Go to Operating and Efficiency
        oae = wait.until(ec.visibility_of_element_located((By.ID, 'keyStatsOperatingAndEfficiency')))
        #oae=driver.find_element_by_id("keyStatsOperatingAndEfficiency")
        oae.click();
        #time.sleep(10)

        #Get ROE
        #roe_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/main/div[2]/div/div/div[1]/sal-components/div/sal-components-stocks-valuation/div/div[2]/div/div/div[4]/div/div/div/div/div[1]/table/tbody/tr[7]'
        roe_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-valuation/div/div[2]/div/div/div[4]/div/div/div/div/div[1]/table/tbody/tr[7]'
        try:
            #roe = driver.find_element(By.XPATH, roe_xpath).text
            roe = wait.until(ec.visibility_of_element_located((By.XPATH, roe_xpath))).text
        except:
            pdb.set_trace()
        roe = roe.replace('Return on Equity % ','')
        roe = roe.split()
        roe = roe[:-1]

        '''Get a list of the last 10 years' and current EPSg of the stock'''
        #Go to Growth
        #growth = driver.find_element_by_id("keyStatsgrowthTable")
        growth = wait.until(ec.visibility_of_element_located((By.ID, 'keyStatsgrowthTable')))
        growth.click()
        #time.sleep(10)

        #Get EPSg
        #epsg_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/main/div[2]/div/div/div[1]/sal-components/div/sal-components-stocks-valuation/div/div[2]/div/div/div[3]/div/div/div/div/div[1]/table/tbody/tr[17]'
        epsg_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-valuation/div/div[2]/div/div/div[3]/div/div/div/div/div/div[1]/table/tbody/tr[17]'
        try:
            #epsg = driver.find_element(By.XPATH, epsg_xpath).text
            epsg = wait.until(ec.visibility_of_element_located((By.XPATH, epsg_xpath))).text
        except:
            pdb.set_trace()
        epsg = epsg.replace('Year Over Year ','')
        epsg = epsg.split()

        '''Get a list of the past 10 years' and current stock PE'''
        #pe_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/main/div[2]/div/div/div[1]/sal-components/div/sal-components-stocks-valuation/div/div[1]/div/div/div[2]/div/div/table/tbody/tr[3]'
        pe_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-valuation/div/div[1]/div/div/div[2]/div/div/table/tbody/tr[3]'
        try:
            #roe = driver.find_element(By.XPATH, roe_xpath).text
            pe = wait.until(ec.visibility_of_element_located((By.XPATH, pe_xpath))).text
        except:
            pdb.set_trace()
        #pe = driver.find_element(By.XPATH, pe_xpath).text
        pe = pe.replace("\n", " ")
        pe = pe.replace("Price/Earnings ","")
        pe = pe.split()
        pe_5yr = pe[-2] #5yr average according to morningstar
        pe = pe[:-2] #pe of the last 10 years and current

        '''Get the stock's free cash flow growth % for the past 10 years'''
        #Go the Cash Flow
        cf = wait.until(ec.visibility_of_element_located((By.ID, 'keyStatscashFlow')))
        #cf = driver.find_element_by_id("keyStatscashFlow")
        cf.click()
        #time.sleep(10)

        #Get the free cash flow growth
        free_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-valuation/div/div[2]/div/div/div[6]/div/div/div/div/div/div[1]/table/tbody/tr[2]'
        #free = driver.find_element(By.XPATH, free_xpath).text
        try:
            #roe = driver.find_element(By.XPATH, roe_xpath).text
            free = wait.until(ec.visibility_of_element_located((By.XPATH, free_xpath))).text
        except:
            pdb.set_trace()
        free = free.replace("Free Cash Flow Growth % YOY ","")
        free = free.split()
        free = free[:-1]

        '''!!!Get the stock's CFO, CFI and CFF
        '''
        '''#Go to Financials
        financials_id = 'stock_tab-financials'
        financials = wait.until(ec.visibility_of_element_located((By.ID, financials_id)))
        financials.click()

        #Go the Cash Flow
        cf_id = 'cashFlow'
        cf = wait.until(ec.visibility_of_element_located((By.ID, cf_id)))
        cf.click()

        #Expand detail view
        expand_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-financials/div/div/div/div/div/div[2]/div[2]/div/div/a/span[1]'
        expand = wait.until(ec.visibility_of_element_located((By.XPATH, expand_xpath)))
        expand.click()

        #collapse CFO row
        cfo_xpath = '//*[@id="tg-3476"]/div[3]/div[2]/div[1]/div/div[13]'
        try:
            cfo_ = wait.until(ec.visibility_of_element_located((By.XPATH, cfo_xpath))).text #!!!can't find cfo element by xpath
        except:
            pdb.set_trace()
'''
        '''!!!need to figure out how to get the stock's EPS
        #Click 'Expand Detail View'
        expand_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/main/div[2]/div/div/div[1]/sal-components/div/sal-components-stocks-financials/div/div/div/div/div/div[2]/div[2]/div/div/a/span[1]'
        expand = driver.find_element(By.XPATH, expand_xpath)
        expand.click()

        #Get EPS
        eps_xpath = '//*[@id="tg-3009"]/div[3]/div[2]/div[1]/div/div[19]'
        eps_xpath='//*[@id="tg-3009"]/div[3]/div[1]/div/div/div[17]/div/div/div'
        eps = driver.find_element(By.XPATH, eps_xpath).text'''

        '''Get the stock's EPSg for next year and the EPSg 5 year average from finviz.com'''
        #Go to finviz.com
        url = f'https://finviz.com/quote.ashx?t={ticker}'
        driver.get(url)
        time.sleep(2)

        #Get next year's estimated epsg
        epsg_next_xpath = '/html/body/div[4]/div/table[2]/tbody/tr[5]/td[6]'
        epsg_next = driver.find_element(By.XPATH, epsg_next_xpath).text

        #Get the EPSg for the last 5 years
        epsg_5yavg_xpath = '/html/body/div[4]/div/table[2]/tbody/tr[7]/td[6]'
        epsg_5yavg = driver.find_element(By.XPATH, epsg_5yavg_xpath).text

        driver.close()
        print(f"FINISHED DATA COLLECTION FOR: {ticker}")

        '''Now that the data has been collected, save data to csv file given lock is acquirable aka no other processes saving atm'''
        with lock:
            sleep_value = random.random()
            print(f'>process {ticker} got the lock, sleeping for {sleep_value}')
            time.sleep(sleep_value)

            print(f"SAVING {ticker} TO: {path}")
            data = pd.read_csv(path)
            if(data['Ticker'].str.contains(ticker).any()):
                data.loc[data.index[data['Ticker']==ticker].to_list()[0], ['ROE (10yrs)','EPSg (10yrs)','Free Cash Flow Growth % (YOY)', 'PE','EPSg (next)','EPSg (5yr avg)']] = [roe, epsg, free, pe, epsg_next, epsg_5yavg]
            else:
                data.loc[len(data.index)] = [ticker, roe, epsg, free, pe, epsg_next, epsg_5yavg]
            data.to_csv(path,index=False)
            print(f'SAVED {ticker} TO {path}')

        data = pd.read_csv(path)
        print(f"DATA:{data}")

        return


    path = 'fa_stats.csv'
    all_tickers = pd.read_csv('all_passed_tickers.csv')['Tickers']
    i = int(len(all_tickers)/3-1)
    tickers = all_tickers.loc[i:]
    #tickers = ['AAPL','BAC','AXP','CVX','KO','KHC','MCO']

    with mp.Manager() as manager:
        lock = manager.Lock()
        with mp.Pool(mp.cpu_count()-1) as p:
            items = [(ticker, path, lock) for ticker in tickers+['PAYC']]
            result = p.starmap_async(update_stock_fastats_mp, items)
            result.wait()
            #p.terminate()
            #p.join()

'''    def calc_fairvalue(beta, eps, pe_5yr_avg, pe_current, spx_pe=18.86):
        Calculate the fair values for a stock given EPS, stock PEs, and
        !!!vectorize this process to be instant. For loops are for noobs
        INPUTS:
            beta: the stocks's beta (float or string, need to add an if statement to filter)
            eps: the stock's past 5yr EPS (list)
            pe_5yr_avg: average of the stock's PE for the past 5 years (float)
            pe_current: the stock's current PE (float)
            spx_pe: the SP500's current PE ratio (float)
        OUTPUT:
            fair_value_spx_cons, fair_value_5y_cons, fair_value_current_cons, fair_value_spx_aggr, fair_value_5y_aggr, fair_value_current_aggr
        
        epsg = (eps[-1]/eps[0])**(1/4)-1
        eps_t1 = eps[-1]*(1+epsg)

        #SPX fair value
        if beta < 1:
            pe = spx_pe
        else:
            pe = spx_pe*beta
        earnings_t1 = eps_t1*pe
        fair_value_spx_cons = earnings_t1/(1+0.095)
        fair_value_spx_aggr = earnings_t1/(1+0.15)

        #5y PE fair value
        pe = pe_5yr_avg
        earnings_t1 = eps_t1*pe
        fair_value_5y_cons = earnings_t1/(1+0.095)
        fair_value_5y_aggr = earnings_t1/(1+0.15)

        #Current PE fair value
        pe = pe_current
        earnings_t1 = eps_t1*pe
        fair_value_current_cons = earnings_t1/(1+0.095)
        fair_value_current_aggr = earnings_t1/(1+0.2)

        return fair_value_spx_cons, fair_value_5y_cons, fair_value_current_cons, fair_value_spx_aggr, fair_value_5y_aggr, fair_value_current_aggr'''

    def random_identifier(n):
        range_start = 10**(n-1)
        range_end = (10**n)-1
        return random.randint(range_start, range_end)

    def get_cf_eps(ticker,path, skip_beta=False):
        driver = webdriver.Chrome(ChromeDriverManager().install())
        wait = WebDriverWait(driver, 30)
        timeout = time.time() + 60*5
        #print(f'SAVING TO {path}')

        #data = pd.read_csv(path)
        print(f"Beginning CF and EPS data extraction for {ticker}...")
        url = f'https://www.morningstar.com/search?query={ticker}'
        driver.get(url)

        #Go to ticker's page
        ticker_page_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/main/div/div/div[1]/div/section[1]/div[2]/a'
        ticker_page = wait.until(ec.visibility_of_element_located((By.XPATH, ticker_page_xpath)))
        #ticker_page = wait.until(ec.visibility_of_element_located((By.XPATH, ticker_page_xpath)))
        ticker_page.click()

        #Go to valuations page
        val_page = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="stock_tab-valuation"]')))
        val_page.click() #Go to valuation page
        pe_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-valuation/div/div[1]/div/div/div[2]/div/div/table/tbody/tr[3]'
        pe = wait.until(ec.visibility_of_element_located((By.XPATH, pe_xpath))).text
        pe = pe.replace("\n", " ")
        pe = pe.replace("Price/Earnings ","")
        pe = pe.split()
        pe_5yr = pe[-2] #5yr average according to morningstar
        pe_10yr = pe[:-2] #pe of the last 10 years and current
        pe_5yr = pe_10yr[5:-1] #pe of the last 5 years
        pe_current = pe_10yr[-1] #current pe
        #def reject_outliers(data, m = 2.):
        #    d = np.abs(data - np.median(data))
        #    mdev = np.median(d)
        #    s = d/mdev if mdev else 0.
        #    return data[s<m]
        #pe_5yr_avg = np.mean(reject_outliers(pe_5yr))

        #Go to Financials
        financials_id = 'stock_tab-financials'
        financials = wait.until(ec.visibility_of_element_located((By.ID, financials_id)))
        financials.click()

        #Get CF
        if os.path.exists("/Users/cyrusleung/Downloads/Cash Flow_Annual_As Originally Reported.xls"):
            os.remove("/Users/cyrusleung/Downloads/Cash Flow_Annual_As Originally Reported.xls")
            print(f"Removed old {ticker} CF file")
        else:
            print(f"Could not find old {ticker} CF file to delete")

        cf_id = 'cashFlow'
        cf = wait.until(ec.visibility_of_element_located((By.ID, cf_id)))
        cf.click()
        try:
            expand_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-financials/div/div/div/div/div/div[2]/div[2]/div/div/a/span[1]'
            expand = wait.until(ec.visibility_of_element_located((By.XPATH, expand_xpath)))
            expand.click()
        except TimeoutException as ex:
            driver.close()
            return "Exception has been thrown. " + str(ex)

        export_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-financials/div/div/div/div/div/div[2]/div[1]/div[2]/div/div/div/div/div/div[2]/div/button'
        export = wait.until(ec.visibility_of_element_located((By.XPATH, export_xpath)))
        export.click()

        while not os.path.exists("/Users/cyrusleung/Downloads/Cash Flow_Annual_As Originally Reported.xls"):
            print("File not in Downloads folder yet. Waiting 1 sec...")
            time.sleep(1)
            if time.time() > timeout:
                #!!!sometimes export fails, reloading does the job so add reloading as a function
                return f"Could not find {ticker} CF file within 10 min, skipping {ticker}"

        #Get Income
        if os.path.exists("/Users/cyrusleung/Downloads/Income Statement_Annual_As Originally Reported.xls"):
            os.remove("/Users/cyrusleung/Downloads/Income Statement_Annual_As Originally Reported.xls")
            print(f"Removed old {ticker} INCOME file")
        else:
            print(f"Could not find old {ticker} INCOME file to delete")

        driver.refresh()
        expand_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-financials/div/div/div/div/div/div[2]/div[2]/div/div/a'
        expand = wait.until(ec.visibility_of_element_located((By.XPATH, expand_xpath)))
        expand.click() #Expand to access export button
        export_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-financials/div/div/div/div/div/div[2]/div[1]/div[2]/div/div/div/div/div/div[2]/div/button'
        export = wait.until(ec.visibility_of_element_located((By.XPATH, export_xpath)))
        export.click() #Export income statement

        while not os.path.exists("/Users/cyrusleung/Downloads/Income Statement_Annual_As Originally Reported.xls"):
            print("File not in Downloads folder yet. Waiting 1 sec...")
            time.sleep(1)
            if time.time() > timeout+60:
                return f"Could not find {ticker} INCOME file within 10 min, skipping {ticker}"

        #Analyze CF
        df = pd.DataFrame(pd.read_excel("/Users/cyrusleung/Downloads/Cash Flow_Annual_As Originally Reported.xls"))

        #Get CFO
        cfo_row = None
        if (df.loc[df[f'{ticker}_cash-flow_Annual_As_Originally_Reported']=='Cash Flow from Operating Activities, Indirect']).empty:
            cfo_row = df.loc[df[f'{ticker}_cash-flow_Annual_As_Originally_Reported']=='    Cash Flow from Operating Activities, Indirect'].iloc[0]
        else:
            cfo_row = df.loc[df[f'{ticker}_cash-flow_Annual_As_Originally_Reported']=='Cash Flow from Operating Activities, Indirect'].iloc[0]
        #pdb.set_trace()
        cfo = []
        for year in df.columns[1:-1]:
            cfo.append(float(cfo_row[year]))

        #Get CFI
        cfi_row = None
        if (df.loc[df[f'{ticker}_cash-flow_Annual_As_Originally_Reported']=='Cash Flow from Investing Activities']).empty:
            cfi_row = df.loc[df[f'{ticker}_cash-flow_Annual_As_Originally_Reported']=='    Cash Flow from Investing Activities'].iloc[0]
        else:
            cfi_row = df.loc[df[f'{ticker}_cash-flow_Annual_As_Originally_Reported']=='Cash Flow from Investing Activities'].iloc[0]
        cfi = []
        for year in df.columns[1:-1]:
            cfi.append(float(cfi_row[year]))

        #Get CFF
        cff_row = None
        if (df.loc[df[f'{ticker}_cash-flow_Annual_As_Originally_Reported']=='Cash Flow from Financing Activities']).empty:
            cff_row = df.loc[df[f'{ticker}_cash-flow_Annual_As_Originally_Reported']=='    Cash Flow from Financing Activities'].iloc[0]
        else:
            cff_row = df.loc[df[f'{ticker}_cash-flow_Annual_As_Originally_Reported']=='Cash Flow from Financing Activities'].iloc[0]
        cff = []
        for year in df.columns[1:-1]:
            cff.append(float(cff_row[year]))

        #Delete the xls file after done extracting the data I want
        if os.path.exists("/Users/cyrusleung/Downloads/Cash Flow_Annual_As Originally Reported.xls"):
            os.remove("/Users/cyrusleung/Downloads/Cash Flow_Annual_As Originally Reported.xls")
        else:
            print(f"Could not find {ticker} CF file to delete")

        #Analyze EPS

        #income_id = 'incomeStatement'
        #income = wait.until(ec.visibility_of_element_located((By.ID, income_id)))
        #income.click() #Go to income statement

        df = pd.DataFrame(pd.read_excel("/Users/cyrusleung/Downloads/Income Statement_Annual_As Originally Reported.xls"))
        eps_row = None
        try:
            eps_row = df.loc[df[f'{ticker}_income-statement_Annual_As_Originally_Reported']=='Diluted EPS'].iloc[-1]
        except:
            return "PROBLEM: Issue with {ticker} EPS"
        eps = [float(eps_row[year]) for year in df.columns[1:-1]]

        #Delete the xls file after done extracting the data I want
        if os.path.exists("/Users/cyrusleung/Downloads/Income Statement_Annual_As Originally Reported.xls"):
            os.remove("/Users/cyrusleung/Downloads/Income Statement_Annual_As Originally Reported.xls")
        else:
            print(f"Could not find {ticker} INCOME file to delete")

        if skip_beta:
            print("Skipped Beta.")
            driver.close()
            print(f"FINISHED DATA COLLECTION FOR: {ticker}")

            print(f"SAVING {ticker} TO: {path}")
            data = pd.read_csv(path)
            if (data['Ticker'].str.contains(ticker).any()):
                cfo = str(cfo)
                cfi = str(cfi)
                cff = str(cff)
                eps = str(eps)
                pe_10yr = str(pe_10yr)
                # pdb.set_trace()
                data.loc[data.index[data['Ticker'] == ticker].to_list()[0], ['CFO', 'CFI', 'CFF', 'EPS','PE (10yr & current)']] = [cfo,cfi,cff,eps,pe_10yr]
            else:
                print(f"{Ticker} DNE")
            data.to_csv(path, index=False)
            print(f'SAVED {ticker} TO {path}')

            data = pd.read_csv(path)
            print(f"DATA:{data[data['Ticker'] == ticker][['CFO', 'EPS']]}")

            return f"COMPLETED: {ticker}"

        #Get beta
        print(f"GETTING beta for {ticker} too.")
        url = f'https://finviz.com/quote.ashx?t={ticker}&p=d'
        driver.get(url)
        time.sleep(2)
        beta_xpath = '/html/body/div[4]/div/table[2]/tbody/tr[7]/td[12]/b'
        beta = wait.until(ec.visibility_of_element_located((By.XPATH, beta_xpath))).text

        #fair_value_spx_cons, fair_value_5y_cons, fair_value_current_cons, fair_value_spx_aggr, fair_value_5y_aggr, fair_value_current_aggr = calc_fairvalue(beta, eps, pe_5yr_avg, pe_current)

        driver.close()
        print(f"FINISHED DATA COLLECTION FOR: {ticker}")


        print(f"SAVING {ticker} TO: {path}")
        data = pd.read_csv(path)
        if(data['Ticker'].str.contains(ticker).any()):
            cfo = str(cfo)
            cfi = str(cfi)
            cff = str(cff)
            eps = str(eps)
            pe_10yr = str(pe_10yr)
            #pdb.set_trace()
            data.loc[data.index[data['Ticker']==ticker].to_list()[0], ['CFO', 'CFI', 'CFF', 'EPS', 'PE (10yr & current)','Beta']] = [cfo, cfi, cff, eps, pe_10yr, beta]
            #data.loc[data['Ticker']==ticker,['CFO', 'CFI', 'CFF', 'EPS', 'PE (10yr & current)','Beta']] = [[cfo, cfi, cff, eps, pe_10yr.tolist(), beta]]
        else:
            print(f"{Ticker} DNE")
        data.to_csv(path,index=False)
        print(f'SAVED {ticker} TO {path}')

        data = pd.read_csv(path)
        print(f"DATA:{data[data['Ticker']==ticker][['CFO','EPS']]}")

        return f"COMPLETED: {ticker}"

    path = 'fa_stats.csv'
    all_tickers = pd.read_csv(path)['Ticker']
    #i = int(len(all_tickers)/3-1)
    #tickers1 = all_tickers.loc[:i]
    #tickers2 = all_tickers.loc[i:2*i]
    #tickers3 = all_tickers.loc[2*i:]
    missing_eps_tickers = ['KHC','TTE','AMT','IBN'] #Ticker H also has some problem too, Index error. List index out of bound
    #all_tickers.index()
    #list(tickers3).index('EC')
    #tickers1[tickers1=='GSK'].index[0]
    #list(tickers3)[list(tickers3).index('AVGO'):]
    for ticker in tqdm(list(all_tickers)[list(all_tickers).index('AVGO'):]):
        get_cf_eps(ticker,path, skip_beta=True)

    def get_beta(ticker):
        #Get stock beta
        url = f'https://finance.yahoo.com/quote/{ticker}?p={ticker}&.tsrc=fin-srch'
        driver.get(url)
        beta_xpath = '//*[@id="quote-summary"]/div[2]/table/tbody/tr[2]/td[2]'
        beta = wait.until(ec.visibility_of_element_located((By.XPATH, beta_xpath))).text
        beta = float(beta)
        return beta

'''---------------Part 2: Analyzing the Data------------------'''

    '''Helper functions'''
    def floatify_ind(list_val):
        '''Convert the individual elements in the list into my standard'''
        if(list_val=='—'):
            return '-'
        if(list_val=='-'):
            return '-'
        if(list_val=='––'):
            return '-'
        if(list_val[-1]=='%'):
            return float(list_val[:-1])
        if(list_val=='nan'):
            return '-'
        else:
            return atof(list_val)

    def floatify_beta(beta):
        if isinstance(beta, float):
            return beta
        if(beta=='—'):
            return '-'
        if(beta=='-'):
            return '-'
        if(beta=='––'):
            return '-'
        if(beta=='nan'):
            return '-'
        else:
            return atof(beta)

    def floatify(row_val):
        return list(map(floatify_ind, list(map(lambda s: s.replace("'",""), row_val.strip('][').split(', ')))))

    def floatify_eps(row_val):
        def floatify_helper(list_val):
            '''Convert the individual elements in the list into my standard'''
            if (list_val == '—'):
                return '-'
            if (list_val == '-'):
                return '-'
            if (list_val == '––'):
                return '-'
            if (list_val == 'nan'):
                return '-'
            else:
                try:
                    return atof(list_val)
                except:
                    return '-'
        return list(map(floatify_helper, list(map(lambda s: s.replace("'",""), row_val.strip('][').split(', ')))))

    #data['EPSg (next)'] = data['EPSg (next)'].map(floatify_ind)
    #data['EPSg (5yr avg)'] = data['EPSg (5yr avg)'].map(floatify_ind)

    '''ROE test
    ROE_5y: max score of 2, if it fails 1 year then score of 1, else score of 0
    ROE_10y: fails nonce: 3, fails once: 2, fails twice: 1; else 0
    '''

    #ROE_5y
    def roe_fail(n):
        if(n=='-'): return True
        if(n==''): return True
        if(n<12): return True
        return False

    def roe5y(roes):
        roe_5y = 2
        fail_count = sum(list(map(roe_fail, roes[5:])))
        roe_5y -= fail_count
        if(roe_5y <= 0): return 0
        return roe_5y

    #ROE_10y
    def roe10y(roes):
        roe_10y = 3
        fail_count = sum(list(map(roe_fail, roes)))
        roe_10y -= fail_count
        if(roe_10y <= 0): return 0
        return roe_10y

    '''EPS test
    EPSg_5y: fails nonce: 2, fails once: 1, else 0
    EPSg_10y: fails nonce: 2, fails once: 1, else 0
    '''

    #EPS_5y
    def epsg_fail(n):
        if(n=='-'): return True
        if(n<12): return True
        return False

    def epsg5y(epsgs):
        epsg_5y = 2
        fail_count = sum(list(map(epsg_fail, epsgs[6:])))
        epsg_5y -= fail_count
        if(epsg_5y <= 0): return 0
        return epsg_5y

    #EPSg_10y
    def epsg10y(epsgs):
        epsg_10y = 2
        fail_count = sum(list(map(epsg_fail, epsgs)))
        epsg_10y -= fail_count
        if(epsg_10y <= 0): return 0
        return epsg_10y

    '''Free cash flow test
    Requirements for a pass:
    1. at least 5 out of 10 years were positive
    2. The sum of all free cash flow growths are positive for all 10 years
    3. (for hard) the free cash flow growth is increasing
    '''

    def trenddetector(array_of_data, order=1):
        result = np.polyfit(list(map(float, range(len(array_of_data)))), array_of_data, order)
        slope = result[-2]
        return float(slope)

    #cfo_wmt = [25591,23257,28564,27389,31350,28337,27753,25255,36074,24181]

    def free_pos(f):
        if(f=='-'): return False
        return True

    def free_sum(frees):
        sum = 0
        for f in frees:
            if(f=='-'): sum+=0
            else: sum+=f
        return sum

    def free_soft(frees):
        if((sum(list(map(free_pos, frees))) >= 5)
            and free_sum(frees) >= 0):
            return 1
        return 0

    '''def free_hard(frees):
        if((len(list(filter(free_pos, frees))) >= 5)
            and free_sum(frees) >= 0
            and trenddetector(frees) >= 0):
            return 0.5
        return 0'''

    '''CF test, total = 3
    CFO: subtract 1 for every negative
    CFI: subtract 1 for every positive
    CFF: if majority positive, subtract 1 for every negative; if majority negative, subtract 1 for every positive; caveat: if transitioning (but how to define transition)

    !!!figure out bonus of if CFO is positive trend by some X% growth per year
    '''
    def cfo_test(cfo):
        '''
        Return 0 if fail nothing, return minus however many points for every failed case
        Failed case is if cfo is negative
        Add 0.5 if passes the positive 12%+ CFO trend test
        '''
        def helper(x):
            if x == '-':
                return -1
            if x>=0:
                return 0
            else:
                return -1
        '''sum_before = sum(list(map(helper, cfo)))
        if '-' in cfo:
            return sum_before
        if any(map(lambda x: True if isinstance(x,str) else False,cfo)):
            return sum_before
        if sum(np.polynomial.polynomial.polyfit(list(range(1,len(cfo)+1)),cfo,1)/cfo > 0.12) == 5:
            return sum_before+0.5
        else:
            return sum_before'''
        return sum(list(map(helper, cfo)))

    def cfi_test(cfi):
        '''
        Return 0 if fail nothing, return minus however many points for every failed case
        Failed case is if cfi is positive
        '''
        def helper(x):
            if x == '-':
                return -1
            if x<0:
                return 0
            else:
                return -1

        return sum(list(map(helper, cfi)))

    def cff_test(cff):
        '''
        Return 0 if fail nothing, return minus however many points for every failed case
        Failed case is if cfi is positive
        cff: list
        !!!consider another if case being the company is transitioning from growth to mature or mature to growth
        '''
        def helper(x):
            if x>=0:
                return 1
            else:
                return -1
        pos_count = np.sum(np.array(list(map(helper,cff))) >= 0, axis=0) #How many pos cff
        neg_count = np.sum(np.array(list(map(helper,cff))) < 0, axis=0) #How many neg cff
        if pos_count < neg_count:
            return -pos_count
        else:
            return -neg_count

    def cfi_test(cfi):
        '''
        CFI should be negative no matter the type of business.
        Subtract one point for every positive cfi year
        '''
        def helper(x):
            if isinstance(x, str):
                print(x, type(x))
            if x>=0:
                return -1
            else:
                return 0
        return sum(list(map(helper, cfi)))

    def calc_fairvalue(data_path, spx_pe=18.86):
        '''Calculate the fair values for a stock given EPS, stock PEs, and
        !!!vectorize this process to be instant. For loops are for noobs
        INPUTS:
            beta: the stocks's beta (float or string, need to add an if statement to filter)
            eps: the stock's past 5yr EPS (list)
            pe_5yr_avg: average of the stock's PE for the past 5 years (float)
            pe_current: the stock's current PE (float)
            spx_pe: the SP500's current PE ratio (float)
        OUTPUT:
            fair_value_spx_cons, fair_value_5y_cons, fair_value_current_cons, fair_value_spx_aggr, fair_value_5y_aggr, fair_value_current_aggr
        '''
        #Clean data first
        data = pd.read_csv(data_path)
        data['ROE (10yrs)'] = data['ROE (10yrs)'].map(floatify)
        data['EPSg (10yrs)'] = data['EPSg (10yrs)'].map(floatify)
        data['Free Cash Flow Growth % (YOY)'] = data['Free Cash Flow Growth % (YOY)'].map(floatify)
        data['PE'] = data['PE'].map(floatify)
        data['CFO'] = data['CFO'].map(floatify)
        data['CFI'] = data['CFI'].map(floatify)
        data['CFF'] = data['CFF'].map(floatify)
        data['EPS'] = data['EPS'].map(floatify_eps)
        data['PE (10yr & current)'] = data['PE (10yr & current)'].map(floatify)
        data['Beta'] = data['Beta'].map(floatify_beta)

        beta = data['Beta']
        eps = data['EPS']
        pe_10yrAndCurrent = data['PE']

        data.to_csv(data_path,index=False)

        #Get the average of the stock's PE for the last 5yrs
        #This works.
        def get_pe_5yravg(lst):
            if np.nan in lst[-6:-1] or '-' in lst[-6:-1]:
                return np.nan
            else:
                return np.mean(lst[-6:-1])
        pe_5yr_avg = pe_10yrAndCurrent.map(lambda k: get_pe_5yravg(k))

        #Get the stock's current PE ratio
        #This works.
        def get_pe_current(lst):
            if isinstance(lst[-1],float):
                return lst[-1]
            return np.nan
        pe_current = pe_10yrAndCurrent.map(lambda k: get_pe_current(k))

        '''def get_epsg(lst):
            if isinstance(lst[-1], float) and isinstance(lst[0], float) and lst[0] != 0.0:
                if (lst[-1] / lst[0]) <= 0:
                    return np.nan
                return (lst[-1]/lst[0])**(1/4)-1
            else:
                return np.nan
        epsg = list(map(get_epsg, eps))'''

        #Project the stock's eps one year from now
        #This works.
        def get_eps_t1(lst):
            def get_epsg(lst):
                if isinstance(lst[-1], float) and isinstance(lst[0], float) and lst[0] != 0.0:
                    if (lst[-1] / lst[0]) <= 0:
                        return np.nan
                    return (lst[-1] / lst[0]) ** (1 / 4) - 1
                else:
                    return np.nan
            epsg = get_epsg(lst)
            if isinstance(lst[-1], float) and lst[-1] > 0:
                return lst[-1] * (1 + epsg)
            else:
                return np.nan
        eps_t1 = list(map(get_eps_t1, eps))

        #Calculate fair value with SPX PE
        #This works.
        def get_earnings_t1(beta, eps_t1):
            if not isinstance(beta, float): #Catch case is beta is nan or '-'
                print("Beta is not a float.")
                return np.nan
            pe = 0
            if beta < 1:
                pe = spx_pe
            else:
                pe = spx_pe*beta
            return round(eps_t1*pe, 2)
        earnings_t1 = list(map(get_earnings_t1, beta, eps_t1))

        #This works.
        fair_value_spx_cons = list(np.around(np.array(earnings_t1)/(1+0.095), 2))
        fair_value_spx_aggr = list(np.around(np.array(earnings_t1)/(1+0.15), 2))

        #5y PE fair value
        #This works.
        pe = pe_5yr_avg #Change to 5y average PE and calculate this fair value
        earnings_t1 = eps_t1*pe
        fair_value_5y_cons = list(np.around(np.array(earnings_t1)/(1+0.095), 2))
        fair_value_5y_aggr = list(np.around(np.array(earnings_t1)/(1+0.15), 2))

        #Current PE fair value
        #This works.
        pe = pe_current #Change to current PE and calculat this fair value
        earnings_t1 = eps_t1*pe
        fair_value_current_cons = list(np.around(np.array(earnings_t1)/(1+0.095), 2))
        fair_value_current_aggr = list(np.around(np.array(earnings_t1)/(1+0.15), 2))

        return fair_value_spx_cons, fair_value_5y_cons, fair_value_current_cons, \
            fair_value_spx_aggr, fair_value_5y_aggr, fair_value_current_aggr

    def debug_fairvalue(debuf_df):
        '''
        :param beta: float
        :param eps: list of eps
        :param pe_10yrAndCurrent: list of pe of the last 10 years and current
        :return:
        '''
        beta = debug_df['Beta'].map(floatify)
        eps = debug_df['EPS'].map(floatify)
        pe_10yrAndCurrent = debug_df['PE (10yr & current)'].map(floatify)

        #Get the average of the stock's PE for the last 5yrs
        #This works.
        def get_pe_5yravg(lst):
            if np.nan in lst[-6:-1] or '-' in lst[-6:-1]:
                return np.nan
            else:
                return np.mean(lst[-6:-1])
        pe_5yr_avg = pe_10yrAndCurrent.map(lambda k: get_pe_5yravg(k))

        #Get the stock's current PE ratio
        #This works.
        def get_pe_current(lst):
            if isinstance(lst[-1],float):
                return lst[-1]
            return np.nan
        pe_current = pe_10yrAndCurrent.map(lambda k: get_pe_current(k))
        print(f"CURRENT PE: \n{pe_current}")

        #Project the stock's eps one year from now
        #This works.
        def get_eps_t1(lst):
            def get_epsg(lst):
                if isinstance(lst[-1], float) and isinstance(lst[0], float) and lst[0] != 0.0:
                    if (lst[-1] / lst[0]) <= 0:
                        return np.nan
                    return (lst[-1] / lst[0]) ** (1 / 4) - 1
                else:
                    return np.nan
            epsg = get_epsg(lst)
            if isinstance(lst[-1], float) and lst[-1] > 0:
                return lst[-1] * (1 + epsg)
            else:
                return np.nan
        eps_t1 = list(map(get_eps_t1, eps))
        print(f"EPS T+1: \n{eps_t1}")

        #Calculate fair value with SPX PE
        #This works.
        def get_earnings_t1(beta, eps_t1):
            beta = beta[0]
            if not isinstance(beta, float): #Catch case is beta is nan or '-'
                return np.nan
            pe = 0
            if beta < 1:
                pe = spx_pe
            else:
                pe = spx_pe*beta
            return round(eps_t1*pe, 2)
        earnings_t1 = list(map(get_earnings_t1, beta, eps_t1))

        #This works.
        fair_value_spx_cons = list(np.around(np.array(earnings_t1)/(1+0.095), 2))
        fair_value_spx_aggr = list(np.around(np.array(earnings_t1)/(1+0.15), 2))

        #5y PE fair value
        #This works.
        pe = pe_5yr_avg #Change to 5y average PE and calculate this fair value
        earnings_t1 = eps_t1*pe
        fair_value_5y_cons = list(np.around(np.array(earnings_t1)/(1+0.095), 2))
        fair_value_5y_aggr = list(np.around(np.array(earnings_t1)/(1+0.15), 2))

        #Current PE fair value
        #This works.
        pe = pe_current #Change to current PE and calculat this fair value
        earnings_t1 = eps_t1*pe
        fair_value_current_cons = list(np.around(np.array(earnings_t1)/(1+0.095), 2))
        fair_value_current_aggr = list(np.around(np.array(earnings_t1)/(1+0.15), 2))

        return fair_value_spx_cons, fair_value_5y_cons, fair_value_current_cons, \
            fair_value_spx_aggr, fair_value_5y_aggr, fair_value_current_aggr

    '''Save test scores'''
    def analyze(data_path, save_path):
        print(f'SCORING:{data_path}')
        print(f'SAVING TO:{save_path}')

        '''!!!Really weird how my changes will not save to the pandas dataframe'''
        data = pd.read_csv(data_path)
        data['ROE (10yrs)'] = data['ROE (10yrs)'].map(floatify)
        data['EPSg (10yrs)'] = data['EPSg (10yrs)'].map(floatify)
        data['Free Cash Flow Growth % (YOY)'] = data['Free Cash Flow Growth % (YOY)'].map(floatify)
        data['PE'] = data['PE'].map(floatify)
        data['CFO'] = data['CFO'].map(floatify)
        data['CFI'] = data['CFI'].map(floatify)
        data['CFF'] = data['CFF'].map(floatify)
        data['EPS'] = data['EPS'].map(floatify_eps)
        data['PE (10yr & current)'] = data['PE (10yr & current)'].map(floatify)
        data['Beta'] = data['Beta'].map(floatify_beta)

        r5y = data['ROE (10yrs)'].map(roe5y)
        r10y = data['ROE (10yrs)'].map(roe10y)
        e5y = data['EPSg (10yrs)'].map(epsg5y)
        e10y = data['EPSg (10yrs)'].map(epsg10y)
        fsoft = data['EPSg (10yrs)'].map(free_soft)
        cfo = data['CFO'].map(cfo_test)
        cfi = data['CFI'].map(cfi_test)
        cff = data['CFF'].map(cff_test)
        cash_flow = (3+cfo+cfi+cff).map(lambda x: x if x>0 else 0)

        #fhard = data['EPSg (10yrs)'].map(free_hard)
        teny_score = round((r10y+e10y+fsoft) / 6.0, 2)
        fivey_score = round((r5y+e5y+fsoft) / 5.0, 2)
        final_10y_score = round((r10y+e10y+fsoft+cash_flow) / 9.0, 2)
        final_5y_score = round((r5y+e5y+fsoft+cash_flow) / 6.0, 2)

        df = pd.DataFrame(columns=['Ticker', 'ROE_10y', 'EPS_10y', 'ROE_5y', 'EPS_5y', 'Free_Soft',
       '10y_score', '5y_score', 'CF_score', 'final_10y_score', 'final_5y_score', 'Cons. Value (SPX)', 'Cons. Value (5y)'
            , 'Cons. Value (Current)', 'Aggr. Value (SPX)', 'Aggr. Value (5y)', 'Aggr. Value (Current)'])
        df['Ticker'] = data['Ticker']
        df['ROE_10y'] = r10y
        df['EPS_10y'] = e10y
        df['ROE_5y'] = r5y
        df['EPS_5y'] = e5y
        df['Free_Soft'] = fsoft
        #df['Free_Hard'] = fhard
        df['10y_score'] = teny_score
        df['5y_score'] = fivey_score
        df['CF_score'] = cash_flow
        df['final_10y_score'] = final_10y_score
        df['final_5y_score'] = final_5y_score
        fair_values = calc_fairvalue(data_path, spx_pe=18.86)
        df['Cons. Value (SPX)'] = fair_values[0]
        df['Cons. Value (5y)'] = fair_values[1]
        df['Cons. Value (Current)'] = fair_values[2]
        df['Aggr. Value (SPX)'] = fair_values[3]
        df['Aggr. Value (5y)'] = fair_values[4]
        df['Aggr. Value (Current)'] = fair_values[5]

        df.to_csv(save_path, index=False)
        print(f"SAVED TO: {save_path}")

    data_path = 'fa_stats.csv'
    save_path = f"{data_path.split('.')[0]}_score.csv"
    def create_fa_csv(name):
        df = pd.DataFrame(columns=['Ticker','ROE (10yrs)','EPSg (10yrs)','Free Cash Flow Growth % (YOY)', 'PE','EPSg (next)','EPSg (5yr avg)'])
        df.to_csv(name, index=False)

    analyze(data_path, save_path)


    def weekly_update(data_path, save_path, skip_beta=False):
        '''
        Purpose: Because the valuations are dependent on pe ratio and beta, I need to update these data
        every week to get an accurate up-to-date overview of which stocks are over or undervalued.
        :param data_path: where to get the data (str)
        :param save_path: where to save the data (str)
        :return:
        '''
        '''!!!Mutltiprocess this'''
        # Get updated pe ratio
        print(f'COLLECTING DATA FOR:{ticker}')

        driver = webdriver.Chrome(ChromeDriverManager().install())
        wait = WebDriverWait(driver, 30)

        url = f'https://www.morningstar.com/search?query={ticker}'
        driver.get(url)

        # time.sleep(20) #!!!what is the optimal pause to ensure a crash doesn't happen? Or maybe the solution is not a pause?
        # Search the ticker on the morningstar home page
        # search_xpath = '//*[@id="__layout"]/div/div/div[2]/div[1]/div/header/div/div[1]/div/form/div/input'
        # search = driver.find_element(By.XPATH, search_xpath)
        # search.send_keys(ticker)
        # search.send_keys(Keys.ENTER)

        # Click on the first result, which should be the stock's info page
        ticker_page_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/main/div/div/div[1]/div/section[1]/div[2]/a'
        ticker_page = wait.until(ec.visibility_of_element_located((By.XPATH, ticker_page_xpath)))
        # ticker_page = wait.until(ec.visibility_of_element_located((By.XPATH, ticker_page_xpath)))
        ticker_page.click()
        # time.sleep(10)

        # Go to the stock's valuation page
        val_page = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="stock_tab-valuation"]')))
        # val_page = driver.find_element_by_id("stock__tab-valuation")
        val_page.click()
        # time.sleep(10)

        '''Get a list of the past 10 years' and current stock PE'''
        #pe_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/main/div[2]/div/div/div[1]/sal-components/div/sal-components-stocks-valuation/div/div[1]/div/div/div[2]/div/div/table/tbody/tr[3]'
        pe_xpath = '//*[@id="__layout"]/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-valuation/div/div[1]/div/div/div[2]/div/div/table/tbody/tr[3]'
        try:
            #roe = driver.find_element(By.XPATH, roe_xpath).text
            pe = wait.until(ec.visibility_of_element_located((By.XPATH, pe_xpath))).text
        except:
            pdb.set_trace()
        pe_10yr = pe[:-2] #pe of the last 10 years and current

        if(data['Ticker'].str.contains(ticker).any()):
            data.loc[data.index[data['Ticker']==ticker].to_list()[0], ['PE (10yr & current)']] = [pe_10yr]
        else:
            print(f"Could not find {ticker} in dataframe for some reason...")

        data.to_csv(path,index=False)
        print(f'SAVED {ticker} TO CSV')

        # Get updated beta

        # Run analyze() to calculate and save the new valuations
        analyze(data_path, save_path)


    def quarterly_update(data_path, start_ticker = '', skip_beta=False):
        '''
        Purpose: Because the valuations are also dependent on quarterly earnings reports, I need to update
        this data every earnings season to get an accurate up-to-date overview of which stocks
        are over or undervalued. I should also update
        :param data_path: where to get the data (str)
        :param save_path: where to save the data (str)
        :return:
        '''
        all_tickers = pd.read_csv(data_path)['Ticker']
        start_tick = all_tickers.iloc[0]
        if start_ticker != '':
            start_tick = start_ticker

        for ticker in tqdm(list(all_tickers)[list(all_tickers).index(start_tick):]):
            get_cf_eps(ticker, data_path, skip_beta=skip_beta)

        return "Completed quarterly update."

    quarterly_update(data_path, start_ticker='', skip_beta=False)


