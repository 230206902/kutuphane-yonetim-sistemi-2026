from flask import Blueprint

borrow = Blueprint('borrow', __name__)

from app.borrow import routes
