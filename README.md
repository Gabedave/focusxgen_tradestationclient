# FocusXgen Tradestation Client

FocusXgen Client for Options trading with multiple accounts

## Table of Contents

- [Overview](#overview)
- [What's in the API](#whats-in-the-api)
- [Requirements](#requirements)
- [API Key & Credentials](#api-key-and-credentials)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Documentation & Resources](#documentation-and-resources)
- [About this Project](#about-this-project)

## Requirements

The following requirements must be met to use this API:

- Docker should be installed

## Installation

Clone to repo from github and add a configuration file to the /config folder

sample.json
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