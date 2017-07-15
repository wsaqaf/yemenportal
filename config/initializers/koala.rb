# In Rails, you could put this in config/initializers/koala.rb
token = Koala::Facebook::OAuth.new(Rails.application.secrets.facebook["app_id"],
  Rails.application.secrets.facebook["secret"]).get_app_access_token

Koala.configure do |config|
  config.access_token = token
  config.app_access_token = token

  config.app_id = Rails.application.secrets.facebook["app_id"]
  config.app_secret = Rails.application.secrets.facebook["secret"]
end
