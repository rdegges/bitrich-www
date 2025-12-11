// Update the limit values (as percentage points).
function update_lower_limit(value) {
  var parsed = parseInt(value, 10);
  if (!parsed || parsed < 1) {
    parsed = 1;
  }
  if (parsed > 100) {
    parsed = 100;
  }

  $('#lower-limit').val(parsed);
}

// Update the limit values (as percentage points).
function update_upper_limit(value) {
  var parsed = parseInt(value, 10);
  if (!parsed || parsed < 1) {
    parsed = 1;
  }
  if (parsed > 100) {
    parsed = 100;
  }

  $('#upper-limit').val(parsed);
}
