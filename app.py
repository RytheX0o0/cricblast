from flask import Flask, Response, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/score')
def score():
    # URL for live cricket scorecard (replace with actual URL or pass via query parameter)
    url = request.args.get('url', 'https://www.cricbuzz.com/live-cricket-scorecard/94586/indw-vs-pakw-7th-match-group-a-icc-womens-t20-world-cup-2024')

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract team name
        team_name_tag = soup.find('div', class_='cb-col cb-col-100 cb-scrd-hdr-rw')
        if team_name_tag:
            # Remove "Innings" and clean team name
            team_name = team_name_tag.text.strip().replace("Innings", "").strip()
            
            # Extract current score
            current_score_tag = team_name_tag.find_next('div', class_='cb-col cb-col-8 text-right text-bold')
            if current_score_tag:
                # Remove the "R" at the end of the score if it's there
                current_score = current_score_tag.text.strip().replace('R', '').strip()
            else:
                return "Error: Could not fetch score"
        else:
            return "Error: Could not fetch team name"

        # Combine team name and score to display
        total_score = f"{team_name}: {current_score}"

        # Creating HTML response for batters and bowlers
        score_data = f'''
        <style>
            table {{ width: 80%; margin: auto; border-collapse: collapse; color: black; }}
            th, td {{ padding: 10px; text-align: center; border: 1px solid white; }}
            th {{ background-color: #ff6600; }}
            .total-score {{ font-size: 30px; font-weight: bold; text-align: center; margin-bottom: 20px; }}
        </style>
        <div class="total-score">{total_score}</div>
        <table>
            <tr><th>Batter</th><th>Dismissal</th><th>Runs</th><th>Balls</th><th>4s</th><th>6s</th><th>Strike Rate</th></tr>
        '''

        # Parse batter data
        batters_table = soup.find_all('div', class_='cb-col cb-col-100 cb-ltst-wgt-hdr')[0]  # Adjust the index if necessary
        players = batters_table.find_all('div', class_='cb-col cb-col-100 cb-scrd-itms')
        for player in players:
            batter_name_tag = player.find('a', class_='cb-text-link')
            dismissal_tag = player.find('span', class_='text-gray')

            if batter_name_tag:
                batter_name = batter_name_tag.text.strip()
                dismissal_info = dismissal_tag.text.strip() if dismissal_tag else 'Not Out'
                details = player.find_all('div', class_='cb-col')

                if len(details) >= 5:
                    runs = details[2].text.strip() if details[2] else 'N/A'
                    balls = details[3].text.strip() if details[3] else 'N/A'
                    fours = details[4].text.strip() if details[4] else 'N/A'
                    sixes = details[5].text.strip() if details[5] else 'N/A'
                    strike_rate = details[6].text.strip() if details[6] else 'N/A'
                    score_data += f'<tr><td>{batter_name}</td><td>{dismissal_info}</td><td>{runs}</td><td>{balls}</td><td>{fours}</td><td>{sixes}</td><td>{strike_rate}</td></tr>'

        score_data += '</table>'

        # Parse and display Fall of Wickets
        fall_of_wickets_section = soup.find('div', text='Fall of Wickets')
        if fall_of_wickets_section:
            fall_of_wickets_data = fall_of_wickets_section.find_next('div').text.strip()
            score_data += f'''
            <h3 style="text-align:center;">Fall of Wickets</h3>
            <p style="text-align:center;">{fall_of_wickets_data.replace(",", ", ")}</p>
            '''

        # Creating HTML for bowlers
        bowlers_table = soup.find_all('div', class_='cb-col cb-col-100 cb-ltst-wgt-hdr')[1]  # Adjust the index if necessary
        score_data += '''
        <h3 style="text-align:center;">Bowlers</h3>
        <table>
            <tr><th>Bowler</th><th>Overs</th><th>Maidens</th><th>Runs</th><th>Wickets</th><th>No Balls</th><th>Wides</th><th>Economy</th></tr>
        '''

        bowlers = bowlers_table.find_all('div', class_='cb-col cb-col-100 cb-scrd-itms')
        for bowler in bowlers:
            bowler_name_tag = bowler.find('a', class_='cb-text-link')

            if bowler_name_tag:
                bowler_name = bowler_name_tag.text.strip()
                details = bowler.find_all('div', class_='cb-col')

                if len(details) >= 7:
                    overs = details[1].text.strip() if details[1] else 'N/A'
                    maidens = details[2].text.strip() if details[2] else 'N/A'
                    runs_conceded = details[3].text.strip() if details[3] else 'N/A'
                    wickets = details[4].text.strip() if details[4] else 'N/A'
                    no_balls = details[5].text.strip() if details[5] else 'N/A'
                    wides = details[6].text.strip() if details[6] else 'N/A'
                    economy = details[7].text.strip() if details[7] else 'N/A'
                    score_data += f'<tr><td>{bowler_name}</td><td>{overs}</td><td>{maidens}</td><td>{runs_conceded}</td><td>{wickets}</td><td>{no_balls}</td><td>{wides}</td><td>{economy}</td></tr>'

        score_data += '</table>'

        return Response(score_data, mimetype='text/html')

    except requests.exceptions.RequestException as e:
        return f"Error fetching scorecard: {e}"

if __name__ == '__main__':
    app.run(debug=True)
