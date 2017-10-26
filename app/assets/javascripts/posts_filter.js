document.addEventListener("turbolinks:load", function() {
  $(document).on('change', '.js-spotlight-form', function(event) {
    event.target.form.submit();
  });

  $(".posts-filter__source-select-box").selectize({
    plugins: ["remove_button", "restore_on_backspace"],
    delimiter: ",",
    create: false,
    persist: false
  });
});
