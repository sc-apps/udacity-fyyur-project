#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from models import db, Show, Venue, Artist, setup_db
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# DONE: connect to a local postgresql database
app = Flask(__name__)
setup_db(app)
moment = Moment(app)
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

# DONE: replace with real venues data. num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
@app.route('/venues')
def venues():
  areas = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).order_by('state').all()
  data = []
  for area in areas:
    venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).order_by('name').all()
    venue_data = []
    data.append({'city': area.city, 'state': area.state, 'venues': venue_data})
    for venue in venues:
      shows = Show.query.filter_by(venue_id=venue.id).all()
      venue_data.append({'id': venue.id, 'name': venue.name, 'num_upcoming_shows': len(shows)})
  return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search = request.form.get('search_term', '')  
  venues = Venue.query.filter(Venue.name.ilike("%" + search + "%")).all()
  data = []
  
  for venue in venues:
    data.append({
      'id': venue.id,
      'name': venue.name,
      })
  response = {
      'count': len(venues),
      'data': data
  }
  return render_template('pages/search_venues.html', results=response, search_term=search)


# DONE: replace with real venue data from the venues table, using venue_id
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  past_shows = db.session.query(Artist,Show).join(Show).join(Venue).filter(Show.venue_id == venue_id, Show.artist_id == Artist.id, Show.start_time < datetime.now()).all()
  upcoming_shows = db.session.query(Artist,Show).join(Show).join(Venue).filter(Show.venue_id == venue_id, Show.artist_id == Artist.id, Show.start_time > datetime.now()).all() 

  data = {
          'id': venue.id,
          'name': venue.name,
          'genres': venue.genres,
          'address': venue.address,
          'city': venue.city,
          'state': venue.state,
          'phone': venue.phone,
          'website': venue.website_link,
          'facebook_link': venue.facebook_link,
          'seeking_talent': venue.seeking_talent,
          'seeking_description': venue.seeking_description,
          'image_link': venue.image_link,
          'past_shows': [{'artist_id': artist.id, 'artist_name': artist.name, 'artist_image_link': artist.image_link, 'start_time': str(show.start_time)} for artist, show in past_shows],
          'upcoming_shows': [{'artist_id': artist.id, 'artist_name': artist.name, 'artist_image_link': artist.image_link, 'start_time': str(show.start_time)} for artist, show in upcoming_shows],
          'past_shows_count': len(past_shows),
          'upcoming_shows_count': len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE: insert form data as a new Venue record in the db, instead
    form = VenueForm()
    if form.validate():
      new_venue = Venue(
        name=request.form.get('name'), 
        genres=request.form.getlist('genres'), 
        address=request.form.get('address'), 
        city=request.form.get('city'), 
        state=request.form.get('state'), 
        phone=request.form.get('phone'), 
        facebook_link=request.form.get('facebook_link'),
        seeking_talent=request.form.get('seeking_talent'), 
        seeking_description=request.form.get('seeking_description'), 
        image_link=request.form.get('image_link'),
        website_link=request.form.get('website_link')
      )   
      db.session.add(new_venue)
      db.session.commit() 

    # DONE: modify data to be the data object returned from db insertion on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    else:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed. Error: {0}'.format(form.errors))
      db.session.rollback()
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # DONE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    venue = Venue.query.get(venue_id)
    show = Show.query.filter_by(venue_id=venue_id).first()
    db.session.delete(venue)
    if show:
      db.session.delete(show)
    db.session.commit()
    flash('The venue has been successfully deleted')
    return render_template('pages/home.html')
  except:
    db.session.rollback()
    flash('An error occurred. Venue could not be deleted.')
  finally:
    db.session.close()


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)
  

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search = request.form.get('search_term', '')  
  artists = Artist.query.filter(Artist.name.ilike("%" + search + "%")).all()
  data = []
  
  for artist in artists:
    data.append({
      'id': artist.id,
      'name': artist.name,
      })
  response = {
      'count': len(artists),
      'data': data
  }
  return render_template('pages/search_artists.html', results=response, search_term=search)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # DONE: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.filter_by(id=artist_id).first_or_404()

  past_shows = db.session.query(Venue,Show).join(Show).join(Artist).filter(Show.artist_id == artist_id, Show.venue_id == Venue.id, Show.start_time < datetime.now()).all()
  upcoming_shows = db.session.query(Venue,Show).join(Show).join(Artist).filter(Show.artist_id == artist_id, Show.venue_id == Venue.id, Show.start_time > datetime.now()).all()

  data = {
          'id': artist.id,
          'name': artist.name,
          'genres': artist.genres,
          'city': artist.city,
          'state': artist.state,
          'phone': artist.phone,
          'website': artist.website_link,
          'facebook_link': artist.facebook_link,
          'seeking_venue': artist.seeking_venue,
          'seeking_description': artist.seeking_description,
          'image_link': artist.image_link,
          'past_shows': [{'venue_id': venue.id, 'venue_name': venue.name, 'venue_image_link': venue.image_link, 'start_time': str(show.start_time)} for venue, show in past_shows],
          'upcoming_shows': [{'venue_id': venue.id, 'venue_name': venue.name, 'venue_image_link': venue.image_link, 'start_time': str(show.start_time)} for venue, show in upcoming_shows],
          'past_shows_count': len(past_shows),
          'upcoming_shows_count': len(upcoming_shows)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # DONE: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  form = ArtistForm()
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.website_link.data = artist.website_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE: take values from the form submitted, and update existing artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  if form.validate():
    artist = Artist.query.filter_by(id=artist_id).first_or_404()
    artist.name = form.name.data
    artist.city = form.city.data 
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.website_link = form.website_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully modified!')
  else:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be modified. Error {0}'.format(form.errors))
    db.session.rollback()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # DONE: populate form with values from venue with ID <venue_id>
  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  form = VenueForm()
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.website_link.data = venue.website_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE: take values from the form submitted, and update existing venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  if form.validate():
    venue = Venue.query.filter_by(id=venue_id).first_or_404()
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.genres = form.genres.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.website_link = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully modified!')
  else:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be modified. Error: {0}'.format(form.errors))
      db.session.rollback()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  
  form = ArtistForm(request.form)
  if form.validate():
    new_artist = Artist(
          name=request.form.get('name'), 
          genres=request.form.getlist('genres'),  
          city=request.form.get('city'), 
          state=request.form.get('state'), 
          phone=request.form.get('phone'), 
          facebook_link=request.form.get('facebook_link'),
          seeking_venue=request.form.get('seeking_venue'),
          seeking_description=request.form.get('seeking_description'), 
          image_link=request.form.get('image_link'),
          website_link=request.form.get('website_link')
        )   
    db.session.add(new_artist)
    db.session.commit()

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
    # DONE: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed. Error {0}'.format(form.errors))
    db.session.rollback()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.
  shows = Show.query.all()
  data = []
  for show in shows:
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)
    data.append({"venue_id": show.venue_id, "venue_name": venue.name, "artist_id": show.artist_id, "artist_name": artist.name, "artist_image_link": artist.image_link, "start_time": str(show.start_time)})
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # DONE: insert form data as a new Show record in the db, instead
  try:
    new_show = Show(
      artist_id=request.form.get('artist_id'), 
      venue_id=request.form.get('venue_id'), 
      start_time=request.form.get('start_time') 
      )
    db.session.add(new_show)
    db.session.commit() 
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
  # DONE: on unsuccessful db insert, flash an error instead. See: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
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
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
