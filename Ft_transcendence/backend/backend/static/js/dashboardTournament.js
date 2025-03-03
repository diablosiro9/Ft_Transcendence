function loopDashboard(){    
    async function tournamentLaunchGame() {
        const tournamentName = window.tournamentName;
        if (!tournamentName) {
            console.log("Tournament name is not set");
            return;
        }
        fetch(`/tournaments/${tournamentName}/launch/`)
        .then(response => response.json())
        .then(data => {
            if (data.current_game !== null && data.context === 1 && data.message === 'play_tournament') {
                stopLoop();
                // console.log("play");
                localStorage.setItem('tournament_username', data.player1);
                localStorage.setItem('tournament_opponentname', data.player2);
                loadPagePlayTournament(data.redirectUrl, data.game_id);
            }
            else if(data.current_game !== null && data.message === 'tournament_in_progress' ) {
                stopLoop();
                // console.log("progress");
                loadPageTournament('tournament_in_progress', tournamentName);
            }
            else if (data.redirected) { // This else if might not be necessary if data.redirected is not being set
                // console.log("elseif: ", data.redirected);
                const path = new URL(data.url).pathname.replace('/tournaments/', '');
                stopLoop();
                loadPageTournament(path);
            }
            else if(data.message === 'forced-finish'){
                stopLoop();
                // console.log("DEBUG FORCE FINISHED********")
                loadPageUsers('home');
            }
            else if(data.message === 'finished'){
                // stopLoop();
                fetchTournamentDetails();
            }
        })
        .catch(error => console.error('Error Lauch:', error));
    }
    launch_interval = setInterval(fetchTournamentDetails, 3000);

    async function fetchTournamentDetails() {
        const tournamentName = window.tournamentName;
        if (!tournamentName) {
            // console.log("Tournament name is not set");
            return;
        }
        fetch(`/tournaments/${tournamentName}/get/`)
            .then(response => response.json())
            .then(data => {
                renderName(data.name);
                renderLevel(data.level);
                renderNbPlayers(data.nb_players);
                renderPlayersRanking(data.players);
                renderGames(data.games);
            })
            .catch(error => console.error('Failed to fetch tournament details', error));
    }
    get_interval = setInterval(tournamentLaunchGame, 3000);

    function stopLoop() {
        // console.log("out");
        if (get_interval && launch_interval) {
            clearInterval(get_interval);
            clearInterval(launch_interval);
        }
    }
}
function renderName(name) {
    const nameContainer = document.getElementById('tournament-name')
    if(nameContainer){
        nameContainer.innerHTML = `
        <h1>Tournament: ${name}</h1>
    `;
    }
}

function renderLevel(level) {
    const levelContainer = document.getElementById('tournament-level');
    if(levelContainer){
        levelContainer.innerHTML = `  
            <div class="dashboard-data-level">
                <i class="fas fa-ranking-star"></i>
                <h4>Level: ${level}</h4>
            </div>
        `;
    }
}

function renderNbPlayers(nbPlayers) {
    const nbPlayersContainer = document.getElementById('tournament-nb-players');
    if(nbPlayersContainer){
        nbPlayersContainer.innerHTML = `
            <div class="dashboard-data-players">
                <i class="fas fa-user-friends"></i>
                <h4>Number of players: ${nbPlayers}</h4>
            </div>
        `;
    }
}


function renderPlayersRanking(players) {
    const playersListContainer = document.getElementById('tournament-ranking');
    if (playersListContainer){
        let playersListHTML = '<div class="dashboard-ranking"><h2>Players Ranking</h2><div class="players-container">';

        players.forEach((player, index) => {
            playersListHTML += `
                <div class="player-item">
                    <h6 class="rank">${player.rank}</h6>
                    <img src="${player.image}" alt="${player.username}">
                    <p>${player.username} aka ${player.alias}</p>
                </div>
            `;
            if (index === players.length - 1 && players.length % 2 !== 0) {
                playersListHTML += '<div class="player-item"></div>'; // Add an empty item to force the last player into a single column
            }
        });

        playersListHTML += '</div></div>';
        playersListContainer.innerHTML = playersListHTML;
    }
}



function renderGames(games) {
    const gamesListContainer = document.getElementById('tournament-games');
    if(gamesListContainer){
        if (games.length == 0) {
            gamesListContainer.innerHTML = `
                <div>
                    <h2>Upcoming Games</h2>
                    <p>Tournament finished, no more games to play !</p>
                </div>
            `;
            return;
        } else {
            gamesListContainer.innerHTML = `
                <div>
                    <h2>Upcoming Games</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Level</th>
                                <th>Player 1</th>
                                <th>Player 2</th>
                                <th>State</th>
                                <th>Score</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${games.map(game => `
                                <tr>
                                    <td>${game.level}</td>
                                    <td>${game.player1}</td>
                                    <td>${game.player2}</td>
                                    <td>${game.state}</td>
                                    <td>${game.score}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }
    }
}
 
function initTournamentPage() {
    const tournamentElement = document.getElementById('tournament-name');
    if (!tournamentElement) {
        return;
    }

    window.tournamentName = tournamentElement.dataset.tournamentName;
    if (!window.tournamentName) {
        if (localStorage.getItem('tournament_name_refresh')){
            window.tournamentName = localStorage.getItem('tournament_name_refresh');
            loopDashboard();
            }
        else 
            return;
    }
    else
        loopDashboard();
    
}

