const table = document.getElementById('items-table');
let allHeroesData = {}; // Store all hero data globally
let currentHeroes = []; // Store filtered/sorted heroes

async function loadJsonData() {
    const response = await fetch('bpData.json');
    allHeroesData = await response.json();
    
    // Initialize filters
    initializeFilters();
    
    // Populate table with all data initially
    applyFilters();
}

function initializeFilters() {
    // Add event listeners to all filter inputs
    document.getElementById('role-filter').addEventListener('change', applyFilters);
    document.getElementById('hero-search').addEventListener('input', applyFilters);
    document.getElementById('sort-by').addEventListener('change', applyFilters);
    document.getElementById('reset-filters').addEventListener('click', resetFilters);
}

function resetFilters() {
    document.getElementById('role-filter').value = 'all';
    document.getElementById('hero-search').value = '';
    document.getElementById('sort-by').value = 'totalItems-desc';
    applyFilters();
}

function applyFilters() {
    // Get filter values
    const roleFilter = document.getElementById('role-filter').value;
    const heroSearch = document.getElementById('hero-search').value.toLowerCase();
    const sortBy = document.getElementById('sort-by').value;

    // Get all hero names
    let heroes = Object.keys(allHeroesData);

    // Apply filters
    heroes = heroes.filter(heroName => {
        const heroData = allHeroesData[heroName];
        
        // Role filter
        if (roleFilter !== 'all' && heroData.role !== roleFilter) {
            return false;
        }
        
        // Hero name search filter
        if (heroSearch && !heroName.toLowerCase().includes(heroSearch)) {
            return false;
        }
        
        return true;
    });

    // Sort heroes
    heroes.sort((heroA, heroB) => {
        const dataA = allHeroesData[heroA];
        const dataB = allHeroesData[heroB];
        
        const [sortField, sortDirection] = sortBy.split('-');
        
        let comparison = 0;
        
        switch(sortField) {
            case 'totalItems':
                comparison = (dataA.totalItems || 0) - (dataB.totalItems || 0);
                break;
            case 'name':
                comparison = heroA.localeCompare(heroB);
                break;
            case 'skins':
                comparison = (dataA["total_Skin"] || 0) - (dataB["total_Skin"] || 0);
                break;
            default:
                comparison = (dataA.totalItems || 0) - (dataB.totalItems || 0);
        }
        
        // Reverse if descending
        if (sortDirection === 'desc') {
            comparison = -comparison;
        }
        
        return comparison;
    });

    // Store current heroes
    currentHeroes = heroes;
    
    // Clear and repopulate table
    clearTable();
    populateTable(heroes);
}

function clearTable() {
    // Remove existing table content
    while (table.firstChild) {
        table.removeChild(table.firstChild);
    }
}

function populateTable(heroes) {
    // Create table header
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

    // Create table body
    const tbody = document.createElement('tbody');
    
    // Add a row for each hero
    heroes.forEach(heroName => {
        const heroData = allHeroesData[heroName];
        const tr = document.createElement('tr');

        // Hero name cell
        const heroCell = document.createElement('td');
        heroCell.className = 'hero-cell';
        heroCell.textContent = heroName;

        // Role cell
        const roleCell = document.createElement('td');
        roleCell.textContent = heroData.role || 'N/A';
        roleCell.className = `role-${heroData.role?.toLowerCase() || 'unknown'}`;

        // Total items cell
        const totalItemsCell = document.createElement('td');
        totalItemsCell.className = 'total-items-cell';
        totalItemsCell.textContent = heroData.totalItems || 0;

        // Skin count cell
        const skinsCell = document.createElement('td');
        skinsCell.textContent = heroData["total_Skin"] || 0;

        // Highlight Intros cell
        const highlightIntrosCell = document.createElement('td');
        highlightIntrosCell.textContent = heroData["total_Highlight Intro"] || 0;

        // Emotes cell
        const emotesCell = document.createElement('td');
        emotesCell.textContent = heroData["total_Emote"] || 0;

        // Victory Poses cell
        const victoryPosesCell = document.createElement('td');
        victoryPosesCell.textContent = heroData["total_Victory Pose"] || 0;

        // Voice Lines cell
        const voiceLinesCell = document.createElement('td');
        voiceLinesCell.textContent = heroData["total_Voice Line"] || 0;

        // Sprays cell
        const spraysCell = document.createElement('td');
        spraysCell.textContent = heroData["total_Spray"] || 0;

        // Icons cell (Player Icons)
        const iconsCell = document.createElement('td');
        iconsCell.textContent = heroData["total_Player Icon"] || 0;

        // Name Cards cell
        const nameCardsCell = document.createElement('td');
        nameCardsCell.textContent = heroData["total_Name Card"] || 0;

        // Append all cells to the row
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

        // Append row to tbody
        tbody.appendChild(tr);
    });

    // Show message if no results
    if (heroes.length === 0) {
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

    // Append tbody to table
    table.appendChild(tbody);
}

document.addEventListener('DOMContentLoaded', loadJsonData);