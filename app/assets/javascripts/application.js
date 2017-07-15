//= require turbolinks
//= require jquery3
//= require jquery_ujs
//= require foundation
//= require selectize
//= require moment
//= require moment/ar-tn.js
//= require_tree .

window.facebookApi = new FacebookApi();

document.addEventListener("turbolinks:before-visit", function() {
  window.facebookApi.saveFbRootBeforeBodyChange(document);
});

document.addEventListener("turbolinks:before-render", function(event) {
  window.facebookApi.restoreFbRootAfterBodyChange(event.data.newBody);
});

document.addEventListener("turbolinks:load", function() {
  $(document).foundation();

  window.facebookApi.parseFbML();
});
