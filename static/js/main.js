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
    // Existing initialization code...
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
// Add these styles to your main.css for the new components
// (Continue with existing main.js code and add the following cart functionality)

// ========================================
// CART FUNCTIONALITY
// ========================================

// Product Detail Page Cart Functionality
function initProductDetailCart() {
    const addToCartBtn = document.getElementById('add-to-cart-btn');
    const quantityCounter = document.getElementById('quantity-counter');
    const quantityInput = document.getElementById('quantity-input');
    const productData = document.getElementById('product-data');
    
    if (!addToCartBtn || !quantityCounter || !quantityInput || !productData) {
        console.log('Missing elements:', { addToCartBtn, quantityCounter, quantityInput, productData });
        return;
    }
    
    const decreaseBtn = quantityCounter.querySelector('[data-action="decrease"]');
    const increaseBtn = quantityCounter.querySelector('[data-action="increase"]');
    
    // Get product data from template - this is the actual cart quantity from Django
    const rawQuantity = productData.dataset.productCartQuantity;
    let currentQuantity = parseInt(rawQuantity) || 0;
    
    console.log('Initial currentQuantity from Django:', currentQuantity);
    
    const productId = productData.dataset.productId;
    const productStock = parseInt(productData.dataset.productStock || 0);
    const addToCartUrl = productData.dataset.addToCartUrl;
    const updateCartUrl = productData.dataset.updateCartUrl;
    const removeCartUrl = productData.dataset.removeCartUrl;
    
    // Initialize the input value with the actual cart quantity
    // This ensures the input shows the correct quantity on page load
    if (currentQuantity > 0) {
        quantityInput.value = currentQuantity;
    } else {
        quantityInput.value = 1; // Default for new additions
    }
    
    // Force initial UI state
    updateProductUI();
    
    // Rest of your existing code stays the same...
    
    // Add to cart / Update cart button click
    addToCartBtn.addEventListener('click', function() {
        const inputValue = parseInt(quantityInput.value) || 0;
        
        console.log('Button clicked - currentQuantity:', currentQuantity, 'inputValue:', inputValue);
        
        if (currentQuantity === 0) {
            // First time adding to cart
            if (inputValue > 0) {
                addToCart(productId, inputValue, addToCartUrl);
            } else {
                showCartMessage('Please enter a valid quantity', 'error');
            }
        } else {
            // Updating existing cart item
            if (inputValue === 0) {
                // User wants to remove the item
                removeFromCart(productId, removeCartUrl);
            } else if (inputValue !== currentQuantity) {
                // Only update if value has changed
                updateCart(productId, inputValue, updateCartUrl);
            } else {
                showCartMessage('Quantity unchanged', 'info');
                removeUpdateButtonHighlight(); // Remove highlight when no change
            }
        }
    });
    
    // Decrease button click - only change input value, don't update cart
    decreaseBtn?.addEventListener('click', function() {
        const currentInputValue = parseInt(quantityInput.value) || 0;
        
        if (currentInputValue > 1) {
            quantityInput.value = currentInputValue - 1;
        } else if (currentInputValue === 1) {
            quantityInput.value = 0; // Allow setting to 0 for removal
        }
        
        // Check if highlight should be shown/removed
        updateHighlightState();
    });
    
    // Increase button click - only change input value, don't update cart
    increaseBtn?.addEventListener('click', function() {
        const currentInputValue = parseInt(quantityInput.value) || 0;
        
        if (currentInputValue < productStock) {
            quantityInput.value = currentInputValue + 1;
            // Check if highlight should be shown/removed
            updateHighlightState();
        } else {
            showCartMessage(`Only ${productStock} items available in stock`, 'error');
        }
    });
    
    // Input field handling
    quantityInput.addEventListener('input', function() {
        let value = parseInt(this.value) || 0;
        
        if (value < 0) {
            value = 0;
            this.value = value;
        }
        if (value > productStock) {
            value = productStock;
            this.value = value;
            showCartMessage(`Only ${productStock} items available in stock`, 'error');
        }
        
        // Check if highlight should be shown/removed
        updateHighlightState();
    });
    
    // Handle Enter key in input field - this updates the cart
    quantityInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const newQuantity = parseInt(this.value) || 0;
            
            console.log('Enter pressed - currentQuantity:', currentQuantity, 'newQuantity:', newQuantity);
            
            if (newQuantity === 0) {
                if (currentQuantity > 0) {
                    removeFromCart(productId, removeCartUrl);
                }
            } else if (currentQuantity === 0) {
                addToCart(productId, newQuantity, addToCartUrl);
            } else if (newQuantity !== currentQuantity) {
                updateCart(productId, newQuantity, updateCartUrl);
            } else {
                // No change needed, just remove highlight
                removeUpdateButtonHighlight();
            }
        }
    });
    
    // Prevent invalid values on blur
    quantityInput.addEventListener('blur', function() {
        let value = parseInt(this.value) || 0;
        
        if (value < 0) {
            value = 0;
        }
        if (value > productStock) {
            value = productStock;
        }
        
        // If product is not in cart and user enters 0, set to 1 for better UX
        if (currentQuantity === 0 && value === 0) {
            value = 1;
        }
        
        this.value = value;
        
        // Update highlight state after value correction
        updateHighlightState();
    });
    
    function addToCart(productId, quantity, url) {
        if (quantity <= 0 || quantity > productStock) {
            showCartMessage('Invalid quantity', 'error');
            return;
        }
        
        console.log('Adding to cart:', productId, quantity);
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentQuantity = quantity;
                updateProductUI();
                updateCartBadge(data.cart_count);
                showCartMessage('Product added to cart', 'success');
                removeUpdateButtonHighlight();
            } else {
                showCartMessage(data.error, 'error');
                // Revert input to current quantity on error
                quantityInput.value = currentQuantity || 1;
                removeUpdateButtonHighlight();
            }
        })
        .catch(error => {
            console.error('Add to cart error:', error);
            showCartMessage('Error adding to cart', 'error');
            quantityInput.value = currentQuantity || 1;
            removeUpdateButtonHighlight();
        });
    }
    
    function updateCart(productId, quantity, url) {
        if (quantity <= 0) {
            removeFromCart(productId, removeCartUrl);
            return;
        }
        
        if (quantity > productStock) {
            showCartMessage(`Only ${productStock} items available in stock`, 'error');
            quantityInput.value = currentQuantity; // Revert to current value
            removeUpdateButtonHighlight();
            return;
        }
        
        console.log('Updating cart:', productId, 'from', currentQuantity, 'to', quantity);
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentQuantity = quantity;
                updateProductUI();
                updateCartBadge(data.cart_count);
                showCartMessage('Cart updated', 'success');
                removeUpdateButtonHighlight();
            } else {
                showCartMessage(data.error, 'error');
                // Revert input to current quantity on error
                quantityInput.value = currentQuantity;
                removeUpdateButtonHighlight();
            }
        })
        .catch(error => {
            console.error('Update cart error:', error);
            showCartMessage('Error updating cart', 'error');
            quantityInput.value = currentQuantity;
            removeUpdateButtonHighlight();
        });
    }
    
    function removeFromCart(productId, url) {
        console.log('Removing from cart:', productId);
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                product_id: productId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentQuantity = 0;
                updateProductUI();
                updateCartBadge(data.cart_count);
                showCartMessage('Product removed from cart', 'success');
                removeUpdateButtonHighlight();
            } else {
                showCartMessage(data.error, 'error');
                // Revert input to current quantity on error
                quantityInput.value = currentQuantity;
                removeUpdateButtonHighlight();
            }
        })
        .catch(error => {
            console.error('Remove from cart error:', error);
            showCartMessage('Error removing from cart', 'error');
            quantityInput.value = currentQuantity;
            removeUpdateButtonHighlight();
        });
    }
    
    function updateProductUI() {
        console.log('UpdateProductUI called with currentQuantity:', currentQuantity);
        
        if (currentQuantity > 0) {
            console.log('Product in cart - showing both counter and update button');
            // Product is in cart - show both counter and button (as "In Your Cart")
            addToCartBtn.style.display = 'flex';
            quantityCounter.style.display = 'flex';
            // DON'T override the input value here - it should keep whatever the user entered
            // Only set it if it's currently showing 0 or less
            if (parseInt(quantityInput.value) <= 0) {
                quantityInput.value = currentQuantity;
            }
            addToCartBtn.querySelector('span').textContent = 'In Your Cart';
        } else {
            console.log('Product not in cart - hiding counter, showing add button');
            // Product not in cart - show only add to cart button, hide counter
            addToCartBtn.style.display = 'flex';
            quantityCounter.style.display = 'none';
            quantityInput.value = 1; // Default value for new addition
            addToCartBtn.querySelector('span').textContent = 'Add to Cart';
        }
        
        console.log('After update - Button text:', addToCartBtn.querySelector('span').textContent);
        console.log('After update - Input value:', quantityInput.value);
        
        // Ensure highlight state is correct after UI update
        updateHighlightState();
    }
    
    // Visual feedback functions
    function updateHighlightState() {
        const inputValue = parseInt(quantityInput.value) || 0;
        
        if (currentQuantity > 0 && inputValue !== currentQuantity) {
            highlightUpdateButton();
        } else {
            removeUpdateButtonHighlight();
        }
    }
    
    function highlightUpdateButton() {
        if (currentQuantity > 0) {
            addToCartBtn.classList.add('button-highlight');
            const buttonText = addToCartBtn.querySelector('span');
            buttonText.textContent = 'Update Cart';
        }
    }
    
    function removeUpdateButtonHighlight() {
        addToCartBtn.classList.remove('button-highlight');
        if (currentQuantity > 0) {
            addToCartBtn.querySelector('span').textContent = 'In Your Cart';
        }
    }
}

// Cart Page Functionality (keeping the existing function)
function initCartPage() {
    const cartItemsList = document.getElementById('cart-items-list');
    const cartUrls = document.getElementById('cart-urls');
    
    if (!cartItemsList || !cartUrls) return;
    
    const updateCartUrl = cartUrls.dataset.updateCartUrl;
    const removeCartUrl = cartUrls.dataset.removeCartUrl;
    
    cartItemsList.addEventListener('click', function(e) {
        const target = e.target.closest('button');
        if (!target) return;
        
        const action = target.dataset.action;
        const productId = target.dataset.productId;
        const cartItem = target.closest('.cart-item');
        const quantityElement = cartItem.querySelector('.quantity-value-cart');
        const currentQuantity = parseInt(quantityElement.textContent);
        
        if (action === 'increase') {
            updateCartQuantity(productId, currentQuantity + 1, cartItem, updateCartUrl);
        } else if (action === 'decrease') {
            if (currentQuantity > 1) {
                updateCartQuantity(productId, currentQuantity - 1, cartItem, updateCartUrl);
            } else {
                removeFromCartPage(productId, cartItem, removeCartUrl);
            }
        } else if (action === 'remove') {
            removeFromCartPage(productId, cartItem, removeCartUrl);
        }
    });
    
    function updateCartQuantity(productId, quantity, cartItem, url) {
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update quantity display
                const quantityElement = cartItem.querySelector('.quantity-value-cart');
                quantityElement.textContent = quantity;
                
                // Update item total price
                const itemTotalElement = cartItem.querySelector('[data-item-total-price]');
                itemTotalElement.textContent = '$' + parseFloat(data.item_total).toFixed(2);
                
                // Update cart total
                updateCartTotal(data.cart_total, data.cart_count);
                
                showCartMessage(data.message, 'success');
            } else {
                showCartMessage(data.error, 'error');
            }
        })
        .catch(error => {
            showCartMessage('Error updating cart', 'error');
        });
    }
    
    function removeFromCartPage(productId, cartItem, url) {
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                product_id: productId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove item from DOM
                cartItem.remove();
                
                // Update cart total
                updateCartTotal(data.cart_total, data.cart_count);
                
                // Check if cart is empty
                if (data.cart_count === 0) {
                    location.reload(); // Reload to show empty cart message
                }
                
                showCartMessage(data.message, 'success');
            } else {
                showCartMessage(data.error, 'error');
            }
        })
        .catch(error => {
            showCartMessage('Error removing item', 'error');
        });
    }
    
    function updateCartTotal(total, count) {
        const totalElement = document.getElementById('cart-total-price');
        const summaryTotal = document.querySelector('.cart-summary__total p:first-child');
        
        if (totalElement) {
            totalElement.textContent = '$' + parseFloat(total).toFixed(2);
        }
        
        if (summaryTotal) {
            summaryTotal.textContent = `Total (${count} item${count !== 1 ? 's' : ''})`;
        }
    }
}

// Shared utility functions for cart
function updateCartBadge(count) {
    const cartBadge = document.querySelector('.cart-badge');
    if (cartBadge) {
        cartBadge.textContent = count;
        cartBadge.style.display = count > 0 ? 'block' : 'none';
    }
}

function showCartMessage(message, type) {
    const messagesContainer = document.getElementById('cart-messages');
    const successMessage = document.getElementById('success-message');
    const errorMessage = document.getElementById('error-message');
    
    if (!messagesContainer || !successMessage || !errorMessage) {
        // Fallback to console if message elements don't exist
        console.log(`${type}: ${message}`);
        return;
    }
    
    // Hide all messages first
    successMessage.style.display = 'none';
    errorMessage.style.display = 'none';
    
    // Show appropriate message
    const messageElement = type === 'success' ? successMessage : errorMessage;
    const messageText = messageElement.querySelector('.message-text');
    
    messageText.textContent = message;
    messageElement.style.display = 'block';
    messagesContainer.style.display = 'block';
    
    // Hide message after 3 seconds
    setTimeout(() => {
        messageElement.style.display = 'none';
        if (successMessage.style.display === 'none' && errorMessage.style.display === 'none') {
            messagesContainer.style.display = 'none';
        }
    }, 3000);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Accordion functionality for product details
function toggleAccordion(accordionId) {
    const accordion = document.getElementById(accordionId);
    if (accordion) {
        accordion.classList.toggle('active');
    }
}

// Initialize cart functionality based on current page
document.addEventListener('DOMContentLoaded', function() {
    // Initialize existing functionality
    displayFilterTags();
    restoreCheckboxStates();
    restoreSearchInput();
    restoreSortState();
    
    // Initialize cart functionality based on the current page
    if (document.getElementById('product-data')) {
        initProductDetailCart();
    } else if (document.getElementById('cart-items-list')) {
        initCartPage();
    }
});