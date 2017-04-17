# In Rails, you could put this in config/initializers/koala.rb
token = Koala::Facebook::OAuth.new(ENV["FACEBOOK_KEY"],  ENV["FACEBOOK_SECRET"]).get_app_access_token

Koala.configure do |config|
  config.access_token = token
  config.app_access_token = token

  config.app_id = ENV["FACEBOOK_KEY"]
  config.app_secret = ENV["FACEBOOK_SECRET"]
end
