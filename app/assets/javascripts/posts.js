document.addEventListener("turbolinks:load", function() {
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

  $('.js-upvote').click(function(e){
    e.preventDefault();
    var $upvote_button = $(this);

    makeRequest($upvote_button)
    changeButtons('upvote', 'downvote', 'success', $upvote_button);
  })


  $('.js-downvote').click(function(e){
    e.preventDefault();
    var $downvote_button = $(this);

    makeRequest($downvote_button)
    changeButtons('downvote', 'upvote', 'alert', $downvote_button);
  })


  var makeRequest = function($button) {
    request = {
      url: ($button.data().path),
      dataType: "json",
      method: "PUT",
      data: []
    };

    $.ajax(request);

    true;
  }

  changeButtons = function(clik, unclik, button_style, $button) {
    var button_value;
    var icon_name = {upvote: 'fi-like', downvote: 'fi-dislike'};
    var $second_button = $button.siblings('a.js-' + unclik)

    button_value = parseInt($button.text())
    $button.after("<button type='button' class='button " + button_style + "'>" + (button_value +1) + " <i class=" + icon_name[clik] + "></i></button>")
    $button.remove()

    second_button_value = $second_button.text()
    $second_button.after("<button type='button' class='button secondary'>" + second_button_value + "<i class=" + icon_name[unclik] + "></i></button>")
    $second_button.remove()

    true;
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
