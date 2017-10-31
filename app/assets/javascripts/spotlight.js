document.addEventListener("turbolinks:load", function() {
  const AUTO_UPDATING_FILTERS = [
    ".posts-spotlight__set-select-box",
    ".posts-spotlight__time-select-box"
  ].join(", ");

  $(document).on("change", AUTO_UPDATING_FILTERS, function(event) {
    event.target.form.submit();
  });

  $(".posts-spotlight__multiple-select-box").selectize({
    plugins: ["remove_button", "restore_on_backspace"],
    delimiter: ",",
    create: false,
    persist: false
  });
});
