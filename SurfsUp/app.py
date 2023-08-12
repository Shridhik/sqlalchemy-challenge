import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################


@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"
    )

# Route to get precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of precipitation data."""
    # Query all precipitation data
    results = session.query(Measurement.date, Measurement.prcp).\
                order_by(Measurement.date).all()

    # Convert the query results to a list of dictionaries with date and prcp
    all_precipitation = []
    for precip in results:
        precip_dict = {}
        precip_dict["date"] = precip.date
        precip_dict["prcp"] = precip.prcp
        all_precipitation.append(precip_dict)

    # Return the JSON representation of precipitation data
    return jsonify(all_precipitation)


# Route to get station data
@app.route("/api/v1.0/stations")
def stations():
    """Return the JSON representation of station data."""
    # Query list of stations and their observation counts
    results = session.query(Measurement.station, func.count(Measurement.station)).\
                group_by(Measurement.station).\
                order_by(func.count(Measurement.station).desc()).all()

    # Convert the query results to a list of dictionaries with station and count
    all_stations = []
    for row in results:
        station_dict = {}
        station_dict["station"] = row[0]
        station_dict["count"] = row[1]
        all_stations.append(station_dict)

    # Return the JSON representation of station data
    return jsonify(all_stations)


# Route to get temperature observations (TOBS) for the last year
@app.route("/api/v1.0/tobs")
def tobs():
    """Return the JSON representation of temperature observations (TOBS) for the last year."""
    # Find the most recent date in the dataset
    last_date = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first()
    for date in last_date:
        split_last_date = date.split('-')

    last_year = int(split_last_date[0])
    last_month = int(split_last_date[1])
    last_day = int(split_last_date[2])

    # Calculate the date one year ago from the last date
    query_date = dt.date(last_year, last_month, last_day) - dt.timedelta(days=365)

    # Query list of TOBS for the last year
    results = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= query_date).\
                order_by(Measurement.date).all()

    # Convert the query results to a list of dictionaries with date and TOBS
    last_12months_tobs = []
    for row in results:
        tobs_dict = {}
        tobs_dict["date"] = row.date
        tobs_dict["tobs"] = row.tobs
        last_12months_tobs.append(tobs_dict)

    # Return the JSON representation of temperature observations (TOBS) for the last year
    return jsonify(last_12months_tobs)


# Route to calculate temperature statistics (TMIN, TAVG, TMAX) starting from a given start date
@app.route("/api/v1.0/<start_date>")
def calc_temps_start(start_date):
    """Return the JSON representation of temperature statistics (TMIN, TAVG, TMAX) for a list of dates starting from a given start_date."""
    # Query temperature statistics for dates greater than or equal to the specified start_date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    # Convert the query results to a list of dictionaries with TMIN, TAVG, and TMAX
    calc_tobs = []
    for row in results:
        calc_tobs_dict = {}
        calc_tobs_dict["TMIN"] = row[0]
        calc_tobs_dict["TAVG"] = row[1]
        calc_tobs_dict["TMAX"] = row[2]
        calc_tobs.append(calc_tobs_dict)

    # Return the JSON representation of temperature statistics (TMIN, TAVG, TMAX) for the specified start_date
    return jsonify(calc_tobs)


# Route to calculate temperature statistics (TMIN, TAVG, TMAX) within a specified date range
@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_temps_start_end(start_date, end_date):
    """Return the JSON representation of temperature statistics (TMIN, TAVG, TMAX) for a list of dates within a specified date range."""
    # Query temperature statistics for dates within the specified date range
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()

    # Convert the query results to a list of dictionaries with TMIN, TAVG, and TMAX
    calc_tobs = []
    for row in results:
        calc_tobs_dict = {}
        calc_tobs_dict["TMIN"] = row[0]
        calc_tobs_dict["TAVG"] = row[1]
        calc_tobs_dict["TMAX"] = row[2]
        calc_tobs.append(calc_tobs_dict)

    # Return the JSON representation of temperature statistics (TMIN, TAVG, TMAX) for the specified date range
    return jsonify(calc_tobs)

# Run the Flask app in debug mode
if __name__ == '__main__':
    app.run(debug=True)