document.addEventListener("turbolinks:load", function() {

  $('#comments-list').on('click', '.delete_button', function() {
    var $this = $(this)[0];

    var request = {
      url: $this.href,
      dataType: "script",
      method: "DELETE"
    }
    $.ajax(request).done(function() {
        $this.closest('.comment').remove()
    });
    return false
  });


  $('#new_comment').submit(function(e){
    var request = {
      url: $('#apply_button').data().path,
      dataType: "script",
      method: "POST",
      data: $('form').serialize()
    }

    if( $('#comment_body').val().length === 0 ) {
      return false;
    }

    $.ajax(request).fail(function(json_error) {
      $('#comment_body').append('<div class="error">'+ SON.parse(json_error)['error'] +'</div>')
      true
    }).done(function(json_comment) {
      $('#comment_body').val('')
      $('#comments-list').append(JSON.parse(json_comment)['html']);
      update_date($('.js-publication-time').last())
    });

    return false;
  });

  var update_date = function($date) {
    var day_ago = moment().subtract(1,'days');
    var publiction_time = moment($date.text(), "DD-MM-YYYY hh:mm");

    if (publiction_time.isAfter(day_ago)) {
      $date.text(publiction_time.fromNow());
    } else {
      $date.text(publiction_time.format('lll'));
    }
    true;
  }
});
