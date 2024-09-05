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
        "/api/v1.0/<start><br/>"
        "/api/v1.0/<start>/<end>" )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    end_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    start_date = dt.datetime.strptime(end_date, '%Y-%m-%d') - dt.timedelta(days=366)
    precep_scores = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()
    print(precep_scores)
    session.close()

    precep_dict = {date: prcp for date, prcp in precep_scores}

    return jsonify(precep_dict)

@app.route("/api/v1.0/stations")
def stations():
    """List jsonified data of all of the stations in the database."""
    session = Session(engine)
    stations = session.query(Station.station).distinct().all()
    session.close()
    print(stations)
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

@app.route("/api/v1.0/<start>")
def start(start):
    """List the min, max, and average temperatures calculated from the given start date to the end of the dataset."""
    session = Session(engine)
    
    end_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    
    until_today = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()
    
    session.close()
    
    totals = [(f'Date range from {start_date} to {end_date}. Minimum: {min}, Maximum: {max}, Average: {round(avg, 2)}') for min, max, avg in until_today]

    
    return jsonify(totals)


@app.route("/api/v1.0/<start>/<end>")
def dates(start, end):
    """List the min, max, and average temperatures calculated from the given start date to the given end date."""
    session = Session(engine)
    
    end_date = start_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    
    date_range = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()
    
    session.close()
    
    totals2 = [(f'Date range from {start_date} to {end_date}. Minimum: {min}, Maximum: {max}, Average: {round(avg, 2)}') for min, max, avg in date_range]

    
    return jsonify(totals2)



if __name__ == "__main__":
    app.run(debug=True)