# Works with php-proxy-app deployed somewhere on our server
class PostProxy
  def initialize(post)
    @post = post
  end

  def iframe_url
    response['location']
  end

  private

  attr_reader :post

  def response
    @_response ||= Net::HTTP.post_form(proxy_url, url: post_link, proxy_secret: proxy_secret)
  rescue
    {
      'location' => post_link
    }
  end

  def proxy_url
    URI(Rails.application.secrets.proxy["url"])
  end

  def post_link
    post.link
  end

  def proxy_secret
    Rails.application.secrets.proxy["secret"]
  end
end
