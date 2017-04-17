# In Rails, you could put this in config/initializers/koala.rb
Koala.configure do |config|
  config.access_token = '589532491165068|DmHvv4umqujsyatNKbX0LkJNG44'
  config.app_access_token = '589532491165068|DmHvv4umqujsyatNKbX0LkJNG44'
  config.app_id = '589532491165068'
  config.app_secret = 'd1d811872c3e144d6e947858ac4a16fb'


  # @oauth = Koala::Facebook::OAuth.new('589532491165068', 'd1d811872c3e144d6e947858ac4a16fb')
  # @oauth.get_app_access_token
  # a = Koala::Facebook::API.new('589532491165068|DmHvv4umqujsyatNKbX0LkJNG44','d1d811872c3e144d6e947858ac4a16fb')
  # a.get_connection('ByRoR', 'posts')
end
