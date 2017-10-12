class LinksRectifier::UrlRectifier
  def initialize(base_url)
    @base_uri = URI.parse(base_url)
  end

  def rectify(relative_url)
    if relative_url.present?
      LinksRectifier::UriRectifier.new(relative_url).rectify(@base_uri)
    else
      relative_url
    end
  end
end
