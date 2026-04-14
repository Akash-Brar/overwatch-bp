const table = document.getElementById('items-table');
let allHeroesData = {};
let currentHeroes = [];
let allSeasons = [];

async function loadJsonData() {
    const response = await fetch('bpData.json');
    allHeroesData = await response.json();

    allSeasons = getAllSeasons(allHeroesData);
    populateSeasonFilter(allSeasons);

    initializeFilters();
    applyFilters();
}

function initializeFilters() {
    document.getElementById('role-filter').addEventListener('change', applyFilters);
    document.getElementById('hero-search').addEventListener('input', applyFilters);
    document.getElementById('season-mode').addEventListener('change', handleSeasonModeChange);
    document.getElementById('season-filter').addEventListener('change', applyFilters);
    document.getElementById('sort-by').addEventListener('change', applyFilters);
    document.getElementById('reset-filters').addEventListener('click', resetFilters);

    handleSeasonModeChange();
}

function resetFilters() {
    document.getElementById('role-filter').value = 'all';
    document.getElementById('hero-search').value = '';
    document.getElementById('season-mode').value = 'all';
    document.getElementById('season-filter').value = 'all';
    document.getElementById('sort-by').value = 'totalItems-desc';

    handleSeasonModeChange();
    applyFilters();
}

function handleSeasonModeChange() {
    const seasonMode = document.getElementById('season-mode').value;
    const seasonFilter = document.getElementById('season-filter');

    if (seasonMode === 'all') {
        seasonFilter.disabled = true;
        seasonFilter.value = 'all';
    } else {
        seasonFilter.disabled = false;
        if (seasonFilter.value === 'all' && allSeasons.length > 0) {
            seasonFilter.value = allSeasons[allSeasons.length - 1];
        }
    }

    applyFilters();
}

function getAllSeasons(data) {
    const seasonSet = new Set();

    Object.values(data).forEach(heroData => {
        Object.keys(heroData).forEach(key => {
            if (isSeasonKey(heroData[key])) {
                seasonSet.add(key);
            }
        });
    });

    return Array.from(seasonSet).sort(compareSeasonKeys);
}

function populateSeasonFilter(seasons) {
    const seasonFilter = document.getElementById('season-filter');
    seasonFilter.innerHTML = '<option value="all">All Seasons</option>';

    seasons.forEach(season => {
        const option = document.createElement('option');
        option.value = season;
        option.textContent = season;
        seasonFilter.appendChild(option);
    });
}

function isSeasonKey(value) {
    return (
        value &&
        typeof value === 'object' &&
        Array.isArray(value.free) &&
        Array.isArray(value.paid)
    );
}

function parseSeasonKey(seasonKey) {
    const yearSeasonMatch = seasonKey.match(/^(\d{4})\s+Season\s+(\d+)$/i);
    if (yearSeasonMatch) {
        return {
            group: 1,
            year: parseInt(yearSeasonMatch[1], 10),
            season: parseInt(yearSeasonMatch[2], 10)
        };
    }

    const seasonMatch = seasonKey.match(/^Season\s+(\d+)$/i);
    if (seasonMatch) {
        return {
            group: 0,
            year: 0,
            season: parseInt(seasonMatch[1], 10)
        };
    }

    return {
        group: 99,
        year: Number.MAX_SAFE_INTEGER,
        season: Number.MAX_SAFE_INTEGER
    };
}

function compareSeasonKeys(a, b) {
    const parsedA = parseSeasonKey(a);
    const parsedB = parseSeasonKey(b);

    if (parsedA.group !== parsedB.group) {
        return parsedA.group - parsedB.group;
    }

    if (parsedA.year !== parsedB.year) {
        return parsedA.year - parsedB.year;
    }

    return parsedA.season - parsedB.season;
}

function getIncludedSeasons(selectedSeason, mode) {
    if (mode === 'all' || selectedSeason === 'all') {
        return [...allSeasons];
    }

    if (mode === 'specific') {
        return [selectedSeason];
    }

    if (mode === 'upto') {
        const selectedIndex = allSeasons.indexOf(selectedSeason);
        if (selectedIndex === -1) {
            return [...allSeasons];
        }
        return allSeasons.slice(0, selectedIndex + 1);
    }

    return [...allSeasons];
}

function getFilteredHeroStats(heroData, includedSeasons) {
    const stats = {
        totalItems: 0,
        total_Skin: 0,
        total_Highlight_Intro: 0,
        total_Emote: 0,
        total_Victory_Pose: 0,
        total_Voice_Line: 0,
        total_Spray: 0,
        total_Player_Icon: 0,
        total_Name_Card: 0
    };

    includedSeasons.forEach(season => {
        const seasonData = heroData[season];
        if (!isSeasonKey(seasonData)) return;

        const items = [...seasonData.free, ...seasonData.paid];

        items.forEach(item => {
            stats.totalItems += 1;

            switch (item.type) {
                case 'Skin':
                    stats.total_Skin += 1;
                    break;
                case 'Highlight Intro':
                    stats.total_Highlight_Intro += 1;
                    break;
                case 'Emote':
                    stats.total_Emote += 1;
                    break;
                case 'Victory Pose':
                    stats.total_Victory_Pose += 1;
                    break;
                case 'Voice Line':
                    stats.total_Voice_Line += 1;
                    break;
                case 'Spray':
                    stats.total_Spray += 1;
                    break;
                case 'Player Icon':
                    stats.total_Player_Icon += 1;
                    break;
                case 'Name Card':
                    stats.total_Name_Card += 1;
                    break;
            }
        });
    });

    return stats;
}

function applyFilters() {
    const roleFilter = document.getElementById('role-filter').value;
    const heroSearch = document.getElementById('hero-search').value.toLowerCase();
    const seasonMode = document.getElementById('season-mode').value;
    const selectedSeason = document.getElementById('season-filter').value;
    const sortBy = document.getElementById('sort-by').value;

    const includedSeasons = getIncludedSeasons(selectedSeason, seasonMode);

    let heroes = Object.keys(allHeroesData);

    heroes = heroes
        .map(heroName => {
            const heroData = allHeroesData[heroName];
            const filteredStats = getFilteredHeroStats(heroData, includedSeasons);

            return {
                heroName,
                heroData,
                filteredStats
            };
        })
        .filter(({ heroName, heroData, filteredStats }) => {
            if (roleFilter !== 'all' && heroData.role !== roleFilter) {
                return false;
            }

            if (heroSearch && !heroName.toLowerCase().includes(heroSearch)) {
                return false;
            }

            if (seasonMode !== 'all' && filteredStats.totalItems === 0) {
                return false;
            }

            return true;
        });

    heroes.sort((a, b) => {
        const [sortField, sortDirection] = sortBy.split('-');
        let comparison = 0;

        switch (sortField) {
            case 'totalItems':
                comparison = a.filteredStats.totalItems - b.filteredStats.totalItems;
                break;
            case 'name':
                comparison = a.heroName.localeCompare(b.heroName);
                break;
            case 'skins':
                comparison = a.filteredStats.total_Skin - b.filteredStats.total_Skin;
                break;
            default:
                comparison = a.filteredStats.totalItems - b.filteredStats.totalItems;
        }

        if (sortDirection === 'desc') {
            comparison = -comparison;
        }

        return comparison;
    });

    currentHeroes = heroes;

    clearTable();
    populateTable(heroes);
}

function clearTable() {
    while (table.firstChild) {
        table.removeChild(table.firstChild);
    }
}

function populateTable(heroEntries) {
    const thead = document.createElement('thead');
    thead.innerHTML = `
        <tr>
            <th>Hero</th>
            <th>Role</th>
            <th>Total Items</th>
            <th>Skins</th>
            <th>Highlight Intros</th>
            <th>Emotes</th>
            <th>Victory Poses</th>
            <th>Voice Lines</th>
            <th>Sprays</th>
            <th>Icons</th>
            <th>Name Cards</th>
        </tr>
    `;
    table.appendChild(thead);

    const tbody = document.createElement('tbody');

    heroEntries.forEach(({ heroName, heroData, filteredStats }) => {
        const tr = document.createElement('tr');

        const heroCell = document.createElement('td');
        heroCell.className = 'hero-cell';
        heroCell.textContent = heroName;

        const roleCell = document.createElement('td');
        roleCell.textContent = heroData.role || 'N/A';
        roleCell.className = `role-${heroData.role?.toLowerCase() || 'unknown'}`;

        const totalItemsCell = document.createElement('td');
        totalItemsCell.className = 'total-items-cell';
        totalItemsCell.textContent = filteredStats.totalItems;

        const skinsCell = document.createElement('td');
        skinsCell.textContent = filteredStats.total_Skin;

        const highlightIntrosCell = document.createElement('td');
        highlightIntrosCell.textContent = filteredStats.total_Highlight_Intro;

        const emotesCell = document.createElement('td');
        emotesCell.textContent = filteredStats.total_Emote;

        const victoryPosesCell = document.createElement('td');
        victoryPosesCell.textContent = filteredStats.total_Victory_Pose;

        const voiceLinesCell = document.createElement('td');
        voiceLinesCell.textContent = filteredStats.total_Voice_Line;

        const spraysCell = document.createElement('td');
        spraysCell.textContent = filteredStats.total_Spray;

        const iconsCell = document.createElement('td');
        iconsCell.textContent = filteredStats.total_Player_Icon;

        const nameCardsCell = document.createElement('td');
        nameCardsCell.textContent = filteredStats.total_Name_Card;

        tr.appendChild(heroCell);
        tr.appendChild(roleCell);
        tr.appendChild(totalItemsCell);
        tr.appendChild(skinsCell);
        tr.appendChild(highlightIntrosCell);
        tr.appendChild(emotesCell);
        tr.appendChild(victoryPosesCell);
        tr.appendChild(voiceLinesCell);
        tr.appendChild(spraysCell);
        tr.appendChild(iconsCell);
        tr.appendChild(nameCardsCell);

        tbody.appendChild(tr);
    });

    if (heroEntries.length === 0) {
        const tr = document.createElement('tr');
        const td = document.createElement('td');
        td.colSpan = 11;
        td.textContent = 'No heroes match your filters.';
        td.style.textAlign = 'center';
        td.style.padding = '40px';
        td.style.color = '#666';
        tr.appendChild(td);
        tbody.appendChild(tr);
    }

    table.appendChild(tbody);
}

document.addEventListener('DOMContentLoaded', loadJsonData);