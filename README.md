# Web scraper and some behave-tests for website boataround.com

This is the solution to a test case from the Boataround team.

## Installation

1. Clone the repository:

        git clone https://github.com/philarete173/boataround_it_tester_case.git

2. Go to project folder, create virtual environment and activate it:

        cd .\boataround_it_tester
        python -m venv venv
        .\venv\Scripts\activate

3. Install requirements (The list of used libraries can be found in the requirements.txt file):

        pip install -r requirements.txt

4. Download ChromeDriver and unzip file chromedriver.exe to project folder. The version available at 
[this link](https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/120.0.6099.71/win64/chrome-win64.zip) 
was used in development (Windows version).

## Usage

### Data scraper

To start the scraper, use the following command (from the command line with the virtual environment activated):

        python scraper.py

In the process, the scraper will display informational messages in the console about the stages of data collection.
It has 5 attempts to request information from each page, each with increasing latency. 
The number of attempts, as well as the period of data collection can be configured on lines 72-78 of the script file:

    # start date of the data collection period
    start_date = date(2024, 5, 1)
    # end date of the data collection period
    end_date = date(2024, 9, 30)
    # main url of requests
    request_url = 'https://bt2stag.boataround.com/search'
    # limit the number of attempts for each request
    request_repeats_max = 5

After the scraper finishes, a file **boats_bookings.xlsx will** be created in the project folder, 
containing a table with the collected data rows.

### Test cases

Behave tests and selenium library were used to test the functionality.
To start the tests, use the following command (from the command line with the virtual environment activated):

      behave

This will launch a version of the Chrome browser for testing and attempt to execute the prepared scenarios.
All scripts are described in the file **features/boataround.feature**

*For reference: this was my first real experience writing tests from scratch, don't judge harshly :)*