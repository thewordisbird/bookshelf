(function() {
   
    const txtEmail = document.getElementById('txtEmail');
    const txtPassWord = document.getElementById('txtPassword');
    const txtNext = document.getElementById('txtNext')
    const btnLogin = document.getElementById('btnLogin');
    const csrfToken = document.getElementById('csrf_token');
    const btnLogOut = document.getElementById('btnLogOut')
    const btnGoogle = document.getElementById('btnGoogle')
    const btnFacebook = document.getElementById('btnFacebook')
    const divLoginMessage = document.getElementById('loginMessage')
    const divProviderMessage = document.getElementById('providerMessage')

    const googleAuthProvider = new firebase.auth.GoogleAuthProvider();
    // Prompt to select account on google login
    googleAuthProvider.setCustomParameters({
        prompt: 'select_account'
    });

    const facebookAuthProvider = new firebase.auth.FacebookAuthProvider();
    // Prompt to select account on facebook login
    facebookAuthProvider.setCustomParameters({
        display: 'select_account'
    });

    const postIdTokenToSessionLogin = (url, idToken, csrfToken, uid) => {
        // POST to session login endpoint.
        return $.ajax({
          type:'POST',
          headers: {
            'X-CSRFToken': csrfToken
          },
          url: url,
          data: {idToken: idToken, uid:uid},
          dataType: 'json',
          contentType: 'application/x-www-form-urlencoded'
        });
      };

    // Add Email/Password Login Event
    btnLogin.addEventListener('click', e => {
        // Get Email and Pass
        const email = txtEmail.value;
        const pass = txtPassword.value;
        const auth = firebase.auth();

        // As httpOnly cookies are to be used, do not persist any state client side.
        auth.setPersistence(firebase.auth.Auth.Persistence.NONE);
        
        // Sign In
        auth.signInWithEmailAndPassword(email, pass).then(({ user }) => {
            // Get the user's ID token as it is needed to exchange for a session cookie.
            return user.getIdToken().then(idToken => {
                // Session login endpoint is queried and the session cookie is set.
                return postIdTokenToSessionLogin('/login', idToken, csrfToken.value, user.uid);
            });
        }).then(() => {
            // A page redirect would suffice as the persistence is set to NONE.
            return auth.signOut();
        }).then(() => {
            window.location.assign(txtNext.value);
        }).catch( error => {
            divLoginMessage.innerHTML = '<span class="error-message">' + error.message + '</span>'            
        });
    });

    // Add Oauth2 Sign In With Google Login Event
    btnGoogle.addEventListener('click', e=> {
        const auth = firebase.auth();
        const provider = new firebase.auth.GoogleAuthProvider();

        // As httpOnly cookies are to be used, do not persist any state client side.
        auth.setPersistence(firebase.auth.Auth.Persistence.NONE);

         // Sign In
         auth.signInWithPopup(googleAuthProvider).then(({ user }) => {
            // Get the user's ID token as it is needed to exchange for a session cookie.
            return user.getIdToken().then(idToken => {
                // Session login endpoint is queried and the session cookie is set.
                return postIdTokenToSessionLogin('/login', idToken, csrfToken.value, user.uid);
            });
        }).then(() => {
            // A page redirect would suffice as the persistence is set to NONE.
            return auth.signOut();
        }).then(() => {
            window.location.assign(txtNext.value);
        }).catch( error => {
            divProviderMessage.innerHTML = '<span class="error-message">' + error.message + '</span>'            
        });
    });

    // Add Oauth2 Sign In With Facebook Login Event
    btnFacebook.addEventListener('click', e=> {
        const auth = firebase.auth();
        const provider = new firebase.auth.FacebookAuthProvider();

        // As httpOnly cookies are to be used, do not persist any state client side.
        auth.setPersistence(firebase.auth.Auth.Persistence.NONE);

         // Sign In
         auth.signInWithPopup(facebookAuthProvider).then(({ user }) => {
            // Get the user's ID token as it is needed to exchange for a session cookie.
            return user.getIdToken().then(idToken => {
                // Session login endpoint is queried and the session cookie is set.
                return postIdTokenToSessionLogin('/login', idToken, csrfToken.value, user.uid);
            });
        }).then(() => {
            // A page redirect would suffice as the persistence is set to NONE.
            return auth.signOut();
        }).then(() => {
            window.location.assign(txtNext.value);
        }).catch( error => {
            divProviderMessage.innerHTML = '<span class="error-message">' + error.message + '</span>'            
        });
    });
}());