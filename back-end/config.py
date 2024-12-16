from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
#     username="sstafford4",
#     password="Simperia1",
#     hostname="sstafford4.mysql.pythonanywhere-services.com",
#     databasename="sstafford4$default",
# )
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/final_project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



