class PageProxy::UriParser
  BLANK_URL = "".freeze

  def initialize(url)
    @url = url
  end

  def parse
    URI.parse(URI.encode(@url))
  rescue URI::InvalidURIError
    URI.parse(BLANK_URL)
  end
end
