# webscrapemorningstar

```markdown
# Web Scraping and Fundamental Analysis

This Python script is designed for web scraping and conducting fundamental analysis on stock data. It utilizes various libraries and modules to extract relevant financial data from websites and compile it into a structured dataset for further analysis.

## Prerequisites

Before using this script, ensure that you have the following Python libraries installed:

- `pandas`
- `numpy`
- `selenium`
- `tqdm`
- `finviz`
- `multiprocess`
- `webdriver_manager`

You can install these libraries using `pip` if you haven't already:

```bash
pip install pandas numpy selenium tqdm finviz multiprocess webdriver_manager
```

## Configuration

### Selenium Webdriver Configuration

Before running the script, make sure to configure the Selenium webdriver properly. The script uses the Chrome webdriver and allows for proxy settings. You can adjust the webdriver options, proxy settings, and other configurations as needed in the script.

```python
# Configure Selenium Webdriver
options = Options()
options.add_argument('--no-proxy-server')
# Add more options as needed
```

### Proxy Configuration (Optional)

If you need to use a proxy, set the `PROXY` variable to your proxy server's address and port:

```python
PROXY = "IpOfTheProxy:PORT"
options.add_argument("--proxy-server=%s" % PROXY)
```

### Exclude Automation Detection

To avoid automation detection, the script includes the following settings:

```python
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
```

## Usage

1. Run the script by executing the following command in your terminal:

```bash
python your_script.py
```

2. The script will prompt you to start the Chrome webdriver. Type 'y' to proceed.

3. The script performs the following tasks:

   - **Step 1: Filter with Finviz**: Scrapes stock tickers that pass initial Finviz tests and saves them to a CSV file.

   - **Step 2: Get ROE, EPSg, FCF, PE, sector for the filtered stocks**: Collects data on Return on Equity (ROE), EPS growth (EPSg), Free Cash Flow Growth, Price-to-Earnings (PE) ratio, sector, and more for the filtered stocks.

   - **Step 3: Get Cash Flow statement and EPS numbers**: Extracts cash flow statement and EPS numbers for the stocks. You can customize the starting point by changing the index.

   - **Step 4: Analyze the scraped data to produce a scoring**: Calculates scores for the scraped data based on your analysis criteria.

4. You can customize and extend the script to suit your specific needs by modifying functions and configurations.

## Multiprocessing

The script includes multiprocessing capabilities to speed up data collection. It utilizes multiple processes to scrape data concurrently, enhancing efficiency.

## Data Saving

The collected data is saved to CSV files, allowing you to further analyze and visualize it using your preferred tools.

This documentation below provides an overview of the Python code you've shared, which appears to be a financial data extraction and analysis script. The code collects financial data for a given stock symbol, including cash flow, income statement, and EPS (Earnings Per Share), and calculates various financial metrics. Here, we will break down the code and provide usage instructions.

## Table of Contents
1. [Description](#description)
2. [Requirements](#requirements)
3. [How to Use](#how-to-use)
4. [Functionality](#functionality)
5. [Contributing](#contributing)
6. [License](#license)

<a name="description"></a>
## 1. Description

The code consists of Python functions for collecting and analyzing financial data for a given stock symbol using web scraping and external APIs. It extracts data such as Cash Flow from Operating Activities (CFO), Cash Flow from Investing Activities (CFI), Cash Flow from Financing Activities (CFF), and Earnings Per Share (EPS) from financial reports. Additionally, it calculates various financial metrics such as CFO growth volatility and CFO average growth.

<a name="requirements"></a>
## 2. Requirements

To run this code, you need the following dependencies:

- Python 3.x
- Selenium (for web scraping)
- NumPy
- pandas
- requests

You also need to have a web driver (e.g., ChromeDriver) installed and set up. Ensure that you have the necessary access and permissions to access financial data sources and websites.

<a name="how-to-use"></a>
## 3. How to Use

Follow these steps to use the code:

1. **Set Up Dependencies**:

   Make sure you have Python installed, and install the required packages using pip:

   ```bash
   pip install selenium numpy pandas requests
   ```

2. **Configure the Web Driver**:

   You need to set up a web driver (e.g., ChromeDriver). Update the code to specify the path to your web driver executable:

   ```python
   # Replace 'your_webdriver_path' with the actual path to your web driver executable.
   driver = webdriver.Chrome(executable_path='your_webdriver_path')
   ```

3. **Usage**:

   The main function for extracting financial data is `get_cf_eps`. You can call this function by providing the stock ticker symbol, a path for saving data, and an optional `skip_beta` flag.

   ```python
   get_cf_eps('TICKER', 'data.csv', skip_beta=False)
   ```

   - `'TICKER'`: Replace this with the stock ticker symbol you want to analyze.
   - `'data.csv'`: Provide the path where you want to save the data (in CSV format).
   - `skip_beta`: Set this flag to `True` if you want to skip collecting beta data.

4. **Run the Script**:

   Execute the script, and it will collect financial data, calculate metrics, and save the results to the specified CSV file.

<a name="functionality"></a>
## 4. Functionality

### `yf_cf(symbol, function)`

This function retrieves financial data for a stock symbol using the Alpha Vantage API. It takes two parameters:

- `symbol`: The stock symbol (e.g., 'AAPL' for Apple Inc.).
- `function`: The type of financial data to retrieve ('CASH_FLOW', 'INCOME_STATEMENT', or 'BALANCE_SHEET').

### `get_cf_eps(ticker, path, skip_beta=False)`

This function performs the following steps:

- Accesses the Morningstar website to retrieve financial data for the specified stock.
- Downloads income statement and cash flow data in XLS format.
- Parses and analyzes the data to calculate various financial metrics.
- Optionally, collects beta data from the Finviz website.
- Saves the collected data to a CSV file specified by `path`.

This documentation below explains the code segments provided below. The code is to a set of functions for analyzing financial data, including retrieving stock beta and performing various tests on financial metrics such as ROE (Return on Equity), EPS (Earnings Per Share) growth, free cash flow, and cash flow components.

---

## 1. `get_beta(ticker)`

This function retrieves the beta value for a given stock symbol by scraping data from Yahoo Finance. It takes the following parameter:

- `ticker`: The stock symbol for which you want to retrieve the beta.

### Usage Example:

```python
beta = get_beta('AAPL')
```

---

## 2. Helper Functions for Data Processing

### `floatify_ind(list_val)`
Converts individual elements in a list into a standard format.

### `floatify_beta(beta)`
Converts beta values into a standard format.

### `floatify(row_val)`
Converts a list of values into a standard format.

### `floatify_nopercent(row_val)`
Converts a list of values (excluding percentages) into a standard format.

### `roe_fail(n)`
Determines if a value indicates a failure in the ROE test.

### `epsg_fail(n)`
Determines if a value indicates a failure in the EPS growth test.

### `trenddetector(array_of_data, order=1)`
Calculates the trend (slope) of an array of data points.

---

## 3. ROE (Return on Equity) and EPS (Earnings Per Share) Tests

### `roe5y(roes)`
Calculates the 5-year ROE score based on the number of failures in the ROE test.

### `roe10y(roes)`
Calculates the 10-year ROE score based on the number of failures in the ROE test.

### `epsg5y(epsgs)`
Calculates the 5-year EPS growth score based on the number of failures in the EPS growth test.

### `epsg10y(epsgs)`
Calculates the 10-year EPS growth score based on the number of failures in the EPS growth test.

---

## 4. Free Cash Flow Test

### `free_pos(f)`
Determines if a value indicates a positive free cash flow.

### `free_sum(frees)`
Calculates the sum of free cash flows.

### `free_soft(frees)`
Performs the free cash flow test and returns a score (0 or 1) based on specific criteria.

---

## 5. Cash Flow Component Tests

### `cfo_test(cfo)`
Performs a cash flow from operating activities (CFO) test and returns a score based on specific criteria.

### `cff_test(cff)`
Performs a cash flow from financing activities (CFF) test and returns a score based on specific criteria.

### `cfi_test(cfi)`
Performs a cash flow from investing activities (CFI) test and returns a score based on specific criteria.

---

For detailed usage instructions and examples, refer to the individual function descriptions above.

```markdown
# stocks_to_tickers

This function takes a CSV file path as input, reads the data, extracts ticker symbols, cleans them, and saves the results to a new CSV file.

## Parameters

- `path` (str): The path to the input CSV file.

## Usage

```python
stocks_to_tickers('/Users/cyrusleung/Downloads/Clean Stocks - Stock to ticker-2.csv')
```

# get_stock_sector

This function retrieves the sector information for a stock from morningstar.com and updates it in a CSV file.

## Parameters

- `ticker` (str): The stock ticker symbol.
- `save_path` (str): The path to the CSV file where the data will be saved.

## Usage

```python
save_path = 'fa_stats_scores.csv'
driver = webdriver.Chrome(ChromeDriverManager().install())
wait = WebDriverWait(driver, 30)
tickers = pd.read_csv(path)['Ticker']
for ticker in tqdm(tickers):
    get_stock_sector(ticker, path)

driver.close()
```

# ticker_to_sector

This function adds a "Sector" column to a CSV file of stock tickers by pulling sector data from another CSV file.

## Parameters

- `data_path` (str): The path to the CSV file containing stock ticker and sector data.
- `save_path` (str): The path to the CSV file where the updated data will be saved.

## Usage

```python
sector_stattoscores('fa_stats.csv', 'fa_stats_scores/fa_stats_score.csv')
sector_stattoscores('fa_stats.csv', 'stocks_to_tickers.csv')
```

# calc_fairvalue

This function calculates the fair values for stocks based on various parameters like beta, EPS, PEs, and SP500 PE ratio.

## Parameters

- `data_path` (str): The path to the CSV file containing stock data.
- `spx_pe` (float): The PE ratio of the S&P 500.

## Usage

```python
fair_values = calc_fairvalue(data_path, spx_pe=19.23)
```

# debug_fairvalue

This function provides detailed debugging information for the fair value calculation process. It takes a DataFrame with stock data as input.

## Parameters

- `debug_df` (DataFrame): The DataFrame containing stock data for debugging.

## Usage

```python
debug_fairvalue(debug_df)
```

# analyze

This function scores and analyzes stock data based on various financial parameters, calculates fair values, and saves the results to a CSV file.

## Parameters

- `data_path` (str): The path to the CSV file containing stock data.
- `save_path` (str): The path to the CSV file where the analysis results will be saved.

## Usage

```python
analyze(data_path, save_path)
```

# get_pe

This function retrieves the PE ratio of a stock from morningstar.com and updates it in a CSV file.

## Parameters

- `ticker` (str): The stock ticker symbol.
- `data_path` (str): The path to the CSV file where the data will be updated.

## Usage

```python
get_pe(ticker, data_path)
```

# weekly_update

This function is used to update stock data on a weekly basis. It retrieves the latest PE ratio data and updates the CSV file.

## Parameters

- `data_path` (str): The path to the CSV file containing stock data.
- `skip_beta` (bool): If True, skip updating beta values.

## Usage

```python
weekly_update(data_path, skip_beta=False)
```

# quarterly_update

This function is used to update stock data on a quarterly basis, typically during earnings seasons. It retrieves the latest data for cash flow and EPS and updates the CSV file.

## Parameters

- `data_path` (str): The path to the CSV file containing stock data.
- `start_ticker` (str): The ticker symbol to start updating from.
- `skip_beta` (bool): If True, skip updating beta values.

## Usage

```python
quarterly_update(data_path, start_ticker='', skip_beta=False)
```

# trading_view_tickers

This function converts a string of tickers copied from Excel into a format that can be entered into TradingView, separating them with commas.

## Parameters

- `tickers` (str): The string of tickers to be converted.

## Usage

```python
tickers = 'AAPL MSFT GOOGL'
formatted_tickers = trading_view_tickers(tickers)
```

<a name="contributing"></a>
## Contributing

If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix: `git checkout -b feature-name`.
3. Make your changes and commit them with descriptive messages.
4. Push your changes to your fork: `git push origin feature-name`.
5. Create a pull request to the original repository.

<a name="license"></a>
## License

This code is provided under the [MIT License](LICENSE). Feel free to use, modify, and distribute it according to the terms of the license.

Please let me know if you need further assistance or have any questions about using this code.

## Acknowledgments

This script relies on various open-source libraries and web sources to gather financial data. Special thanks to the authors and contributors of these resources.

Feel free to reach out if you have any questions or need assistance with the script.

Happy analyzing!
```
