class PageProxy::LinkRectifier
  def initialize(host_url)
    @host_uri = PageProxy::UriParser.new(host_url).parse
  end

  def rectify(relative_url, tag_name, tag_type)
    if relative_url.present?
      link = PageProxy::LinkHoster.new(relative_url, @host_uri).hosted_link
      PageProxy::LinkProxy.new(link, tag_name, tag_type).proxied_link
    else
      relative_url
    end
  end
end
