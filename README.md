# Steam Market Parser

Python parser to get the information about purchases/sales of items for a certain period from [steam](https://steamcommunity.com/market/).
The received information is matched by item names in order to systematize and identify the difference in the prices of purchase and sale.

## Setup

Install all requirements:

`pip install -r requirements.txt`

Then, launch the script *parser.py*:

`python parser.py `

## Usage

The following data is required for the parser to work:
* *date of the last transaction* (since the year of the transaction is not displayed in the history of transactions in steam, it is calculated based on this date. The break in trading should not be more than a year, otherwise the determination of the year will be incorrect)
* *start date of the analysis period* 
* *end date of the analysis period*
* *steam account login*
* *steam account password*
* *two-factor code from SDA or Steam Guard*

The result of the parser's work is the result.csv file, which will be created in the same folder as the scripts.

![example](https://github.com/annachs/steamParser/assets/120400708/8f700640-e55c-4c68-8adc-5405ad04933d)

## Acknowledgments

The authorization process in the project was implemented using [this module](https://github.com/ValvePython/steam).
