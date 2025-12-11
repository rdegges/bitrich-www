/**
 * BitRich Custom JavaScript
 * Modern ES6+ version
 */

'use strict';

// Utility functions
const BitRich = {
  /**
   * Clamp a value between min and max
   * @param {number} value - The value to clamp
   * @param {number} min - Minimum value
   * @param {number} max - Maximum value
   * @returns {number} - Clamped value
   */
  clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  },

  /**
   * Format currency value
   * @param {number} value - The value to format
   * @returns {string} - Formatted currency string
   */
  formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  },

  /**
   * Format percentage value
   * @param {number} value - The value to format
   * @returns {string} - Formatted percentage string
   */
  formatPercentage(value) {
    return `${value}%`;
  }
};

/**
 * Update the investment amount
 * Ensures minimum $20 investment
 * @param {string|number} value - Input value
 */
function update_amount(value) {
  const parsedValue = parseFloat(value);
  const minAmount = 20.00;
  
  // Ensure minimum amount and round to 2 decimal places
  const amount = isNaN(parsedValue) ? minAmount : Math.max(parsedValue, minAmount);
  const roundedAmount = Math.round(amount * 100) / 100;
  
  const amountInput = document.getElementById('amount');
  if (amountInput) {
    amountInput.value = roundedAmount.toFixed(2);
  }
}

/**
 * Update the lower limit value
 * @param {string|number} value - Input value
 */
function update_lower_limit(value) {
  const parsedValue = parseInt(value, 10);
  const limit = isNaN(parsedValue) || parsedValue < 1 ? 50 : BitRich.clamp(parsedValue, 1, 100);
  
  const lowerLimitInput = document.getElementById('lower-limit');
  if (lowerLimitInput) {
    lowerLimitInput.value = limit;
  }
}

/**
 * Update the upper limit value
 * @param {string|number} value - Input value
 */
function update_upper_limit(value) {
  const parsedValue = parseInt(value, 10);
  const limit = isNaN(parsedValue) || parsedValue < 1 ? 50 : BitRich.clamp(parsedValue, 1, 100);
  
  const upperLimitInput = document.getElementById('upper-limit');
  if (upperLimitInput) {
    upperLimitInput.value = limit;
  }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      
      // Skip if it's just "#" or empty
      if (href === '#' || !href) return;
      
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });

  // Auto-dismiss alerts after 5 seconds
  document.querySelectorAll('.alert:not(.alert-warning)').forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    }, 5000);
  });

  // Add loading state to forms on submit
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function() {
      const submitBtn = this.querySelector('button[type="submit"]');
      if (submitBtn && !submitBtn.disabled) {
        submitBtn.disabled = true;
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Loading...';
        
        // Re-enable after 10 seconds (failsafe)
        setTimeout(() => {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
        }, 10000);
      }
    });
  });

  // Initialize tooltips if Bootstrap is available
  if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].map(el => new bootstrap.Tooltip(el));
  }

  console.log('🪙 BitRich initialized');
});
