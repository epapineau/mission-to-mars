from flask import Flask, render_template
from scrape_mars import scrape
import datetime as dt
import pymongo

# Initialize flask app
app = Flask(__name__)

# Establish mongo connection, db, and collection
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client.mars_db
mars = db.mars_scrape

# Home Route
@app.route('/')
def index():
    mars_dict = db.mars.find_one()
    # Need to find newest entry
    # scrapeQ = db.mars.find().sort({'scrape_date' : -1})
    return render_template('index.html', mars_dict = mars_dict)

@app.route('/scraper')
def scraper():
    # Run scrape function to gather mars data
    mars_dict = scrape()
    mars_dict['scrape_date'] = dt.datetime.now()
    db.mars.insert_one(mars_dict)
    return render_template('index.html', mars_dict = mars_dict)


# Debugger on
if __name__ == "__main__":
    app.run(debug = True)