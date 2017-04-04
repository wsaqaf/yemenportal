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
});
