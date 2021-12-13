#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import os
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.orm import backref, query
from forms import *
from datetime import datetime
from sqlalchemy import desc
from models import db, Venue, Artist, Show, pre_load_data
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.app = app
db.init_app(app)




# TODO: connect to a local postgresql database
migrate = Migrate(app, db)



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  query = db.session.query(Venue.state, Venue.city)
  for (state, city) in query.distinct().order_by(Venue.state).all():
    venues = Venue.query.filter_by(state=state, city=city).order_by('name').all()
    data.append({
      'city': city,
      'state': state,
      "venues": [{
        'id': venue.id,
        'name': venue.name
      } for venue in venues]
    })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).order_by('name').all()
  response = {
    "count": len(venues),
    "data": [{
      'id': venue.id,
      'name': venue.name
    } for venue in venues]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  data = dict(venue.__dict__)
  # check the keys in data
  print(data.keys())
  data.pop('_sa_instance_state', None)

  # query = Show.query.filter_by(venue_id=venue_id)
  # modified and now using JOIN
  query = db.session.query(Show).join(Show.venue)
  upcoming_shows = query.filter(Show.start_time >= datetime.today()).order_by('start_time').all()
  past_shows = query.filter(Show.start_time < datetime.today()).order_by(desc('start_time')).all()

  data['upcoming_shows_count'] = len(upcoming_shows)
  data['upcoming_shows'] = [{
    'artist_id': show.artist.id,
    'artist_name': show.artist.name,
    'artist_image_link': show.artist.image_link,
    'start_time': show.start_time.strftime("%m-%d-%Y %H:%M:%S")
  } for show in upcoming_shows]
  data['past_shows_count'] = len(past_shows)
  data['past_shows'] = [{
    'artist_id': show.artist.id,
    'artist_name': show.artist.name,
    'artist_image_link': show.artist.image_link,
    'start_time': show.start_time.strftime("%m-%d-%Y %H:%M:%S")
  } for show in past_shows]
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  try:
    kargs = dict(request.form)
    kargs['genres'] = request.form.getlist('genres')
    # if the checkbox is checked, request.form['seeking_talent'] = 'y', else None
    kargs['seeking_talent'] = True if request.form.get('seeking_talent') else False
    print(kargs)
    venue = Venue(**kargs)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    print(sys.exc_info())
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

#  Delete Venue
#  ----------------------------------------------------------------

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # implemented in show_venue.html
  try:
    venue = Venue.query.get_or_404(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully deleted!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
  finally:
    db.session.close()

  return jsonify({'success':True}) 

#  Update Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  query = Venue.query.filter_by(id=venue_id)
  if (query.all() == []):
    return render_template('errors/404.html'), 404
  try:
    kargs = dict(request.form)
    kargs['genres'] = request.form.getlist('genres')
    # if the checkbox is checked, request.form['seeking_talent'] = 'y', else None
    kargs['seeking_talent'] = True if request.form.get('seeking_talent') else False
    print(kargs)
    query.update(kargs)
    db.session.commit()
    flash('Venue ' + kargs['name'] + ' was successfully edited!')
  except:
    print(sys.exc_info())
    db.session.rollback()
    flash('An error occurred. Venue could not be edited.')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.order_by('name').all()
  data = [{
    'id': artist.id,
    'name': artist.name
  } for artist in artists]

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).order_by('name').all()
  response = {
    "count": len(artists),
    "data": [{
      'id': artist.id,
      'name': artist.name
    } for artist in artists]
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  data = dict(artist.__dict__)
  # check the keys in data
  print(data.keys())
  data.pop('_sa_instance_state', None)

  # query = Show.query.filter_by(artist_id=artist_id)
  # Using JOIN query
  query = db.session.query(Show).join(Show.artist)
  upcoming_shows = query.filter(Show.start_time >= datetime.today()).order_by('start_time').all()
  past_shows = query.filter(Show.start_time < datetime.today()).order_by(desc('start_time')).all()

  data['upcoming_shows_count'] = len(upcoming_shows)
  data['upcoming_shows'] = [{
    'venue_id': show.venue.id,
    'venue_name': show.venue.name,
    'venue_image_link': show.venue.image_link,
    'start_time': show.start_time.strftime("%m-%d-%Y %H:%M:%S")
  } for show in upcoming_shows]
  data['past_shows_count'] = len(past_shows)
  data['past_shows'] = [{
    'venue_id': show.venue.id,
    'venue_name': show.venue.name,
    'venue_image_link': show.venue.image_link,
    'start_time': show.start_time.strftime("%m-%d-%Y %H:%M:%S")
  } for show in past_shows]
  
  return render_template('pages/show_artist.html', artist=data)


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    kargs = dict(request.form)
    kargs['genres'] = request.form.getlist('genres')
    # if the checkbox is checked, request.form['seeking_venue'] = 'y', else None
    kargs['seeking_venue'] = True if request.form.get('seeking_venue') else False
    print(kargs)
    artist = Artist(**kargs)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    print(sys.exc_info())
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

#  Delete Artist
#  ----------------------------------------------------------------

@app.route('/artists/<artist_id>/delete', methods=['DELETE'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # implemented in show_venue.html
  try:
    artist = Artist.query.get_or_404(artist_id)
    db.session.delete(artist)
    db.session.commit()
    flash('Artist ' + artist.name + ' was successfully deleted!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + artist.name + ' could not be deleted.')
  finally:
    db.session.close()

  return jsonify({'success':True}) 

#  Update Artist
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  query = Artist.query.filter_by(id=artist_id)
  if (query.all() == []):
    return render_template('errors/404.html'), 404
  try:
    kargs = dict(request.form)
    kargs['genres'] = request.form.getlist('genres')
    # if the checkbox is checked, request.form['seeking_venue'] = 'y', else None
    kargs['seeking_venue'] = True if request.form.get('seeking_venue') else False
    print(kargs)
    query.update(kargs)
    db.session.commit()
    flash('Artist ' + kargs['name'] + ' was successfully edited!')
  except:
    print(sys.exc_info())
    db.session.rollback()
    flash('An error occurred. Artist could not be edited.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))




#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = Show.query.order_by(desc('start_time')).all()
  for show in shows:
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)
    data.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime("%m-%d-%Y %H:%M:%S")
    })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    show = Show(**request.form)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    print(sys.exc_info())
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:
if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=5000)
