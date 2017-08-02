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

  $('select.strong-multiselect').selectize({
    plugins: ['remove_button', 'restore_on_backspace'],
    delimiter: ',',
    create: false,
    persist: false
  });

  $('.js-post-categories').change(function(){
    var $this = $(this);
    var post_data = {}

    if ($this.val().length > 0) {
      post_data[$this.data().type] = $this.val()
    } else {
      post_data[$this.data().type] = ['']
    }

    $.ajax({
      url: ("/posts/" + $this.data().id),
      dataType: "script",
      method: "PUT",
      data: post_data
    });

    return true;
  })

  $('.js-publication-time').each(function() {
    var $this = $(this);
    var day_ago = moment().subtract(1,'days');
    var publiction_time = moment($this.text());

    if (publiction_time.isAfter(day_ago)) {
      $this.text(publiction_time.fromNow());
    } else {
      $this.text(publiction_time.format('lll'));
    }
  });
});
