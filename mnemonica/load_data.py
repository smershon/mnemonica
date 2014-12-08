import sys
import sqlite3

DEFAULT_DB_PATH = 'data/mnemonica.db'

def memdb(func):
    def inner(*args, **kwargs):
        conn = kwargs.get('conn')
        if not conn:
            conn = sqlite3.connect(DEFAULT_DB_PATH)
            kwargs.update(conn=conn)
            ret = func(*args, **kwargs)
            conn.commit()
            conn.close()
        else:
            ret = func(*args, **kwargs)
        return ret

    return inner

class Country(object):
    name = ''
    capital = ''
    largest_cities = ['']*5
    population = 0
    area = 0
    highest_point = 0
    neighbors = set()
    
    def __repr__(self):
        return '%s [%s] %r %d %d %d %r' % (
            self.name, self.capital, self.largest_cities, self.population,
            self.area, self.highest_point, self.neighbors)


@memdb
def create_schema(conn):
    c = conn.cursor()
    c.execute("""
        CREATE TABLE data (
            country text, 
            capital text, 
            largest_cities text, 
            population integer, 
            area integer,
            highest_point integer,
            neighbors text)
        """)

@memdb
def get_country(country_name, conn):
    c = conn.cursor()
    c.execute("""
        SELECT * FROM data WHERE country=?""",
        (country_name,))
    result = c.fetchone()

    country = Country()
    if result:
        country.name = result[0]
        country.capital = result[1]
        country.largest_cities = result[2].split('\t')
        country.population = result[3]
        country.area = result[4]
        country.highest_point = result[5]
        country.neighbors = set(result[6].split('\t')) - set([''])
    else:
        country.name = country_name

    return country

@memdb
def add_country(country, conn):
    largest_cities = '\t'.join(country.largest_cities)
    neighbors = '\t'.join(country.neighbors)
    c = conn.cursor()
    c.execute("""
        DELETE FROM data WHERE country=?""",
        (country.name,))
    c.execute("""
        INSERT OR REPLACE INTO data VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (country.name,
         country.capital,
         largest_cities,
         country.population,
         country.area,
         country.highest_point,
         neighbors))

def add_fact(country, field, value):
    """
    Add this value for the given field on a country. 
    If the country does not already exist, create it with default values.
    """
    country = get_country(country)
    if field in ['capital', 'population', 'area', 'highest_point']:
        setattr(country, field, value)
    elif field.startswith('largest_cities'):
        rank = int(field.split(':')[-1]) - 1
        country[rank] = value
    elif field == 'neighbor':
        country.neighbors.add(value)
    else:
        raise ValueError('field %r not a valid field name' % field)
    add_country(country)

if __name__ == '__main__':
    arg = sys.argv[1]
    if arg.lower() == 'create':
        create_schema()
