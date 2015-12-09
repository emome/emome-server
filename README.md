# emome-server
[![Build Status](https://travis-ci.org/emome/emome-server.svg?branch=master)](https://travis-ci.org/emome/emome-server)
[![Code Climate](https://codeclimate.com/github/emome/emome-server/badges/gpa.svg)](https://codeclimate.com/github/emome/emome-server)

#### Clone Repository
```
git clone https://github.com/emome/emome-server.git
cd emome-server
```
#### Intsall MongoDB
```
brew install mongodb
```


#### Intall Project Dependencies
```
virtualenv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

#### Run Server
```
mongod # Start MongoDB daemon process first
python server.py # Listen to port 5000
```

#### Testing
```
python tests.py
```
