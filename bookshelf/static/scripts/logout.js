(function() {
    const btnLogout = document.getElementById('btnLogOut')

    const postToSessionLogOut = function(url) {
        // POST to session login endpoint.
        return $.ajax({
          type:'POST',
          url: url,
          contentType: 'application/x-www-form-urlencoded'
        });
      };

      // Add Logout Event
      btnLogout.addEventListener('click', e => {
        postToSessionLogOut('/sessionLogout').then(() => {
                window.location.assign('/login');
        });
      });
}());