const table = document.getElementById('items-table');

async function loadJsonData() {
    const response = await fetch('bpData.json');
    const data = await response.json();
    
    // Now pass the data object to populateTable
    populateTable(data);
}

function populateTable(data) {
    // Get all hero names
    const heroes = Object.keys(data);
    
    // Sort heroes by total items (descending), then by name
    heroes.sort((heroA, heroB) => {
        const totalItemsA = data[heroA]?.totalItems || 0;
        const totalItemsB = data[heroB]?.totalItems || 0;
        
        // First sort by totalItems (descending)
        if (totalItemsA !== totalItemsB) {
            return totalItemsB - totalItemsA;
        }
        
        // Then by hero name
        return heroA.localeCompare(heroB);
    });

    // Create table header
    const thead = document.createElement('thead');
    thead.innerHTML = `
        <tr>
            <th>Hero</th>
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
        const heroData = data[heroName];
        const tr = document.createElement('tr');

        // Hero name cell
        const heroCell = document.createElement('td');
        heroCell.className = 'hero-cell';
        heroCell.textContent = heroName;

        // Total items cell
        const totalItemsCell = document.createElement('td');
        totalItemsCell.className = 'total-items-cell';
        totalItemsCell.textContent = heroData.totalItems || 0;

        // Skin count cell
        const skinsCell = document.createElement('td');
        skinsCell.textContent = heroData.total_Skin || 0;

        // Highlight Intros cell
        const highlightIntrosCell = document.createElement('td');
        highlightIntrosCell.textContent = heroData['total_Highlight Intro'] || 0;

        // Emotes cell
        const emotesCell = document.createElement('td');
        emotesCell.textContent = heroData.total_Emote || 0;

        // Victory Poses cell
        const victoryPosesCell = document.createElement('td');
        victoryPosesCell.textContent = heroData['total_Victory Pose'] || 0;

        // Voice Lines cell
        const voiceLinesCell = document.createElement('td');
        voiceLinesCell.textContent = heroData['total_Voice Line'] || 0;

        // Sprays cell
        const spraysCell = document.createElement('td');
        spraysCell.textContent = heroData.total_Spray || 0;

        // Icons cell (Player Icons)
        const iconsCell = document.createElement('td');
        iconsCell.textContent = heroData['total_Player Icon'] || 0;

        // Name Cards cell
        const nameCardsCell = document.createElement('td');
        nameCardsCell.textContent = heroData['total_Name Card'] || 0;
        
        // Append all cells to the row
        tr.appendChild(heroCell);
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

    // Append tbody to table
    table.appendChild(tbody);
}

document.addEventListener('DOMContentLoaded', loadJsonData);