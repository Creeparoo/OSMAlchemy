# OSMAlchemy

OSMAlchemy is a bridge between SQLAlchemy and the OpenStreetMap API.

## Goal

OSMAlchemy's goal is to provide completely transparent integration of
the real-world OpenStreetMap data within projects using SQLAlchemy. It
provides two things:

 1. Model declaratives resembling the structure of the main
    OpenStreetMap database, with some limitations, usable wherever
    SQLAlchemy is used, and
 2. Transparent proxying and data-fetching from OpenStreetMap data.

The idea is that the model can be queried using SQLAlchemy, and
OSMAlchemy will either satisfy the query from the database directly or
fetch data from OpenStreetMap. That way, projects already using
SQLAlchemy do not need another database framework to use OpenStreetMap
data, and the necessity to keep a local copy of planet.osm is relaxed.

If, for example, a node with a certain id is queried, OSMAlchemy will…

 * …try to get the node from the database/ORM directly, then…
   * …if it is available, check its caching age, and…
     * …if it is too old, refresh it from OSM, or…
   * …else, fetch it from OSM, and…
 * …finally create a real, ORM-mapped database object.

That's the rough idea, and it counts for all kinds of OSM elements and
queries.

OSMAlchemy uses Overpass to satisfy complex queries.

### Non-goals

OSMAlchemy does not aim to replace large-scale OSM data frameworks like
PostGIS, Osmosis or whatever. In fact, in terms of performance and
otherwise, it cannot keep up with them.

If you are running a huge project that handles massive amounts of map
data, has millions of requests or users, then OSMAlchemy is not for you
(YMMV).

OSMAlchemy fills a niche for projects that have limited resources and
cannot handle a full copy of planet.osm and an own API backend and
expect to handle limited amounts of map data.

It might, however, be cool to use OSMAlchemy as ORM proxy with an own
API backend. Who knows?

It might, as well, turn out that OSMAlchemy is an incredibly silly idea
under all circumstances.

### Projects using OSMAlchemy

OSMAlchemy was designed for use in the Veripeditus Augmented Reality
framework.

## Development and standards

Albeit taking the above into account, OSMAlchemy is developed with
quality and good support in mind. That means code shall be well-tested
and well-documented.

OSMAlchemy is tested against the following SQLAlchemy backends:

 * SQLite
 * PostgreSQL
 * MySQL

However, we recommend PostgreSQL. MySQL acts strangely with some data
and is incredibly slow, and SQLite just doesn't scale too well (however,
it is incredibly fast, in comparison).

### Code status

[![Build Status](https://scrutinizer-ci.com/g/Natureshadow/OSMAlchemy/badges/build.png?b=master)](https://scrutinizer-ci.com/g/Natureshadow/OSMAlchemy/build-status/master)
[![Code Coverage](https://scrutinizer-ci.com/g/Natureshadow/OSMAlchemy/badges/coverage.png?b=master)](https://scrutinizer-ci.com/g/Natureshadow/OSMAlchemy/?branch=master)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/Natureshadow/OSMAlchemy/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/Natureshadow/OSMAlchemy/?branch=master)

## License

OSMAlchemy is licensed under the MIT license. Alternatively, you are
free to use OSMAlchemy under Simplified BSD, The MirOS Licence, GPL-2+,
LGPL-2.1+, AGPL-3+ or the same terms as Python itself.
