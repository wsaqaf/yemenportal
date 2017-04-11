document.addEventListener("turbolinks:load", function() {
  $( ".sources .textarea" ).each(function() {
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
      url: ("/source/" + post_id + "/source_updater"),
      dataType: "script",
      method: "PUT",
      data: { [name] : new_value}
    }).fail(function() {
      $this.val($this.prop("defaultValue"));
    });

    true;
  }
});
