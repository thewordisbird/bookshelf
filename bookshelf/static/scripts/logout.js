(function() {
    const btnsLogout = document.getElementsByClassName('btn-logout')

    const postToSessionLogOut = function(url) {
        // POST to session login endpoint.
        return $.ajax({
          type:'POST',
          url: url,
          contentType: 'application/x-www-form-urlencoded'
        });
      };

      // Add Event Listener to Logout Buttons
      for (let i=0; i<btnsLogout.length; i++) {
          btnsLogout[i].addEventListener('click', e=> {
            postToSessionLogOut('/sessionLogout').then(() => {
                window.location.assign('/login');
            }); 
        });
      };    
}());