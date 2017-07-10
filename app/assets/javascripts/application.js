//= require turbolinks
//= require jquery3
//= require jquery_ujs
//= require foundation
//= require selectize
//= require moment
//= require moment/ar-tn.js
//= require_tree .

document.addEventListener("turbolinks:load", function() {
  $(document).foundation();
  $(document).foundation('topbar', 'reflow');
});
