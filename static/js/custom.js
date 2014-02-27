// Update the amount (in cents) of the investment the user is going to make.
// This happens whenever the user changes the investment amount when making a
// new investment.
function update_amount(value) {
  var value = parseFloat(value);
  if (value < 10) {
    value = 10.00;
  }

  // Round the amount to two decimal places.
  $('#amount').val(Math.round(value * 100) / 100);

}

// Update the limit values (as percentage points).
function update_lower_limit(value) {
  var value = parseInt(value);
    if (!value) {
      value = 5;
    }

    $('#lower-limit').val(value);
}

// Update the limit values (as percentage points).
function update_upper_limit(value) {
  var value = parseInt(value);
    if (!value) {
      value = 5;
    }

    $('#upper-limit').val(value);
}
