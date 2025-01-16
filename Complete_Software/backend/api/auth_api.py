from flask import Blueprint, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.db import db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = db.users.find_one({'username': username})
    
    if user and check_password_hash(user['password'], password):
        session['user_id'] = str(user['_id'])
        return jsonify({
            'success': True,
            'user': {
                'username': user['username'],
                'role': user['role']
            }
        })
    
    return jsonify({
        'success': False,
        'message': 'Invalid credentials'
    }), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@auth_bp.route('/status')
def status():
    if 'user_id' in session:
        user = db.users.find_one({'_id': session['user_id']})
        return jsonify({
            'authenticated': True,
            'user': {
                'username': user['username'],
                'role': user['role']
            }
        })
    return jsonify({'authenticated': False})

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    
    if db.users.find_one({'username': data['username']}):
        return jsonify({
            'success': False,
            'message': 'Username already exists'
        }), 400
    
    user = {
        'username': data['username'],
        'password': generate_password_hash(data['password']),
        'role': 'user',  # Default role
        'created_at': datetime.utcnow(),
        'status': 'active'
    }
    
    db.users.insert_one(user)
    
    return jsonify({
        'success': True,
        'message': 'User registered successfully'
    })

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'message': 'Not authenticated'
        }), 401
    
    data = request.json
    user = db.users.find_one({'_id': session['user_id']})
    
    if not check_password_hash(user['password'], data['current_password']):
        return jsonify({
            'success': False,
            'message': 'Current password is incorrect'
        }), 400
    
    db.users.update_one(
        {'_id': session['user_id']},
        {'$set': {'password': generate_password_hash(data['new_password'])}}
    )
    
    return jsonify({
        'success': True,
        'message': 'Password updated successfully'
    }) 