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
    var postId = $(this).data().id;
    $('.accordion').foundation('down', $('#'+ postId))
  })

  $('.js-upvote').click(function(e){
    e.preventDefault();
    var $upvoteButton = $(this);

    makeRequest($upvoteButton)
  })

  $('.js-downvote').click(function(e){
    e.preventDefault();
    var $downvoteButton = $(this);

    makeRequest($downvoteButton)
  })

  var makeRequest = function($button) {
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
    var $second_button = $button.parents('.vote_info').find('a.js-' + opposite_name[type])

    if (type == 'downvote') {
      count_offset = -1
    } else {
      count_offset = 1
    }

    if (old_state == 'new') {
      changeButtonStyle($button, type, 'secondary', button_class[type], 1 * count_offset)
    } else if (old_state == type) {
      changeButtonStyle($button, type, button_class[type], 'secondary', -1 * count_offset)
    } else {
      changeButtonStyle($button, type, 'secondary', button_class[type], 2 * count_offset)
      changeButtonStyle($second_button, opposite_name[type], button_class[opposite_name[type]], 'secondary', 0)
    }

    true;
  }

  changeButtonStyle = function($button, type, remove_class, add_class, value) {
    $counter = $button.parent().siblings('.vote_count')
    button_value = parseInt($counter.text())
    $button.removeClass(remove_class).addClass(add_class)
    $counter.html((button_value + value))
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
