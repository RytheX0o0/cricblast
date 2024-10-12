import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, request

app = Flask(__name__)

# Function to scrape cricket data
def scrape_cricket_data():
    url = 'https://www.cricbuzz.com/live-cricket-scorecard/97212/hyd-vs-guj-elite-group-b-ranji-trophy-elite-2024-25'
    
    # Handle network errors
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError if the response was unsuccessful
    except requests.exceptions.RequestException as e:
        return {'error': f"Failed to retrieve data: {e}"}
    
    soup = BeautifulSoup(response.text, 'html.parser')

    def get_text_or_none(element, selector=None):
        if element is None:
            return "N/A"
        if selector:
            el = element.find(selector)
        else:
            el = element
        return el.text.strip() if el else "N/A"

    # First innings: Batting and Bowling
    innings_data = soup.find_all('div', class_='cb-col cb-col-100 cb-ltst-wgt-hdr')
    
    if len(innings_data) < 2:
        return {'error': 'Incomplete innings data'}
    
    first_innings_batting = innings_data[0]  # Batting
    first_innings_bowling = innings_data[1]  # Bowling

    # Second innings: Batting and Bowling (if available)
    second_innings = soup.find('div', id='innings_2')
    
    if second_innings:
        second_innings_batting = second_innings.find('div', class_='cb-col cb-col-100 cb-ltst-wgt-hdr')
        second_innings_bowling = second_innings.find_all('div', class_='cb-col cb-col-100 cb-ltst-wgt-hdr')[1]
    else:
        second_innings_batting, second_innings_bowling = None, None

    # Extract team names and scores
    first_innings_team = get_text_or_none(first_innings_batting.find('span'))
    first_innings_score = get_text_or_none(first_innings_batting.find('span', class_='pull-right'))

    second_innings_team = get_text_or_none(second_innings_batting.find('span')) if second_innings_batting else "N/A"
    second_innings_score = get_text_or_none(second_innings_batting.find('span', class_='pull-right')) if second_innings_batting else "N/A"

    # Extract player scores for first innings
    first_innings_player_scores = []
    players = first_innings_batting.find_all('div', class_='cb-col cb-col-100 cb-scrd-itms')
    for player in players:
        player_columns = player.find_all('div', class_='cb-col')
        if len(player_columns) < 7:
            continue
        first_innings_player_scores.append({
            'name': get_text_or_none(player.find('a', class_='cb-text-link')),
            'dismissal': get_text_or_none(player.find('span', class_='text-gray')),
            'runs': get_text_or_none(player_columns[2]),
            'balls': get_text_or_none(player_columns[3]),
            'fours': get_text_or_none(player_columns[4]),
            'sixes': get_text_or_none(player_columns[5]),
            'strike_rate': get_text_or_none(player_columns[6])
        })

    # Extract bowling data for first innings
    first_innings_bowling_data = []
    bowlers = first_innings_bowling.find_all('div', class_='cb-col cb-col-100 cb-scrd-itms')
    for bowler in bowlers:
        bowler_columns = bowler.find_all('div', class_='cb-col')
        if len(bowler_columns) < 8:
            continue
        first_innings_bowling_data.append({
            'name': get_text_or_none(bowler.find('a', class_='cb-text-link')),
            'overs': get_text_or_none(bowler_columns[1]),
            'maidens': get_text_or_none(bowler_columns[2]),
            'runs': get_text_or_none(bowler_columns[3]),
            'wickets': get_text_or_none(bowler_columns[4]),
            'nb': get_text_or_none(bowler_columns[5]),
            'wd': get_text_or_none(bowler_columns[6]),
            'eco': get_text_or_none(bowler_columns[7])
        })

    # Extract player scores for second innings
    second_innings_player_scores = []
    if second_innings_batting:
        second_innings_players = second_innings_batting.find_all('div', class_='cb-col cb-col-100 cb-scrd-itms')
        for player in second_innings_players:
            player_columns = player.find_all('div', class_='cb-col')
            if len(player_columns) < 7:
                continue
            second_innings_player_scores.append({
                'name': get_text_or_none(player.find('a', class_='cb-text-link')),
                'dismissal': get_text_or_none(player.find('span', class_='text-gray')),
                'runs': get_text_or_none(player_columns[2]),
                'balls': get_text_or_none(player_columns[3]),
                'fours': get_text_or_none(player_columns[4]),
                'sixes': get_text_or_none(player_columns[5]),
                'strike_rate': get_text_or_none(player_columns[6])
            })

    # Extract bowling data for second innings
    second_innings_bowling_data = []
    if second_innings_bowling:
        second_innings_bowlers = second_innings_bowling.find_all('div', class_='cb-col cb-col-100 cb-scrd-itms')
        for bowler in second_innings_bowlers:
            bowler_columns = bowler.find_all('div', class_='cb-col')
            if len(bowler_columns) < 8:
                continue
            second_innings_bowling_data.append({
                'name': get_text_or_none(bowler.find('a', class_='cb-text-link')),
                'overs': get_text_or_none(bowler_columns[1]),
                'maidens': get_text_or_none(bowler_columns[2]),
                'runs': get_text_or_none(bowler_columns[3]),
                'wickets': get_text_or_none(bowler_columns[4]),
                'nb': get_text_or_none(bowler_columns[5]),
                'wd': get_text_or_none(bowler_columns[6]),
                'eco': get_text_or_none(bowler_columns[7])
            })

    # Extract fall of wickets for both innings
    first_innings_fall_of_wickets = get_text_or_none(soup.find('div', class_='cb-col cb-col-100 cb-col-rt cb-font-13'))
    second_innings_fall_of_wickets = get_text_or_none(second_innings.find('div', class_='cb-col cb-col-100 cb-col-rt cb-font-13')) if second_innings else "N/A"

    return {
        'first_innings_team': first_innings_team,
        'first_innings_score': first_innings_score,
        'first_innings_player_scores': first_innings_player_scores,
        'first_innings_fall_of_wickets': first_innings_fall_of_wickets,
        'first_innings_bowling_data': first_innings_bowling_data,
        'second_innings_team': second_innings_team,
        'second_innings_score': second_innings_score,
        'second_innings_player_scores': second_innings_player_scores,
        'second_innings_fall_of_wickets': second_innings_fall_of_wickets,
        'second_innings_bowling_data': second_innings_bowling_data
    }

# Flask route to display paginated scorecard pages
@app.route('/')
def home():
    # Get the current page from query parameters, default to 1
    page = int(request.args.get('page', 1))

    # Scrape the data
    data = scrape_cricket_data()

    # If there's an error during scraping, show the error message
    if 'error' in data:
        return data['error']

    # HTML template for displaying the data
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cricket Scorecard - Enhanced Visuals</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&family=Roboto+Slab:wght@400;700&display=swap');
        
        /* Background Animation */
        @keyframes bgAnimation {
            0% { background-color: #0B192C; }
            25% { background-color: #1E3E62; }
            50% { background-color: #0B192C; }
            75% { background-color: #FF6500; }
            100% { background-color: #1E3E62; }
        }

        body {
            margin: 0;
            padding: 0;
            font-family: 'Poppins', sans-serif;
            color: #dcdcdc;
            width: 90%;
            margin: auto;
            transition: all 0.5s ease;
            overflow-x: hidden;
            background-color: #0B192C;
            animation: bgAnimation 15s infinite alternate ease-in-out;
        }

        .team-score-wrapper {
            position: fixed;
            top: 0;
            left: 91px;
            width: 88%;
            background-color: #0b182b;
            height: 30px;
            z-index: 999;
            margin: auto;
            opacity: 0;
            animation: fadeInTeamScore 2s ease 1s forwards;
        }

        @keyframes fadeInTeamScore {
            0% { opacity: 0; transform: translateY(-20px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        .team-score {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            max-width: 1200px;
            padding: 25px;
            background: linear-gradient(135deg, #FF6500, #1E3E62);
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.8);
            color: #fff;
            position: sticky;
            top: 30px;
            z-index: 1000;
            overflow: hidden;
            font-family: 'Roboto Slab', serif;
            animation: fadeInScore 2s ease;
        }

        @keyframes fadeInScore {
            0% { opacity: 0; transform: translateY(-30px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        .team-name {
            font-size: 60px;
            font-weight: 700;
            letter-spacing: 3px;
            font-style: italic;
            text-transform: uppercase;
            color: #FFF;
            text-shadow: 0 4px 8px rgba(255, 101, 0, 0.7);
        }

        .score {
            font-size: 56px;
            font-weight: bold;
            font-style: italic;
            text-align: right;
            color: #FFF;
            text-shadow: 0 4px 8px rgba(30, 62, 98, 0.7);
        }

        .container {
            padding-top: 32px;
            padding-bottom: 25px;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            width: 100%;
            background-color: rgb(12, 24, 42);
            border-radius: 15px;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.6);
            position: relative;
            z-index: 1;
            animation: fadeIn 2s ease-in-out;
        }

        .player-scores, .fall-of-wickets, .bowling-scores {
            width: 100%;
            max-width: 1200px;
            margin-top: 12px;
            margin-bottom: 20px;
            background-color: rgba(30, 62, 98, 0.95);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 101, 0, 0.4);
            opacity: 0.9; /* Added opacity */
            animation: fadeInSection 2s ease-in-out; /* Smooth fade-in for sections */
        }

        @keyframes fadeInSection {
            0% { opacity: 0; transform: translateY(20px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        /* Table */
        table {
            width: 100%;
            border-collapse: collapse;
            background-color: rgba(51, 51, 51, 0.9);
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.5);
        }

        th, td {
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid #555;
            font-size: 22px;
            color: #f0f0f0;
            transition: transform 0.3s ease;
            font-family: 'Poppins', sans-serif;
            cursor: pointer;
        }

        th {
            background-color: rgba(68, 68, 68, 0.8);
            color: #ffd700;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
        }

        td:hover {
            transform: scale(1.05);
            background-color: rgba(85, 85, 85, 0.9);
            box-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
        }

        /* Subheader Styling (Same as Fall of Wickets) */
        h3 {
            color: #ffb400;
            font-size: 28px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            text-align: center;
            text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.7);
            margin-bottom: 10px;
            margin-top: -12px;
        }

        .fall-of-wickets-content {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            background-color: rgba(51, 51, 51, 0.95);
            color: #ffd700;
            font-size: 24px;
            text-align: center;
            max-width: 1200px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }

        .fall-of-wickets-content h3 {
            color: #ffb400;
            font-size: 28px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.7);
            margin-bottom: 15px;
        }

        /* Player Modal Styling */
        .modal {
            display: none;
            position: fixed;
            z-index: 1001;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            background-color: rgba(30, 62, 98, 0.95);
            border-radius: 15px;
            width: 50%;
            max-width: 600px;
            padding: 30px;
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.5);
        }

        .modal-content {
            color: #fff;
            font-size: 22px;
            text-align: center;
        }

        .modal-header {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 20px;
        }

        .modal-close {
            position: absolute;
            top: 15px;
            right: 20px;
            font-size: 24px;
            cursor: pointer;
            color: #ffd700;
        }
    </style>
    <script>
        // Modal handling
        function showPlayerDetails(playerName, dismissal, runs, balls, fours, sixes, strikeRate) {
            const modal = document.getElementById('playerModal');
            const modalContent = document.getElementById('modalContent');
            modal.style.display = 'block';
            modalContent.innerHTML = `
                <div class="modal-header">${playerName}</div>
                <div>Dismissal: ${dismissal}</div>
                <div>Runs: ${runs}</div>
                <div>Balls: ${balls}</div>
                <div>Fours: ${fours}</div>
                <div>Sixes: ${sixes}</div>
                <div>Strike Rate: ${strikeRate}</div>
            `;
        }

        function closeModal() {
            const modal = document.getElementById('playerModal');
            modal.style.display = 'none';
        }

        // Arrow key navigation
        document.addEventListener('DOMContentLoaded', function () {
            document.addEventListener('keydown', function (event) {
                let currentPage = {{ page }};
                if (event.key === 'ArrowRight') {
                    let nextPage = currentPage < 4 ? currentPage + 1 : 1;
                    window.location.href = `/?page=${nextPage}`;
                } else if (event.key === 'ArrowLeft') {
                    let previousPage = currentPage > 1 ? currentPage - 1 : 4;
                    window.location.href = `/?page=${previousPage}`;
                }
            });
        });
    </script>
</head>
<body>
    <div class="team-score-wrapper"></div> <!-- Fixed padding to fill the gap -->
    <div class="container">
        {% if page == 1 %}
        <div class="team-score">
            <div class="team-name">{{ first_innings_team.replace('Innings', '').strip() }}</div>
            <div class="score">{{ first_innings_score }}</div>
        </div>
        <div class="player-scores">
            <h3>Batting</h3>
            <table>
                <thead>
                    <tr>
                        <th>Player</th>
                        <th>Dismissal</th>
                        <th class="highlight">R</th>
                        <th>B</th>
                        <th>4s</th>
                        <th>6s</th>
                        <th>SR</th>
                    </tr>
                </thead>
                <tbody>
                    {% for player in first_innings_player_scores %}
                    <tr onclick="showPlayerDetails('{{ player.name }}', '{{ player.dismissal }}', '{{ player.runs }}', '{{ player.balls }}', '{{ player.fours }}', '{{ player.sixes }}', '{{ player.strike_rate }}')">
                        <td>{{ player.name }}</td>
                        <td>{{ player.dismissal }}</td>
                        <td class="highlight">{{ player.runs }}</td>
                        <td>{{ player.balls }}</td>
                        <td>{{ player.fours }}</td>
                        <td>{{ player.sixes }}</td>
                        <td>{{ player.strike_rate }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <div class="fall-of-wickets-content">
            <h3>Fall of Wickets</h3>
            <p>Fall of Wickets: {{ first_innings_fall_of_wickets }}</p>
        </div>
        {% elif page == 2 %}
        <div class="team-score">
            <div class="team-name">{{ first_innings_team.replace('Innings', '').strip() }}</div>
            <div class="score">{{ first_innings_score }}</div>
        </div>
        <div class="bowling-scores">
            <h3>Bowling</h3>
            <table>
                <thead>
                    <tr>
                        <th>Bowler</th>
                        <th>O</th>
                        <th>M</th>
                        <th>R</th>
                        <th>W</th>
                        <th>NB</th>
                        <th>WD</th>
                        <th>ECO</th>
                    </tr>
                </thead>
                <tbody>
                    {% for bowler in first_innings_bowling_data %}
                    <tr>
                        <td>{{ bowler.name }}</td>
                        <td>{{ bowler.overs }}</td>
                        <td>{{ bowler.maidens }}</td>
                        <td>{{ bowler.runs }}</td>
                        <td>{{ bowler.wickets }}</td>
                        <td>{{ bowler.nb }}</td>
                        <td>{{ bowler.wd }}</td>
                        <td>{{ bowler.eco }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% elif page == 3 %}
        <div class="team-score">
            <div class="team-name">{{ second_innings_team.replace('Innings', '').strip() }}</div>
            <div class="score">{{ second_innings_score }}</div>
        </div>
        <div class="player-scores">
            <h3>Batting</h3>
            <table>
                <thead>
                    <tr>
                        <th>Player</th>
                        <th>Dismissal</th>
                        <th class="highlight">R</th>
                        <th>B</th>
                        <th>4s</th>
                        <th>6s</th>
                        <th>SR</th>
                    </tr>
                </thead>
                <tbody>
                    {% for player in second_innings_player_scores %}
                    <tr onclick="showPlayerDetails('{{ player.name }}', '{{ player.dismissal }}', '{{ player.runs }}', '{{ player.balls }}', '{{ player.fours }}', '{{ player.sixes }}', '{{ player.strike_rate }}')">
                        <td>{{ player.name }}</td>
                        <td>{{ player.dismissal }}</td>
                        <td class="highlight">{{ player.runs }}</td>
                        <td>{{ player.balls }}</td>
                        <td>{{ player.fours }}</td>
                        <td>{{ player.sixes }}</td>
                        <td>{{ player.strike_rate }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <div class="fall-of-wickets-content">
            <h3>Fall of Wickets</h3>
            <p>Fall of Wickets: {{ second_innings_fall_of_wickets }}</p>
        </div>
        {% elif page == 4 %}
        <div class="team-score">
            <div class="team-name">{{ second_innings_team.replace('Innings', '').strip() }}</div>
            <div class="score">{{ second_innings_score }}</div>
        </div>
        <div class="bowling-scores">
            <h3>Bowling</h3>
            <table>
                <thead>
                    <tr>
                        <th>Bowler</th>
                        <th>O</th>
                        <th>M</th>
                        <th>R</th>
                        <th>W</th>
                        <th>NB</th>
                        <th>WD</th>
                        <th>ECO</th>
                    </tr>
                </thead>
                <tbody>
                    {% for bowler in second_innings_bowling_data %}
                    <tr>
                        <td>{{ bowler.name }}</td>
                        <td>{{ bowler.overs }}</td>
                        <td>{{ bowler.maidens }}</td>
                        <td>{{ bowler.runs }}</td>
                        <td>{{ bowler.wickets }}</td>
                        <td>{{ bowler.nb }}</td>
                        <td>{{ bowler.wd }}</td>
                        <td>{{ bowler.eco }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
    </div>

    <!-- Modal for Player Details -->
    <div id="playerModal" class="modal">
        <span class="modal-close" onclick="closeModal()">&times;</span>
        <div id="modalContent" class="modal-content"></div>
    </div>
</body>
</html>
"""

    return render_template_string(
        html_template,
        page=page,
        first_innings_team=data['first_innings_team'],
        first_innings_score=data['first_innings_score'],
        first_innings_player_scores=data['first_innings_player_scores'],
        first_innings_fall_of_wickets=data['first_innings_fall_of_wickets'],
        first_innings_bowling_data=data['first_innings_bowling_data'],
        second_innings_team=data['second_innings_team'],
        second_innings_score=data['second_innings_score'],
        second_innings_player_scores=data['second_innings_player_scores'],
        second_innings_fall_of_wickets=data['second_innings_fall_of_wickets'],
        second_innings_bowling_data=data['second_innings_bowling_data']
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
