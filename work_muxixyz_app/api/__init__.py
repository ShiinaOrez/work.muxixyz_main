from flask import Blueprint

api=Blueprint("api",__name__)

from . import auth, management, project, file, share, status
