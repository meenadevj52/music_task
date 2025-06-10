$(document).ready(function () {

    function fetchPlaylists() {
        const resultTbody = $('#result');

        fetch('http://localhost:8000/api/v1/playlists')     
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
              
                let resultHtml = '';
                data?.results?.forEach(playlist => {
                    resultHtml += `
                        <tr>
                            <td class="playlist-name" onclick="openPlaylist(${playlist.uuid})">
                                ${playlist.name}
                                <ul>
                                    ${playlist.tracks.map(trackInfo => `<li>Order: ${trackInfo.order} - ${trackInfo.track_name}</li>`).join('')}
                                </ul>    
                            </td>
                            <td><a href="#" class="edit-btn" data-id="${playlist.uuid}"><i class="bi bi-pencil-square"></i></a></td>
                            <td><a href="#" class="delete-btn" data-id="${playlist.uuid}"><i class="bi bi-trash"></i></a></td>
                        </tr>
                    `;
                });
                resultTbody.html(resultHtml);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
                resultTbody.html('<tr><td colspan="3">Error fetching data</td></tr>');
            });
    }

 
    fetchPlaylists();


    // Edit functionality for opening popup
    $(document).on('click', '.edit-btn', function () {
        var playlistId = $(this).data('id');

        $.ajax({
            url: '/api/v1/playlists/' + playlistId,
            type: 'GET',
            success: function (playlist) {
                
                $('#editPlaylistId').val(playlist.uuid);
                $('#editPlaylistNameInput').val(playlist.name);

                $.ajax({
                    url: '/api/v1/tracks',  
                    type: "GET",
                    dataType: "json",
                    success: function (tracks) {
                        var editTrackOrderList = $('#editTrackOrderList');
                        editTrackOrderList.empty();

                        // Process each trackInfo from playlist.tracks
                        playlist?.tracks?.forEach(trackInfo => {
                            var trackOrderItem = `
                            <div class="trackOrderItem">
                                <div class="form-group">
                                    <label for="editTrackSelect">Track</label>
                                    <select class="form-control editTrackSelect" name="track">
                                        ${tracks?.results?.map(track => `
                                            <option value="${track.uuid}" ${track.uuid == trackInfo.uuid ? 'selected' : ''}>${track.name}</option>
                                        `).join('')}
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="editOrderInput">Order</label>
                                    <input type="number" class="form-control editOrderInput" name="order" value="${trackInfo.order}">
                                </div>
                            </div>
                        `;
                            editTrackOrderList.append(trackOrderItem);
                        });
                        fetchPlaylists();
                    },
                    error: function (xhr, status, error) {
                        console.error("Error fetching tracks:", error);
                    }
                });

               
                $('#editPlaylistModal').modal('show');
            },
            error: function (xhr, status, error) {
                console.error('Error fetching playlist details:', error);
            }
        });
    });


 
    $(document).on('click', '.saveEditPlaylist', function () {
        var playlistId = $('#editPlaylistId').val();
        var newName = $('#editPlaylistNameInput').val();

       
        var updatedPlaylistData = {
            name: newName,
            tracks: []
        };
        $('.trackOrderItem').each(function () {
            var trackId = $(this).find('.editTrackSelect').val();
            var order = $(this).find('.editOrderInput').val();
            if (trackId && order) {
                updatedPlaylistData.tracks.push({
                    track: trackId,
                    order: order
                });
            }
        });

        
        $.ajax({
            url: '/api/v1/playlists/' + playlistId, 
            type: 'PUT',
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': getCookie('csrftoken') 
            },
            data: JSON.stringify(updatedPlaylistData),
            success: function (response) {
                $('#editPlaylistModal').modal('hide');  
                location.reload();  
                fetchPlaylists();  
            },
            error: function (xhr, status, error) {
                console.error('Error updating playlist:', error);
                
            }
        });
    });

    $(document).ready(function () {

        // Function to add track order fields dynamically
        $(document).on('click', '.addEditTrackOrderButton', function () {
            var newTrackOrderItem = `
                <div class="trackOrderItem">
                    <div class="form-group">
                        <label for="editTrackSelect">Track</label>
                        <select class="form-control editTrackSelect" name="track">
                            <!-- Options will be populated dynamically -->
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="editOrderInput">Order</label>
                        <input type="number" class="form-control editOrderInput" name="order" placeholder="Enter order number">
                    </div>
                </div>
            `;
            $('#editTrackOrderList').append(newTrackOrderItem);

            // Fetch tracks and populate the select element
            $.ajax({
                url: '/api/v1/tracks',  
                type: "GET",
                dataType: "json",
                success: function (response) {
                    var editTrackSelect = $('.editTrackSelect').last(); 
                    editTrackSelect.empty(); 
                    response?.results?.forEach(track => {
                        editTrackSelect.append(`<option value="${track.uuid}">${track.name}</option>`);
                    });
                },
                error: function (xhr, status, error) {
                    console.error("Error fetching tracks:", error);
                }
            });
        });

        // Other existing JavaScript code goes here...

    });

    // Delete functionality
    $(document).on('click', '.delete-btn', function (event) {
        event.preventDefault();
        var playlistId = $(this).data('id');
        $.ajax({
            url: '/api/v1/playlists/' + playlistId ,
            type: 'DELETE',
            headers: {
                "X-CSRFToken": getCookie('csrftoken') 
            },
            success: function (result) {
                fetchPlaylists(); 
            },
            error: function (xhr, status, error) {
                console.error('Error deleting playlist:', error);
            }
        });
    });

    function loadTracks(url = '/api/v1/tracks') {
    $.ajax({
        url: url,
        method: 'GET',
        success: function (response) {
            const trackSelect = $('#track_data');

            if (!response.previous) {
                trackSelect.empty();
            }

            response.results.forEach(function (track) {
                trackSelect.append(
                    `<option value="${track.id || track.uuid}">${track.name}</option>`
                );
            });

            if (response.next) {
                loadTracks(response.next);
            }
        },
        error: function () {
            alert("Failed to load tracks.");
        }
    });
}

$(document).ready(function () {
    loadTracks();
});


    function resetCreatePlaylistModal() {
        const modal = document.getElementById('exampleModal');

        const playlistNameInput = modal.querySelector('.playlistNameInput');
        if (playlistNameInput) {
            playlistNameInput.value = '';
        }

        const trackOrderItems = modal.querySelectorAll('.trackOrderItem');
        if (trackOrderItems.length > 0) {
            const firstItem = trackOrderItems[0];

            for (let i = 1; i < trackOrderItems.length; i++) {
                trackOrderItems[i].remove();
            }

            const select = firstItem.querySelector('.trackSelect');
            if (select) {
                select.value = '';
            }

            const orderInput = firstItem.querySelector('.orderInput');
            if (orderInput) {
                orderInput.value = '';
            }
        }
    }

    $('.playlist_save').on('click', function () {
        var playlistName = $('.playlistNameInput').val();
        var trackOrders = [];

        $('#trackOrderList .trackOrderItem').each(function () {
            var track = $(this).find('.trackSelect').val(); 
            var order = $(this).find('.orderInput').val();

            if (!track || track === 'undefined') {
                return;
            }

            trackOrders.push({
                track: track,
                order: order
            });
        });

        $.ajax({
            url: '/api/v1/playlists',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                name: playlistName,
                tracks: trackOrders
            }),
            success: function (response) {
                resetCreatePlaylistModal();
                $('#exampleModal').modal('hide');
                fetchPlaylists();
            },
            error: function (xhr) {
                console.error('Failed:', xhr.responseText);
            }
        });
    });

    $(document).on('click', '.addTrackOrderButton', function () {
        var newTrackOrderItem = `
            <div class="trackOrderItem">
                <div class="form-group">
                    <label for="trackSelect">Track</label>
                    <select class="form-control trackSelect" name="track">
                        ${$('#track_data').html()} <!-- Copy options from the existing track select -->
                    </select>
                </div>
                <div class="form-group">
                    <label for="orderInput">Order</label>
                    <input type="number" class="form-control orderInput" name="order" placeholder="Enter order number">
                </div>
            </div>
        `;
        $('#trackOrderList').append(newTrackOrderItem);
    });

});


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}