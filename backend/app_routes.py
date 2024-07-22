import re
from datetime import datetime
import requests
from flask import Blueprint, request, flash, redirect, url_for, render_template, current_app
from models import db, Show, Episode, AppSettings

bp = Blueprint('app_routes', __name__)

def search_show(title):
    BASE_URL = AppSettings.get_setting('BASE_URL')
    API_KEY = AppSettings.get_setting('API_KEY')
    url = f"{BASE_URL}?t=search&q={title}&apikey={API_KEY}&o=json"
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
        db.session.delete(show)
        db.session.commit()
        flash('Show deleted successfully!', 'success')
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
    return render_template('search_results.html', results=filtered_results, show_title=show_title)

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
    shows = Show.query.all()
    for show in shows:
        remove_duplicate_episodes(show.id)

def check_for_new_episodes():
    shows = Show.query.all()
    for show in shows:
        results = search_show(show.title)
            # Process results to check for new episodes and notify the user or add to a list
