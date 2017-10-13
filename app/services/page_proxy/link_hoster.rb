class PageProxy::LinkHoster
  def initialize(link, host_uri)
    @host_uri = host_uri
    @link = PageProxy::UriParser.new(link).parse
  end

  def hosted_link
    host_to_absolute if relative_link?
    @link.to_s
  end

  private

  def host_to_absolute
    @link.scheme = @host_uri.scheme
    @link.host = @host_uri.host
  rescue URI::InvalidURIError
    false
  end

  def relative_link?
    @link.host.blank?
  end
end
