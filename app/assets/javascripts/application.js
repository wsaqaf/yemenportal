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

  var initializeFacebookSDK;

  var params =  $('#fb-root').data()

  initializeFacebookSDK = function() {
    var ref, ref1;
    FB.init({
      appId: params.appId,
      cookie: true,
      xfmbl: true,
      version: params.appVersion
    });
    return typeof FB !== "undefined" && FB !== null ? (ref1 = FB.XFBML) != null ? ref1.parse() : void 0 : void 0;
  };

  jQuery(function() {
    delete FB;
    return $.getScript("//connect.facebook.net/" + params.appLocale + "/sdk.js#xfbml=1&version=v2.3&appId=" + params.appId, function() {
      return initializeFacebookSDK();
    });
  });
});
