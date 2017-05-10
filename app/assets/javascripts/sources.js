document.addEventListener("turbolinks:load", function() {
  $('.sources .textarea').each(function() {
    var $this = $(this);
    $this[0].defaultValue = $this.text();
  });

  $('.sources input').focusout(function(){
    var $this = $(this);
    var new_value = $this.val();
    var name = $this[0].name

    doRequest($this, new_value, name)
  })

  $('.sources .textarea').focusout(function(){
    var $this = $(this);
    var new_value = $this.text()
    var name = $this[0].getAttribute('name')

    doRequest($this, new_value, name)
  })


  doRequest = function($this, new_value, name) {
    var post_id = $this.closest('.sources').find('input:hidden')[0].id;

    $.ajax({
      url: ("/api/sources/" + post_id),
      dataType: "script",
      method: "PUT",
      data: { [name] : new_value}
    }).fail(function(xhr) {
      var errors = $.parseJSON(xhr.responseText).errors
      if ($this.next('small').length != 0) {
        $this.next('small').remove();
      }

      if (errors[name] != undefined) {
        $this.after("<small class='error'>" + errors[name] + "</small>");
      }
      $this.val($this.prop("defaultValue"));
    }).done(function() {
      if ($this.next('small').length != 0) {
        $this.next('small').remove();
      }
    });

    true;
  }
});
