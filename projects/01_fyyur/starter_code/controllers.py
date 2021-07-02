"""Controllers."""
import sys
from datetime import datetime

from flask import render_template, request, Response, flash, redirect, url_for, Blueprint

from forms import *
from models import *

app = Blueprint('', __name__)

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = {}
  raw_data = Venue.query.all()
  for venue in raw_data:
    venue_data = {
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': 0,
    }
    name_key = f'{venue.city}-{venue.state}'
    if name_key in data:
        data[name_key]['venues'].append(venue_data)
    else:
        data[name_key] = {
            'city': venue.city,
            'state': venue.state,
            'venues': [venue_data]
        }
  
  return render_template('pages/venues.html', areas=data.values());

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_keyword = request.form.get('search_term', '')
  query = Venue.query.filter(Venue.name.ilike(f'%{search_keyword}%')).all()
  response={
    "count": len(query),
    "data": query
  }
  
  return render_template('pages/search_venues.html', results=response, search_term=search_keyword)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = Venue.query.get(venue_id)
  past_shows = Show.query.filter(Show.start_time < datetime.now(), Show.venue_id == venue_id, Venue.id == Show.venue_id, Artist.id == Show.artist_id).with_entities(
    Show.artist_id, Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link'), Show.start_time
  ).all()
  data.past_shows = past_shows
  data.past_shows_count = len(past_shows)
  upcoming_shows = Show.query.filter(Show.start_time >= datetime.now(), Show.venue_id == venue_id, Venue.id == Show.venue_id, Artist.id == Show.artist_id).with_entities(
    Show.artist_id, Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link'), Show.start_time
  ).all()
  data.upcoming_shows = upcoming_shows
  data.upcoming_shows_count = len(upcoming_shows)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = ''
  try:
    genres = request.form.getlist('genres')
    request_data = dict(request.form)
    del request_data['genres']

    request_data['website'] = request_data.get('website_link', '')
    del request_data['website_link']

    request_data['seeking_talent'] = request_data.get('seeking_talent', 'y') == 'y'
    
    venue = Venue(**request_data)
    genres_list = list(Genre.query.filter(Genre.name.in_(genres)).all())
    venue.genres = genres_list
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.', 'error')
    error = sys.exc_info()
  finally:
    db.session.close()
  
  if error:
    return render_template('forms/new_venue.html', form=VenueForm(request.form))

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash('Venue successfully deleted!')
    except:
        db.session.rollback()
        flash('Cannot delete venue!', 'error')
    finally:
        db.session.close()
    
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_keyword = request.form.get('search_term', '')
  query = Artist.query.filter(Artist.name.ilike(f'%{search_keyword}%')).all()
  response={
    "count": len(query),
    "data": query
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_keyword)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data = Artist.query.get(artist_id)
  past_shows = Show.query.filter(Show.start_time < datetime.now(), Show.artist_id == artist_id, Venue.id == Show.venue_id, Artist.id == Show.artist_id).with_entities(
    Venue.id.label('venue_id'), Venue.name.label('venue_name'),
    Venue.image_link.label('venue_image_link'), Show.start_time
  ).all()
  data.past_shows = past_shows
  data.past_shows_count = len(past_shows)
  upcoming_shows = Show.query.filter(Show.start_time >= datetime.now(), Show.artist_id == artist_id, Venue.id == Show.venue_id, Artist.id == Show.artist_id).with_entities(
    Venue.id.label('venue_id'), Venue.name.label('venue_name'),
    Venue.image_link.label('venue_image_link'), Show.start_time
  ).all()
  data.upcoming_shows = upcoming_shows
  data.upcoming_shows_count = len(upcoming_shows)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  genres = artist.genres
  form = ArtistForm(data=dict(artist.__dict__))
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  genres = request.form.getlist('genres')
  request_data = dict(request.form)
  del request_data['genres']

  request_data['website'] = request_data.get('website_link', '')
  del request_data['website_link']

  request_data['seeking_venue'] = request_data.get('seeking_venue', 'y') == 'y'
  
  artist = Artist.query.get(artist_id)

  for key, value in request_data.items():
    if getattr(artist, key) != value:
      setattr(artist, key, value)
  
  genres_list = list(Genre.query.filter(Genre.name.in_(genres)).all())
  artist.genres = genres_list

  db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  genres = venue.genres
  form = VenueForm(data=dict(venue.__dict__))
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  genres = request.form.getlist('genres')
  request_data = dict(request.form)
  del request_data['genres']

  request_data['website'] = request_data.get('website_link', '')
  del request_data['website_link']

  request_data['seeking_talent'] = request_data.get('seeking_talent', 'y') == 'y'

  venue = Venue.query.get(venue_id)

  for key, value in request_data.items():
    if getattr(venue, key) != value:
      setattr(venue, key, value)
  
  genres_list = list(Genre.query.filter(Genre.name.in_(genres)).all())
  venue.genres = genres_list

  db.session.commit()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = ''
  try:
    genres = request.form.getlist('genres')
    request_data = dict(request.form)
    del request_data['genres']

    request_data['website'] = request_data.get('website_link', '')
    del request_data['website_link']

    request_data['seeking_venue'] = request_data.get('seeking_venue', 'y') == 'y'
    
    artist = Artist(**request_data)
    genres_list = list(Genre.query.filter(Genre.name.in_(genres)).all())
    artist.genres = genres_list
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.', 'error')
    error = sys.exc_info()
  finally:
    db.session.close()
  
  if error:
    return render_template('forms/new_artist.html', form=ArtistForm(request.form))

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = Show.query.filter(Venue.id == Show.venue_id, Artist.id == Show.artist_id).with_entities(
    Venue.id.label('venue_id'), Venue.name.label('venue_name'), Show.artist_id, Artist.name.label('artist_name'),
    Artist.image_link.label('artist_image_link'), Show.start_time
  ).all()
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = ''
  try:
    request_data = dict(request.form)
    show = Show(**request_data)
    
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.', 'error')
    error = sys.exc_info()
  finally:
    db.session.close()
  
  if error:
    return render_template('forms/new_show.html', form=ShowForm(request.form))

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
