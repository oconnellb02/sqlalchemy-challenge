# Import dependencies & Flask
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask setup
app = Flask(__name__)

# Flask routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperatures: /api/v1.0/tobs<br/>"
        f"Temperature start date: /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature start to end date: /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

# Precipitation - List of dates & prcp from dataset
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    all_precip = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        all_precip.append(prcp_dict)
    return jsonify(all_precip)

# Stations - List of stations from dataset
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station, Station.name).all()
    session.close()

    all_stations = []
    for station, name in results:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        all_stations.append(station_dict)
    return jsonify(all_stations)

# Tobs - Query dates & temps of the most active station for last year
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    date_format = dt.datetime.strptime(last_date, '%Y-%m-%d')
    querydate = dt.date(date_format.year -1, date_format.month, date_format.day)

    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= querydate).all()
    session.close()

    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Temperature"] = tobs
        all_tobs.append(tobs_dict)
    return jsonify(all_tobs)

# Start date
@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    all_temps = []
    for min, max, avg in results:
        temp_dict = {}
        temp_dict["Min Temp"] = min
        temp_dict["Max Temp"] = max
        temp_dict["Avg Temp"] = avg
        all_temps.append(temp_dict)
    return jsonify(all_temps)

# Start to End date
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    all_temps = []
    for min, max, avg in results:
        temp_dict = {}
        temp_dict["Min Temp"] = min
        temp_dict["Max Temp"] = max
        temp_dict["Avg Temp"] = avg
        all_temps.append(temp_dict)
    return jsonify(all_temps)

if __name__ == '__main__':
    app.run(debug=True)
