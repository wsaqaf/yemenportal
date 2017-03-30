$(document).ready(function(){
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
    var params, request;

    params = {category_ids: $this.val()}

    request = {
      url: ("/posts/" + $this.data().id),
      dataType: "script",
      method: "PUT",
      data: params
    };

    $.ajax(request);

    true;
  })

  $('.js-like').click(function(e){
    e.preventDefault();
    var $this = $(this);

    doRequest($this)
    changeButtons('like', 'dislike', 'success', $this);
  })


  $('.js-dislike').click(function(){
    e.preventDefault();
    var $this = $(this);

    doRequest($this)
    changeButtons('dislike', 'like', 'alert', $this);
  })


  doRequest = function($this) {
    request = {
      url: ($this.data().path),
      dataType: "json",
      method: "PUT",
      data: []
    };

    $.ajax(request);

    true;
  }

  changeButtons = function(clik, unclik, button_style, $this) {
    var button_value;
    var $second_button = $this.siblings('a.js-' + unclik)

    button_value = parseInt($this.text())
    $this.after("<button type='button' class='button " + button_style + "'>" + (button_value +1) + " <i class=fi-" + clik + "></i></button>")
    $this.remove()

    second_button_value = $second_button.text()
    $second_button.after("<button type='button' class='button secondary'>" + second_button_value + "<i class=fi-" + unclik + "></i></button>")
    $second_button.remove()

    true;
  }
});
