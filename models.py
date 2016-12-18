from tasks import db
from sqlalchemy.dialects.postgresql import JSON
from flask import Flask, render_template, request, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy



class Result(db.Model):
    __tablename__ = 'Result'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    task_id = db.Column(db.String(500))
    query = db.Column(db.String(500))