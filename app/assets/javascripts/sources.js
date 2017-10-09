document.addEventListener("turbolinks:load", function() {
  const ENTER_KEY_CODE = 13;

  $('.sources .textarea').each(function() {
    var $this = $(this);
    $this[0].defaultValue = $this.text();
  });

  $('.sources input').focusout(function(){
    var $this = $(this);
    var new_value = $this.val();
    var name = $this[0].name;

    doRequest($this, new_value, name)
  });

  $('.sources .textarea').focusout(function(){
    var $this = $(this);
    var new_value = $this.text();
    var name = $this[0].getAttribute('name');

    doRequest($this, new_value, name)
  });

  $('.sources input').keypress(function (event) {
    if (event.keyCode === ENTER_KEY_CODE) {
        $(this).blur();
    }
  }).bind(ENTER_KEY_CODE);


  doRequest = function($this, newValue, name) {
    var postId = $this.closest('.sources').find('input:hidden')[0].id;
    var postData = {};
    postData[name] = newValue;

    $.ajax({
      url: ("/api/sources/" + postId),
      dataType: "script",
      method: "PUT",
      data: postData
    }).fail(function(xhr) {
      var errors = $.parseJSON(xhr.responseText).errors;
      if ($this.next('small').length !== 0) {
        $this.next('small').remove();
      }
      if (errors[name] !== undefined) {
        $this.after("<small class='error'>" + errors[name] + "</small>");
      }
      $this.val($this.prop("defaultValue"));
    }).done(function() {
      if ($this.next('small').length !== 0) {
        $this.next('small').remove();
      }
    });
  }
});
