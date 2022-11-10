import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
SQLALCHEMY_DATABASE_NAME = 'trivia'
SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}/{}'.format('postgres', 'postgres','localhost:5432', SQLALCHEMY_DATABASE_NAME)
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Connect to test database
SQLALCHEMY_DATABASE_TEST_NAME = 'trivia_test'
os.environ['SQLALCHEMY_DATABASE_TEST_URI'] = 'postgresql://{}:{}@{}/{}'.format('postgres', 'postgres','localhost:5432', 'trivia_test')
os.environ['SQLALCHEMY_TRACK_TEST_MODIFICATIONS'] = 'True'

