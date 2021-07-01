"""Models."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class BasicInfo:
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500), nullable=True)
    image_link = db.Column(db.String(500))


class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    start_time = db.Column(db.DateTime, nullable=True)


VenueGenre = db.Table('venue_genre',
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True),
    db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True),
)


class Venue(BasicInfo, db.Model):
    __tablename__ = 'venue'

    address = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    genres = db.relationship('Genre', secondary=VenueGenre, backref=db.backref('venues', lazy=True))
    shows = db.relationship('Show', backref=db.backref('venues', lazy=True))


ArtistGenre = db.Table('artist_genre',
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True),
)


class Artist(BasicInfo, db.Model):
    __tablename__ = 'artist'

    seeking_venue = db.Column(db.Boolean, default=False)
    shows = db.relationship('Show', backref=db.backref('artists', lazy='immediate'))
    genres = db.relationship('Genre', secondary=ArtistGenre, backref=db.backref('artist', lazy='selectin'))


class Genre(db.Model):
    __tablename__ = 'genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __repr__(self):
      return self.name
