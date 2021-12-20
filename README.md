# FocusXgen Tradestation Client

FocusXgen Client for Options trading with multiple accounts

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)

## Requirements

The following requirements must be met to use this API:

- Docker should be installed

## Installation

Clone to repo from github
```
git clone https://github.com/Gabedave/focusxgen_tradestationclient.git
```

Add configuration file named "config.json" to the /config folder

"sample.json"
```
[
    {
        "username" : "username1",
        "client_id" : "client_id1",
        "client_secret": "client_secret1"
    },
    {
        "username" : "username2",
        "client_id" : "client_id2",
        "client_secret": "client_secret2"
    },
    {
        "username" : "username3",
        "client_id" : "client_id3",
        "client_secret": "client_secret3"
    }
]
```

Run the following commands in the terminal
```
docker build --tag focusxgen_tradestation .  

docker run --publish 3000:3000 focusxgen_tradestation
```

## Usage

Access the app from http://localhost:3000