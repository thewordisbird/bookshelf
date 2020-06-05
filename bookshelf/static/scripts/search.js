(function () {

    const txtSearch = document.getElementById('search');
    const btnSearch = document.getElementById('btnSearch');
    const divResults = document.getElementById('divResults');
    const maxResults = 25
    let startIndex = 0
    const getBookSearchResults = (formData) => {
        const endpoint = 'https://www.googleapis.com/books/v1/volumes'
        // GET request to google books api to get book information
        let resp = $.ajax({
            type:'GET',
            url: endpoint + '?q=' + formData + '&Type=books' + '&startIndex='+ startIndex + '&maxResults=' + maxResults,
            dataType: 'json',
            contentType: "application/json"
          });
          startIndex += maxResults
          console.log(startIndex)
          return resp 
    };

    const get_obj = (object, key, default_val) => {
        let result = object[key];
        return (typeof result !== "undefined") ? result : default_val;
    }
    
    // Query google books API on search
    btnSearch.addEventListener('click', e => {
        startIndex = 0

        const formData = txtSearch.value;
        divResults.innerHTML = ''
        if (formData) {
            getBookSearchResults(formData).then( resp => {
                console.log(resp.items)
                
                //console.log(resp.items)
                for (item of resp.items) {
                    let id = get_obj(item, 'id', '')
                    let title = get_obj(item.volumeInfo, 'title', '')
                    let authors = get_obj(item.volumeInfo, 'authors', []).join(', ')
                    let thumbnail = get_obj(item.volumeInfo.imageLinks, 'thumbnail', '')
                    
                    let description = get_obj(item.volumeInfo, 'description', '').slice(0, 300) + '...'
                    
                
                    //TODO:
                    //  - Iterate over authors
                    //  - Link to book main page
                    let htmlString = 
                                    `<div class="row">` +
                                        `<div class="col m10 offset-m1">` +
                                            `<div class="col m2">` +
                                                `<a href="/book/` + id +`"><img class="cover-img" src=` + thumbnail + `></a>` +
                                            `</div>` +
                                            `<div class="col m8">` +
                                                `<h4><a class="title-link" href="/book/` + id +`">` + title + `</a></h4>` +
                                                `<span class="author">` + authors + `</span><br>` +
                                                `<span class="description">` + description + `</span>`+                                    
                                            `</div>` +
                                        `</div>` +
                                    `</div>`
                    divResults.innerHTML += htmlString;
                }
            })   
        }
    });


    $( window ).scroll( () => {
        let bottom = document.body.scrollHeight - window.innerHeight;
        const formData = txtSearch.value;
        if (document.body.scrollTop == bottom || document.documentElement.scrollTop == bottom) {
            getBookSearchResults(formData, startIndex).then( resp => {
                console.log(resp.items)
                
                //console.log(resp.items)
                for (item of resp.items) {
                    let id = get_obj(item, 'id', '')
                    let title = get_obj(item.volumeInfo, 'title', '')
                    let authors = get_obj(item.volumeInfo, 'authors', []).join(', ')
                    let thumbnail = get_obj(item.volumeInfo.imageLinks, 'thumbnail', '')
                    
                    let description = get_obj(item.volumeInfo, 'description', '').slice(0, 300) + '...'
                    
                
                    //TODO:
                    //  - Iterate over authors
                    //  - Link to book main page
                    let htmlString = 
                                    `<div class="row">` +
                                        `<div class="col m10 offset-m1">` +
                                            `<div class="col m2">` +
                                                `<a href="/book/` + id +`"><img class="cover-img" src=` + thumbnail + `></a>` +
                                            `</div>` +
                                            `<div class="col m8">` +
                                                `<h4><a class="title-link" href="/book/` + id +`">` + title + `</a></h4>` +
                                                `<span class="author">` + authors + `</span><br>` +
                                                `<span class="description">` + description + `</span>`+                                    
                                            `</div>` +
                                        `</div>` +
                                    `</div>`
                    divResults.innerHTML += htmlString;
                }
            })  

        }
    })


}());