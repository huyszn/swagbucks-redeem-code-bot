# Swagbucks Swag Code Redeem Bot

A bot that scrapes Swag Codes found on sbcodez.com and redeems them on swagbucks.com. The bot currently does not automatically redeem Mobile App / SwagButton extension only Swag Codes. You can copy these codes printed from terminal and enter them in the Mobile App and/or the SwagButton extension.

## Examples

![Console output Swag Code Box](images/Console%20-%20Swag%20Code%20Box.png)

<p align="center">
  <b>Swag Code Box Non-Offer-Page Swag Code</b>
</p>


![Console output SwagButton](images/Console%20-%20SwagButton.png)

<p align="center">
  <b>SwagButton Offer-Page Swag Code</b>
</p>

## Setup the bot

### Requirements

Clone this repository, cd into it, and install dependencies:
```sh
git clone https://github.com/huyszn/swagbucks-redeem-code-bot.git
cd swagbucks-redeem-code-bot
pip install -r requirements.txt
```

### config.py

Copy the contents of `config-example.py` into a new file `config.py`.
```sh
touch config.py
cp config-example.py config.py
```

Replace the `EMAIL` and `PASSWORD` fields with your account email and password in `config.py`.

```
EMAIL = "your email"
PASSWORD = "your password"
```
### Country Filter
The bot defaults to getting and redeeming only US codes.\
If you want to redeem codes from another country, then change the list values in `COUNTRY_FILTER` and the value in `COUNTRY`\
The `country_filter` list and `country` variable are located in the beginning of the `redeem-swag-codes.py` file.\
For example, this code snippet below gets only UK codes.
```
COUNTRY_FILTER = ['CA', 'US', 'AU']
COUNTRY = 'UK'
```


## Run the bot

If you want to run the bot once:
```sh
python3 redeem-swag-codes.py
```

If you want to run the bot every hour:
```sh
python3 redeem-swag-codes.py --hourly
```

![Console output hourly argument](images/Console%20-%20Redeem%20Swag%20Code%20Hourly.png)

<p align="center">
  <b>Swag Code Redeemed with --hourly Argument</b>
</p>

To stop the bot, press <kbd>CTRL</kbd>+<kbd>C</kbd> / <kbd>Control</kbd>+<kbd>C</kbd> on your keyboard in the terminal window.\
I recommend you run the bot with the hourly argument in the afternoon (12pm) in your local time and stop the bot at around the evening (7pm) in your local time.

<div align="center">

### **Normal Swag Code Schedule (US)**

| Day of the Week  | Number of Swag Codes |
| :---: | :---: |
| Sunday  | One Swag Code  |
| Monday  | Two Swag Codes  |
| Tuesday  | One Swag Code  |
| Wednesday  | One Swag Code  |
| Thursday  | One SwagButton Swag Code  |
| Friday  | Two Swag Codes  |
| Saturday  | One Swag Code  |

There is a iSPY code once a week between Monday-Friday.

</div>


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details