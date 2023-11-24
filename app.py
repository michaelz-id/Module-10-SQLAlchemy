# Python SQL toolkit and Object Relational Mapper
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify

#################################################
# DB Setup
#################################################

# Create connection
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# run Flask Setup

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f'<h2>Hello, explore climate records for Hawaii.</h2>'
        f'<p><ul><h3>Available routes for Hawaian Climate Data are:</h3><ol></br>'
        f'<li>Daily Rainfall (mm) record set:  /api/v1.0/precipitation</li>'
        f'<li>Weather Stations:  /api/v1.0/stations</li>'
        f'<li>Daily temperatures between the dates: 23/08/16 and 23/08/2017 (Station USC00519281):  /api/v1.0/temperatures</li>'
        f'<li>Summary from a specified start date (yyyy-mm-dd): /api/v1.0/start<start><br/></li>'
        f'<li>Summary from a specified start date and end date (yyyy-mm-dd): /api/v1.0/start_end/<start>/<end><br/></li></ol></ul></br>'
        )
    

# Rainfall data


@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Return a list of rainfall observations
    results = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= '2016-08-23').all()
       
    session.close()

    #create dictionary
    all_rainfall = []
    for date, prcp in results:
        rainfall_dict = {}
        rainfall_dict["date"] = date
        rainfall_dict["prcp"] = prcp
        all_rainfall.append(rainfall_dict)
    
    return jsonify(all_rainfall)

# return a JSON list of stations from the dataset.


@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Return a list of all stations
    results = session.query(station.station).all()
       
    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))
    
        
    return jsonify(all_stations)


# temp

@app.route("/api/v1.0/temperatures")
def temperatures():

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
     
    sel = [measurement.date, measurement.tobs, measurement.station]
    active_station = session.query(*sel).\
    filter(func.strftime(measurement.date) >= '2016-08-23').\
        filter(measurement.station == 'USC00519281').all()
            
    #active_station
               
    session.close()

    #create dictionary
    all_temps = []
    for date, tobs, station in active_station:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        temp_dict["station"] = station
        all_temps.append(temp_dict)
    
    return jsonify(all_temps)


@app.route("/api/v1.0/start/<start>")
def summary_by_start(start=None):



    # Create our session (link) from Python to the DB
    session = Session(engine)
    
     #Fetch the temperatures from the start# date that matches

    sel = [func.min(measurement.tobs),
          func.avg(measurement.tobs),
          func.max(measurement.tobs)]
    start_tobs = session.query(*sel).filter(measurement.date >= start).all()
       
    first_date = session.query(func.min(measurement.date)).scalar()
    # print(first_date)
             
    session.close()
    
    #print(start_tobs)

    s_temps = []
    for min, avg, max in start_tobs:
        s_temp_dict = {}
        s_temp_dict["min"] = min
        s_temp_dict["average"] = avg
        s_temp_dict["max"] = max
        s_temps.append(s_temp_dict)
    
    #Find first date for error message
    first_date = session.query(func.min(measurement.date)).scalar()
    #print(first_date)
    
    # Return the results else return an error message.
    # return an error message if the date is before the first record date
    
    if first_date > start:
        return jsonify({"error": f"Date {start} is too early, our records begin {first_date}."}), 404      
    
    elif s_temp_dict["min"]: 
        return jsonify(s_temps)
    
    else:
        return jsonify({"error": f"Date {start} does not exist or is not formatted yyyy-mm-dd."}), 404
    
# min/max temp

@app.route("/api/v1.0/start_end/<start>/<end>")
def summary_by_range(start=None,end=None):

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
#select temp from the start and end dates entered

    sel = [func.min(measurement.tobs),
          func.avg(measurement.tobs),
          func.max(measurement.tobs)]
    start_end_tobs = session.query(*sel).filter(measurement.date >= start).filter(measurement.date <= end).all()
       
                
    session.close()
   
    #Find first date for error message
    first_date = session.query(func.min(measurement.date)).scalar()
    last_date = session.query(func.max(measurement.date)).scalar()

    #create dictionary
    se_temps = []
    for min, avg, max in start_end_tobs:
        se_temp_dict = {}
        se_temp_dict["min"] = min
        se_temp_dict["average"] = avg
        se_temp_dict["max"] = max
        se_temps.append(se_temp_dict)
    
    # If the results not null values show, else return an error message
    if first_date > start:
        return jsonify({"error": f"Date {start} is too early, our records begin {first_date}."}), 404      
    
    elif last_date < end:
        return jsonify({"error": f"Date {end} is too recent, our records end {last_date}."}), 404  

    elif se_temp_dict["min"]: 
        return jsonify(se_temps)
    
    else:
        return jsonify({"error": f"Date(s) are not formatted yyyy-mm-dd."}), 404
    


if __name__ == '__main__':
    app.run(debug=True)