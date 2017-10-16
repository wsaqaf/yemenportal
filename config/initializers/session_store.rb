# Be sure to restart your server when you modify this file.

Rails.application.config.session_store :cookie_store,
  key: "_yemenportal_session",
  secure: Rails.application.config_for(:external_site_embedding)["cookies_security_flag"]
