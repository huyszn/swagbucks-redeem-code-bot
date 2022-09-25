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

Replace the `EMAIL` and `PASSWORD` fields with your account email and password.

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

```sh
python3 redeem-swag-codes.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details