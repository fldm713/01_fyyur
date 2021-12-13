from app import *

for venue in Venue.query.filter(Venue.id<=3):
    db.session.delete(venue)
for artist in Artist.query.filter(Artist.id<=3):
    db.session.delete(artist)
db.session.commit()

venues = [
  {
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "city": "San Francisco",
    "state": "CA",    
    "address": "1015 Folsom Street",        
    "phone": "123-123-1234",
    "website_link": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  }, {
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "city": "New York",
    "state": "NY",
    "address": "335 Delancey Street",
    "phone": "914-003-1132",
    "website_link": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "seeking_talent": False,
  }, {
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "city": "San Francisco",
    "state": "CA",
    "address": "34 Whiskey Moore Ave",
    "phone": "415-000-1234",
    "website_link": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "seeking_talent": False,
  }
]

for venue in venues:
  db.session.add(Venue(**venue))

artists = [
  {
    "id": 1,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website_link": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",    
  }, {
    "id": 2,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "seeking_venue": False,
  }, {
    "id": 3,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "seeking_venue": False,
  }
]

for artist in artists:
  db.session.add(Artist(**artist))


db.session.add(Show(id=1, venue_id=1, artist_id=1, start_time='2021-12-11 21:00:00'))
db.session.add(Show(id=2, venue_id=2, artist_id=1, start_time='2021-12-08 21:00:00'))
db.session.add(Show(id=3, venue_id=3, artist_id=2, start_time='2021-12-15 21:00:00'))
db.session.add(Show(id=4, venue_id=3, artist_id=3, start_time='2022-01-17 21:00:00'))
db.session.add(Show(id=5, venue_id=3, artist_id=3, start_time='2021-12-29 21:00:00'))
db.session.add(Show(id=6, venue_id=2, artist_id=3, start_time='2021-12-12 21:00:00'))

db.session.commit()
db.session.close()

db.engine.execute("ALTER SEQUENCE venues_id_seq RESTART WITH 4;")
db.engine.execute("ALTER SEQUENCE artists_id_seq RESTART WITH 4;")
db.engine.execute("ALTER SEQUENCE shows_id_seq RESTART WITH 7;")
