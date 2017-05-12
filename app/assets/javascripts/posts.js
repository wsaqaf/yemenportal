document.addEventListener("turbolinks:load", function() {
  var opposite_name = {upvote: 'downvote', downvote: 'upvote'};
  var button_class = {upvote: 'success', downvote: 'alert'};
  var icon_name = {upvote: 'fi-like', downvote: 'fi-dislike'};

  $('select.multiselect').selectize({
    plugins: ['remove_button', 'restore_on_backspace'],
    delimiter: ',',
    persist: false,
    create: function(input) {
      return {
        value: input,
        text: input
      }
    }
  });

  $('.js-post-categories').change(function(){
    var $this = $(this);

    $.ajax({
      url: ("/posts/" + $this.data().id),
      dataType: "script",
      method: "PUT",
      data: {
        category_ids: $this.val()
      }
    });

    return true;
  })


  $('.info_button').click(function(e){
    var post_id = $(this).data().id;
    $('.accordion').foundation('down', $('#'+ post_id))
  })

  $('.js-upvote').click(function(e){
    e.preventDefault();
    var $upvote_button = $(this);

    makeRequest($upvote_button)
  })

  $('.js-downvote').click(function(e){
    e.preventDefault();
    var $downvote_button = $(this);

    makeRequest($downvote_button)
  })

  var makeRequest = function($button) {
    var a;

    request = {
      url: ($button.data().path),
      dataType: "json",
      method: "PUT",
      data: []
    };

    $.ajax(request).done(function(res) {
      changeButtons(res['result'], $button)
    });

    return true;
  }


  changeButtons = function(old_state, $button) {
    var type = $button.data().type;
    var $second_button = $button.siblings('a.js-' + opposite_name[type])

    if (old_state == 'new') {
      changeButtonStyle($button, type, 'secondary', button_class[type], 1)
    } else if (old_state == type) {
      changeButtonStyle($button, type, button_class[type], 'secondary', -1)
    } else {
      changeButtonStyle($button, type, 'secondary', button_class[type], 1)
      changeButtonStyle($second_button, opposite_name[type], button_class[opposite_name[type]], 'secondary', -1)
    }

    true;
  }

  changeButtonStyle = function($button, type, remove_class, add_class, value) {
    button_value = parseInt($button.text())
    $button.removeClass(remove_class)
    $button.addClass(add_class)
    $button.html((button_value + value) + " <i class=" + icon_name[type] + "></i>")
  }


  $('.js-publication-time').each(function() {
    var $this = $(this);
    var day_ago = moment().subtract(1,'days');
    var publiction_time = moment($this.text(), "DD-MM-YYYY hh:mm");

    if (publiction_time.isAfter(day_ago)) {
      $this.text(publiction_time.fromNow());
    } else {
      $this.text(publiction_time.format('lll'));
    }
  });
});
