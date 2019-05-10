from flask import Flask, render_template
from flask_pymongo import PyMongo 
import scrape_mars
#MUST run from Anaconda Prompt - windows search for anaconda prompt 

app = Flask(__name__) 

app.config["MONGO_URI"]=  "mongodb://localhost:27017/mars_app"
mongo=PyMongo(app)

@app.route('/') # 3:04:30 vid
def index():
    print("I'm here")
    mars=mongo.db.mars.find_one() #**************error no attribute 'one' ***************************************************
    print(mars)
    return render_template("index.html", mars=mars)

@app.route('/scrape') 
def scraper():
    mars = mongo.db.mars
    mars_data=scrape_mars.scrape_all() #calls the function to get all the scrapings and store in mars
    mars.update({}, mars_data, upsert=True) 
    return "Scraping Succesfull"

if __name__ == "__main__":
    app.run()
