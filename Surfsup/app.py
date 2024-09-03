# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func
from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables

Base.prepare(autoload_with=engine)
Base.classes.keys()

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
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/start<br/>"
        "/api/v1.0/start_end" )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    end_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    start_date = dt.datetime.strptime(end_date, '%Y-%m-%d') - dt.timedelta(days=366)

    precep_scores = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()

    session.close()

    precep_dict = {date: prcp for date, prcp in precep_scores}

    return jsonify(precep_dict)

@app.route("/api/v1.0/stations")
def stations():
    """List jsonified data of all of the stations in the database."""
    session = Session(engine)
    stations = session.query(Station.station).distinct().all()
    session.close()
    station_list = [station[0] for station in stations]
    return jsonify (station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    end_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    start_date = dt.datetime.strptime(end_date, '%Y-%m-%d') - dt.timedelta(days=366)
    
    top_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).first()[0]
    
    station_data = session.query(Measurement.tobs).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).\
        filter(Measurement.station == top_station).all()
    
    session.close()
    
    temperatures = [tobs[0] for tobs in station_data]

    
    return jsonify(temperatures)

@app.route("/api/v1.0/start")
def start():
    """List jthe min, max, and average temperatures calculated from the given start date to the end of the dataset."""
    return (
        f"Available Routes:<br/>4" )

@app.route("/api/v1.0/start_end")
def start_end():
    """List the min, max, and average temperatures calculated from the given start date to the given end date."""
    return (
        f"Available Routes:<br/>5" )



if __name__ == "__main__":
    app.run(debug=True)