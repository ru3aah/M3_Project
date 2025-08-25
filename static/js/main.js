// 3. Filter Logic (Keywords and Checkboxes)
const keywordsList = document.querySelector('.keywords-list');

function displayFilterTags() {
    const urlParams = new URLSearchParams(window.location.search);
    const categories = urlParams.get('categories');
    
    if (categories && keywordsList) {
        const categoryArray = categories.split(',');
        
        // Clear existing tags
        keywordsList.innerHTML = '';
        
        categoryArray.forEach(category => {
            const tag = document.createElement('span');
            tag.className = 'filter-tag';
            tag.innerHTML = `
                ${category}
                <button type="button" class="remove-tag" data-category="${category}">×</button>
            `;
            keywordsList.appendChild(tag);
        });
        
        // Add event listeners to remove buttons
        document.querySelectorAll('.remove-tag').forEach(button => {
            button.addEventListener('click', function() {
                removeFilter(this.getAttribute('data-category'));
            });
        });
    } else if (keywordsList) {
        // Clear tags if no categories in URL
        keywordsList.innerHTML = '';
    }
}

// Function to remove a specific filter
function removeFilter(categoryToRemove) {
    const urlParams = new URLSearchParams(window.location.search);
    const categories = urlParams.get('categories');
    
    if (categories) {
        const categoryArray = categories.split(',');
        const filteredCategories = categoryArray.filter(cat => cat !== categoryToRemove);
        
        // Update URL parameters
        if (filteredCategories.length > 0) {
            urlParams.set('categories', filteredCategories.join(','));
        } else {
            urlParams.delete('categories');
        }
        
        // Reset to the first page when removing filters
        urlParams.delete('page');
        
        const newUrl = `${window.location.pathname}?${urlParams.toString()}`;
        window.location.href = newUrl;
    }
}

// Function to restore checkbox states from URL parameters
function restoreCheckboxStates() {
    const urlParams = new URLSearchParams(window.location.search);
    const categories = urlParams.get('categories');
    
    // First, uncheck all checkboxes
    document.querySelectorAll('.checkbox-group input[type="checkbox"]').forEach(checkbox => {
        checkbox.checked = false;
    });
    
    // Then check the ones that should be checked based on URL
    if (categories) {
        const categoryArray = categories.split(',');
        
        categoryArray.forEach(category => {
            const checkbox = document.querySelector(`input[type="checkbox"][data-keyword="${category}"]`);
            if (checkbox) {
                checkbox.checked = true;
            }
        });
    }
}

// Function to restore search input value from URL
function restoreSearchInput() {
    const urlParams = new URLSearchParams(window.location.search);
    const searchQuery = urlParams.get('q');
    const searchInput = document.querySelector('.search-input');
    
    if (searchQuery && searchInput) {
        searchInput.value = searchQuery;
    }
}

// Function to restore active sort button from URL
function restoreSortState() {
    const urlParams = new URLSearchParams(window.location.search);
    const sort = urlParams.get('sort') || 'new';
    
    // Remove active class from all sort buttons
    document.querySelectorAll('.sort-button').forEach(button => {
        button.classList.remove('active-sort');
    });
    
    // Map URL sort values to button text
    let targetButtonText = 'New'; // Default
    switch(sort) {
        case 'new':
            targetButtonText = 'New';
            break;
        case 'price_asc':
            targetButtonText = 'Price ascending';
            break;
        case 'price_desc':
            targetButtonText = 'Price descending';
            break;
        case 'rating':
            targetButtonText = 'Rating';
            break;
    }
    
    // Find and activate the corresponding button
    document.querySelectorAll('.sort-button').forEach(button => {
        if (button.textContent.trim() === targetButtonText) {
            button.classList.add('active-sort');
        }
    });
}

// Function to remove all filters
function removeAllFilters() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Remove categories parameter
    urlParams.delete('categories');
    
    // Reset to first page when removing all filters
    urlParams.delete('page');
    
    const newUrl = `${window.location.pathname}?${urlParams.toString()}`;
    window.location.href = newUrl;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    displayFilterTags();
    restoreCheckboxStates();
    restoreSearchInput();
    restoreSortState();
    // Removed addCheckboxListeners() - checkboxes no longer auto-apply filters
});

// Search functionality
const searchInput = document.querySelector('.search-input');
const searchButton = document.querySelector('.search-button');

if (searchButton && searchInput) {
    // Handle search button click
    searchButton.addEventListener('click', function(e) {
        e.preventDefault();
        performSearch();
    });
    
    // Handle Enter key in search input
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            performSearch();
        }
    });
}

function performSearch() {
    const searchQuery = searchInput.value.trim();
    const urlParams = new URLSearchParams(window.location.search);
    
    // Update or remove search parameter
    if (searchQuery) {
        urlParams.set('q', searchQuery);
    } else {
        urlParams.delete('q');
    }
    
    // Reset to the first page when searching
    urlParams.delete('page');
    
    const newUrl = `${window.location.pathname}?${urlParams.toString()}`;
    window.location.href = newUrl;
}

// Sort button functionality
document.querySelectorAll('.sort-button').forEach(button => {
    button.addEventListener('click', function() {
        // Remove the active class from all buttons
        document.querySelectorAll('.sort-button').forEach(btn => {
            btn.classList.remove('active-sort');
        });
        
        // Add the active class to clicked button
        this.classList.add('active-sort');
        
        // Get current URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const sortText = this.textContent.trim();
        
        // Map display text to Django view keys
        let sort = 'new';
        switch(sortText) {
            case 'New':
                sort = 'new';
                break;
            case 'Price ascending':
                sort = 'price_asc';
                break;
            case 'Price descending':
                sort = 'price_desc';
                break;
            case 'Rating':
                sort = 'rating';
                break;
            default:
                sort = 'new';
        }
        
        urlParams.set('sort', sort);
        
        // Reset to the first page when sorting
        urlParams.delete('page');
        
        const newUrl = `${window.location.pathname}?${urlParams.toString()}`;
        window.location.href = newUrl;
    });
});

// Filter button functionality - now the main way to apply filters
const filterButton = document.querySelector('#filter-button');
if (filterButton) {
    filterButton.addEventListener('click', function(e){
        e.preventDefault();
        
        // Get current URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const q = urlParams.get('q') || '';
        
        // Get sort value - map display text to Django view keys
        const activeSort = document.querySelector('.sort-options .sort-button.active-sort');
        let sort = 'new'; // Default to lowercase 'new'
        
        if (activeSort) {
            const sortText = activeSort.textContent.trim();
            
            // Map display text to lowercase keys for Django
            switch(sortText) {
                case 'New':
                    sort = 'new';  // lowercase
                    break;
                case 'Price ascending':
                    sort = 'price_asc';
                    break;
                case 'Price descending':
                    sort = 'price_desc';
                    break;
                case 'Rating':
                    sort = 'rating';
                    break;
                default:
                    sort = 'new';
            }
        }
        
        // Collect selected filters from checkboxes
        const selectedFilters = [];
        const checkedBoxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]:checked');
        
        checkedBoxes.forEach(checkbox => {
            const filterValue = checkbox.getAttribute('data-keyword');
            if (filterValue) {
                selectedFilters.push(filterValue);
            }
        });
        
        const searchParams = new URLSearchParams();
        
        if (q) searchParams.append('q', q);
        searchParams.append('sort', sort);
        
        if (selectedFilters.length > 0) {
            searchParams.append('categories', selectedFilters.join(','));
        }
        
        // Reset to the first page when applying filters
        searchParams.delete('page');
        
        const newUrl = `${window.location.pathname}?${searchParams.toString()}`;
        window.location.href = newUrl;
    });
}

// Remove filters button functionality
const removeFiltersButton = document.querySelector('#remove-filters-button');
if (removeFiltersButton) {
    removeFiltersButton.addEventListener('click', function(e) {
        e.preventDefault();
        removeAllFilters();
    });
}