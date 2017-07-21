document.addEventListener("turbolinks:load", function() {
  $(".js-users-filter__roles").selectize({
    plugins: ["remove_button"]
  });
});
