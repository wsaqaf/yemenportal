document.addEventListener("turbolinks:load", function() {
  $(".post-reviews__categories-selector").selectize({
    plugins: ["remove_button", "restore_on_backspace"],
    delimiter: ",",
    create: false,
    persist: false
  });

  $(".post-reviews__categories-selector").change(function() {
    var $this = $(this);

    $.ajax({
      url: $this.data().updatePath,
      dataType: "JSON",
      method: "PUT",
      data: { category_ids: $this.val() },
      success: function (data) {
        $('.post__subtitle-item--categories').html(data.category_names);
      }
    });

    return true;
  })
});
