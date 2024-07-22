import re
from datetime import datetime
import requests
from flask import Blueprint, request, flash, redirect, url_for, render_template, current_app, jsonify
from models import db, Show, Episode, AppSettings
import requests

bp = Blueprint('app_routes', __name__)

@bp.route('/send_to_sabnzbd', methods=['POST'])
def send_to_sabnzbd():
    sabnzbd_url = AppSettings.get_setting('SABNZBD_URL')
    sabnzbd_api = AppSettings.get_setting('SABNZBD_API')
    
    if not sabnzbd_url or not sabnzbd_api:
        return jsonify({'success': False, 'message': 'SABnzbd URL or API key not set'}), 400

    # Construct the SABnzbd API URL
    api_url = f"{sabnzbd_url}/api"
    
    # Prepare the base parameters for the SABnzbd API call
    params = {
        'apikey': sabnzbd_api,
        'output': 'json'
    }

    # Log the API URL and parameters (mask the API key)
    masked_params = params.copy()
    masked_params['apikey'] = '*' * len(masked_params['apikey'])
    current_app.logger.info(f"Sending request to SABnzbd API. URL: {api_url}, Params: {masked_params}")

    # First, test the API connection
    test_params = params.copy()
    test_params['mode'] = 'version'
    try:
        test_response = requests.get(api_url, params=test_params)
        test_response.raise_for_status()
        test_result = test_response.json()
        if 'version' not in test_result:
            current_app.logger.error(f"SABnzbd API test failed. Response: {test_result}")
            return jsonify({'success': False, 'message': 'Failed to connect to SABnzbd API', 'details': test_result}), 400
    except requests.RequestException as e:
        current_app.logger.error(f"Error testing SABnzbd API connection: {str(e)}")
        return jsonify({'success': False, 'message': 'Error connecting to SABnzbd API', 'details': str(e)}), 500

    if 'nzb_file' in request.files:
        # File upload case
        nzb_file = request.files['nzb_file']
        params['mode'] = 'addfile'
        files = {'nzbfile': (nzb_file.filename, nzb_file)}
        response = requests.post(api_url, params=params, files=files)
    elif 'nzb_url' in request.form:
        # URL-based case
        params['mode'] = 'addurl'
        params['name'] = request.form['nzb_url']
        response = requests.get(api_url, params=params)
    elif 'local_path' in request.form:
        # Local file path case
        params['mode'] = 'addlocalfile'
        params['name'] = request.form['local_path']
        response = requests.get(api_url, params=params)
    else:
        return jsonify({'success': False, 'message': 'No NZB file, URL, or local path provided'}), 400

    if 'nzbname' in request.form:
        params['nzbname'] = request.form['nzbname']

    try:
        response.raise_for_status()
        
        # Log the response status and content
        current_app.logger.info(f"SABnzbd API response status: {response.status_code}")
        current_app.logger.info(f"SABnzbd API response content: {response.text[:1000]}...")  # Log first 1000 characters

        # Try to parse JSON, but handle the case where it's not JSON
        try:
            result = response.json()
            if result.get('status'):
                return jsonify({'success': True, 'message': 'Successfully sent to SABnzbd'})
            else:
                current_app.logger.error(f"SABnzbd API returned error: {result}")
                return jsonify({'success': False, 'message': 'Failed to send to SABnzbd', 'details': result}), 400
        except ValueError:
            # Response is not JSON
            current_app.logger.error(f"Unexpected response from SABnzbd (not JSON): {response.text}")
            return jsonify({'success': False, 'message': 'Unexpected response from SABnzbd (not JSON)'}), 500
    except requests.RequestException as e:
        current_app.logger.error(f"Error sending to SABnzbd: {str(e)}")
        return jsonify({'success': False, 'message': 'Error communicating with SABnzbd', 'details': str(e)}), 500

def search_show(title):
    BASE_URL = AppSettings.get_setting('BASE_URL')
    API_KEY = AppSettings.get_setting('API_KEY')
    url = f"{BASE_URL}?t=search&q={title}&apikey={API_KEY}&o=json"
    masked_url = url.replace(API_KEY, '*' * len(API_KEY))
    print(f"API Request: {masked_url}")  # Output the masked URL to console
    response = requests.get(url)
    return response.json()

def download_nzb(nzb_id):
    BASE_URL = AppSettings.get_setting('BASE_URL')
    API_KEY = AppSettings.get_setting('API_KEY')
    url = f"{BASE_URL}?t=get&id={nzb_id}&apikey={API_KEY}"
    response = requests.get(url)
    return response.content

def extract_show_name_date_and_episode(title):
    # Regex to extract show name, date, and episode name (up to the marker)
    match = re.match(r'^(?P<show_name>[^.]+)\.(?P<date>\d{2})\.(?P<month>\d{2})\.(?P<day>\d{2})\.(?P<episode_name>[^.]+)', title, re.IGNORECASE)
    if match:
        show_name = match.group('show_name').lower()  # Ensure case insensitivity
        date = datetime.strptime(f"{match.group('date')}.{match.group('month')}.{match.group('day')}", '%y.%m.%d')
        episode_name = match.group('episode_name')
        return show_name, date, episode_name
    return None, None, None

def extract_date_from_title(title):
    _, date, _ = extract_show_name_date_and_episode(title)
    return date

@bp.route('/add', methods=['POST'])
def add_show():
    title = request.form.get('title').lower()  # Save in lowercase
    current_app.logger.debug(f'Adding show with title: {title}')
    if title:
        new_show = Show(title=title)
        db.session.add(new_show)
        db.session.commit()
        flash('Show added successfully!', 'success')
        current_app.logger.debug(f'Added show: {new_show}')
    else:
        flash('Title cannot be empty.', 'danger')
        current_app.logger.debug('Title cannot be empty.')
    return redirect(url_for('routes.dashboard'))

@bp.route('/delete/<int:show_id>', methods=['POST'])
def delete_show(show_id):
    show = Show.query.get(show_id)
    if show:
        # Delete all associated episodes first
        Episode.query.filter_by(show_id=show_id).delete()
        # Then delete the show
        db.session.delete(show)
        db.session.commit()
        flash('Show and its episodes deleted successfully!', 'success')
    else:
        flash('Show not found.', 'danger')
    return redirect(url_for('routes.dashboard'))

def remove_duplicate_episodes(show_id):
    episodes = Episode.query.filter_by(show_id=show_id).all()
    unique_episodes = {}
    for episode in episodes:
        key = (episode.show_id, episode.date)
        if key in unique_episodes:
            if len(episode.name) < len(unique_episodes[key].name):
                db.session.delete(unique_episodes[key])
                unique_episodes[key] = episode
            else:
                db.session.delete(episode)
        else:
            unique_episodes[key] = episode
    db.session.commit()

@bp.route('/search/<show_title>')
def search(show_title):
    current_app.logger.debug(f'Searching for show title: {show_title}')
    results = search_show(show_title)
    filtered_results = [result for result in results['channel']['item'] if '1080p' in result['title']]
    
    show = Show.query.filter_by(title=show_title).first()
    current_app.logger.debug(f'Show found: {show}')
    for result in filtered_results:
        title = result['title']
        show_name, date, episode_name = extract_show_name_date_and_episode(title)
        if show_name and date and episode_name:
            # Ensure no duplicates
            existing_episode = Episode.query.filter_by(show_id=show.id, date=date, name=episode_name).first()
            if not existing_episode:
                new_episode = Episode(show_id=show.id, date=date, name=episode_name)
                db.session.add(new_episode)
                current_app.logger.debug(f'Added episode: {new_episode}')
                db.session.commit()
    
    remove_duplicate_episodes(show.id)

    filtered_results.sort(key=lambda x: extract_date_from_title(x['title']) or datetime.min, reverse=True)
    
    # Add SABnzbd API details to the results
    sabnzbd_url = AppSettings.get_setting('SABNZBD_URL')
    sabnzbd_api = AppSettings.get_setting('SABNZBD_API')
    
    return render_template('search_results.html', results=filtered_results, show_title=show_title,
                           sabnzbd_url=sabnzbd_url, sabnzbd_api=sabnzbd_api)

@bp.route('/episodes/<int:show_id>')
def episodes(show_id):
    show = Show.query.get_or_404(show_id)
    episodes = Episode.query.filter_by(show_id=show.id).order_by(Episode.date.desc()).all()
    current_app.logger.debug(f'Episodes for show {show.title}: {episodes}')
    return render_template('episodes.html', show=show, episodes=episodes)

@bp.route('/handle_download/<path:nzb_id>')
def handle_download(nzb_id):
    base_nzb_id = nzb_id.split('/')[-1].split('?')[0]
    title = request.args.get('title')

    current_app.logger.debug(f'Downloading file with title: {title}')
    
    # Extract show name, date, and episode name from title
    show_name, date, episode_name = extract_show_name_date_and_episode(title)

    if show_name and date and episode_name:
        current_app.logger.debug(f'Extracted show name: {show_name}, date: {date}, episode name: {episode_name}')

        # Save the NZB ID to the database
        show = Show.query.filter_by(title=show_name).first()
        if show:
            current_app.logger.debug(f'Show found: {show}')
            episodes = Episode.query.filter_by(show_id=show.id, date=date).all()
            for episode in episodes:
                current_app.logger.debug(f'Checking episode: {episode.name}')
                if episode_name.lower() in episode.name.lower():  # Ensure case insensitivity
                    episode.nzb_id = base_nzb_id
                    db.session.commit()
                    current_app.logger.debug(f'Saved NZB ID {base_nzb_id} for episode {episode.name}')
                    break
            else:
                current_app.logger.debug(f'No matching episode found with show name {show_name}, date {date}, and episode name {episode_name}')
        else:
            current_app.logger.debug(f'No show found with title {show_name}')
    else:
        current_app.logger.debug(f'Failed to extract show name, date, or episode name from title: {title}')

    # Use the 'get' function to download the NZB file
    BASE_URL = AppSettings.get_setting('BASE_URL')
    API_KEY = AppSettings.get_setting('API_KEY')
    download_url = f"{BASE_URL}?t=get&id={base_nzb_id}&apikey={API_KEY}"
    return redirect(download_url)

@bp.route('/search_all')
def search_all():
    shows = Show.query.all()
    for show in shows:
        search(show.title)
    return redirect(url_for('index'))

@bp.before_app_first_request
def initialize():
    try:
        shows = Show.query.all()
        if shows:
            for show in shows:
                remove_duplicate_episodes(show.id)
        else:
            current_app.logger.info("No shows found in the database.")
    except Exception as e:
        current_app.logger.error(f"Error initializing: {str(e)}")

def check_for_new_episodes():
    shows = Show.query.all()
    for show in shows:
        results = search_show(show.title)
            # Process results to check for new episodes and notify the user or add to a list
