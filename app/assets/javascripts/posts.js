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
});
