(function () {
    const txtSearch = document.getElementById('search');
    const btnSearch = document.getElementById('btnSearch');
    const divResults = document.getElementById('divResults');
    const divMessage = document.getElementById('divMessage');
    const divLoading = document.getElementById('divLoading')
    const maxResults = 25
    let startIndex = 0


    // GET request to Google Books API
    const getBookSearchResults = (formData) => {
        const endpoint = 'https://www.googleapis.com/books/v1/volumes'
        // GET request to google books api to get book information
        startIndex += maxResults
        console.log(startIndex)
        return $.ajax({
            type:'get',
            url: endpoint + '?q=' + formData + '&Type=books' + '&startIndex='+ startIndex + '&maxResults=' + maxResults,
            dataType: 'json',
            contentType: "application/json"
        });
    };


    // Retrieve JSON data from api response allowing for a default value if key doesn't exist
    const get_obj = (object, key, default_val) => {
        let result = object[key];
        return (typeof result !== "undefined") ? result : default_val;
    };


    // Inject API query results into page.
    const loadBooks = resp => {
        
        if (resp.totalItems > 0) {
            for (item of resp.items) {
                let id = get_obj(item, 'id', '');
                let title = get_obj(item.volumeInfo, 'title', '');
                let authors = get_obj(item.volumeInfo, 'authors', []).join(', ');
                let thumbnail = get_obj(item.volumeInfo.imageLinks, 'thumbnail', '');
                let description = get_obj(item.volumeInfo, 'description', '').slice(0, 300) + '...'
                let htmlString = 
                    `<div class="row">` +
                        `<div class="col m10 offset-m1">` +
                            `<div class="card">` +
                                `<div class="card-content">` +
                                    `<div class="row">` +
                                        `<div class="col m2">` +
                                            `<a href="/books/` + id +`"><img class="cover-img" src=` + thumbnail + `></a>` +
                                        `</div>` +
                                        `<div class="col m10">` +
                                            `<h4><a class="title-link" href="/books/` + id +`">` + title + `</a></h4>` +
                                            `<span class="author">` + authors + `</span><br>` +
                                            `<span class="description">` + description + `</span>`+         
                                        `</div> 
                                    </div>                    
                                </div>
                            </div>
                        </div>
                    </div>`                           
                divResults.innerHTML += htmlString;
            };
        }else{
            divMessage.innerHTML = 'No Results Found';
        };        
    };
    

    // Query google books API on search
    btnSearch.addEventListener('click', e => {
        startIndex = 0

        const formData = txtSearch.value;
        divResults.innerHTML = ''
        divMessage.innerHTML = ''
        divLoading.innerHTML = ''
        if (formData) {
            divLoading.innerHTML=
            `<div class="progress">
                <div class="indeterminate"></div>
            </div>`;
            getBookSearchResults(formData).then( resp => {
                loadBooks(resp)
                divLoading.innerHTML='';
            });   
        };
    });


    // Pagination on scroll.
    $( window ).scroll( () => {
        let bottom = document.body.scrollHeight - window.innerHeight;
        // Use this if you end up doing a get request to the server and then read the url
        //const queryString = window.location.search;
        //const urlParams = new URLSearchParams(queryString);
        const formData = txtSearch.value;
        divMessage.innerHTML = ''       
        if (document.body.scrollTop == bottom || document.documentElement.scrollTop == bottom) {
            getBookSearchResults(formData).then( resp => {
                loadBooks(resp)
                divLoading.innerHTML='';
            });  
        };
    });
}());