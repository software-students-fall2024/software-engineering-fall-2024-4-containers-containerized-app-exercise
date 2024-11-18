// Function to display messages
function showMessage(message, type = 'success') {
    const messageContainer = document.getElementById('message-container');
    messageContainer.textContent = message;
    messageContainer.classList.add(type); // success or error class
    messageContainer.style.display = 'block';
  
    // Hide the message after 4 seconds
    setTimeout(() => {
      messageContainer.style.display = 'none';
      messageContainer.classList.remove(type); // Remove the class to reset style
    }, 4000);
  }
  
  // Switch to signup form
  document.getElementById('go-to-signup').addEventListener('click', function() {
    document.getElementById('login-form-container').style.display = 'none';
    document.getElementById('signup-form-container').style.display = 'block';
    document.getElementById('message-container').style.display = 'none'; // Hide message when switching forms
  });
  
  // Switch to login form
  document.getElementById('go-to-login').addEventListener('click', function() {
    document.getElementById('signup-form-container').style.display = 'none';
    document.getElementById('login-form-container').style.display = 'block';
    document.getElementById('message-container').style.display = 'none'; // Hide message when switching forms
  });
  
  // Handle login form submission
  document.getElementById('login-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    fetch('http://localhost:3000/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        showMessage('Login successful!', 'success');
        // Redirect to another page or dashboard
      } else {
        showMessage('Invalid credentials!', 'error');
      }
    })
    .catch(error => {
      showMessage('An error occurred. Please try again later.', 'error');
      console.error('Error:', error);
    });
  });
  
  // Handle signup form submission
  document.getElementById('signup-form').addEventListener('submit', function(e) {
    e.preventDefault();
  
    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
  
    fetch('http://localhost:3000/api/signup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name, email, password })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        showMessage('Account created successfully!', 'success');
        document.getElementById('signup-form').reset();
        document.getElementById('signup-form-container').style.display = 'none';
        document.getElementById('login-form-container').style.display = 'block';
      } else {
        showMessage('Error creating account. Please try again.', 'error');
      }
    })
    .catch(error => {
      showMessage('An error occurred. Please try again later.', 'error');
      console.error('Error:', error);
    });
  });