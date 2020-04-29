var updateName = false; //true when username needs to be updated
var updateStore = false; //true when storeid needs to be updated
var username;
var storeid;

//add admin cloud function
const adminForm = document.querySelector('.admin-actions');
adminForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const adminEmail = document.querySelector('#admin-email').value;
    const addAdminRole = functions.httpsCallable('addAdminRole');
    addAdminRole({email: adminEmail}).then(result => {
        console.log(result);
    })
})

// listen for auth status changes
auth.onAuthStateChanged(user => {
  if (user) {
    user.getIdTokenResult().then(idTokenResult => {
      user.admin = idTokenResult.claims.admin;

      //add username
      if (updateName) {
        user.updateProfile({
          displayName: username,
        }).then(function() {
          console.log(user.username);
        }).catch(function(error) {
          console.log(error.message);
        });
      }
      //update store ID (for storeowners)
      if (updateStore) {
        user.updateProfile({
          photoURL: storeid,
        }).then(function() {
          console.log("URL " + user.photoURL);
        }).catch(function(error) {
          console.log(error.message);
        });
      }
      setupUI(user);
  })
  } else {
    setupUI();
  }
})

// signup
const signupForm = document.querySelector('#signup-form');
signupForm.addEventListener('submit', (e) => {
  e.preventDefault();
  
  // get user info
  const email = signupForm['signup-email'].value;
  const password = signupForm['signup-password'].value;
  username = signupForm['signup-username'].value;
  storeid = signupForm['signup-storeid'].value;

  // sign up the user
  auth.createUserWithEmailAndPassword(email, password).then(cred => {
    // close the signup modal & reset form
    const modal = document.querySelector('#modal-signup');
    M.Modal.getInstance(modal).close();
    signupForm.reset();
    
    updateName = true;
    if (storeid!==null) {
      updateStore = true;
    }
    signupForm.querySelector('.error').innerHTML = '';
  }).catch(err => {
    updateName=false;
    updateStore = false;
    signupForm.querySelector('.error').innerHTML = err.message;
  });
});

// logout
const logout = document.querySelector('#logout');
logout.addEventListener('click', (e) => {
  e.preventDefault();
  auth.signOut();
});

// login
const loginForm = document.querySelector('#login-form');
loginForm.addEventListener('submit', (e) => {
  e.preventDefault();
  
  // get user info
  const email = loginForm['login-email'].value;
  const password = loginForm['login-password'].value;

  // log the user in
  auth.signInWithEmailAndPassword(email, password).then((cred) => {
    // close the signup modal & reset form
    const modal = document.querySelector('#modal-login');
    M.Modal.getInstance(modal).close();
    loginForm.reset();

    loginForm.querySelector('.error').innerHTML = '';
  }).catch(err => {
    loginForm.querySelector('.error').innerHTML = err.message;
  });
});